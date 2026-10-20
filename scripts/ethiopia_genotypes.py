"""Extract source-attributed genotype trial means from open-access JATS XML.

Study: Seid et al. 2023, Plants 12(14):2625, DOI 10.3390/plants12142625.
Single location (Holetta, Ethiopia), 2019, 45 genotypes, three
experimental replications. Published means are NOT plot-level observations.

Keep dry-weight Fe/Zn concentrations distinct from fresh-weight yield.
Only descriptive dominance/Pareto screening: no causal claims or p-values.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from decimal import Decimal, InvalidOperation
from pathlib import Path

SOURCE_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10383430/fullTextXML"
SOURCE_SHA256 = "f3afe300384cd6f7b0c24bf44dbe24ebad8ef1de6ceefcd414845794e6aacd78"
STUDY_DOI = "10.3390/plants12142625"
TABLE_ID = "plants-12-02625-t002"
COUNT = 45
FIELDS = [
    "genotype", "yield_kg_m2_fresh", "dry_matter_pct", "iron_mg_kg_dry",
    "zinc_mg_kg_dry", "iron_g_ha_theoretical", "zinc_g_ha_theoretical",
    "pareto_yield_iron_zinc", "source_doi", "site", "study_year", "data_level"
]


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def decimal(raw: str, *, positive: bool = True) -> Decimal:
    try:
        value = Decimal(raw)
    except (InvalidOperation, ValueError) as error:
        raise ValueError(f"Invalid numeric entry {raw!r}") from error
    if not value.is_finite() or value < 0 or (positive and value == 0):
        raise ValueError(f"Non-positive/non-finite numeric entry {raw!r}")
    return value


def read_rows(path: Path, expected_sha: str = SOURCE_SHA256) -> list[dict]:
    actual = sha256(path)
    if actual != expected_sha:
        raise ValueError("Source fullTextXML SHA-256 differs from audited release")
    root = ET.fromstring(Path(path).read_bytes())
    ids = {"".join(x.itertext()).strip() for x in root.findall(".//article-id[@pub-id-type='doi']")}
    if STUDY_DOI not in ids:
        raise ValueError(f"Unexpected article DOI: {sorted(ids)}")
    found = root.findall(f".//table-wrap[@id='{TABLE_ID}']")
    if len(found) != 1:
        raise ValueError("Cannot locate unique source Table 2")
    table = found[0].find(".//table")
    if table is None:
        raise ValueError("Source Table 2 has no structured table")
    rows = []
    for tr in table.findall(".//tr"):
        cells = [" ".join("".join(cell.itertext()).split())
                 for cell in tr if cell.tag in ("td", "th")]
        if not cells:
            continue
        if len(cells) != 9:
            raise ValueError(f"Table 2 row with unexpected number of columns: {cells}")
        name = cells[0]
        if name in ("Genotypes", "Range", "Mean"):
            continue
        if not (re.fullmatch(r"CIP[0-9]{6}\.[0-9]{3}",name) or name=="Gudanie"):
            raise ValueError(f"Unexpected genotype identifier {name}")
        numbers = []
        for index in (3,4,7,8):
            # Every relevant cell begins with a numeric mean; followed by
            # a superscript Tukey-letter grouping that MUST NOT be interpreted
            # as a second measurement.
            token = re.match(r"^([0-9]+(?:\.[0-9]+)?)(?:\s|$)",cells[index])
            if not token:
                raise ValueError(f"Missing published mean in {name}: {cells[index]}")
            numbers.append(decimal(token.group(1)))
        yield_fresh, dry_pct, fe_dry, zn_dry = numbers
        if dry_pct > 100:
            raise ValueError(f"Impossible dry matter percentage: {name}")
        # kg fresh/m2 * DM% / 100 => kg dry/m2; concentration mg/kg dry
        # *10,000 m2/ha /1000 mg/g = g/ha; illustrative nutrient mass
        # before harvest loss, cooking, absorption, and safety constraints.
        iron_g_ha = yield_fresh * dry_pct / 100 * fe_dry * 10
        zinc_g_ha = yield_fresh * dry_pct / 100 * zn_dry * 10
        rows.append({
            "genotype":name, "yield_kg_m2_fresh":str(yield_fresh),
            "dry_matter_pct":str(dry_pct),
            "iron_mg_kg_dry":str(fe_dry), "zinc_mg_kg_dry":str(zn_dry),
            "iron_g_ha_theoretical":str(iron_g_ha),
            "zinc_g_ha_theoretical":str(zinc_g_ha),
            "pareto_yield_iron_zinc":"",
            "source_doi":STUDY_DOI, "site":"Holetta, Ethiopia",
            "study_year":"2019", "data_level":"genotype_reported_means",
        })
    if len(rows) != COUNT or len({r["genotype"] for r in rows}) != COUNT:
        raise ValueError(f"Expected {COUNT} unique genotype rows, got {len(rows)}")
    index = {r["genotype"]:r for r in rows}
    for genotype,field,value in [
        ("Gudanie","iron_mg_kg_dry","14.68"),
        ("Gudanie","yield_kg_m2_fresh","1.91"),
        ("CIP312767.014","iron_mg_kg_dry","26.07"),
        ("CIP312767.014","zinc_mg_kg_dry","19.14"),
        ("CIP312735.062","yield_kg_m2_fresh","2.26"),
    ]:
        if index.get(genotype,{}).get(field)!=value:
            raise ValueError(f"Primary table anchor mismatch for {genotype}/{field}")
    goals=("yield_kg_m2_fresh","iron_mg_kg_dry","zinc_mg_kg_dry")
    for candidate in rows:
        dominates = any(
            all(Decimal(other[key])>=Decimal(candidate[key]) for key in goals) and
            any(Decimal(other[key])>Decimal(candidate[key]) for key in goals)
            for other in rows if other is not candidate
        )
        candidate["pareto_yield_iron_zinc"] = "false" if dominates else "true"
    return rows


def execute(source: Path, output: Path, expected_sha: str = SOURCE_SHA256) -> dict:
    rows = read_rows(source, expected_sha=expected_sha)
    output = Path(output)
    output.mkdir(parents=True,exist_ok=True)
    csv_path=output/"genotype_trial_holetta_2019.csv"
    with csv_path.open("w",encoding="utf-8",newline="") as file:
        writer=csv.DictWriter(file,fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    count_pareto=sum(r["pareto_yield_iron_zinc"]=="true" for r in rows)
    summary={
        "doi":STUDY_DOI, "source":SOURCE_URL, "source_sha256":sha256(source),
        "derived_csv_sha256":sha256(csv_path), "table_id":TABLE_ID,
        "genotypes":len(rows), "pareto_candidates":count_pareto,
        "site":"Holetta, Ethiopia", "year":2019,
        "design":"published means from three-replication single-site trial; not plot-level observations",
        "units":"fresh yield kg/m2, dry matter percentage, Fe/Zn mg per kg DRY; mass potential g/ha theoretical",
        "limitations":[
            "Genotype-specific means from only one location/year, NOT multi-environment validation.",
            "No confidence intervals or genotype significance tests can be reconstructed from genotype means alone.",
            "Pareto dominance is descriptive of reported point estimates; not statistical superiority.",
            "Nutrient mass/ha is theoretical before losses, edible fraction, processing or human bioavailability.",
            "Do not pool with USDA fresh 100-g concentrations, or infer cultivar registration or deployability.",
        ],
    }
    (output/"genotype_trial_provenance.json").write_text(
        json.dumps(summary,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
    pareto=[r for r in rows if r["pareto_yield_iron_zinc"]=="true"]
    lines=[
        "# Cultivares y clones de papa: Holetta, Etiopía (2019)",
        "",
        f"**Estudio publicado:** DOI [{STUDY_DOI}](https://doi.org/{STUDY_DOI});",
        "**45 genotipos, tres repeticiones, un único ambiente.**",
        "Se usan las medias de Tabla 2 y no se reconstruyen réplicas ni efectos G×E.",
        "",
        f"Se identificaron **{count_pareto} genotipos no dominados** en el espacio",
        "(rendimiento de tubérculo fresco, concentración de hierro y concentración de zinc).",
        "Esto es un filtro **descriptivo de medias publicadas**, no una recomendación varietal.",
        "",
        "| Genotipo no dominado | Rendimiento kg/m² fresco | Fe mg/kg SECO | Zn mg/kg SECO |",
        "|---|---:|---:|---:|",
    ]
    for r in sorted(pareto,key=lambda x:Decimal(x["yield_kg_m2_fresh"]),reverse=True):
        lines.append(
            f'| {r["genotype"]} | {r["yield_kg_m2_fresh"]} | '
            f'{r["iron_mg_kg_dry"]} | {r["zinc_mg_kg_dry"]} |')
    lines += [
        "", "La masa potencial de nutrientes por hectárea es una **ilustración dimensional**",
        "de rendimiento fresco × fracción de materia seca × concentración en peso seco.",
        "No equivale a nutrientes comestibles, disponibles, absorbidos ni producción multisitio.",
        "No mezclar mg/kg **seco** del estudio con mg/100g **fresco** del USDA.",
        "La investigación de cultivo en otros sitios es una tarea separada y pendiente.",
        "",
        f"Fuente primaria XML: {SOURCE_URL}",
        f"SHA-256 fuente: {summary['source_sha256']}",
    ]
    (output/"genotype_trial_report.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    return summary


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--xml",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(execute(args.xml,args.out),indent=2))


if __name__=="__main__":
    main()

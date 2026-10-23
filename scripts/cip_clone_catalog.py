"""Reproducible extraction of CIP 29-clone biofortification catalogue.

Original file: CIP Dataverse doi:10.21223/P3/LQOT7Z, version 1.2.
CC BY 4.0 according to Dataverse "termsOfUse". XLS original checked against
Dataverse MD5 AND pinned source SHA-256. Source is 29 clone-level CATALOG
RECORDS, *not* a replicated, multi-site genotype-environment experiment.

Uses xlrd 2.0.2 ONLY for old Excel 97-2003 .xls format in this importer.
All analytical outputs are CSV/JSON/Markdown and can be tested offline.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path

SOURCE_DOI = "10.21223/P3/LQOT7Z"
SOURCE_VERSION = "1.2"
SOURCE_LINK = f"https://doi.org/{SOURCE_DOI}"
SOURCE_URL = "https://data.cipotato.org/api/access/datafile/2211"
DICTIONARY_URL = "https://data.cipotato.org/api/access/datafile/2212"
SOURCE_SHA256 = "58706bfb9052220dccc89412d14033c750e7911861d03b5e6c4c5871b2135226"
DICTIONARY_SHA256 = "905c0cf39f4ad1d2b9d34dfb698440f49304992d6370f3ec8a76afbdb7298525"
SOURCE_MD5 = "9899ade1e320484b2a909e75a3e1d486"
DICTIONARY_MD5 = "755da0d1d91d09873ec95fe68451f928"
EXPECTED_SHEET = "Catalog_BIOT_clones"
N_CLONES = 29

# Prefix columns are intentionally anchored to the official source sheet.
HEADERS = [
    "Accession Number","Collecting number/Breeder code","Population Group",
    "Parent Female","Parent Male","Predominant tuber skin color",
    "Tuber skin secondary color","Distribution of secondary tuber skin color",
    "Predominant tuber flesh color","Tuber flesh secondary color",
    "Distribution of secondary flesh color","General tuber shape",
    "Unusual tuber shape","Tuber shape depth of eyes","Late blight (LB)",
    "Potato virus Y (PVY)","Tuber yield (Kg/plants)",
    "Growing period lowland","Growing period highland","Dry matter (%)",
    "Chipping color","After cooking darkening","Texture of tuber after cooking",
    "Flavour","Vitamin C (mg/100g, dry weight basis)",
    "Fe (mg/kg, dry weight basis)","Fe (mg/kg, dry weight basis) min",
    "Fe (mg/kg, dry weight basis) max","Zn (mg/kg, dry weight basis)",
    "Zn (mg/kg, dry weight basis) min","Zn (mg/kg, dry weight basis) max"
]
OUT = [
    "accession_id","breeder_code","female_parent","male_parent",
    "yield_kg_per_plant","dry_matter_percent",
    "vitamin_c_mg_per_100g_dry","vitamin_c_status",
    "iron_mg_per_kg_dry","iron_min_mg_per_kg_dry","iron_max_mg_per_kg_dry",
    "zinc_mg_per_kg_dry","zinc_min_mg_per_kg_dry","zinc_max_mg_per_kg_dry",
    "late_blight_label","pvy_label","flavour_label",
    "pareto_yield_fe_zn","source_doi","data_level",
]


def digest(path: Path, algorithm: str = "sha256") -> str:
    h=hashlib.new(algorithm)
    with Path(path).open("rb") as file:
        for block in iter(lambda:file.read(1024*1024),b""):
            h.update(block)
    return h.hexdigest()


def _parse_number(val, *, field, can_be_blank=False) -> Decimal | None:
    if val is None or val=="":
        if can_be_blank:return None
        raise ValueError(f"{field} unexpectedly missing: ND cannot be zero")
    try:
        parsed=Decimal(str(val))
    except (ValueError,InvalidOperation) as exc:
        raise ValueError(f"Invalid numeric {field}: {val!r}") from exc
    if not parsed.is_finite() or parsed<=0:
        raise ValueError(f"Expected positive finite {field}: {val!r}")
    return parsed


def parse_catalog(header: list, records: list[list]) -> list[dict[str,str]]:
    prefix = [str(x).strip() for x in header[:len(HEADERS)]]
    if prefix != HEADERS:
        wrong=[(i,w,a) for i,(w,a) in enumerate(zip(HEADERS,prefix)) if w!=a]
        raise ValueError(f"Original CIP columns changed: {wrong[:5]}")
    if len(records)!=N_CLONES:
        raise ValueError(f"Expected exactly {N_CLONES} CIP catalogue clone entries")
    result=[]
    for number, row in enumerate(records,2):
        if len(row)<len(HEADERS):
            raise ValueError(f"Missing CIP columns on Excel row {number}")
        code=str(row[0]).strip()
        if not re.fullmatch(r"CIP[0-9]{6}\.[0-9]{3}",code):
            raise ValueError(f"Unexpected accession identifier at row {number}: {code!r}")
        if code in (r["accession_id"] for r in result):
            raise ValueError(f"Duplicate accession in catalogue: {code}")
        yield_=_parse_number(row[16],field=f"{code} yield")
        dm=_parse_number(row[19],field=f"{code} dry matter")
        if dm>100:
            raise ValueError(f"Dry matter greater than 100% for {code}")
        c=_parse_number(row[24],field=f"{code} vitamin C",can_be_blank=True)
        fe=_parse_number(row[25],field=f"{code} iron")
        fe_min=_parse_number(row[26],field=f"{code} iron min")
        fe_max=_parse_number(row[27],field=f"{code} iron max")
        zn=_parse_number(row[28],field=f"{code} zinc")
        zn_min=_parse_number(row[29],field=f"{code} zinc min")
        zn_max=_parse_number(row[30],field=f"{code} zinc max")
        if not fe_min<=fe<=fe_max or not zn_min<=zn<=zn_max:
            raise ValueError(f"Published minimum/mean/maximum inconsistent for {code}")
        result.append({
            "accession_id":code,
            "breeder_code":str(row[1]).strip(),
            "female_parent":str(row[3]).strip(),
            "male_parent":str(row[4]).strip(),
            "yield_kg_per_plant":str(yield_),
            "dry_matter_percent":str(dm),
            "vitamin_c_mg_per_100g_dry":str(c) if c is not None else "",
            "vitamin_c_status":"observed" if c is not None else "not_reported",
            "iron_mg_per_kg_dry":str(fe),
            "iron_min_mg_per_kg_dry":str(fe_min),
            "iron_max_mg_per_kg_dry":str(fe_max),
            "zinc_mg_per_kg_dry":str(zn),
            "zinc_min_mg_per_kg_dry":str(zn_min),
            "zinc_max_mg_per_kg_dry":str(zn_max),
            "late_blight_label":str(row[14]).strip(),
            "pvy_label":str(row[15]).strip(),
            "flavour_label":str(row[23]).strip(),
            "pareto_yield_fe_zn":"",
            "source_doi":SOURCE_DOI,
            "data_level":"catalogue_clone_summary",
        })
    goals=("yield_kg_per_plant","iron_mg_per_kg_dry","zinc_mg_per_kg_dry")
    for candidate in result:
        dominated=any(
            all(Decimal(other[k])>=Decimal(candidate[k]) for k in goals) and
            any(Decimal(other[k])>Decimal(candidate[k]) for k in goals)
            for other in result if other is not candidate
        )
        candidate["pareto_yield_fe_zn"] = "false" if dominated else "true"
    return result


def read_xls(source: Path) -> tuple[list,list[list]]:
    try:
        import xlrd
    except ImportError as exc:
        raise RuntimeError("CIP legacy Excel importer needs pinned dependency xlrd==2.0.2") from exc
    book=xlrd.open_workbook(str(source))
    if book.sheet_names()!=[EXPECTED_SHEET]:
        raise ValueError(f"Unexpected CIP Excel sheets: {book.sheet_names()}")
    sheet=book.sheet_by_name(EXPECTED_SHEET)
    if sheet.nrows!=N_CLONES+1 or sheet.ncols<31:
        raise ValueError(f"Source dimensions mismatch: {sheet.nrows} rows, {sheet.ncols} columns")
    return [sheet.cell_value(0,i) for i in range(sheet.ncols)],[
        [sheet.cell_value(row,i) for i in range(sheet.ncols)]
        for row in range(1,sheet.nrows)
    ]


def run(source: Path,dictionary: Path,output: Path) -> dict:
    expected = (
        (source,SOURCE_SHA256,SOURCE_MD5),
        (dictionary,DICTIONARY_SHA256,DICTIONARY_MD5)
    )
    for path,sha,md5 in expected:
        if digest(path)!=sha or digest(path,"md5")!=md5:
            raise ValueError(f"Unverified CIP file release or modified data: {path}")
    # Both files must be recognized as XLS. Dictionary not interpreted as a
    # genotype dataset; it is retained as source-defined ontology documentation.
    header,contents=read_xls(source)
    dict_header,dict_records=read_xls_dictionary(dictionary)
    result=parse_catalog(header,contents)
    output=Path(output)
    output.mkdir(parents=True,exist_ok=True)
    outfile=output/"cip_29_clones_catalogue.csv"
    with outfile.open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=OUT);writer.writeheader();writer.writerows(result)
    pareto=[r for r in result if r["pareto_yield_fe_zn"]=="true"]
    provenance={
        "doi":SOURCE_DOI,"dataverse_version":SOURCE_VERSION,
        "source_url":SOURCE_URL,"dictionary_url":DICTIONARY_URL,
        "license":"CC BY 4.0 per Dataverse dataset termsOfUse",
        "source_sha256":digest(source),"dictionary_sha256":digest(dictionary),
        "derived_csv_sha256":digest(outfile),
        "source_sheet":EXPECTED_SHEET,
        "source_rows":N_CLONES,"source_column_count":len(header),
        "dictionary_variables":len(dict_records),
        "clone_summaries":len(result),"pareto_candidates":len(pareto),
        "trait_definition":{
            "yield":"kg/plant as labeled in source, NOT t/ha",
            "iron":"mg/kg DRY matter",
            "zinc":"mg/kg DRY matter",
            "vitamin_c":"mg/100g DRY matter",
            "reported_min_max":"published range; not a confidence interval, no sample sizes provided",
        },
        "restrictions":[
            "The 29 entries are catalogue-level summaries, not replicate plot data or multi-environment study.",
            "No genotype-by-environment model or statistical significance may be computed from catalogue ranges.",
            "Comparing concentration and yield by Pareto is descriptive; not validation of combined performance.",
            "Catalogue disease labels and flavor are categorical, not safety or farmer acceptance certificates.",
            "Min/max must not be imputed as confidence intervals; missing vitamin C must not become zero.",
            "Yield kg/plant cannot be converted to t/ha without planting density and plot design.",
            "Dried-basis nutrients cannot be compared to fresh-weight USDA values without matched conversions.",
            "Source retains pedigree identifiers, not confirmed whole-genome sequence or genotype proof.",
        ],
    }
    (output/"cip_29_clones_provenance.json").write_text(
        json.dumps(provenance,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    lines=[
        "# CIP — 29 clones de papa biofortificada (catálogo publicado)",
        "",
        f"Fuente DOI [{SOURCE_DOI}]({SOURCE_LINK}), Dataverse {SOURCE_VERSION}, CC BY 4.0.",
        "**Datos catalogados, no un nuevo experimento de OpenPotato ni un ensayo G×E.**",
        "",
        f"Se verificaron {len(result)} accesiones con identificador CIP y "
        f"**{len(pareto)} no dominadas** en rendimiento kg/planta, Fe y Zn mg/kg seco.",
        "",
        "| Accesión no dominada | Rendimiento kg/planta | Fe mg/kg SECO | Zn mg/kg SECO | Vit C mg/100g SECO |",
        "|---|---:|---:|---:|---:|",
    ]
    for r in sorted(pareto,key=lambda r:Decimal(r["yield_kg_per_plant"]),reverse=True):
        lines.append(
            f'| {r["accession_id"]} | {r["yield_kg_per_plant"]} | '
            f'{r["iron_mg_per_kg_dry"]} | {r["zinc_mg_per_kg_dry"]} | '
            f'{r["vitamin_c_mg_per_100g_dry"] or "ND"} |'
        )
    lines.extend([
        "", "Los rangos mínimos/máximos originales están disponibles en CSV,",
        "pero no traen replicación y población de muestreo comprobables:",
        "**NO son intervalos de confianza ni evidencian estabilidad genética.**",
        "",
        "No calcular nutrientes por superficie desde rendimiento kg/planta sin densidad verificada.",
        "No combinar numéricamente este estudio con muestras USDA ni con Holetta 2019.",
        "",
        f"Fuente Dataverse: {SOURCE_LINK}",
        f"SHA-256 original: {digest(source)}",
        "",
    ])
    (output/"cip_29_clones_report.md").write_text("\n".join(lines),encoding="utf-8")
    return provenance


def read_xls_dictionary(path: Path):
    import xlrd
    book=xlrd.open_workbook(str(path))
    if "Sheet1" not in book.sheet_names():
        raise ValueError("CIP dictionary sheet missing")
    sheet=book.sheet_by_name("Sheet1")
    if sheet.nrows<20:
        raise ValueError("Incomplete dictionary file")
    cols=[str(sheet.cell_value(0,i)).strip() for i in range(sheet.ncols)]
    if cols[:2]!=["Variable ID","Variable name"]:
        raise ValueError("Unexpected CIP dictionary schema")
    return cols, [[sheet.cell_value(i,j) for j in range(sheet.ncols)]
                  for i in range(1,sheet.nrows)]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--xls",required=True,type=Path)
    p.add_argument("--dictionary",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    print(json.dumps(run(args.xls,args.dictionary,args.out),indent=2,ensure_ascii=False))


if __name__=="__main__":
    main()

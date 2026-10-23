"""Auditable intersection of two published CIP clone datasets (not G×E).

Sources:
- CIP Dataverse Catalogue DOI 10.21223/P3/LQOT7Z (clone summaries);
- Seid et al. 2023, DOI 10.3390/plants12142625 (Holetta 2019 means).

Exact clone accession IDs are joined. Fe and Zn both mg/kg DRY.
Yield is NEVER compared (kg/plant vs kg/m²), nor are these data
treated as an experimental matched multi-location design.
"""
import argparse
import csv
import hashlib
import json
from decimal import Decimal
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
A=ROOT/"datasets"/"cip_catalogue"/"cip_29_clones_catalogue.csv"
B=ROOT/"datasets"/"cultivars"/"genotype_trial_holetta_2019.csv"
PM_A=ROOT/"datasets"/"cip_catalogue"/"cip_29_clones_provenance.json"
PM_B=ROOT/"datasets"/"cultivars"/"genotype_trial_provenance.json"
HEADERS=[
    "clone","iron_catalogue_mg_kg_dry","iron_holetta_mg_kg_dry","iron_delta_holetta_minus_catalogue",
    "zinc_catalogue_mg_kg_dry","zinc_holetta_mg_kg_dry","zinc_delta_holetta_minus_catalogue",
    "catalogue_vitamin_c_mg_100g_dry","catalogue_vitamin_c_status",
    "catalogue_yield_unit","holetta_yield_unit","comparison_design"
]

def checksum(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def rows(path,key):
    with Path(path).open(newline="",encoding="utf-8") as f:
        reader=csv.DictReader(f)
        output={}
        for row in reader:
            name=row[key]
            if not name or name in output:raise ValueError(f"Missing/duplicate clone identifier in {path}")
            output[name]=row
        return output

def run(a:A.__class__=A,b:B.__class__=B,pa=PM_A,pb=PM_B,out=ROOT/"reports"/"m1-cross-studies"):
    pa=json.loads(Path(pa).read_text())
    pb=json.loads(Path(pb).read_text())
    if checksum(a)!=pa["derived_csv_sha256"] or checksum(b)!=pb["derived_csv_sha256"]:
        raise ValueError("Source snapshot SHA-256 mismatch; cannot join")
    if pa["doi"]!="10.21223/P3/LQOT7Z" or pb["doi"]!="10.3390/plants12142625":
        raise ValueError("DOI source mismatch")
    cat=rows(a,"accession_id")
    eth=rows(b,"genotype")
    common=sorted(set(cat)&set(eth))
    if not common:raise ValueError("No identified shared accessions")
    compared=[]
    for name in common:
        ca,et=cat[name],eth[name]
        fe_a,fe_b=Decimal(ca["iron_mg_per_kg_dry"]),Decimal(et["iron_mg_kg_dry"])
        zn_a,zn_b=Decimal(ca["zinc_mg_per_kg_dry"]),Decimal(et["zinc_mg_kg_dry"])
        if min(fe_a,fe_b,zn_a,zn_b)<=0:
            raise ValueError("Invalid or missing chemical concentration")
        if ca["vitamin_c_status"] not in ("observed","not_reported"):
            raise ValueError("Invalid vitamin C missingness state")
        if ca["vitamin_c_status"]=="not_reported" and ca["vitamin_c_mg_per_100g_dry"]:
            raise ValueError("ND vitamin C has invented number")
        compared.append({
            "clone":name,
            "iron_catalogue_mg_kg_dry":str(fe_a),
            "iron_holetta_mg_kg_dry":str(fe_b),
            "iron_delta_holetta_minus_catalogue":str(fe_b-fe_a),
            "zinc_catalogue_mg_kg_dry":str(zn_a),
            "zinc_holetta_mg_kg_dry":str(zn_b),
            "zinc_delta_holetta_minus_catalogue":str(zn_b-zn_a),
            "catalogue_vitamin_c_mg_100g_dry":ca["vitamin_c_mg_per_100g_dry"],
            "catalogue_vitamin_c_status":ca["vitamin_c_status"],
            "catalogue_yield_unit":"kg/plant",
            "holetta_yield_unit":"kg/m2_fresh",
            "comparison_design":"non_matched_published_summaries",
        })
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    csvpath=out/"matched_cip_clones.csv"
    with csvpath.open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=HEADERS);writer.writeheader();writer.writerows(compared)
    report={
        "catalogue_doi":pa["doi"],"holetta_doi":pb["doi"],
        "catalogue_sha256":checksum(a),"holetta_sha256":checksum(b),
        "derived_csv_sha256":checksum(csvpath),
        "catalogue_accessions":len(cat),"holetta_accessions":len(eth),
        "exactly_matching_accessions":len(common),
        "iron_holetta_lower_count":sum(Decimal(r["iron_delta_holetta_minus_catalogue"])<0 for r in compared),
        "zinc_holetta_lower_count":sum(Decimal(r["zinc_delta_holetta_minus_catalogue"])<0 for r in compared),
        "design":"EXPLORATORY source reconciliation only; NOT a paired field experiment or G×E",
        "units":"Fe/Zn mg/kg dry matter in both sources; yields incomparable and not analyzed",
        "limits":[
            "Catalogue sampling environments/year and laboratory equivalence NOT verified.",
            "Same clone accession ID does not imply a common randomized design or identical planting stock.",
            "Do not attribute deltas to environment or genetics or compute statistical significance.",
            "Published catalogue minima/maxima do not imply confidence intervals or sample size.",
            "Vitamin C exists for only some catalogue clones; no matching Holetta vitamin C values.",
        ],
    }
    (out/"matched_cip_provenance.json").write_text(
        json.dumps(report,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")
    lines=[
        "# Cruce de 15 accesiones CIP entre fuentes científicas",
        "",
        "**NO es un ensayo genotipo × ambiente:** los datos provienen de publicaciones",
        "diferentes, sin condiciones de muestreo y laboratorio equiparadas.",
        "",
        f"Coincidencias exactas de identificadores: {len(common)} clones de "
        f"{len(cat)} en catálogo CIP y {len(eth)} en Holetta 2019.",
        "",
        "| Clon | Fe catálogo | Fe Holetta | Diferencia | Zn catálogo | Zn Holetta | Diferencia |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for r in compared:
        lines.append(
            f'| {r["clone"]} | {r["iron_catalogue_mg_kg_dry"]} | '
            f'{r["iron_holetta_mg_kg_dry"]} | {r["iron_delta_holetta_minus_catalogue"]} | '
            f'{r["zinc_catalogue_mg_kg_dry"]} | {r["zinc_holetta_mg_kg_dry"]} | '
            f'{r["zinc_delta_holetta_minus_catalogue"]} |'
        )
    lines += [
        "",
        "**Unidad de Fe y Zn: mg/kg en peso SECO en ambas fuentes.**",
        "Diferencia = cifra de Holetta menos cifra de catálogo; signo ≠ efecto causal.",
        "",
        "**No se comparan rendimientos:** CIP reporta kg/planta y Holetta kg/m².",
        "Las condiciones y fechas de las mediciones del catálogo no están",
        "establecidas como iguales ni emparejadas con las de Holetta.",
        "",
        "Siguiente paso: obtener registros originales por parcela, bloque, año,",
        "lugar y procedimiento analítico para poder formular inferencias G×E.",
        "",
        "Catálogo: https://doi.org/10.21223/P3/LQOT7Z",
        "Ensayo Holetta: https://doi.org/10.3390/plants12142625",
    ]
    (out/"matched_cip_report.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    return report

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(run(out=args.out),ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()

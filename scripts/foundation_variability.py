"""USDA Foundation: linked retail sample-level nutrient dispersion (M1-03).

Joins ONLY documented FDC relations:
foundation root -> input_food -> sample_food -> sub_sample_food ->
food_nutrient -> sub_sample_result, plus acquisition_samples -> market_acquisition.

Units are from nutrient definitions in the pinned Foundation extractor.
Descriptive purchase-sample statistics only: NOT genetic/environmental causality.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from decimal import Decimal, getcontext
from pathlib import Path

from scripts.usda_foundation import SOURCE_URL, TARGETS, extract as extract_foundation, filehash, nonnegative, table
import zipfile

SOURCE_SHA = "70457ee9d9342f43bda2010318c85f04210c689fdeb9cd2da4c513b0e8dbc655"
FOCUS = {"iron": 1089, "zinc": 1095, "potassium": 1092, "vitamin_c": 1162}
REQUIRED_PER_MARKET_TYPE = 8
MEASUREMENT_FIELDS = [
    "market_type","foundation_fdc_id","sample_fdc_id","sub_sample_fdc_id",
    "food_nutrient_id","nutrient","unit","adjusted_amount_per_100g",
    "lab_method_id","acquisition_fdc_id","acquisition_date","store_city","store_state"
]
SUMMARY_FIELDS = [
    "market_type","nutrient","unit","n_acquisition_samples","mean","median",
    "minimum","maximum","range","sample_sd","published_mean","published_median",
    "published_min","published_max","published_data_points","mean_difference",
    "range_reconciled","median_reconciled",
]


def write_csv(path, fields, records):
    with Path(path).open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)


def median_dec(vals):
    ordered = sorted(vals)
    n = len(ordered)
    return (ordered[n//2 - 1] + ordered[n//2])/2 if n % 2 == 0 else ordered[n//2]


def sample_sd(vals, mean):
    if len(vals) < 2:
        return None
    return (sum((x-mean)**2 for x in vals)/Decimal(len(vals)-1)).sqrt()


def analyze(archive_path: Path, destination: Path, *, expected_sha256: str = SOURCE_SHA) -> dict:
    archive_path = Path(archive_path)
    destination = Path(destination)
    actual_hash = filehash(archive_path)
    if actual_hash != expected_sha256:
        raise ValueError("Foundation ZIP checksum differs from pinned primary release")
    # Reuse the existing extractor's verified food IDs and strict nutrient IDs.
    base_output = destination / "foundation_reference"
    base = extract_foundation(archive_path, base_output, expected_sha256=expected_sha256)
    roots = {data["fdc_id"]: kind for kind, data in base["foods"].items()}
    purchase_ids = defaultdict(list)
    with zipfile.ZipFile(archive_path) as z:
        for row in table(z, "input_food.csv"):
            if row["fdc_id"] in roots:
                sid = row["fdc_of_input_food"]
                if not sid:
                    raise ValueError("Broken input_food link")
                purchase_ids[roots[row["fdc_id"]]].append(sid)
        if set(purchase_ids) != set(roots.values()):
            raise ValueError("Missing market type in input_food")
        all_samples = [x for sub in purchase_ids.values() for x in sub]
        if len(all_samples) != len(set(all_samples)):
            raise ValueError("Repeated purchase sample link")
        if any(len(group) != REQUIRED_PER_MARKET_TYPE for group in purchase_ids.values()):
            raise ValueError("Unexpected number of acquisition samples per market type")
        sample_to_kind = {sid: kind for kind, group in purchase_ids.items() for sid in group}
        declared_sample_ids = {row["fdc_id"] for row in table(z, "sample_food.csv")
                               if row["fdc_id"] in sample_to_kind}
        if declared_sample_ids != set(sample_to_kind):
            raise ValueError("input_food references unidentified sample_food")
        acquisition_links = defaultdict(list)
        for row in table(z, "acquisition_samples.csv"):
            if row["fdc_id_of_sample_food"] in sample_to_kind:
                acquisition_links[row["fdc_id_of_sample_food"]].append(row["fdc_id_of_acquisition_food"])
        if set(acquisition_links) != set(sample_to_kind) or any(len(a)!=1 for a in acquisition_links.values()):
            raise ValueError("Acquisition ID missing/ambiguous for purchase sample")
        acquisition_ids = {items[0] for items in acquisition_links.values()}
        market = {row["fdc_id"]: row for row in table(z, "market_acquisition.csv")
                  if row["fdc_id"] in acquisition_ids}
        if set(market) != acquisition_ids:
            raise ValueError("Acquisition details not found")
        child_to_parent = {}
        for row in table(z, "sub_sample_food.csv"):
            if row["fdc_id_of_sample_food"] in sample_to_kind:
                sid = row["fdc_id"]
                if sid in child_to_parent:
                    raise ValueError("Duplicate sub_sample_food FDC ID")
                child_to_parent[sid] = row["fdc_id_of_sample_food"]
        if not child_to_parent:
            raise ValueError("No sub samples linked to selected purchases")
        nid_to_name = {id:name for name,id in FOCUS.items()}
        per_child = {}
        published = {}
        for row in table(z, "food_nutrient.csv"):
            fdc_id = row["fdc_id"]
            nid = int(row["nutrient_id"])
            if nid not in nid_to_name: continue
            if fdc_id in roots:
                key = (roots[fdc_id], nid)
                if key in published: raise ValueError("Duplicate published nutrient row")
                published[key] = row
            if fdc_id not in child_to_parent: continue
            key = (fdc_id, nid)
            if key in per_child:
                raise ValueError("Duplicate measurement per sub-sample and nutrient")
            if not row["amount"].strip():
                raise ValueError("Missing chemical amount in a selected sub-sample")
            per_child[key] = row
        by_food_nutrient = {row["id"]: (child_id,nid,row)
                            for (child_id,nid),row in per_child.items()}
        lab_result = {}
        for row in table(z, "sub_sample_result.csv"):
            key = row["food_nutrient_id"]
            if key not in by_food_nutrient: continue
            if key in lab_result: raise ValueError("Duplicate analytical result")
            numeric = nonnegative(row["adjusted_amount"], f"adjusted_amount {key}")
            original = nonnegative(by_food_nutrient[key][2]["amount"], f"amount {key}")
            if numeric != original:
                raise ValueError(f"Analytical adjusted amount differs from food_nutrient amount: {key}")
            if not row["lab_method_id"].strip():
                raise ValueError("Missing lab method ID")
            lab_result[key] = row
        if set(by_food_nutrient) != set(lab_result):
            raise ValueError("Unlinked measurement IDs between food_nutrient and sub_sample_result")
    samples_by_type = defaultdict(list)
    for nutrient_id, (sub_sample_id,nid,food_row) in sorted(by_food_nutrient.items()):
        parent = child_to_parent[sub_sample_id]
        kind = sample_to_kind[parent]
        acquisition_id = acquisition_links[parent][0]
        meta = market[acquisition_id]
        nutrient = nid_to_name[nid]
        unit = TARGETS[nutrient][1]
        samples_by_type[(kind,nutrient)].append({
            "market_type":kind, "foundation_fdc_id":next(k for k,v in roots.items() if v==kind),
            "sample_fdc_id":parent, "sub_sample_fdc_id":sub_sample_id,
            "food_nutrient_id":nutrient_id, "nutrient":nutrient, "unit":unit,
            "adjusted_amount_per_100g":str(nonnegative(lab_result[nutrient_id]["adjusted_amount"],nutrient)),
            "lab_method_id":lab_result[nutrient_id]["lab_method_id"],
            "acquisition_fdc_id":acquisition_id,
            "acquisition_date":meta["acquisition_date"], "store_city":meta["store_city"],
            "store_state":meta["store_state"]
        })
    summaries = []
    all_measurements = []
    for kind in ("russet","red","gold"):
        for nutrient in ("iron","zinc","potassium","vitamin_c"):
            group = sorted(samples_by_type.get((kind,nutrient),[]),key=lambda x:x["sample_fdc_id"])
            if len(group)!=REQUIRED_PER_MARKET_TYPE or len({r["sample_fdc_id"] for r in group})!=len(group):
                raise ValueError(f"{kind}/{nutrient}: not one analysis per 8 acquired samples")
            values = [Decimal(r["adjusted_amount_per_100g"]) for r in group]
            n=Decimal(len(values))
            avg=sum(values)/n
            med=median_dec(values)
            low,high=min(values),max(values)
            sd=sample_sd(values,avg)
            entry=published.get((kind,FOCUS[nutrient]))
            if entry is None: raise ValueError("Published aggregate is missing")
            if entry["data_points"] != str(REQUIRED_PER_MARKET_TYPE):
                raise ValueError("Published aggregate data_points inconsistent with sample count")
            for key in ("amount","median","min","max"):
                if not entry[key].strip(): raise ValueError(f"Published {key} not provided")
            pub_avg=nonnegative(entry["amount"],"published mean")
            pub_median=nonnegative(entry["median"],"published median")
            pub_min=nonnegative(entry["min"],"published min")
            pub_max=nonnegative(entry["max"],"published max")
            # Differences may reflect rounding and original published calculation.
            # Disclose deltas instead of forcing approximate identity.
            summaries.append({
                "market_type":kind,"nutrient":nutrient,"unit":TARGETS[nutrient][1],
                "n_acquisition_samples":str(int(n)),"mean":str(avg),
                "median":str(med),"minimum":str(low),"maximum":str(high),
                "range":str(high-low),"sample_sd":str(sd),
                "published_mean":str(pub_avg),"published_median":str(pub_median),
                "published_min":str(pub_min),"published_max":str(pub_max),
                "published_data_points":entry["data_points"],
                "mean_difference":str(avg-pub_avg),
                "range_reconciled":str(low==pub_min and high==pub_max).lower(),
                "median_reconciled":str(med==pub_median).lower()
            })
            all_measurements.extend(group)
    destination.mkdir(parents=True,exist_ok=True)
    measurements_path = destination/"retail_sample_measurements.csv"
    summary_path = destination/"retail_sample_summary.csv"
    write_csv(measurements_path, MEASUREMENT_FIELDS, all_measurements)
    write_csv(summary_path, SUMMARY_FIELDS, summaries)
    lines = [
        "# USDA Foundation — variación entre muestras de compra de papa (M1-03)", "",
        "**24 muestras comerciales relacionadas documentalmente: ocho por tipo (russet, roja, dorada).**",
        "Resultados químicos de 4 nutrientes por tipo. **No son 24 plantas genotipadas**,",
        "ni un ensayo de genotipo × ambiente, ni garantizan independencia geográfica.",
        "Estas papas fueron analizadas **crudas y sin piel**.", "",
        "| Tipo comercial | Nutriente | n compras | Media | Min–max | Desv. estándar muestral |",
        "|---|---|---:|---:|---|---:|",
    ]
    for s in summaries:
        lines.append(f'| {s["market_type"]} | {s["nutrient"]} ({s["unit"]}/100g) | '
                     f'{s["n_acquisition_samples"]} | {Decimal(s["mean"]):.4f} | '
                     f'{s["minimum"]} – {s["maximum"]} | {Decimal(s["sample_sd"]):.4f} |')
    lines.extend([
        "", "El rango y la dispersión son **descriptivos**, no intervalos de confianza.",
        "Las muestras pueden compartir tiendas, zonas de distribución, temporadas o cultivares desconocidos.",
        "No se realizan test t, ANOVA ni inferencias sobre causalidad genética.",
        "La composición cocinada y la biodisponibilidad siguen sin analizarse en este conjunto.", "",
        "## Auditoría contra promedios publicados",
        "",
        "| Tipo | Nutriente | Media reconstruida − USDA | Rango exacto | Mediana exacta |",
        "|---|---|---:|---|---|",
    ])
    for s in summaries:
        lines.append(f'| {s["market_type"]} | {s["nutrient"]} | '
                     f'{Decimal(s["mean_difference"]):+.6f} | '
                     f'{s["range_reconciled"]} | {s["median_reconciled"]} |')
    lines += ["", "La diferencia puede reflejar redondeo o criterios agregados del USDA;",
              "una discrepancia queda explícita y no se corrige arbitrariamente.", "",
              "Fuente primaria: "+SOURCE_URL,
              "Archivo original SHA-256: "+actual_hash, ""]
    (destination/"retail_sample_report.md").write_text("\n".join(lines), encoding="utf-8")
    provenance = {
        "source_url": SOURCE_URL, "archive_sha256": actual_hash,
        "foundation_ids":base["foods"], "selection":"input_food -> sample_food -> sub_sample_food -> food_nutrient -> sub_sample_result",
        "acquisitions":"acquisition_samples -> market_acquisition",
        "n_purchase_samples_per_market_type":REQUIRED_PER_MARKET_TYPE,
        "nutrients": list(FOCUS), "measurement_rows":len(all_measurements),
        "limitations":"Retail samples not independent genotypes, not an agricultural randomized field design.",
        "files": {
            "retail_sample_measurements.csv":filehash(measurements_path),
            "retail_sample_summary.csv":filehash(summary_path),
        },
    }
    (destination/"retail_sample_provenance.json").write_text(
        json.dumps(provenance,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")
    return provenance

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zip",type=Path,required=True)
    parser.add_argument("--output-dir",type=Path,required=True)
    args = parser.parse_args()
    report=analyze(args.zip,args.output_dir)
    print(json.dumps(report,indent=2,ensure_ascii=False))

if __name__ == "__main__":
    main()

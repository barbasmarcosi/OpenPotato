"""Reproducible comparison of USDA Foundation Foods potato MARKET TYPES.

Input: USDA Foundation Foods CSV ZIP April 30 2026. Raw, peeled market
classes are neither named genetically-verified cultivars nor cooked foods.
Missing nutrient data and below-LOQ records are never treated as zero.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import zipfile
from decimal import Decimal, InvalidOperation
from pathlib import Path

SOURCE_URL = "https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_foundation_food_csv_2026-04-30.zip"
EXPECTED = {
    "russet": "Potatoes, russet, without skin, raw",
    "red": "Potatoes, red, without skin, raw",
    "gold": "Potatoes, gold, without skin, raw",
}
# Exact FDC nutrient identifiers; never use NDB numeric codes here.
TARGETS = {
    # Foundation since 2020 uses two Atwater energy definitions (2047, 2048).
    # Never synthesize a kcal value from carbohydrates without a justified method.
    "energy_atwater_general_kcal": (2047, "kcal"),
    "energy_atwater_specific_kcal": (2048, "kcal"),
    "protein": (1003, "g"),
    "total_lipid": (1004, "g"), "carbohydrate": (1005, "g"),
    "fiber": (1079, "g"), "iron": (1089, "mg"),
    "zinc": (1095, "mg"), "calcium": (1087, "mg"),
    "magnesium": (1090, "mg"), "potassium": (1092, "mg"),
    "phosphorus": (1091, "mg"), "vitamin_c": (1162, "mg"),
    "vitamin_a_rae": (1106, "ug_RAE"), "folate_dfe": (1190, "ug_DFE"),
    "vitamin_e": (1109, "mg"), "vitamin_b12": (1178, "ug"),
    "vitamin_d": (1114, "ug"),
}
FIELDS = ["market_type", "fdc_id", "nutrient", "unit", "amount_per_100g",
          "status", "loq", "data_points", "source_id"]


def filehash(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for part in iter(lambda: handle.read(1024*1024), b""):
            h.update(part)
    return h.hexdigest()


def table(archive: zipfile.ZipFile, filename: str):
    matches = [item for item in archive.namelist()
               if Path(item).name.casefold() == filename.casefold()]
    if len(matches) != 1:
        raise ValueError(f"Expected one {filename}, found {len(matches)}")
    with archive.open(matches[0]) as binary:
        with io.TextIOWrapper(binary, encoding="utf-8-sig", newline="") as decoded:
            yield from csv.DictReader(decoded)


def nonnegative(raw: str, label: str) -> Decimal:
    try:
        value = Decimal(raw)
    except (InvalidOperation, ValueError) as error:
        raise ValueError(f"Invalid {label}: {raw!r}") from error
    if not value.is_finite() or value < 0:
        raise ValueError(f"Invalid {label}: {raw!r}")
    return value


def extract(archive_path: Path, output_dir: Path, expected_sha256: str | None = None) -> dict:
    archive_path, output_dir = Path(archive_path), Path(output_dir)
    archive_hash = filehash(archive_path)
    if expected_sha256 is not None and archive_hash != expected_sha256:
        raise ValueError("Foundation archive SHA-256 mismatch")
    with zipfile.ZipFile(archive_path) as archive:
        by_description = {name.casefold():kind for kind, name in EXPECTED.items()}
        versions = {kind: [] for kind in EXPECTED}
        for entry in table(archive, "food.csv"):
            kind = by_description.get(entry["description"].strip().casefold())
            if kind is None:
                continue
            if entry["data_type"].casefold() not in ("foundation_food", "foundation"):
                # Different FDC data types may share the exact same food description.
                # Only use Foundation, NEVER substitute historical SR Legacy rows.
                continue
            versions[kind].append({
                "fdc_id": entry["fdc_id"],
                "description": entry["description"],
                "publication_date": entry.get("publication_date", "").strip(),
            })
        if any(not versions[kind] for kind in EXPECTED):
            raise ValueError(f"Missing market classes: {[k for k,v in versions.items() if not v]}")
        found = {}
        for kind, entries in versions.items():
            if len(entries) == 1:
                found[kind] = entries[0]
                continue
            if any(not x["publication_date"] for x in entries):
                raise ValueError(f"Historical duplicates without publication dates: {kind}")
            dates = sorted({x["publication_date"] for x in entries})
            latest = dates[-1]
            candidates = [x for x in entries if x["publication_date"] == latest]
            if len(candidates) != 1:
                raise ValueError(f"More than one Foundation record at latest publication date for {kind}: {candidates}")
            found[kind] = candidates[0]
        by_fdc = {info["fdc_id"]:kind for kind, info in found.items()}
        wanted = {nid for nid, unit in TARGETS.values()}
        nutrient_meta = {int(n["id"]): n for n in table(archive, "nutrient.csv")
                         if int(n["id"]) in wanted}
        for name, (nid, unit) in TARGETS.items():
            if nid not in nutrient_meta:
                raise ValueError(f"Missing nutrient definition for {name}/{nid}")
            original_unit = nutrient_meta[nid]["unit_name"].lower().replace("µ", "u").replace("μ", "u")
            canonical = "ug" if unit.startswith("ug_") else unit
            if original_unit != canonical:
                raise ValueError(f"{name}: unit mismatch {original_unit} != {canonical}")
        observations = {kind:{} for kind in EXPECTED}
        for entry in table(archive, "food_nutrient.csv"):
            kind = by_fdc.get(entry["fdc_id"])
            if kind is None:
                continue
            nid = int(entry["nutrient_id"])
            if nid not in wanted:
                continue
            if nid in observations[kind]:
                raise ValueError(f"Duplicate nutrient {nid} in {kind}; ambiguous input")
            raw = entry["amount"].strip()
            amount = nonnegative(raw, f"{kind}/{nid}") if raw else None
            loq = entry.get("loq", "").strip()
            if loq:
                loq = str(nonnegative(loq, f"LOQ {kind}/{nid}"))
            points = entry.get("data_points", "").strip()
            if points:
                if not points.isdigit():
                    raise ValueError(f"Invalid data_points for {kind}/{nid}")
            # USDA Foundation records may publish 0 for below-quantitation values:
            # 0 and LOQ positive is NOT evidence of absence.
            status = ("not_reported" if amount is None else
                      "below_quantification" if amount == 0 and loq and Decimal(loq) > 0 else
                      "reported_zero" if amount == 0 else "observed")
            observations[kind][nid] = {
                "value": "" if amount is None or status == "below_quantification" else str(amount),
                "loq": loq, "data_points": points, "status": status,
            }
    records = []
    for kind in ("russet", "red", "gold"):
        for nutrient, (nid, unit) in TARGETS.items():
            sample = observations[kind].get(nid, {
                "value": "", "loq": "", "data_points": "", "status": "not_reported"
            })
            records.append({
                "market_type": kind, "fdc_id": found[kind]["fdc_id"],
                "nutrient": nutrient, "unit": unit,
                "amount_per_100g": sample["value"], "status": sample["status"],
                "loq": sample["loq"], "data_points": sample["data_points"],
                "source_id": f"USDA_FOUNDATION_2026_{found[kind]['fdc_id']}_N_{nid}",
            })
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "foundation_market_types.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(records)
    meta = {
        "release": "USDA Foundation Foods April 2026",
        "source_url": SOURCE_URL,
        "archive_sha256": archive_hash,
        "csv_sha256": filehash(csv_path),
        "foods": found,
        "historical_versions": versions,
        "selection_rule": "most recent publication_date; reject ties",
        "categories": "market types; no confirmation of genetic cultivar identity",
        "form": "raw potato flesh without skin; NOT cooked",
        "interpretation": "Composition from published USDA data; not a randomized experiment or proof of genetics",
        "missing": "not_reported and below_quantification are not zeros",
    }
    (output_dir / "foundation_provenance.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    return meta


def compare(records_path: Path, report_path: Path) -> list[dict]:
    with Path(records_path).open(encoding="utf-8", newline="") as file:
        records = list(csv.DictReader(file))
    expected_count = len(EXPECTED) * len(TARGETS)
    if len(records) != expected_count:
        raise ValueError(f"Expected {expected_count} observations, got {len(records)}")
    grouped = {}
    for row in records:
        key=(row["market_type"],row["nutrient"])
        if key in grouped or row["market_type"] not in EXPECTED or row["nutrient"] not in TARGETS:
            raise ValueError(f"Duplicate/unknown market type or nutrient: {key}")
        if row["unit"] != TARGETS[row["nutrient"]][1]:
            raise ValueError(f"Incompatible unit: {key}")
        if row["status"] not in ("observed","reported_zero","not_reported","below_quantification"):
            raise ValueError(f"Unknown status: {key}")
        if row["status"] not in ("observed","reported_zero") and row["amount_per_100g"] != "":
            raise ValueError(f"Unknown/censored value must not be numeric: {key}")
        if row["status"] in ("observed","reported_zero") and not row["amount_per_100g"]:
            raise ValueError(f"Missing number with numeric status: {key}")
        grouped[key]=row
    report_path = Path(report_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# USDA Foundation Foods (04/2026) — comparación entre tipos comerciales de papa",
        "",
        "**Solo materia cruda sin piel. Russet, red y gold son tipos comerciales y no demuestran un efecto genético causal.**",
        "",
        "| Nutriente | Unidad/100g | Russet | Roja | Dorada | Lectura |",
        "|---|---|---:|---:|---:|---|",
    ]
    observations=[]
    for nutrient, (_,unit) in TARGETS.items():
        cells=[grouped[(kind,nutrient)] for kind in ("russet","red","gold")]
        values=[nonnegative(row["amount_per_100g"],nutrient)
                if row["status"] in ("observed","reported_zero") else None for row in cells]
        known=[v for v in values if v is not None]
        if len(known) == 3:
            note = "Comparables en crudo; no inferir causalidad"
        elif len(known) > 0:
            note = "Comparación parcial: faltan análisis"
        else:
            note = "No informado o censurado"
        fmt = lambda val,row: str(val) if val is not None else ("<LOQ" if row["status"]=="below_quantification" else "ND")
        lines.append(f"| {nutrient} | {unit} | " +
                     " | ".join(fmt(v,r) for v,r in zip(values,cells)) + f" | {note} |")
        observations.append({"nutrient": nutrient, "unit": unit, "complete":len(known)==3,
                             "min":str(min(known)) if known else None,
                             "max":str(max(known)) if known else None,
                             "span":str(max(known)-min(known)) if len(known)==3 else None})
    lines.extend([
        "", "No comparar directamente con los registros USDA de papa **hervida**: cambia la preparación.",
        "Sin datos emparejados de suelo, cultivar genético, rendimientos, incertidumbre ni biodisponibilidad,",
        "estos valores describen la composición alimentaria de categorías comerciales y **no** el potencial",
        "de mejoramiento genético dentro de una población vegetal.", "",
        "Faltantes (ND) y valores bajo límite de cuantificación (<LOQ) nunca se interpretan como cero.",
        "Datos originales y hashes: datasets/foundation/foundation_provenance.json.",
        "Fuente: https://fdc.nal.usda.gov/download-datasets/", "",
    ])
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return observations


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zip", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--expected-sha256", default=None)
    args = parser.parse_args()
    info = extract(args.zip, args.output_dir, args.expected_sha256)
    observations = compare(args.output_dir / "foundation_market_types.csv",
                           args.output_dir / "foundation_comparison.md")
    print(json.dumps({"source_sha":info["archive_sha256"],
                      "food_ids":{k:v["fdc_id"] for k,v in info["foods"].items()},
                      "nutrients":len(observations),
                      "comparable_nutrients":sum(int(i["complete"]) for i in observations)},
                     indent=2))


if __name__ == "__main__":
    main()

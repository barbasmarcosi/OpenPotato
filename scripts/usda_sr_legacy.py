"""Extract official USDA SR Legacy potato records without imputation."""
from __future__ import annotations
import argparse, csv, hashlib, io, json, zipfile
from decimal import Decimal
from pathlib import Path

USDA_URL = "https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_sr_legacy_food_csv_2018-04.zip"
PINNED_ARCHIVE_SHA256 = "b80817294b8850530aaedf2e515c02593b1824f763a0ff356e5c2081643e6fd0"
FOOD_NAMES = {"170438": "Potatoes, boiled, cooked in skin, flesh, without salt",
              "170440": "Potatoes, boiled, cooked without skin, flesh, without salt"}
# FoodData Central nutrient IDs (different from legacy NDB nutrient numbers).
NUTRIENTS = {
    "energy_kcal": (1008,"kcal","Energy"), "protein": (1003,"g","Protein"),
    "total_lipid": (1004,"g","Total lipid"), "carbohydrate": (1005,"g","Carbohydrate"),
    "fiber": (1079,"g","Fiber"), "calcium": (1087,"mg","Calcium"),
    "iron": (1089,"mg","Iron"), "magnesium": (1090,"mg","Magnesium"),
    "phosphorus": (1091,"mg","Phosphorus"), "potassium": (1092,"mg","Potassium"),
    "sodium": (1093,"mg","Sodium"), "zinc": (1095,"mg","Zinc"),
    "copper": (1098,"mg","Copper"), "selenium": (1103,"ug","Selenium"),
    "vitamin_a_rae": (1106,"ug_RAE","Vitamin A, RAE"),
    "vitamin_e": (1109,"mg","Vitamin E"), "vitamin_c": (1162,"mg","Vitamin C"),
    "vitamin_b12": (1178,"ug","Vitamin B-12"), "vitamin_d": (1114,"ug","Vitamin D"),
    "folate_dfe": (1190,"ug_DFE","Folate, DFE"),
    "vitamin_b6": (1175,"mg","Vitamin B-6"), "vitamin_k": (1185,"ug","Vitamin K"),
    "thiamin": (1165,"mg","Thiamin"), "riboflavin": (1166,"mg","Riboflavin"),
    # 18:2 and 18:3 undifferentiated are not guaranteed to identify the essential isomers.
    "linoleic_acid": (None,"g","unresolved"), "alpha_linolenic_acid": (None,"g","unresolved"),
}
FIELDS = ["nutrient","unit","amount_per_100g","status","source_id"]

def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1048576), b""):
            h.update(block)
    return h.hexdigest()

def csv_rows(archive, name):
    candidates = [n for n in archive.namelist() if Path(n).name.lower() == name]
    if len(candidates) != 1:
        raise ValueError(f"{name}: expected one CSV, found {len(candidates)}")
    with archive.open(candidates[0]) as stream:
        with io.TextIOWrapper(stream, encoding="utf-8-sig", newline="") as text:
            yield from csv.DictReader(text)

def extract(archive_path, output_dir, expected_archive_sha=None):
    archive_path, output_dir = Path(archive_path), Path(output_dir)
    source_sha = sha256(archive_path)
    if expected_archive_sha is not None and source_sha != expected_archive_sha:
        raise ValueError("USDA archive checksum changed; audit release before proceeding")
    with zipfile.ZipFile(archive_path) as z:
        foods = {r["fdc_id"]:r for r in csv_rows(z,"food.csv") if r["fdc_id"] in FOOD_NAMES}
        if foods.keys() != FOOD_NAMES.keys():
            raise ValueError("missing USDA food IDs: two preparations required")
        for fid, name in FOOD_NAMES.items():
            if foods[fid]["description"].strip().casefold() != name.casefold():
                raise ValueError(f"{fid}: incompatible description")
            if foods[fid]["data_type"] not in ("sr_legacy_food","SR Legacy"):
                raise ValueError(f"{fid}: not SR Legacy")
        wanted = {id for id,_,_ in NUTRIENTS.values() if id is not None}
        metadata = {int(r["id"]):r for r in csv_rows(z,"nutrient.csv") if int(r["id"]) in wanted}
        for label,(nid,unit,name) in NUTRIENTS.items():
            if nid is None: continue
            if nid not in metadata: raise ValueError(f"{label}: nutrient definition missing")
            item = metadata[nid]
            source_unit = item["unit_name"].lower().replace("µ","u").replace("μ","u")
            if source_unit != ("ug" if unit.startswith("ug_") else unit):
                raise ValueError(f"{label}: unexpected unit {source_unit}")
            if name.casefold() not in item["name"].casefold():
                raise ValueError(f"{label}: nutrient identity mismatch {item['name']}")
        values = {fid:{} for fid in FOOD_NAMES}
        for row in csv_rows(z,"food_nutrient.csv"):
            fid = row["fdc_id"]
            if fid not in values: continue
            nid = int(row["nutrient_id"])
            if nid not in wanted: continue
            if nid in values[fid]:
                raise ValueError(f"{fid}/{nid}: duplicate nutrient")
            val = Decimal(row["amount"])
            if not val.is_finite() or val < 0:
                raise ValueError(f"{fid}/{nid}: invalid value")
            values[fid][nid] = str(val)
    for fid in FOOD_NAMES:
        if Decimal(values[fid].get(1008, "0")) <= 0:
            raise ValueError(f"{fid}: no positive kcal energy")
    output_dir.mkdir(parents=True,exist_ok=True)
    files = {}
    for fid,name in FOOD_NAMES.items():
        output = output_dir / f"potato_fdc_{fid}_usda.csv"
        with output.open("w",newline="",encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(FIELDS)
            for label,(nid,unit,_) in NUTRIENTS.items():
                val = values[fid].get(nid) if nid is not None else None
                state = "not_reported" if val is None else ("reported_zero" if Decimal(val)==0 else "observed")
                writer.writerow([label,unit,val if val is not None else "",state,
                                 f"USDA_SR_2018_{fid}_N_{nid}" if nid is not None else f"USDA_SR_2018_{fid}_UNRESOLVED"])
        files[fid]={"description":name,"filename":output.name,"sha256":sha256(output),"reported_nutrients":len(values[fid])}
    manifest={"source_url":USDA_URL,"release":"SR Legacy April 2018","archive_sha256":source_sha,
              "records":files,"no_imputation":True,
              "caveat":"Historical analytical/calculated values; not cultivar-specific or proof of bioavailability."}
    (output_dir/"provenance.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return manifest

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zip",type=Path,required=True)
    parser.add_argument("--output-dir",type=Path,required=True)
    parser.add_argument("--no-pinned-check",action="store_true",help="only after separately auditing an alternate ZIP release")
    args=parser.parse_args()
    expected=None if args.no_pinned_check else PINNED_ARCHIVE_SHA256
    print(json.dumps(extract(args.zip,args.output_dir,expected_archive_sha=expected),indent=2))

if __name__=="__main__": main()

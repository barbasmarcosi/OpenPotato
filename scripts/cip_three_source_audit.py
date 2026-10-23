"""M1-08: cruce documental de resúmenes CIP Perú, catálogo y Holetta.

Las tres fuentes NO forman un mismo experimento ni aportan réplicas
intercambiables. Nunca se mezclan medias ni se estiman efectos GxE.
"""
import argparse
import csv
import hashlib
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    "peru": ("datasets/cip_peru_summary/peru_selected_aggregate_fe_zn.csv",
             "datasets/cip_peru_summary/peru_selected_provenance.json",
             "10.21223/N11QJS", "source_doi"),
    "catalogue": ("datasets/cip_catalogue/cip_29_clones_catalogue.csv",
                  "datasets/cip_catalogue/cip_29_clones_provenance.json",
                  "10.21223/P3/LQOT7Z", "doi"),
    "holetta": ("datasets/cultivars/genotype_trial_holetta_2019.csv",
                "datasets/cultivars/genotype_trial_provenance.json",
                "10.3390/plants12142625", "doi"),
}
CONTROLS = {"CIP391691.96", "CIP720064"}
FIELDS = [
    "accession", "material_role", "peru_n_fe_reported", "peru_n_zn_reported",
    "fe_peru_mean_mg_kg_dry", "fe_peru_sd_mg_kg_dry",
    "fe_catalogue_mg_kg_dry", "fe_holetta_mg_kg_dry",
    "zn_peru_mean_mg_kg_dry", "zn_peru_sd_mg_kg_dry",
    "zn_catalogue_mg_kg_dry", "zn_holetta_mg_kg_dry",
    "catalogue_yield_kg_per_plant", "holetta_yield_kg_m2_fresh",
    "peru_source_doi", "catalogue_source_doi", "holetta_source_doi",
    "evidence_design",
]
DESIGN = "nonmatched_published_summaries_no_gxe_inference"


def checksum(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_verified(name, override=None):
    source = SOURCES[name]
    csv_path, manifest_path = override or (ROOT / source[0], ROOT / source[1])
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    if manifest.get(source[3]) != source[2]:
        raise ValueError(name + ": source DOI mismatch")
    actual_hash = checksum(csv_path)
    if actual_hash != manifest.get("derived_csv_sha256"):
        raise ValueError(name + ": derived CSV SHA-256 mismatch")
    with Path(csv_path).open(encoding="utf-8-sig", newline="") as stream:
        records = list(csv.DictReader(stream))
    if not records or any(record.get("source_doi") != source[2] for record in records):
        raise ValueError(name + ": empty data or row DOI mismatch")
    return records, actual_hash


def index_unique(records, field):
    index = {}
    for record in records:
        key = record.get(field, "").strip()
        if not key or key in index:
            raise ValueError("Missing or duplicate biological identifier")
        index[key] = record
    return index


def number(value, label, allow_zero=False):
    try:
        result = Decimal(value)
    except (TypeError, ValueError, InvalidOperation):
        raise ValueError(label + ": not numeric") from None
    if not result.is_finite() or result < 0 or (result == 0 and not allow_zero):
        raise ValueError(label + ": invalid numeric value")
    return result


def peru_pairs(records):
    indexed = {}
    for row in records:
        accession = row.get("accession", "").strip()
        trait = row.get("nutrient", "")
        if not accession or trait not in ("iron", "zinc"):
            raise ValueError("Invalid Peru accession or trait")
        if row.get("unit") != "mg/kg_dry" or row.get("data_level") != "published_multi_location_aggregate":
            raise ValueError("Incompatible Peru unit or data level")
        pair = indexed.setdefault(accession, {})
        if trait in pair:
            raise ValueError("Duplicate Peru accession and nutrient combination")
        n = number(row.get("reported_n"), "n")
        if n != n.to_integral_value():
            raise ValueError("Published n must be integer")
        mean = number(row.get("published_mean"), "mean")
        low = number(row.get("published_min"), "min")
        high = number(row.get("published_max"), "max")
        number(row.get("published_sd"), "sd", allow_zero=True)
        if not low <= mean <= high:
            raise ValueError("Mean outside published range")
        pair[trait] = row
    if any(set(pair) != {"iron", "zinc"} for pair in indexed.values()):
        raise ValueError("Incomplete Fe/Zn pair in Peru source")
    return indexed


def run(out, overrides=None):
    overrides = overrides or {}
    peru, ph = read_verified("peru", overrides.get("peru"))
    catalogue, ch = read_verified("catalogue", overrides.get("catalogue"))
    holetta, hh = read_verified("holetta", overrides.get("holetta"))
    groups = peru_pairs(peru)
    cat = index_unique(catalogue, "accession_id")
    hol = index_unique(holetta, "genotype")
    if len(groups) != 14 or not CONTROLS.issubset(groups):
        raise ValueError("Unexpected Peru Table 16 population")
    selected = set(groups) - CONTROLS
    if len(selected) != 12 or not selected.issubset(cat) or CONTROLS.intersection(cat):
        raise ValueError("Selected clones or commercial controls do not match catalogue")
    records = []
    for accession in sorted(groups):
        fe, zn = groups[accession]["iron"], groups[accession]["zinc"]
        ca, ho = cat.get(accession), hol.get(accession)
        if ca:
            if ca.get("data_level") != "catalogue_clone_summary":
                raise ValueError("Invalid catalogue observation level")
            for field in ("iron_mg_per_kg_dry", "zinc_mg_per_kg_dry", "yield_kg_per_plant"):
                number(ca.get(field), "Catalogue " + field)
        if ho:
            if ho.get("data_level") != "genotype_reported_means":
                raise ValueError("Invalid Holetta observation level")
            for field in ("iron_mg_kg_dry", "zinc_mg_kg_dry", "yield_kg_m2_fresh"):
                number(ho.get(field), "Holetta " + field)
        records.append({
            "accession": accession,
            "material_role": "commercial_control" if accession in CONTROLS else "selected_clone",
            "peru_n_fe_reported": fe["reported_n"], "peru_n_zn_reported": zn["reported_n"],
            "fe_peru_mean_mg_kg_dry": fe["published_mean"],
            "fe_peru_sd_mg_kg_dry": fe["published_sd"],
            "fe_catalogue_mg_kg_dry": ca["iron_mg_per_kg_dry"] if ca else "",
            "fe_holetta_mg_kg_dry": ho["iron_mg_kg_dry"] if ho else "",
            "zn_peru_mean_mg_kg_dry": zn["published_mean"],
            "zn_peru_sd_mg_kg_dry": zn["published_sd"],
            "zn_catalogue_mg_kg_dry": ca["zinc_mg_per_kg_dry"] if ca else "",
            "zn_holetta_mg_kg_dry": ho["zinc_mg_kg_dry"] if ho else "",
            "catalogue_yield_kg_per_plant": ca["yield_kg_per_plant"] if ca else "",
            "holetta_yield_kg_m2_fresh": ho["yield_kg_m2_fresh"] if ho else "",
            "peru_source_doi": SOURCES["peru"][2],
            "catalogue_source_doi": SOURCES["catalogue"][2] if ca else "",
            "holetta_source_doi": SOURCES["holetta"][2] if ho else "",
            "evidence_design": DESIGN,
        })
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    csvpath = out / "three_source_accession_audit.csv"
    with csvpath.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(records)
    matched = sum(bool(r["fe_holetta_mg_kg_dry"]) for r in records)
    provenance = {
        "source_dois": {k: s[2] for k, s in SOURCES.items()},
        "source_csv_sha256": {"peru": ph, "catalogue": ch, "holetta": hh},
        "derived_csv_sha256": checksum(csvpath),
        "peru_materials": len(records), "peru_controls": 2,
        "selected_clones_in_catalogue": len(selected),
        "peru_clones_in_all_three_sources": matched,
        "evidence_design": DESIGN,
        "unit_iron_zinc": "mg/kg dry matter, separate original source figures",
        "yield_units": {"catalogue": "kg per plant", "holetta": "kg per m2 fresh"},
        "limits": [
            "Documentary accession match is not a paired trial.",
            "No pooling, ranking, p-values, confidence intervals, GxE or causal effects.",
            "Peru n cannot be assumed to represent independent plot replicates.",
            "Peru SD is not a residual variance or a standard error.",
            "Absent source values stay blank; no zero imputation.",
            "Catalogue and Holetta yield figures have incompatible units.",
        ],
    }
    (out / "three_source_provenance.json").write_text(
        json.dumps(provenance, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# M1-08: auditoría documental de tres fuentes de papa",
        "",
        "NO es un ensayo emparejado ni identifica efectos genotipo × ambiente.",
        "Fe y Zn: mg/kg de materia seca; valores conservados por fuente, sin promediarlos.",
        "Rendimientos con unidades incompatibles (kg/planta y kg/m² fresco) no se comparan.",
        "",
        f"Perú: {len(records)} materiales, 12 clones seleccionados y dos controles.",
        f"Clones presentes en el catálogo: {len(selected)}; también en Holetta: {matched}.",
        "",
        "| Accesión | Papel | Fe Perú | Fe catálogo | Fe Holetta | Zn Perú | Zn catálogo | Zn Holetta |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for r in records:
        vals = [r[k] or "ND" for k in (
            "fe_peru_mean_mg_kg_dry", "fe_catalogue_mg_kg_dry", "fe_holetta_mg_kg_dry",
            "zn_peru_mean_mg_kg_dry", "zn_catalogue_mg_kg_dry", "zn_holetta_mg_kg_dry",
        )]
        lines.append("| " + " | ".join([r["accession"], r["material_role"], *vals]) + " |")
    lines += [
        "",
        "Los n y SD peruanos son agregados publicados. No son réplicas individuales.",
        "Dos controles comerciales permanecen identificados como tales.",
        "",
        "Fuentes: https://doi.org/10.21223/N11QJS ;",
        "https://doi.org/10.21223/P3/LQOT7Z ; https://doi.org/10.3390/plants12142625",
    ]
    (out / "three_source_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return provenance


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.out), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

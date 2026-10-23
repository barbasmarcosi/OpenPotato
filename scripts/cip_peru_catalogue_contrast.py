"""M1-12 source-discrepancy audit, NOT a matched multi-environment trial.

Compare the same CIP accession IDs across two independently *published*
aggregate datasets. Study independence, sampling years, locations and assay
calibration are NOT established. No pooled means, p values, causal effects,
GxE estimates, confidence intervals, or cultivar recommendations.
"""
import argparse
import csv
import hashlib
import json
from decimal import Decimal, InvalidOperation, localcontext
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PERU_CSV = ROOT / "datasets/cip_peru_table12/peru_table12_fe_zn_summaries.csv"
PERU_META = ROOT / "datasets/cip_peru_table12/peru_table12_provenance.json"
CAT_CSV = ROOT / "datasets/cip_catalogue/cip_29_clones_catalogue.csv"
CAT_META = ROOT / "datasets/cip_catalogue/cip_29_clones_provenance.json"
PERU_DOI = "10.21223/N11QJS"
CAT_DOI = "10.21223/P3/LQOT7Z"
DATA_LEVEL = "published_program_aggregate_not_plot"
DESIGN = "cross_source_documentary_contrast_independence_unknown"
TRAITS = (
    ("iron", "iron_mg_per_kg_dry"),
    ("zinc", "zinc_mg_per_kg_dry"),
)
HEADERS = [
    "accession", "trait", "unit",
    "cip_catalogue_published_mean", "cip_peru_table12_published_mean",
    "peru_minus_catalogue_descriptive", "peru_to_catalogue_ratio_descriptive",
    "peru_reported_n_not_independent_replicates",
    "peru_published_sd_not_standard_error",
    "cip_catalogue_doi", "cip_peru_doi", "peru_source_tsv_line",
    "source_independence", "comparison_design",
]


def checksum(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_verified(csvfile, manifestfile, doi, id_key, expected_level):
    info = json.loads(Path(manifestfile).read_text(encoding="utf-8"))
    if info.get(id_key) != doi or info.get("derived_csv_sha256") != checksum(csvfile):
        raise ValueError("Source DOI/SHA-256 provenance mismatch")
    with Path(csvfile).open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames:
            raise ValueError("Missing CSV headers")
        result = []
        for row in reader:
            if None in row or any(v is None for v in row.values()):
                raise ValueError("Ragged source CSV row")
            if row.get("source_doi") != doi or row.get("data_level") != expected_level:
                raise ValueError("Source DOI or biological evidence level mismatch")
            result.append(row)
    if not result:
        raise ValueError("Empty source CSV")
    return result, info


def positive(value, label):
    try:
        x = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(label + " missing or not decimal") from None
    if not x.is_finite() or x <= 0:
        raise ValueError(label + " not finite and positive")
    return x


def indexed_peru(rows):
    index, roles = {}, {}
    for r in rows:
        accession = r.get("accession", "").strip()
        trait = r.get("nutrient", "")
        if not accession or trait not in ("iron", "zinc"):
            raise ValueError("Peru missing accession or trait")
        key = accession, trait
        if key in index:
            raise ValueError("Peru duplicate accession and trait")
        if r.get("unit") != "mg/kg_dry" or r.get("source_file_id") != "6980":
            raise ValueError("Peru non-dry unit or invalid source file")
        role = r.get("material_role")
        if role not in ("evaluated_biofortified_clone", "commercial_control"):
            raise ValueError("Peru unknown material role")
        if accession in roles and roles[accession] != role:
            raise ValueError("Peru inconsistent material role")
        roles[accession] = role
        positive(r.get("published_mean"), "Peru mean")
        positive(r.get("reported_n"), "Peru published n")
        if Decimal(r["reported_n"]) != Decimal(r["reported_n"]).to_integral_value():
            raise ValueError("Peru n is not an integer")
        sd = Decimal(r.get("published_sd", ""))
        if not sd.is_finite() or sd < 0:
            raise ValueError("Peru negative/non-finite published SD")
        index[key] = r
    if len(index) != 68 or len(roles) != 34:
        raise ValueError("Unexpected Peru Table 12 published summary population")
    if any(set(t for a, t in index if a == accession) != {"iron", "zinc"} for accession in roles):
        raise ValueError("Peru incomplete Fe/Zn source pair")
    return index, roles


def indexed_catalogue(rows):
    indexed = {}
    for r in rows:
        accession = r.get("accession_id", "").strip()
        if not accession or accession in indexed:
            raise ValueError("Catalogue missing/duplicate accession")
        for _, f in TRAITS:
            positive(r.get(f), "Catalogue " + f)
        indexed[accession] = r
    if len(indexed) != 29:
        raise ValueError("Expected 29 accession-level catalogue summaries")
    return indexed


def median_decimal(items):
    if not items:
        raise ValueError("No observations for descriptive median")
    s = sorted(items)
    center = len(s) // 2
    return s[center] if len(s) % 2 else (s[center-1] + s[center]) / 2


def run(out, peru_csv=PERU_CSV, peru_meta=PERU_META,
        catalogue_csv=CAT_CSV, catalogue_meta=CAT_META):
    peru, pm = load_verified(peru_csv, peru_meta, PERU_DOI, "source_doi", DATA_LEVEL)
    cat, cm = load_verified(catalogue_csv, catalogue_meta, CAT_DOI,
                            "doi", "catalogue_clone_summary")
    if pm.get("source_file_id") != 6980 or pm.get("materials") != 34 or pm.get("mineral_summary_rows") != 68:
        raise ValueError("Invalid Peru source snapshot scope")
    if cm.get("clone_summaries") != 29:
        raise ValueError("Invalid CIP catalogue snapshot scope")
    pi, roles = indexed_peru(peru)
    ci = indexed_catalogue(cat)
    evaluated = {a for a, r in roles.items() if r == "evaluated_biofortified_clone"}
    controls = {a for a, r in roles.items() if r == "commercial_control"}
    if len(evaluated) != 30 or len(controls) != 4 or not set(ci).issubset(evaluated):
        raise ValueError("CIP catalogue IDs not exactly within 30 evaluated Peru clones")
    extras = sorted(evaluated - set(ci))
    if len(extras) != 1 or set(ci) & controls:
        raise ValueError("Unmatched clone/control identity inconsistent")
    records = []
    ratios = {name: [] for name, _ in TRAITS}
    lower = {name: 0 for name, _ in TRAITS}
    for accession in sorted(ci):
        c = ci[accession]
        for nutrient, cat_field in TRAITS:
            r = pi[(accession, nutrient)]
            from_catalogue = positive(c[cat_field], "catalogue concentration")
            from_peru = positive(r["published_mean"], "Peru concentration")
            delta = from_peru - from_catalogue
            with localcontext() as ctx:
                ctx.prec = 28
                ratio = from_peru / from_catalogue
            ratios[nutrient].append(ratio)
            lower[nutrient] += delta < 0
            records.append({
                "accession": accession, "trait": nutrient, "unit": "mg/kg_dry",
                "cip_catalogue_published_mean": str(from_catalogue),
                "cip_peru_table12_published_mean": str(from_peru),
                "peru_minus_catalogue_descriptive": str(delta),
                "peru_to_catalogue_ratio_descriptive": str(ratio),
                "peru_reported_n_not_independent_replicates": r["reported_n"],
                "peru_published_sd_not_standard_error": r["published_sd"],
                "cip_catalogue_doi": CAT_DOI, "cip_peru_doi": PERU_DOI,
                "peru_source_tsv_line": r["source_tsv_line"],
                "source_independence": "NOT_ESTABLISHED",
                "comparison_design": DESIGN,
            })
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    csvfile = out / "peru_catalogue_29_clone_contrast.csv"
    with csvfile.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(records)
    metadata = {
        "source_dois": {"peru": PERU_DOI, "catalogue": CAT_DOI},
        "source_csv_sha256": {"peru": checksum(peru_csv), "catalogue": checksum(catalogue_csv)},
        "derived_csv_sha256": checksum(csvfile),
        "matched_accessions": len(ci), "trait_contrasts": len(records),
        "peru_evaluated_clones": len(evaluated), "peru_controls_excluded": len(controls),
        "peru_clone_not_in_catalogue": extras,
        "below_catalogue_counts": lower,
        "median_peru_to_catalogue_ratio_descriptive": {
            name: str(median_decimal(values)) for name, values in ratios.items()
        },
        "design": DESIGN,
        "independence_and_assay_equivalence": "unknown",
        "limits": [
            "This is NOT a paired multienvironment experiment, independent replication or technical validation.",
            "Published catalogue and Peru summaries may share upstream study material.",
            "Different sample collection years, environments, tissues and laboratory calibration are unverified.",
            "No causal interpretation, statistical tests, p-values, phenotype prediction or candidate superiority.",
            "Fe/Zn from these source summaries both use mg/kg dry matter; no yield units are compared.",
            "Peru n may be pooled; its SD is not independent plot residual variance or standard error.",
            "Published ratios/medians are documentary descriptions of point estimates, NOT treatment effects.",
        ]
    }
    (out / "peru_catalogue_29_clone_provenance.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False, sort_keys=True)+"\n",
        encoding="utf-8")
    lines = [
        "# M1-12 — Contraste documental completo CIP Perú vs catálogo (29 clones)",
        "",
        "**NO es un ensayo experimental emparejado** ni valida diferencias causales.",
        "La independencia y equivalencia de laboratorio entre los dos conjuntos no está establecida.",
        "",
        f"- Accesiones exactas presentes en ambas fuentes: **{len(ci)}**.",
        f"- Contrastes documentales Fe/Zn: **{len(records)}**.",
        f"- Fe en Perú inferior al catálogo: **{lower['iron']} de {len(ci)}**.",
        f"- Zn en Perú inferior al catálogo: **{lower['zinc']} de {len(ci)}**.",
        f"- Clon adicional de Tabla 12: **{extras[0]}**.",
        "- Los cuatro testigos comerciales no se atribuyen al catálogo de clones.",
        "",
        "Cocientes de medias publicadas, únicamente descriptivos (Perú / catálogo):",
        "",
        "| Mineral | Mediana del cociente documental |",
        "|---|---:|",
    ]
    for trait, ratio in metadata["median_peru_to_catalogue_ratio_descriptive"].items():
        lines.append(f"| {trait} | {ratio} |")
    lines += [
        "",
        "Estos cocientes NO son factores de respuesta al ambiente, ni evidencias de",
        "reproducibilidad entre laboratorios, ni estimadores de pérdida nutricional.",
        "No se reconstruye G×E, varianza biológica, rendimientos, seguridad ni p-valores.",
        "",
        "CIP Perú: https://doi.org/10.21223/N11QJS",
        "Catálogo CIP: https://doi.org/10.21223/P3/LQOT7Z",
    ]
    (out / "peru_catalogue_29_clone_report.md").write_text(
        "\n".join(lines)+"\n", encoding="utf-8")
    return metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.out), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

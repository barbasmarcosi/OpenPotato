"""OP-M1-09: row-level lineage between public CIP Table 16 and its audited CSV.

This is a documentary audit of *published summaries*, not source plot data.
Source row number and datafile ID are technical provenance, NOT plot identity.
Every mineral statistic is compared exactly using Decimal (no tolerance or imputation).
Only file 6979 from CIP Dataverse DOI 10.21223/N11QJS is accepted.
"""
import argparse
import csv
import hashlib
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

from scripts.cip_peru_selected import (
    DOI, FILE_ID, MAPPING, FIELDS, EXPECTED_ROWS, PUBLIC_SHA
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV = ROOT / "datasets/cip_peru_summary/peru_selected_aggregate_fe_zn.csv"
DEFAULT_MANIFEST = ROOT / "datasets/cip_peru_summary/peru_selected_provenance.json"
LEVEL = "published_multi_location_aggregate"
AUDIT_FIELDS = [
    "source_dataset_doi", "source_file_id", "source_tsv_line",
    "source_material_id_raw", "source_breeder_code_raw",
    "nutrient", "source_n_raw", "source_mean_raw", "source_sd_raw",
    "source_min_raw", "source_max_raw", "derived_csv_line",
    "derived_accession", "derived_unit", "evidence_level"
]
FOOTER_FIELDS = [
    "source_dataset_doi", "source_file_id", "source_tsv_line",
    "source_material_id_raw", "source_breeder_code_raw",
    "fe_footer_label_raw", "zn_footer_label_raw", "classification"
]


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def decimal_equal(a, b, label):
    if a is None or b is None or str(a).strip() == "" or str(b).strip() == "":
        raise ValueError(label + ": missing measurement cannot be zero-filled")
    try:
        first, second = Decimal(str(a)), Decimal(str(b))
    except (InvalidOperation, ValueError):
        raise ValueError(label + ": non-numeric value") from None
    if not first.is_finite() or not second.is_finite() or first != second:
        raise ValueError(label + ": source/derivative statistic mismatch")


def read_source(tsv, source_sha):
    if sha256(tsv) != source_sha:
        raise ValueError("CIP TSV source SHA-256 mismatch")
    with Path(tsv).open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        required = {"INSTN", "BREEDERCODE"}
        for _, n, mean, sd, minimum, maximum, _ in MAPPING:
            required.update((n, mean, sd, minimum, maximum))
        if not required.issubset(set(reader.fieldnames or [])):
            raise ValueError("CIP TSV missing required statistical fields")
        source = []
        for record in reader:
            if None in record or any(v is None for v in record.values()):
                raise ValueError("CIP TSV ragged or invalid row")
            source.append((reader.line_num, record))
    if len(source) != EXPECTED_ROWS:
        raise ValueError("CIP TSV wrong table row count")
    # Only the three OBSERVED summary labels of public table 6979 are excluded.
    labels = [(
        record["INSTN"].strip(), record["BREEDERCODE"].strip(),
        record["nFEDW"].strip(), record["nZNDW"].strip()
    ) for _, record in source[-3:]]
    if labels != [
        ("", "", "Mean", "Prom"),
        ("", "", "Max", "Max"),
        ("", "", "Min", "Min")
    ]:
        raise ValueError("Unexpected CIP global footer row semantics")
    return source


def read_derivative(csv_path, manifest_path, source_sha):
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    if (manifest.get("source_doi") != DOI
        or manifest.get("file_id") != FILE_ID
        or manifest.get("dataverse_tsv_export_sha256") != source_sha
        or manifest.get("accessions") != 14
        or manifest.get("nutrient_rows") != 28):
        raise ValueError("CIP provenance metadata do not match the source")
    if sha256(csv_path) != manifest.get("derived_csv_sha256"):
        raise ValueError("CIP derived CSV SHA-256 mismatch")
    with Path(csv_path).open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != FIELDS:
            raise ValueError("CIP derived CSV unexpected fields")
        rows = [(reader.line_num, record) for record in reader]
    if len(rows) != 28:
        raise ValueError("CIP derivative missing or extra mineral summary")
    index = {}
    for line, row in rows:
        accession, nutrient = row["accession"], row["nutrient"]
        key = (accession, nutrient)
        if not accession or nutrient not in {"iron", "zinc"} or key in index:
            raise ValueError("CIP derivative invalid or duplicate accession+nutrient")
        if row["source_doi"] != DOI or row["data_level"] != LEVEL:
            raise ValueError("CIP derivative incompatible source or evidence level")
        index[key] = (line, row)
    return index


def run(tsv, out, derived=DEFAULT_CSV, manifest=DEFAULT_MANIFEST, source_sha=PUBLIC_SHA):
    source = read_source(tsv, source_sha)
    index = read_derivative(derived, manifest, source_sha)
    matched = set()
    trace = []
    for line, raw in source[:-3]:
        accession = raw["INSTN"].strip()
        if not accession:
            raise ValueError("Empty accession in 14 source material records")
        for nutrient, n, mean, sd, minimum, maximum, unit in MAPPING:
            key = (accession, nutrient)
            if key in matched:
                raise ValueError("Duplicate source material and nutrient statistic")
            if key not in index:
                raise ValueError("Unmatched source statistic; no silent row deletion")
            csv_line, row = index[key]
            if row["breeder_code"] != raw["BREEDERCODE"].strip():
                raise ValueError("CIP breeder code mismatch")
            if row["unit"] != unit:
                raise ValueError("CIP source/derivative unit mismatch")
            for source_name, derived_name in (
                (n, "reported_n"), (mean, "published_mean"),
                (sd, "published_sd"), (minimum, "published_min"),
                (maximum, "published_max")
            ):
                decimal_equal(raw[source_name], row[derived_name], source_name)
            trace.append({
                "source_dataset_doi": DOI, "source_file_id": FILE_ID,
                "source_tsv_line": line, "source_material_id_raw": raw["INSTN"],
                "source_breeder_code_raw": raw["BREEDERCODE"],
                "nutrient": nutrient, "source_n_raw": raw[n],
                "source_mean_raw": raw[mean], "source_sd_raw": raw[sd],
                "source_min_raw": raw[minimum], "source_max_raw": raw[maximum],
                "derived_csv_line": csv_line, "derived_accession": accession,
                "derived_unit": unit, "evidence_level": LEVEL
            })
            matched.add(key)
    if matched != set(index):
        raise ValueError("Derivative has orphan mineral summary records")
    # Document excluded rows instead of erasing them, preserving the true raw ID.
    excluded = []
    for line, record in source[-3:]:
        excluded.append({
            "source_dataset_doi": DOI, "source_file_id": FILE_ID,
            "source_tsv_line": line, "source_material_id_raw": record["INSTN"],
            "source_breeder_code_raw": record["BREEDERCODE"],
            "fe_footer_label_raw": record["nFEDW"],
            "zn_footer_label_raw": record["nZNDW"],
            "classification": "source_global_summary_not_a_material"
        })
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    files = (
        ("peru_row_lineage.csv", AUDIT_FIELDS, trace),
        ("peru_source_footer_ledger.csv", FOOTER_FIELDS, excluded),
    )
    for filename, headers, entries in files:
        with (out / filename).open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=headers)
            writer.writeheader()
            writer.writerows(entries)
    report = {
        "source_doi": DOI, "source_file_id": FILE_ID, "source_tsv_sha256": source_sha,
        "derived_source_csv_sha256": sha256(derived),
        "material_rows": len(source) - len(excluded),
        "matched_source_statistics": len(matched),
        "excluded_global_summary_rows": len(excluded),
        "row_lineage_sha256": sha256(out / "peru_row_lineage.csv"),
        "excluded_footer_ledger_sha256": sha256(out / "peru_source_footer_ledger.csv"),
        "epistemic_limitations": [
            "TSV line number is a provenance locator and NOT a parcel or biological replicate.",
            "The published n count is not independently validated at plot level.",
            "Footer summary rows are preserved for audit, NOT counted as genotypes.",
            "No environmental identities or site-specific values can be reconstructed.",
            "This audit does not infer GxE, heritability, significance, or genetic causation.",
        ]
    }
    (out / "peru_row_lineage_provenance.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out / "peru_row_lineage_report.md").write_text(
        "# OP-M1-09 — Trazabilidad fila a fila de la Tabla 16 del CIP\n\n"
        f"- Fuente: https://doi.org/{DOI}; archivo público Dataverse {FILE_ID}.\n"
        f"- {report['material_rows']} filas originales de materiales, "
        f"{report['matched_source_statistics']} estadísticas Fe/Zn trazadas una a una.\n"
        f"- {report['excluded_global_summary_rows']} filas globales de pie registradas aparte.\n"
        "- Ninguna fila material se elimina ni se rellenan accesiones vacías.\n"
        "- Los valores publicados coinciden con sus derivados por igualdad decimal exacta.\n"
        "- La fila TSV no representa parcela, bloque, campaña, ni réplica independiente.\n"
        "- Los archivos XRF por parcela restringidos siguen sin incorporarse.\n",
        encoding="utf-8",
    )
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tsv", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--derived", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()
    print(json.dumps(run(args.tsv, args.out, args.derived, args.manifest), indent=2))


if __name__ == "__main__":
    main()

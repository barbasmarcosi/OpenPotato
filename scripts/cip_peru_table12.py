"""CIP Peru Table 12: 34 materials, 68 PUBLISHED Fe/Zn summaries.

Dataverse DOI 10.21223/N11QJS, public file 6980. The 14-material
Table 16 (file 6979) is a subset with the SAME published statistics.
No individual plot replicates, site-specific estimates or GxE inferred.
Yields and glycoalkaloids deliberately NOT decoded without a dictionary.
"""
import argparse
import csv
import hashlib
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

from scripts.cip_peru_selected import MAPPING

ROOT = Path(__file__).resolve().parents[1]
DOI = "10.21223/N11QJS"
FILE_ID = 6980
SHA256 = "0f33b843e286eab15ad71c6c110592adc60709997d75b2b1c5f7365ca99f6152"
EXPORT_MD5 = "b6335e33f8bc8ab3309a56904083911a"
STORED_MD5 = "6ba7f982da7cc2073693cf0b1e13f253"
URL = "https://data.cipotato.org/api/access/datafile/6980"
TABLE16 = ROOT / "datasets/cip_peru_summary/peru_selected_aggregate_fe_zn.csv"
TABLE16_META = ROOT / "datasets/cip_peru_summary/peru_selected_provenance.json"
CONTROLS = {"Ccompis", "CIP380389.1", "CIP391691.96", "CIP720064"}
RECORD_COUNT = 41
MATERIAL_COUNT = 34
DATA_LEVEL = "published_program_aggregate_not_plot"
FIELDS = [
    "accession", "breeder_code", "material_role", "source_tsv_line",
    "source_file_id", "nutrient", "unit", "reported_n", "published_mean",
    "published_sd", "published_min", "published_max", "source_doi", "data_level",
    "also_in_table16_same_statistic",
]
NONMATERIAL_FIELDS = [
    "source_doi", "source_file_id", "source_tsv_line", "row_type",
    "accession_raw", "breeder_code_raw", "iron_n_label_raw", "zinc_n_label_raw",
]


def checksum(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def decimal(value, context, zero=False, integral=False):
    if value is None or str(value).strip() == "":
        raise ValueError(context + ": missing number")
    try:
        n = Decimal(str(value))
    except (ValueError, InvalidOperation) as exc:
        raise ValueError(context + ": invalid number") from exc
    if not n.is_finite() or n < 0 or (not zero and n == 0):
        raise ValueError(context + ": invalid positive number")
    if integral and (n != n.to_integral_value() or n > 10000):
        raise ValueError(context + ": n is not a reasonable integer")
    return n


def read_table16(csvpath, manifestpath):
    manifest = json.loads(Path(manifestpath).read_text(encoding="utf-8"))
    if (manifest.get("source_doi") != DOI or manifest.get("file_id") != 6979
            or manifest.get("accessions") != 14 or manifest.get("nutrient_rows") != 28):
        raise ValueError("Table 16 provenance or population mismatch")
    if checksum(csvpath) != manifest.get("derived_csv_sha256"):
        raise ValueError("Table 16 checksum mismatch")
    with Path(csvpath).open(encoding="utf-8-sig", newline="") as stream:
        table = list(csv.DictReader(stream))
    if len(table) != 28:
        raise ValueError("Table 16 expected 28 mineral summaries")
    index = {}
    for item in table:
        key = (item.get("accession"), item.get("nutrient"))
        if not key[0] or key[1] not in ("iron", "zinc") or key in index:
            raise ValueError("Table 16 duplicate or invalid mineral record")
        if item.get("unit") != "mg/kg_dry" or item.get("source_doi") != DOI:
            raise ValueError("Table 16 unit/DOI inconsistent")
        index[key] = item
    if len({a for a, _ in index}) != 14:
        raise ValueError("Table 16 malformed mineral pairs")
    return index


def read_raw(tsv, source_sha):
    if checksum(tsv) != source_sha:
        raise ValueError("Table 12 source SHA-256 mismatch")
    with Path(tsv).open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        fields = set(reader.fieldnames or ())
        required = {"ORD", "INSTN", "BREEDERCODE"}
        for _, n, mean, sd, lo, hi, _ in MAPPING:
            required.update((n, mean, sd, lo, hi))
        if not required.issubset(fields):
            raise ValueError("Table 12 required columns missing")
        rows = []
        for record in reader:
            if None in record or any(v is None for v in record.values()):
                raise ValueError("Table 12 ragged input row")
            rows.append((reader.line_num, record))
    if len(rows) != RECORD_COUNT:
        raise ValueError("Table 12 expected 41 rows after header")
    return rows


def verify_nonmaterials(rows):
    # Based on ALL 41 rows observed in public CIP 6980 inventory Action.
    ledger = []
    if [line for line, _ in rows[MATERIAL_COUNT:]] != list(range(36, 43)):
        raise ValueError("Table 12 nonmaterial source row positions changed")
    for line, record in rows[MATERIAL_COUNT:]:
        if any(record[x].strip() for x in ("ORD", "INSTN", "BREEDERCODE")):
            raise ValueError("Nonmaterial row unexpectedly identifies a genotype")
        label_fe = record["nFEDW"].strip()
        label_zn = record["nZNDW"].strip()
        if line in (37, 38, 39):
            label = {37: "Prom", 38: "Max", 39: "Min"}[line]
            if label_fe != label or label_zn != label:
                raise ValueError("Unexpected Table 12 global summary labels")
            row_type = "global_summary_not_genotype"
        else:
            if any(record[x].strip() for x in (
                "nFEDW", "nZNDW", "MeanFEDW", "MeanZNDW"
            )):
                raise ValueError("Unexpected nonempty blank row")
            row_type = "source_blank_not_genotype"
        ledger.append({
            "source_doi": DOI, "source_file_id": FILE_ID,
            "source_tsv_line": line, "row_type": row_type,
            "accession_raw": record["INSTN"],
            "breeder_code_raw": record["BREEDERCODE"],
            "iron_n_label_raw": record["nFEDW"],
            "zinc_n_label_raw": record["nZNDW"],
        })
    return ledger


def run(tsv, out, table16=TABLE16, table16_meta=TABLE16_META, source_sha=SHA256):
    source = read_raw(tsv, source_sha)
    footers = verify_nonmaterials(source)
    subset = read_table16(table16, table16_meta)
    seen_materials = set()
    output = []
    matches = set()
    for expected_ordinal, (line, raw) in enumerate(source[:MATERIAL_COUNT], 1):
        accession = raw["INSTN"].strip()
        if not accession or accession in seen_materials:
            raise ValueError("Table 12 missing or repeated material identifier")
        seen_materials.add(accession)
        ordinal = decimal(raw["ORD"], accession + " ordinal", integral=True)
        if ordinal != expected_ordinal:
            raise ValueError("Table 12 material ordinal not aligned with source")
        breeder = raw["BREEDERCODE"].strip()
        if not breeder:
            raise ValueError("Table 12 empty breeder code")
        for trait, count, mean, sd, minimum, maximum, unit in MAPPING:
            n = decimal(raw[count], accession + " n", integral=True)
            m = decimal(raw[mean], accession + " mean")
            dispersion = decimal(raw[sd], accession + " SD", zero=True)
            low = decimal(raw[minimum], accession + " minimum")
            high = decimal(raw[maximum], accession + " maximum")
            if low > m or m > high:
                raise ValueError("Table 12 mean outside published range")
            key = (accession, trait)
            other = subset.get(key)
            if other:
                if breeder != other["breeder_code"]:
                    raise ValueError("Table 16 breeder code conflict")
                for raw_value, cell in (
                    (n, "reported_n"), (m, "published_mean"),
                    (dispersion, "published_sd"), (low, "published_min"),
                    (high, "published_max")
                ):
                    if raw_value != decimal(other[cell], "Table 16 " + cell, zero=(cell=="published_sd")):
                        raise ValueError("Table 12 and Table 16 share discordant statistic")
                matches.add(key)
            output.append({
                "accession": accession, "breeder_code": breeder,
                "material_role": "commercial_control" if accession in CONTROLS else "selected_clone",
                "source_tsv_line": line, "source_file_id": FILE_ID,
                "nutrient": trait, "unit": unit, "reported_n": int(n),
                "published_mean": raw[mean], "published_sd": raw[sd],
                "published_min": raw[minimum], "published_max": raw[maximum],
                "source_doi": DOI, "data_level": DATA_LEVEL,
                "also_in_table16_same_statistic": "true" if other else "false",
            })
    if len(seen_materials) != MATERIAL_COUNT or len(CONTROLS & seen_materials) != 4:
        raise ValueError("Table 12 expected 30 selected clones and four commercial controls")
    if matches != set(subset):
        raise ValueError("Table 16 not fully contained in public Table 12")
    # Non-overlapping records belong to different materials in the same programme.
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    csvpath = out / "peru_table12_fe_zn_summaries.csv"
    with csvpath.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(output)
    footer_path = out / "peru_table12_nonmaterials.csv"
    with footer_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=NONMATERIAL_FIELDS)
        writer.writeheader()
        writer.writerows(footers)
    report = {
        "source_doi": DOI, "source_file_id": FILE_ID, "source_url": URL,
        "source_export_sha256": source_sha,
        "source_export_md5": EXPORT_MD5, "source_stored_metadata_md5": STORED_MD5,
        "table16_source_file_id": 6979,
        "table16_derived_sha256": checksum(table16),
        "materials": len(seen_materials), "selected_clones": 30, "controls": 4,
        "mineral_summary_rows": len(output),
        "statistics_overlapping_table16": len(matches),
        "materials_overlapping_table16": len({key[0] for key in matches}),
        "materials_not_in_table16": len(seen_materials - {key[0] for key in matches}),
        "excluded_nonmaterial_rows": len(footers),
        "derived_csv_sha256": checksum(csvpath),
        "excluded_rows_csv_sha256": checksum(footer_path),
        "limits": [
            "Table 16 is a source subset of Table 12, not an independent cohort or replication.",
            "Summary n is not known to represent independent biological plots.",
            "Published SD/min/max cannot recover environment-specific residual variation.",
            "No p-values, causal genetic conclusions, GxE, heritability or inferential ranking.",
            "Other tabular traits (TTYNA/TglyFW) excluded pending verified variable dictionary and units.",
            "No genotype-specific soil matches or human bioavailability data are inferred.",
        ]
    }
    (out / "peru_table12_provenance.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    (out / "peru_table12_report.md").write_text(
        "# OP-M1-11 — Tabla 12 pública CIP Perú: Fe/Zn agregados\n\n"
        f"Archivo Dataverse {FILE_ID}; https://doi.org/{DOI}.\n\n"
        f"- {len(seen_materials)} materiales = 30 clones seleccionados + 4 controles.\n"
        f"- {len(output)} registros Fe/Zn con n, media, SD y rango **publicados**.\n"
        f"- Los {len(matches)} registros de los 14 materiales de Tabla 16 son **idénticos**, "
        "no réplicas independientes.\n"
        f"- {len(footers)} filas no materiales trazadas (4 vacías + 3 resúmenes generales).\n"
        "- Rendimiento y glicoalcaloides no reinterpretados sin diccionario/ontología.\n"
        "- Prohibido derivar G×E, significancia genética o seguridad alimentaria de estos agregados.\n",
        encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tsv", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.tsv, args.out), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

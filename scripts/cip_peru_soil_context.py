"""M1-10: CIP Peru nine-locality SOIL summary; NOT tuber mineral data.

Original public Dataverse datafile 6970, 10.21223/N11QJS.
Soil Zn/Fe concentrations use source 'ppm' column names. No clone/plot join.
Source placeholders ('*', blank) and detection thresholds ('< value') are
preserved, not interpreted as zero or as independently replicated samples.
"""
import argparse
import csv
import hashlib
import json
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path

DOI = "10.21223/N11QJS"
FILE_ID = 6970
PUBLIC_SHA = "bd64f98a69694dd057b0f808308acc080eeca7b839875c3fd583a5d2f40bc158"
API = f"https://data.cipotato.org/api/access/datafile/{FILE_ID}"
TRAITS = (
    ("soil_pH", "SoilpHmean", "SoilpHsd", "pH_unitless"),
    ("soil_zinc", "Zincppmmean", "Zincppmsd", "ppm_in_source_soil_table"),
    ("soil_iron", "Ironppmmean", "Ironppmsd", "ppm_in_source_soil_table"),
)
FIELDS = (
    "source_doi", "source_file_id", "source_tsv_line", "city_raw", "locality_raw",
    "altitude_raw_unit_unverified", "soil_trait", "source_mean_raw",
    "mean_status", "mean_exact_if_observed", "mean_upper_bound_if_censored",
    "source_sd_raw", "sd_status", "sd_exact_if_observed",
    "sd_upper_bound_if_censored", "reported_unit", "data_level",
)
NUM = re.compile(r"^(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[Ee][+-]?[0-9]+)?$")
LIMIT = re.compile(r"^<\s*((?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[Ee][+-]?[0-9]+)?)$")


def checksum(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def parse_cell(raw):
    """Return status, observed numeric string, upper bound; no imputations."""
    val = (raw or "").strip()
    if not val:
        return "blank_in_source", "", ""
    if val == "*":
        return "asterisk_placeholder_source_meaning_unverified", "", ""
    candidate = LIMIT.fullmatch(val)
    if candidate:
        bound = Decimal(candidate.group(1))
        if not bound.is_finite() or bound <= 0:
            raise ValueError("Invalid soil censor threshold")
        return "reported_below_threshold", "", str(bound)
    if not NUM.fullmatch(val):
        raise ValueError("Unsupported soil numeric/qualifier token: " + val)
    try:
        number = Decimal(val)
    except InvalidOperation as exc:
        raise ValueError("Invalid soil number") from exc
    if not number.is_finite() or number < 0:
        raise ValueError("Invalid negative or non-finite soil number")
    return "observed_reported_summary", val, ""


def run(tsv, out, source_sha=PUBLIC_SHA):
    if checksum(tsv) != source_sha:
        raise ValueError("CIP soil TSV SHA-256 mismatch: audit new source first")
    with Path(tsv).open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        required = {"Ciudad", "Locality", "Altitude"}
        for _, mean, sd, _ in TRAITS:
            required.update((mean, sd))
        if not required.issubset(set(reader.fieldnames or [])):
            raise ValueError("CIP soil source missing expected pH, Fe, or Zn fields")
        source = []
        for record in reader:
            if None in record or any(v is None for v in record.values()):
                raise ValueError("Ragged soil source row")
            source.append((reader.line_num, record))
    if len(source) != 9:
        raise ValueError("Expected nine public CIP soil-site summary records")
    seen = set()
    result = []
    for line, record in source:
        city, locality = record["Ciudad"].strip(), record["Locality"].strip()
        if not city or not locality or (city, locality) in seen:
            raise ValueError("Missing/duplicate CIP soil-site locality")
        seen.add((city, locality))
        # Even though the column says Altitude, the table header does not say
        # whether it is m/ft; retain raw text without inventing a unit.
        altitude = record["Altitude"]
        if altitude.strip():
            parse = parse_cell(altitude)
            if parse[0] != "observed_reported_summary":
                raise ValueError("Altitude source has unsupported qualifier")
        for label, m, sd, unit in TRAITS:
            mean_raw = record[m]
            sd_raw = record[sd]
            ms, mv, ml = parse_cell(mean_raw)
            ss, sv, sl = parse_cell(sd_raw)
            if ms == "observed_reported_summary":
                val = Decimal(mv)
                if label == "soil_pH" and not 0 <= val <= 14:
                    raise ValueError("Reported pH outside physical 0-14 range")
            # An SD value is not an independent observation or replicate.
            result.append({
                "source_doi": DOI, "source_file_id": FILE_ID,
                "source_tsv_line": line, "city_raw": record["Ciudad"],
                "locality_raw": record["Locality"],
                "altitude_raw_unit_unverified": altitude,
                "soil_trait": label, "source_mean_raw": mean_raw,
                "mean_status": ms, "mean_exact_if_observed": mv,
                "mean_upper_bound_if_censored": ml,
                "source_sd_raw": sd_raw, "sd_status": ss,
                "sd_exact_if_observed": sv,
                "sd_upper_bound_if_censored": sl,
                "reported_unit": unit, "data_level": "published_soil_site_aggregate"
            })
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    csvpath = out / "peru_soil_site_context.csv"
    with csvpath.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(result)
    report = {
        "source_doi": DOI, "file_id": FILE_ID, "source_url": API,
        "source_sha256": source_sha, "derived_csv_sha256": checksum(csvpath),
        "site_rows": len(seen), "site_trait_summaries": len(result),
        "traits": [item[0] for item in TRAITS],
        "mean_status_counts": {label: sum(r["mean_status"] == label for r in result)
                               for label in sorted(set(r["mean_status"] for r in result))},
        "sd_status_counts": {label: sum(r["sd_status"] == label for r in result)
                             for label in sorted(set(r["sd_status"] for r in result))},
        "limitations": [
            "Soil iron/zinc ppm are NOT potato tuber iron/zinc dry-weight concentrations.",
            "Site aggregate soil summaries are NOT genotype, treatment, plot or batch observations.",
            "Do not join soil sites to clone-specific Peru Table 16 summaries absent source keys.",
            "Source asterisk meaning has not been verified; kept as uninterpreted placeholder.",
            "Censored values are NOT replaced by zero or a threshold midpoint.",
            "Column Altitude contains no explicit unit; numeric raw text is preserved without unit.",
            "No genotype by environment effect, soil causation, p-value or heritability estimated."
        ]
    }
    (out / "peru_soil_site_provenance.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8"
    )
    (out / "peru_soil_site_report.md").write_text(
        "# OP-M1-10 — Contexto de suelos de nueve sitios peruanos\n\n"
        f"Fuente primaria pública: https://doi.org/{DOI} (archivo {FILE_ID}).\n\n"
        f"- {len(seen)} localidades de suelo y {len(result)} resúmenes sitio × rasgo.\n"
        "- Rasgos: pH de suelo, Fe de suelo y Zn de suelo (columnas ppm).\n"
        "- Se conservan caracteres de censura, asteriscos y campos vacíos sin imputación.\n"
        "- Altitud conservada como texto original porque su unidad no aparece en el encabezado.\n"
        "- Las estadísticas de suelo NO son concentraciones de tubérculos ni medidas por parcela.\n"
        "- Ningún sitio fue unido artificialmente a un clon, laboratorio o bloque.\n",
        encoding="utf-8"
    )
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tsv", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.tsv, args.out), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

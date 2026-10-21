"""M1-13: audit six public CIP Peru table *schemas*, not participant records.

This produces only file metadata / CSV header and field coverage. Some
public PVS tables may include participant data: no cell values, IDs, names
or row examples are exported. A table name suggesting 'per plot' does NOT
prove any row can be linked to a chemical Fe/Zn assay.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path

DOI = "10.21223/N11QJS"
SOURCES = {
    "mineral_shipment": {
        "id": 6982, "sha": "7b56c321e63e4bd9a33543b32f339c70e88e69ec441ae365d80e7b6e119082aa",
        "rows": 8, "columns": 7, "kind": "shipment_schedule_not_assay_values",
    },
    "field_calendar": {
        "id": 6972, "sha": "35a8060590288bf67dc5eec94d1f7850f6e8746431dfe883c8aaaa2601ef8a1b",
        "rows": 14, "columns": 17, "kind": "field_calendar",
    },
    "flowering_selection": {
        "id": 6971, "sha": "a44760b27715de114307c1f0efe058b2d5e9c0d17243989daf835c8e18d7abaa",
        "rows": 39, "columns": 21, "kind": "participatory_selection_not_chemical_assay",
    },
    "harvest_selection": {
        "id": 6968, "sha": "5b28f757d1cf2478e2be3e2eebe05af3e37b9bbb884f4de6faf1bc0be9ae0fb3",
        "rows": 40, "columns": 21, "kind": "participatory_selection_not_chemical_assay",
    },
    "soil_sample_list": {
        "id": 6975, "sha": "5058b84cea069d72ee92fb855ce0692c004ed8cb5a7bac41367490fa4d4972ae",
        "rows": 11, "columns": 9, "kind": "soil_sampling_context_not_tuber_assay",
    },
    "tuber_mineral_summary": {
        "id": 6980, "sha": "0f33b843e286eab15ad71c6c110592adc60709997d75b2b1c5f7365ca99f6152",
        "rows": 42, "columns": 84, "kind": "genotype_published_aggregate_not_plot",
    },
}
FIELDS = [
    "source_doi", "file_id", "table_role", "export_sha256",
    "table_rows_excluding_header", "source_columns", "source_header_kind",
    "contains_verified_plot_level_mineral_assay", "verified_join_to_assay_plot",
    "biological_unit_documented", "next_required_evidence",
]
PVS_TABLES = {"flowering_selection", "harvest_selection"}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def audit(sources, out):
    if set(sources) != set(SOURCES):
        raise ValueError("Provide exactly the six separately verified public CIP sources")
    summaries = []
    for label, expected in SOURCES.items():
        path = Path(sources[label])
        if sha256(path) != expected["sha"]:
            raise ValueError(f"{label}: source SHA-256 mismatch")
        with path.open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.reader(handle, delimiter="\t"))
        if len(rows) != expected["rows"] or not rows or len(rows[0]) != expected["columns"]:
            raise ValueError(f"{label}: source row count or column schema changed")
        if any(len(row) != expected["columns"] for row in rows):
            raise ValueError(f"{label}: irregular TSV row layout")
        header = rows[0]
        if label in PVS_TABLES:
            if not header[0].startswith("Tabla") or header[1:] != [
                    chr(i) for i in range(ord("B"), ord("U")+1)]:
                raise ValueError(f"{label}: unexpected positional spreadsheet header")
            kind = "positional_spreadsheet_letters"
        elif label == "field_calendar":
            if header != [chr(i) for i in range(ord("A"), ord("Q")+1)]:
                raise ValueError("Calendar column layout changed")
            kind = "positional_spreadsheet_letters"
        elif label == "mineral_shipment":
            if not header[0].startswith("Tabla11:") or header[1:] != list("BCDEFG"):
                raise ValueError("Shipment source sheet changed")
            kind = "positional_spreadsheet_letters"
        elif label == "soil_sample_list":
            if header[:3] != ["ORD", "Adm1", "Adm2"]:
                raise ValueError("Soil sample list source schema changed")
            kind = "named_source_columns"
        else:
            if ("INSTN" not in header or "MeanFEDW" not in header
                    or "MeanZNDW" not in header or "nFEDW" not in header):
                raise ValueError("Tuber summary source unexpectedly lacks published aggregate columns")
            kind = "named_genotype_aggregate_columns"
        # Source sheets can contain sensitive or community-participant records.
        # Only source *schema*, no row contents or headers identifying people, goes to artifacts.
        summaries.append({
            "source_doi": DOI,
            "file_id": expected["id"],
            "table_role": expected["kind"],
            "export_sha256": expected["sha"],
            "table_rows_excluding_header": len(rows)-1,
            "source_columns": expected["columns"],
            "source_header_kind": kind,
            "contains_verified_plot_level_mineral_assay": "NOT_ESTABLISHED",
            "verified_join_to_assay_plot": "NO",
            "biological_unit_documented": "source_table_only_no_verified_chemical_plot_link",
            "next_required_evidence": "accession_site_year_block_plot_chemical_sample_original_keys",
        })
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    csvfile = out / "cip_public_linkage_readiness.csv"
    with csvfile.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(summaries)
    provenance = {
        "source_doi": DOI,
        "source_dataset_version": "1.0",
        "public_source_count": len(SOURCES),
        "source_export_sha256": {k: v["sha"] for k, v in SOURCES.items()},
        "verified_plot_to_mineral_assay_linkages": 0,
        "admission_to_mineral_gxe_model": "DENIED_UNTIL_LINKABLE_PRIMARY_ASSAYS",
        "derived_csv_sha256": sha256(csvfile),
        "privacy": "No row-level or person-level source values emitted; source bytes are transient.",
        "limits": [
            "NO verified genotype × location × season × block × plot × lab-sample Fe/Zn data here.",
            "Positional columns are NOT evidence of per-plot chemistry keys.",
            "A flowering/harvest PVS preference is NOT a mineral assay.",
            "The mineral shipment calendar is NOT a table of measured mineral outcomes.",
            "The soil sample list describes SOIL samples, not tuber tissue Fe/Zn assays.",
            "Table 12 Fe/Zn entries are pooled genotype-level published summaries, NOT plots.",
            "Absence of validated links is not proof that plot measurements do not exist elsewhere.",
            "No participant-level values retained, joined, logged or redistributed.",
        ],
    }
    (out / "cip_public_linkage_provenance.json").write_text(
        json.dumps(provenance, ensure_ascii=False, indent=2, sort_keys=True)+"\n",
        encoding="utf-8")
    (out / "cip_public_linkage_report.md").write_text(
        "# M1-13 — Vinculación de ensayos y muestras públicas CIP: auditoría de aptitud\n\n"
        "**Resultado: seis tablas públicas autenticadas, ningún vínculo de ensayo químico por parcela verificado.**\n\n"
        "La tabla de envío de muestras describe logística, no valores Fe/Zn de muestras individuales. "
        "Los formularios PVS describen selección participativa, no química nutricional por parcela. "
        "Las tablas abiertas de Fe/Zn contienen resúmenes por genotipo. La lista de suelos "
        "no identifica mediciones minerales en tubérculos.\n\n"
        "Los encabezados posicionales A/B/C no pueden mapearse automáticamente a "
        "genotipo, año, bloque o muestra. Esta auditoría NO vuelca datos de participantes.\n\n"
        "Falta confirmar una clave original genotipo × localidad × año × bloque × parcela × "
        "ID muestra liofilizada × Fe/Zn con unidad/método analítico y permiso legítimo.\n\n"
        "CIP: https://doi.org/10.21223/N11QJS\n",
        encoding="utf-8",
    )
    return provenance


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input-dir", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    source_paths = {label: args.input_dir / (str(info["id"])+".tab")
                    for label, info in SOURCES.items()}
    print(json.dumps(audit(source_paths, args.out), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

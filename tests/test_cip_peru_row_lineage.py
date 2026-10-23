"""Synthetic source rows for M1-09. No synthetic material is presented as science."""
import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.cip_peru_selected import MAPPING, transform, sha256
from scripts.cip_peru_row_lineage import run


def build_fixture(folder, change_source=None, change_derived=None):
    folder = Path(folder)
    header = ["INSTN", "BREEDERCODE"]
    for _, count, mean, sd, low, high, _ in MAPPING:
        header.extend((count, mean, sd, low, high))
    rows = []
    for i in range(14):
        r = {"INSTN": f"CIP{i+1:06d}.001", "BREEDERCODE": f"BIOT-{i+1}"}
        for _, count, mean, sd, low, high, _ in MAPPING:
            r.update({count: "8", mean: "20.40", sd: "2.10", low: "15.0", high: "30.0"})
        rows.append(r)
    for fe, zn in [("Mean", "Prom"), ("Max", "Max"), ("Min", "Min")]:
        r = dict.fromkeys(header, "")
        r["nFEDW"] = fe
        r["nZNDW"] = zn
        rows.append(r)
    if change_source:
        change_source(rows)
    tsv = folder / "test_source.tsv"
    with tsv.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=header, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)
    generated = folder / "derivative"
    # The existing importer is the single truth for converting *valid* fixtures.
    if len(rows) == 17 and [r["nFEDW"] for r in rows[-3:]] == ["Mean", "Max", "Min"]:
        # If the fixture intentionally duplicates an ID or has a broken source, a
        # valid derivative is instead produced from the unmodified source later.
        pass
    return tsv, generated


def prepared_fixture(folder):
    tsv, generated = build_fixture(folder)
    transform(tsv, generated, pinned_sha=sha256(tsv))
    return tsv, generated / "peru_selected_aggregate_fe_zn.csv", generated / "peru_selected_provenance.json"


def rewrite_csv(path, manifest_path, mutate):
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        fields, rows = reader.fieldnames, list(reader)
    mutate(rows)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    m = json.loads(manifest_path.read_text(encoding="utf-8"))
    m["derived_csv_sha256"] = sha256(path)
    manifest_path.write_text(json.dumps(m), encoding="utf-8")


class PeruRowLineageTests(unittest.TestCase):
    def test_real_semantics_fixture_traces_every_statistic_and_footer(self):
        with tempfile.TemporaryDirectory() as td:
            tsv, derivative, manifest = prepared_fixture(td)
            result = run(tsv, Path(td) / "lineage", derivative, manifest, sha256(tsv))
            self.assertEqual(result["material_rows"], 14)
            self.assertEqual(result["matched_source_statistics"], 28)
            self.assertEqual(result["excluded_global_summary_rows"], 3)
            with (Path(td) / "lineage/peru_row_lineage.csv").open() as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual({int(r["source_tsv_line"]) for r in rows}, set(range(2, 16)))
            self.assertEqual(rows[0]["source_mean_raw"], "20.40")
            self.assertEqual(rows[0]["source_file_id"], "6979")
            with (Path(td) / "lineage/peru_source_footer_ledger.csv").open() as stream:
                excluded = list(csv.DictReader(stream))
            self.assertEqual([r["fe_footer_label_raw"] for r in excluded], ["Mean", "Max", "Min"])
            self.assertTrue(all(r["source_material_id_raw"] == "" for r in excluded))

    def test_raw_identifier_preserved_separately_from_normalized_accession(self):
        with tempfile.TemporaryDirectory() as td:
            tsv, out = build_fixture(td, lambda rows: rows[0].__setitem__("INSTN", "  CIP000001.001  "))
            transform(tsv, out, pinned_sha=sha256(tsv))
            result = run(tsv, Path(td) / "lineage", out / "peru_selected_aggregate_fe_zn.csv",
                         out / "peru_selected_provenance.json", sha256(tsv))
            self.assertEqual(result["matched_source_statistics"], 28)
            with (Path(td) / "lineage/peru_row_lineage.csv").open() as stream:
                records = list(csv.DictReader(stream))
            self.assertEqual(records[0]["source_material_id_raw"], "  CIP000001.001  ")
            self.assertEqual(records[0]["derived_accession"], "CIP000001.001")

    def test_derivative_statistic_swap_rejected_even_with_recomputed_hash(self):
        with tempfile.TemporaryDirectory() as td:
            tsv, data, meta = prepared_fixture(td)
            rewrite_csv(data, meta, lambda rows: rows[0].__setitem__("published_mean", "21.5"))
            with self.assertRaisesRegex(ValueError, "statistic mismatch"):
                run(tsv, Path(td) / "audit", data, meta, sha256(tsv))

    def test_derivative_missing_statistic_rejected_even_with_recomputed_hash(self):
        with tempfile.TemporaryDirectory() as td:
            tsv, data, meta = prepared_fixture(td)
            rewrite_csv(data, meta, lambda rows: rows[0].__setitem__("published_sd", ""))
            with self.assertRaisesRegex(ValueError, "missing measurement"):
                run(tsv, Path(td) / "audit", data, meta, sha256(tsv))

    def test_duplicate_source_accession_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            tsv, data, meta = prepared_fixture(td)
            with tsv.open(newline="", encoding="utf-8") as stream:
                reader = csv.DictReader(stream, delimiter="\t")
                headers, rows = reader.fieldnames, list(reader)
            rows[1]["INSTN"] = rows[0]["INSTN"]
            with tsv.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=headers, delimiter="\t")
                writer.writeheader()
                writer.writerows(rows)
            # The fixed manifest and source hash must reject source tampering.
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                run(tsv, Path(td) / "audit", data, meta)

    def test_unexpected_footer_refused_without_forward_filling(self):
        with tempfile.TemporaryDirectory() as td:
            tsv, data, meta = prepared_fixture(td)
            with tsv.open(newline="", encoding="utf-8") as stream:
                reader = csv.DictReader(stream, delimiter="\t")
                headers, rows = reader.fieldnames, list(reader)
            rows[-3]["nZNDW"] = "NOT_A_FOOTER"
            with tsv.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=headers, delimiter="\t")
                writer.writeheader()
                writer.writerows(rows)
            with self.assertRaisesRegex(ValueError, "footer"):
                run(tsv, Path(td) / "audit", data, meta, sha256(tsv))

    def test_missing_or_extra_tsv_record_refused(self):
        with tempfile.TemporaryDirectory() as td:
            tsv, data, meta = prepared_fixture(td)
            with tsv.open(newline="", encoding="utf-8") as stream:
                reader = csv.DictReader(stream, delimiter="\t")
                headers, rows = reader.fieldnames, list(reader)
            rows.pop(5)
            with tsv.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=headers, delimiter="\t")
                writer.writeheader()
                writer.writerows(rows)
            with self.assertRaisesRegex(ValueError, "row count"):
                run(tsv, Path(td) / "audit", data, meta, sha256(tsv))


if __name__ == "__main__":
    unittest.main()

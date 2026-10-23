"""M1-08 tests with pinned real public source derivatives, no invented field plots."""
import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.cip_three_source_audit import ROOT, SOURCES, run


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def rewrite_peru(tmp, edit):
    source = ROOT / SOURCES["peru"][0]
    manifest = ROOT / SOURCES["peru"][1]
    with source.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames
        rows = list(reader)
    edit(rows)
    target = Path(tmp) / "peru.csv"
    with target.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    metadata = json.loads(manifest.read_text(encoding="utf-8"))
    metadata["derived_csv_sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()
    target_manifest = Path(tmp) / "manifest.json"
    target_manifest.write_text(json.dumps(metadata), encoding="utf-8")
    return {"peru": (target, target_manifest)}


class TripleSourceAuditTests(unittest.TestCase):
    def test_real_pinned_sources_and_empty_missing_values(self):
        with tempfile.TemporaryDirectory() as td:
            meta = run(Path(td) / "out")
            self.assertEqual(meta["peru_materials"], 14)
            self.assertEqual(meta["peru_controls"], 2)
            self.assertEqual(meta["selected_clones_in_catalogue"], 12)
            self.assertEqual(meta["peru_clones_in_all_three_sources"], 8)
            rows = read_csv(Path(td) / "out" / "three_source_accession_audit.csv")
            self.assertEqual(len(rows), 14)
            self.assertEqual(sum(r["material_role"] == "commercial_control" for r in rows), 2)
            self.assertEqual(sum(bool(r["fe_holetta_mg_kg_dry"]) for r in rows), 8)
            self.assertEqual(sum(bool(r["fe_catalogue_mg_kg_dry"]) for r in rows), 12)
            for row in rows:
                self.assertEqual(row["evidence_design"], "nonmatched_published_summaries_no_gxe_inference")
                self.assertNotIn("p_value", row)
                if row["material_role"] == "commercial_control":
                    self.assertEqual(row["fe_catalogue_mg_kg_dry"], "")
                    self.assertEqual(row["fe_holetta_mg_kg_dry"], "")
            self.assertIn("No pooling", " ".join(meta["limits"]))

    def test_detects_tampered_source(self):
        with tempfile.TemporaryDirectory() as td:
            source = ROOT / SOURCES["peru"][0]
            csvpath = Path(td) / "altered.csv"
            csvpath.write_bytes(source.read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                run(Path(td) / "out", overrides={
                    "peru": (csvpath, ROOT / SOURCES["peru"][1])
                })

    def test_refuses_duplicate_accession_trait_even_with_updated_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            edits = rewrite_peru(td, lambda rows: rows.append(dict(rows[0])))
            with self.assertRaisesRegex(ValueError, "Duplicate Peru"):
                run(Path(td) / "out", overrides=edits)

    def test_refuses_missing_zinc_summary(self):
        with tempfile.TemporaryDirectory() as td:
            edits = rewrite_peru(td, lambda rows: rows.pop(1))
            with self.assertRaisesRegex(ValueError, "Incomplete Fe/Zn"):
                run(Path(td) / "out", overrides=edits)

    def test_refuses_dry_fresh_unit_mismatch(self):
        with tempfile.TemporaryDirectory() as td:
            edits = rewrite_peru(td, lambda rows: rows[0].__setitem__("unit", "mg/kg_fresh"))
            with self.assertRaisesRegex(ValueError, "unit"):
                run(Path(td) / "out", overrides=edits)

    def test_refuses_published_count_as_fractional_n(self):
        with tempfile.TemporaryDirectory() as td:
            edits = rewrite_peru(td, lambda rows: rows[0].__setitem__("reported_n", "2.5"))
            with self.assertRaisesRegex(ValueError, "integer"):
                run(Path(td) / "out", overrides=edits)


if __name__ == "__main__":
    unittest.main()

"""M1-12 integrity, provenance and interpretive safeguards on pinned derivatives."""
import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.cip_peru_catalogue_contrast import (
    run, ROOT, PERU_CSV, PERU_META, CAT_CSV, CAT_META
)


def patch_snapshot(folder, source, manifest, mutate):
    folder = Path(folder)
    with Path(source).open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        headers, rows = reader.fieldnames, list(reader)
    mutate(rows)
    output = folder / ("modified_" + Path(source).name)
    with output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    metadata = json.loads(Path(manifest).read_text(encoding="utf-8"))
    metadata["derived_csv_sha256"] = hashlib.sha256(output.read_bytes()).hexdigest()
    manifest_copy = folder / ("modified_" + Path(manifest).name)
    manifest_copy.write_text(json.dumps(metadata), encoding="utf-8")
    return output, manifest_copy


class PeruCatalogueContrastTests(unittest.TestCase):
    def test_pinned_primary_sources_all_29_exact_ids_and_no_pseudo_replicates(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "out"
            result = run(out)
            self.assertEqual(result["matched_accessions"], 29)
            self.assertEqual(result["trait_contrasts"], 58)
            self.assertEqual(result["peru_evaluated_clones"], 30)
            self.assertEqual(result["peru_controls_excluded"], 4)
            self.assertEqual(result["peru_clone_not_in_catalogue"], ["CIP312686.019"])
            self.assertEqual(result["below_catalogue_counts"], {"iron": 29, "zinc": 29})
            for v in result["median_peru_to_catalogue_ratio_descriptive"].values():
                self.assertLess(float(v), 1.0)
            with (out / "peru_catalogue_29_clone_contrast.csv").open() as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(len(rows), 58)
            self.assertEqual(len({r["accession"] for r in rows}), 29)
            self.assertEqual({r["trait"] for r in rows}, {"iron", "zinc"})
            self.assertTrue(all(r["source_independence"] == "NOT_ESTABLISHED" for r in rows))
            self.assertTrue(all(r["unit"] == "mg/kg_dry" for r in rows))
            self.assertTrue(all(float(r["peru_minus_catalogue_descriptive"]) < 0 for r in rows))
            self.assertTrue(all(float(r["peru_to_catalogue_ratio_descriptive"]) < 1 for r in rows))
            self.assertTrue(all("pvalue" not in r for r in rows))
            self.assertTrue(any("NOT a paired" in x for x in result["limits"]))
            out2 = Path(td) / "again"
            second = run(out2)
            self.assertEqual(result["derived_csv_sha256"], second["derived_csv_sha256"])

    def test_source_tampering_without_manifest_update_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            filename = Path(td) / "tampered.csv"
            filename.write_bytes(PERU_CSV.read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                run(Path(td) / "out", peru_csv=filename)

    def test_source_doi_tampering_even_with_updated_snapshot_hash_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            csvpath, manifest = patch_snapshot(
                td, PERU_CSV, PERU_META,
                lambda rows: rows[0].__setitem__("source_doi", "10.0000/NOT-CIP"))
            with self.assertRaisesRegex(ValueError, "DOI"):
                run(Path(td) / "out", peru_csv=csvpath, peru_meta=manifest)

    def test_same_clone_two_fe_rows_is_rejected_even_with_updated_hash(self):
        with tempfile.TemporaryDirectory() as td:
            def break_rows(rows):
                rows[1]["nutrient"] = "iron"
            csvpath, manifest = patch_snapshot(td, PERU_CSV, PERU_META, break_rows)
            with self.assertRaisesRegex(ValueError, "duplicate"):
                run(Path(td) / "out", peru_csv=csvpath, peru_meta=manifest)

    def test_missing_mean_rejected_without_renormalization(self):
        with tempfile.TemporaryDirectory() as td:
            csvpath, manifest = patch_snapshot(
                td, PERU_CSV, PERU_META,
                lambda rows: rows[0].__setitem__("published_mean", ""))
            with self.assertRaisesRegex(ValueError, "missing"):
                run(Path(td) / "out", peru_csv=csvpath, peru_meta=manifest)

    def test_fresh_weight_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            csvpath, manifest = patch_snapshot(
                td, PERU_CSV, PERU_META,
                lambda rows: rows[0].__setitem__("unit", "mg/kg_fresh"))
            with self.assertRaisesRegex(ValueError, "unit"):
                run(Path(td) / "out", peru_csv=csvpath, peru_meta=manifest)

    def test_catalogue_id_not_in_same_peru_population_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            csvpath, manifest = patch_snapshot(
                td, CAT_CSV, CAT_META,
                lambda rows: rows[0].__setitem__("accession_id", "CIP000000.999"))
            with self.assertRaisesRegex(ValueError, "not exactly within"):
                run(Path(td) / "out", catalogue_csv=csvpath, catalogue_meta=manifest)

    def test_duplicate_catalogue_accession_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            csvpath, manifest = patch_snapshot(
                td, CAT_CSV, CAT_META,
                lambda rows: rows[1].__setitem__("accession_id", rows[0]["accession_id"]))
            with self.assertRaisesRegex(ValueError, "duplicate"):
                run(Path(td) / "out", catalogue_csv=csvpath, catalogue_meta=manifest)


if __name__ == "__main__":
    unittest.main()

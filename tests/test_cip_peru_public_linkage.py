"""Synthetic structural fixtures: never reproduce actual PVS participant records."""
import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import cip_peru_public_linkage as mod


def generate(root, mutate=None):
    root = Path(root)
    test_sources = {}
    paths = {}
    for label, info in mod.SOURCES.items():
        x = dict(info)
        if label == "field_calendar":
            header = [chr(i) for i in range(ord("A"), ord("Q")+1)]
        elif label in ("harvest_selection", "flowering_selection"):
            header = ["Tabla TEST synthetic participants"] + list("BCDEFGHIJKLMNOPQRSTU")
        elif label == "mineral_shipment":
            header = ["Tabla11:TEST synthetic shipment"] + list("BCDEFG")
        elif label == "soil_sample_list":
            header = ["ORD", "Adm1", "Adm2"] + [f"FIELD{i}" for i in range(6)]
        else:
            header = ["INSTN", "MeanFEDW", "MeanZNDW", "nFEDW"] + [
                f"FIELD{i}" for i in range(info["columns"]-4)]
        assert len(header) == info["columns"], label
        rows = [header] + [["FAKE_PRIVATE_NAME_NOT_FOR_EXPORT"]*len(header)
                           for _ in range(info["rows"]-1)]
        if mutate:
            mutate(label, rows)
        filename = root / f"{info['id']}.tab"
        with filename.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter="\t")
            writer.writerows(rows)
        x["sha"] = mod.sha256(filename)
        test_sources[label] = x
        paths[label] = filename
    return test_sources, paths


class PublicLinkageTests(unittest.TestCase):
    def test_synthetic_six_file_audit_denies_false_chemistry_linkage(self):
        with tempfile.TemporaryDirectory() as temp:
            sources, paths = generate(temp)
            with patch.dict(mod.SOURCES, sources, clear=True):
                result = mod.audit(paths, Path(temp)/"derived")
                self.assertEqual(result["public_source_count"], 6)
                self.assertEqual(result["verified_plot_to_mineral_assay_linkages"], 0)
                self.assertEqual(result["admission_to_mineral_gxe_model"],
                                 "DENIED_UNTIL_LINKABLE_PRIMARY_ASSAYS")
                for filepath in (Path(temp)/"derived").iterdir():
                    text = filepath.read_text(encoding="utf-8")
                    self.assertNotIn("FAKE_PRIVATE_NAME_NOT_FOR_EXPORT", text)
                report=json.loads((Path(temp)/"derived/cip_public_linkage_provenance.json")
                                  .read_text())
                self.assertTrue(report["privacy"].startswith("No row-level"))

    def test_source_tampering_even_after_inventory_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            sources, paths = generate(temp)
            with paths["mineral_shipment"].open("a") as stream:
                stream.write("malicious\tentry\n")
            with patch.dict(mod.SOURCES, sources, clear=True):
                with self.assertRaisesRegex(ValueError, "SHA-256"):
                    mod.audit(paths, Path(temp)/"out")

    def test_misleading_friendly_spreadsheet_header_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            def mutate(label, rows):
                if label == "flowering_selection": rows[0][3]="plot_id"
            sources, paths = generate(temp, mutate)
            with patch.dict(mod.SOURCES, sources, clear=True):
                with self.assertRaisesRegex(ValueError, "positional"):
                    mod.audit(paths, Path(temp)/"out")

    def test_wrong_actual_row_count_rejected_with_valid_test_hash(self):
        with tempfile.TemporaryDirectory() as temp:
            def mutate(label, rows):
                if label == "soil_sample_list": rows.pop()
            sources, paths = generate(temp, mutate)
            with patch.dict(mod.SOURCES, sources, clear=True):
                with self.assertRaisesRegex(ValueError, "row count"):
                    mod.audit(paths, Path(temp)/"out")

    def test_extra_unverified_source_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            sources, paths = generate(temp)
            paths["unlisted"] = paths["soil_sample_list"]
            with patch.dict(mod.SOURCES, sources, clear=True):
                with self.assertRaisesRegex(ValueError, "exactly six"):
                    mod.audit(paths, Path(temp)/"out")


if __name__ == "__main__":
    unittest.main()

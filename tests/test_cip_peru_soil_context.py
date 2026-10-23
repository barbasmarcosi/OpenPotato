"""Synthetic nine-location context fixtures; never claims synthetic values are CIP measurements."""
import csv
import tempfile
import unittest
from pathlib import Path

from scripts.cip_peru_soil_context import run, checksum, parse_cell


def fixture(path, modify=None):
    header = [
        "Ciudad", "Locality", "Altitude",
        "SoilpHmean", "SoilpHsd",
        "Zincppmmean", "Zincppmsd",
        "Ironppmmean", "Ironppmsd",
    ]
    rows = []
    for i in range(9):
        rows.append({
            "Ciudad": f"Region-{i}", "Locality": f"Site-{i}",
            "Altitude": "2500", "SoilpHmean": "5.5",
            "SoilpHsd": "0.3", "Zincppmmean": "0.7",
            "Zincppmsd": "0.1", "Ironppmmean": "35.1",
            "Ironppmsd": "2.5",
        })
    rows[0]["Ironppmmean"] = "< 0.02"
    rows[0]["Ironppmsd"] = "*"
    rows[1]["Zincppmsd"] = ""
    if modify:
        modify(rows)
    with Path(path).open("w", newline="", encoding="utf-8") as stream:
        w = csv.DictWriter(stream, fieldnames=header, delimiter="\t")
        w.writeheader()
        w.writerows(rows)


class SoilContextTests(unittest.TestCase):
    def test_censor_placeholder_and_blank_are_not_zero(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "source.tab"
            fixture(src)
            report = run(src, Path(td) / "output", source_sha=checksum(src))
            self.assertEqual(report["site_rows"], 9)
            self.assertEqual(report["site_trait_summaries"], 27)
            with (Path(td) / "output/peru_soil_site_context.csv").open() as stream:
                rec = list(csv.DictReader(stream))
            self.assertEqual(rec[2]["soil_trait"], "soil_iron")
            self.assertEqual(rec[2]["source_mean_raw"], "< 0.02")
            self.assertEqual(rec[2]["mean_status"], "reported_below_threshold")
            self.assertEqual(rec[2]["mean_exact_if_observed"], "")
            self.assertEqual(rec[2]["mean_upper_bound_if_censored"], "0.02")
            self.assertEqual(rec[2]["sd_status"], "asterisk_placeholder_source_meaning_unverified")
            self.assertEqual(rec[2]["sd_exact_if_observed"], "")
            self.assertEqual(rec[4]["sd_status"], "blank_in_source")
            self.assertTrue(all(r["data_level"] == "published_soil_site_aggregate" for r in rec))
            self.assertTrue(all(r["reported_unit"].startswith(("pH_", "ppm_")) for r in rec))

    def test_duplicate_site_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "soil.tsv"
            def make_duplicate(rows):
                rows[1]["Ciudad"] = rows[0]["Ciudad"]
                rows[1]["Locality"] = rows[0]["Locality"]
            fixture(path, make_duplicate)
            with self.assertRaisesRegex(ValueError, "duplicate"):
                run(path, Path(td) / "out", source_sha=checksum(path))

    def test_source_sha_change_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "soil.tsv"
            fixture(path)
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                run(path, Path(td) / "out")

    def test_non_numeric_token_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unsupported"):
            parse_cell("maybe")

    def test_pH_out_of_bounds_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "soil.tsv"
            fixture(path, lambda rows: rows[0].__setitem__("SoilpHmean", "15.2"))
            with self.assertRaisesRegex(ValueError, "pH"):
                run(path, Path(td) / "out", source_sha=checksum(path))

    def test_negative_and_bad_detection_threshold_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unsupported"):
            parse_cell("-3.4")
        with self.assertRaisesRegex(ValueError, "Invalid soil censor"):
            parse_cell("<0")


if __name__ == "__main__":
    unittest.main()

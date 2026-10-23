"""Integrity tests against versioned USDA Foundation market type snapshots."""
import csv
import json
import unittest
from decimal import Decimal
from pathlib import Path
from scripts.usda_foundation import compare, filehash, EXPECTED

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"datasets"/"foundation"
EXPECTED_ZIP_SHA="70457ee9d9342f43bda2010318c85f04210c689fdeb9cd2da4c513b0e8dbc655"

class FoundationSnapshotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.meta=json.loads((SOURCE/"foundation_provenance.json").read_text(encoding="utf-8"))
        with (SOURCE/"foundation_market_types.csv").open(encoding="utf-8",newline="") as file:
            cls.rows=list(csv.DictReader(file))
        cls.index={(r["market_type"],r["nutrient"]):r for r in cls.rows}

    def test_official_archive_and_derived_hashes(self):
        self.assertEqual(self.meta["archive_sha256"],EXPECTED_ZIP_SHA)
        self.assertEqual(filehash(SOURCE/"foundation_market_types.csv"),self.meta["csv_sha256"])

    def test_three_raw_categories_are_not_confused_with_cooked_foods(self):
        self.assertEqual({k: v["fdc_id"] for k,v in self.meta["foods"].items()},
                         {"russet":"2346401","red":"2346402","gold":"2346403"})
        for kind in EXPECTED:
            self.assertEqual(self.meta["foods"][kind]["publication_date"],"2022-10-28")
        self.assertIn("raw",self.meta["form"])
        self.assertIn("no confirmation",self.meta["categories"])

    def test_vitamin_c_and_minerals_are_from_primary_snapshot(self):
        self.assertEqual(self.index["russet","vitamin_c"]["amount_per_100g"],"10.9")
        self.assertEqual(self.index["red","vitamin_c"]["amount_per_100g"],"21.29")
        self.assertEqual(self.index["gold","vitamin_c"]["amount_per_100g"],"23.3")
        self.assertEqual(self.index["red","iron"]["amount_per_100g"],"0.3911")
        self.assertEqual(self.index["gold","zinc"]["amount_per_100g"],"0.3739")

    def test_energy_methods_are_separate(self):
        for kind in EXPECTED:
            general=self.index[kind,"energy_atwater_general_kcal"]
            specific=self.index[kind,"energy_atwater_specific_kcal"]
            self.assertNotEqual(general["amount_per_100g"],specific["amount_per_100g"])
            self.assertEqual(general["unit"],"kcal")
            self.assertEqual(specific["unit"],"kcal")

    def test_absent_does_not_mean_zero(self):
        for kind in EXPECTED:
            for nutrient in ("vitamin_b12","folate_dfe","fiber"):
                self.assertEqual(self.index[kind,nutrient]["status"],"not_reported")
                self.assertEqual(self.index[kind,nutrient]["amount_per_100g"],"")

    def test_comparison_uses_only_available_all_three_types(self):
        # Work directly with the frozen primary dataset, no network.
        import tempfile
        with tempfile.TemporaryDirectory() as temp:
            summary=compare(SOURCE/"foundation_market_types.csv",Path(temp)/"report.md")
            by_nutrient={r["nutrient"]:r for r in summary}
            self.assertEqual(sum(r["complete"] for r in summary),12)
            self.assertFalse(by_nutrient["vitamin_b12"]["complete"])
            self.assertEqual(Decimal(by_nutrient["vitamin_c"]["span"]),Decimal("12.4"))

if __name__=="__main__":
    unittest.main()

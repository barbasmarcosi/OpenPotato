"""Pinned Foundation purchase-sample data: offline audit tests."""
import csv
import json
import unittest
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

from scripts.usda_foundation import filehash

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "datasets" / "variability"
EXPECTED_ARCHIVE_SHA = "70457ee9d9342f43bda2010318c85f04210c689fdeb9cd2da4c513b0e8dbc655"


def read(name):
    with (DATA / name).open(encoding="utf-8",newline="") as f:
        return list(csv.DictReader(f))


class VariabilitySnapshotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.provenance=json.loads((DATA/"retail_sample_provenance.json").read_text(encoding="utf-8"))
        cls.samples=read("retail_sample_measurements.csv")
        cls.summary=read("retail_sample_summary.csv")
        cls.by_pair={(r["market_type"],r["nutrient"]):r for r in cls.summary}

    def test_snapshot_checksums_and_archive_provenance(self):
        self.assertEqual(self.provenance["archive_sha256"],EXPECTED_ARCHIVE_SHA)
        for name,sha in self.provenance["files"].items():
            self.assertEqual(filehash(DATA/name),sha,name)

    def test_24_distinct_purchases_and_96_measurements(self):
        self.assertEqual(len(self.samples),96)
        self.assertEqual(len(self.summary),12)
        unique={r["sample_fdc_id"] for r in self.samples}
        self.assertEqual(len(unique),24)
        self.assertEqual({r["market_type"] for r in self.samples},{"russet","red","gold"})
        for kind in ("russet","red","gold"):
            self.assertEqual(len({r["sample_fdc_id"] for r in self.samples if r["market_type"]==kind}),8)
            for n in ("iron","zinc","potassium","vitamin_c"):
                self.assertEqual(len([r for r in self.samples if r["market_type"]==kind and r["nutrient"]==n]),8)

    def test_reconstructs_original_usda_ranges_and_medians(self):
        for row in self.summary:
            self.assertEqual(row["range_reconciled"],"true")
            self.assertEqual(row["median_reconciled"],"true")
            self.assertEqual(row["published_data_points"],"8")
            self.assertLessEqual(abs(Decimal(row["mean_difference"])),Decimal("0.05"))
            self.assertGreater(Decimal(row["sample_sd"]),0)

    def test_vitamin_c_spread_and_overlap_not_only_means(self):
        russet=self.by_pair["russet","vitamin_c"]
        red=self.by_pair["red","vitamin_c"]
        gold=self.by_pair["gold","vitamin_c"]
        self.assertEqual((russet["minimum"],russet["maximum"]),("7.44","19.8"))
        self.assertEqual((red["minimum"],red["maximum"]),("14.2","29.6"))
        self.assertEqual((gold["minimum"],gold["maximum"]),("16.6","30.3"))
        self.assertGreater(Decimal(russet["maximum"]),Decimal(gold["minimum"]))
        self.assertGreater(Decimal(red["maximum"]),Decimal(gold["minimum"]))

    def test_acquisitions_localized_and_cannot_be_globalized(self):
        self.assertEqual({r["store_state"] for r in self.samples},{"VA"})
        self.assertEqual({r["store_city"] for r in self.samples},
                         {"Blacksburg","Christiansburg","Wytheville"})
        self.assertEqual({r["acquisition_date"][:4] for r in self.samples},{"2022"})
        self.assertEqual(len({r["acquisition_fdc_id"] for r in self.samples}),24)


if __name__ == "__main__":
    unittest.main()

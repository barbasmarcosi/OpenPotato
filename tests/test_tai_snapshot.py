"""Frozen derived metrics for a historically identified multi-environment yield experiment.

The source raw CSV is fetched and checked in CI; this test never copies or
manufactures original plot-level observations or Fe/Zn nutrient measurements.
"""
import csv
import json
import unittest
from decimal import Decimal
from pathlib import Path

from scripts.potato_gxe import filehash

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/"datasets"/"multienvironment"


class TaiHistoricalSnapshotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.meta=json.loads((D/"gxE_provenance.json").read_text())
        with (D/"yield_stability.csv").open(encoding="utf-8",newline="") as f:
            cls.rows=list(csv.DictReader(f))
        with (D/"rank_crossovers.csv").open(encoding="utf-8",newline="") as f:
            cls.pairs=list(csv.DictReader(f))

    def test_original_source_pinned_to_git_commit_and_sha256(self):
        self.assertEqual(self.meta["source_sha256"],
                         "6a758579b091050f02da6a352742201a73d5e3bd7ee2c7624f2a7e9e141a9055")
        self.assertIn("1dcc2bf5f955cc1224a3e1307256e1fe86b68dae",self.meta["source"])
        for name,digest in self.meta["derived_files"].items():
            self.assertEqual(filehash(D/name),digest)

    def test_design_is_mean_level_and_no_minerals(self):
        self.assertEqual(self.meta["environments"],6)
        self.assertEqual(self.meta["genotypes"],8)
        self.assertEqual(len(self.rows),8)
        self.assertEqual({r["observation_level"] for r in self.rows},{"published_aggregate_means"})
        self.assertTrue(self.meta["no_residual_variance_estimate"])
        self.assertIn("NO Fe/Zn",self.meta["trait"])

    def test_sum_squares_and_crossovers_are_descriptive(self):
        total=Decimal(self.meta["total_sum_squares"])
        parts=sum(Decimal(self.meta[f"{k}_sum_squares"]) for k in
                  ("genotype","environment","interaction"))
        self.assertLess(abs(total-parts),Decimal("1e-20"))
        self.assertEqual(len(self.pairs),19)
        self.assertEqual(self.meta["pairs_of_genotypes"],28)
        self.assertEqual(self.meta["pairwise_rank_crossovers"],19)
        self.assertTrue(Decimal(self.meta["environment_share_of_total"]) > Decimal("0.47"))

    def test_genotype_identity_disagreement_requires_manual_primary_check(self):
        # Rdatasets raw table says F6031, but agridat text cites F6032.
        self.assertIn("F6031",{r["variety"] for r in self.rows})
        self.assertNotIn("F6032",{r["variety"] for r in self.rows})


if __name__=="__main__":
    unittest.main()

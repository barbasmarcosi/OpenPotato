"""Integrity tests of scientific means derived from pinned open-access JATS table."""
import csv
import json
import unittest
from decimal import Decimal
from pathlib import Path

from scripts.ethiopia_genotypes import SOURCE_SHA256, sha256

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"datasets"/"cultivars"


class EthiopiaGenotypeSnapshotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.provenance=json.loads((DATA/"genotype_trial_provenance.json").read_text(encoding="utf-8"))
        with (DATA/"genotype_trial_holetta_2019.csv").open(newline="",encoding="utf-8") as handle:
            cls.rows=list(csv.DictReader(handle))
        cls.index={r["genotype"]:r for r in cls.rows}

    def test_pinned_source_and_derived_csv(self):
        self.assertEqual(self.provenance["source_sha256"], SOURCE_SHA256)
        self.assertEqual(
            sha256(DATA/"genotype_trial_holetta_2019.csv"),
            self.provenance["derived_csv_sha256"]
        )
        self.assertEqual(self.provenance["table_id"],"plants-12-02625-t002")

    def test_distinct_genotype_means_not_pseudoreplicates(self):
        self.assertEqual(len(self.rows),45)
        self.assertEqual(len(self.index),45)
        self.assertEqual({r["site"] for r in self.rows},{"Holetta, Ethiopia"})
        self.assertEqual({r["study_year"] for r in self.rows},{"2019"})
        self.assertEqual({r["data_level"] for r in self.rows},{"genotype_reported_means"})
        self.assertIn("single-site",self.provenance["design"])

    def test_study_values_and_dry_matter_units(self):
        self.assertEqual(self.index["Gudanie"]["yield_kg_m2_fresh"],"1.91")
        self.assertEqual(self.index["Gudanie"]["iron_mg_kg_dry"],"14.68")
        self.assertEqual(self.index["CIP312767.014"]["iron_mg_kg_dry"],"26.07")
        self.assertEqual(self.index["CIP312767.014"]["zinc_mg_kg_dry"],"19.14")
        self.assertEqual(self.index["CIP312735.062"]["yield_kg_m2_fresh"],"2.26")
        self.assertIn("dry",self.provenance["units"])
        self.assertIn("fresh",self.provenance["units"])

    def test_15_descriptive_non_dominated_candidates(self):
        names={r["genotype"] for r in self.rows if r["pareto_yield_iron_zinc"]=="true"}
        self.assertEqual(len(names),15)
        self.assertEqual(self.provenance["pareto_candidates"],15)
        self.assertIn("CIP312767.014",names)
        self.assertIn("CIP312735.062",names)

    def test_theoretical_nutrient_mass_is_dimensional_not_assimilation(self):
        sample=self.index["CIP312725.110"]
        expected=(Decimal(sample["yield_kg_m2_fresh"]) *
                  Decimal(sample["dry_matter_pct"])/100 *
                  Decimal(sample["iron_mg_kg_dry"])*10)
        self.assertEqual(Decimal(sample["iron_g_ha_theoretical"]),expected)
        self.assertIn("before losses", self.provenance["limitations"][3])


if __name__ == "__main__":
    unittest.main()

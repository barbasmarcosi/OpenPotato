"""OP-N1-01: test evidence provenance, endpoint non-interchangeability and USDA."""
import copy
import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from openpotato.absorption_opportunity import (
    DEFAULT_STUDIES, DEFAULT_USDA, compile_opportunity,
    publish, usda_baseline, validate_studies
)

class AbsorptionOpportunityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evidence=json.loads(DEFAULT_STUDIES.read_text(encoding="utf-8"))

    def test_separate_two_primary_trials_not_same_genotype(self):
        studies=validate_studies(self.evidence)
        self.assertEqual([x["nutrient"] for x in studies],["iron","zinc"])
        self.assertTrue(all(s["independent_crossover_trial_not_joint_genotype"] for s in studies))
        self.assertEqual({s["participants_women_peru"] for s in studies},{28,37})
        self.assertEqual({s["meal_g"] for s in studies},{"460","500"})

    def test_absorbed_improvement_and_decreasing_fraction_are_distinct(self):
        studies={x["nutrient"]:x for x in validate_studies(self.evidence)}
        self.assertEqual(Decimal(studies["iron"]["absorbed_absolute_difference_mg_per_study_meal"]),Decimal("0.11"))
        self.assertEqual(Decimal(studies["zinc"]["absorbed_absolute_difference_mg_per_study_meal"]),Decimal("0.09"))
        self.assertEqual(Decimal(studies["iron"]["absorbed_difference_pct_based_on_rounded_group_means"]),
                         Decimal("0.11")/Decimal("0.24")*100)
        self.assertEqual(Decimal(studies["zinc"]["absorbed_difference_pct_based_on_rounded_group_means"]),
                         Decimal("22.500"))
        for x in studies.values():
            self.assertLess(Decimal(x["biofortified_fractional_absorption_pct"]),
                            Decimal(x["control_fractional_absorption_pct"]))
            self.assertGreater(Decimal(x["biofortified_concentration_mg_per_100g"]),
                               Decimal(x["control_concentration_mg_per_100g"]))
            self.assertFalse(x["paired_difference_uncertainty_computed"])

    def test_original_doi_and_cohort_masses_cannot_change(self):
        d=copy.deepcopy(self.evidence)
        d["studies"][0]["meal_g"]="500"
        with self.assertRaisesRegex(ValueError,"meal mass"):
            validate_studies(d)
        d=copy.deepcopy(self.evidence)
        d["studies"][1]["doi"]="not_peer_reviewed"
        with self.assertRaisesRegex(ValueError,"provenance"):
            validate_studies(d)

    def test_different_study_materials_cannot_be_marked_as_joint(self):
        d=copy.deepcopy(self.evidence)
        d["same_genotype_both_minerals_measured_in_humans"]=True
        with self.assertRaisesRegex(ValueError,"NOT demonstrated"):
            validate_studies(d)
        d=copy.deepcopy(self.evidence)
        d["studies"][0]["material_linkage"]="same_as_zinc_study"
        with self.assertRaisesRegex(ValueError,"same genotype"):
            validate_studies(d)

    def test_absorbed_mg_not_mg_per_100g(self):
        d=copy.deepcopy(self.evidence)
        d["studies"][0]["unit_absorbed"]="mg_per_100g"
        with self.assertRaisesRegex(ValueError,"unit"):
            validate_studies(d)

    def test_reject_fraction_over_one_hundred_or_negative(self):
        d=copy.deepcopy(self.evidence)
        d["studies"][0]["control"]["fractional_absorption_pct"]="101"
        with self.assertRaisesRegex(ValueError,"100%"):
            validate_studies(d)
        d=copy.deepcopy(self.evidence)
        d["studies"][0]["control"]["absorbed_mg_per_meal"]="-0.2"
        with self.assertRaisesRegex(ValueError,"nonfinite"):
            validate_studies(d)

    def test_fraction_content_and_absorbed_amount_must_reconcile(self):
        d=copy.deepcopy(self.evidence)
        d["studies"][1]["control"]["absorbed_mg_per_meal"]="0.90"
        with self.assertRaisesRegex(ValueError,"numerically inconsistent"):
            validate_studies(d)

    def test_mutated_primary_published_mean_rejected_even_if_plausible(self):
        d=copy.deepcopy(self.evidence)
        d["studies"][0]["biofortified"]["absorbed_mg_per_meal"]="0.34"
        with self.assertRaisesRegex(ValueError,"primary abstract endpoint changed"):
            validate_studies(d)
        d=copy.deepcopy(self.evidence)
        d["studies"][1]["control"]["fractional_absorption_pct"]="25.4"
        with self.assertRaisesRegex(ValueError,"primary abstract endpoint changed"):
            validate_studies(d)

    def test_group_ci_cannot_be_renamed_or_paired_effect_reconstructed(self):
        d=copy.deepcopy(self.evidence)
        del d["studies"][0]["control"]["absorbed_group_ci95_mg"]
        with self.assertRaisesRegex(ValueError,"group CI"):
            validate_studies(d)
        d=copy.deepcopy(self.evidence)
        d["studies"][1]["control"]["absorbed_group_ci95_mg"]=["0.3","0.5"]
        with self.assertRaisesRegex(ValueError,"Mixing zinc SD"):
            validate_studies(d)

    def test_USDA_records_verified_separately_from_absorption_studies(self):
        a=usda_baseline(DEFAULT_USDA,
                        DEFAULT_USDA.parent/"adult_references_31_50.csv")
        self.assertFalse(a["directly_comparable_to_peruvian_human_isotope_trial"])
        data={(r["fdc_id"],r["nutrient"]):r for r in a["targeted_observations"]}
        self.assertEqual(data["170438","iron"]["amount_mg_per_400g_prepared_food"],"1.24")
        self.assertEqual(data["170440","iron"]["amount_mg_per_400g_prepared_food"],"1.24")
        self.assertEqual(data["170438","zinc"]["amount_mg_per_400g_prepared_food"],"1.2")
        self.assertEqual(data["170440","zinc"]["amount_mg_per_400g_prepared_food"],"1.08")
        self.assertIsNone(data["170438","linoleic_acid"]["amount_per_100g_raw_FDC_unit"])
        self.assertEqual(data["170438","linoleic_acid"]["food_report_status"],"not_reported")
        self.assertFalse(any(row["absorption_adjustment_applied"]
                             for row in a["adult_RDA_context_not_clinical_requirement_or_bioavailability"]))

    def test_USDA_sha_tampering_fails_before_report(self):
        with tempfile.TemporaryDirectory() as temp:
            dest=Path(temp)
            for f in DEFAULT_USDA.iterdir():
                if f.is_file():
                    (dest/f.name).write_bytes(f.read_bytes())
            with (dest/"potato_fdc_170438_usda.csv").open("a") as fd:
                fd.write("\n")
            with self.assertRaisesRegex(ValueError,"SHA256"):
                usda_baseline(dest,DEFAULT_USDA.parent/"adult_references_31_50.csv")

    def test_no_unjustified_health_novelty_yield_or_joint_claim_and_deterministic(self):
        report=compile_opportunity()
        for field in ("can_claim_joint_fe_zn_improvement","can_compare_USDA_dietary_RDA_to_absorbed_mg",
                      "can_claim_iron_deficiency_or_anemia_reduction",
                      "can_claim_first_in_world_or_prior_work_absent",
                      "can_claim_yield_or_glycoalkaloid_safety",
                      "can_claim_potato_variety_developed_by_openpotato"):
            self.assertIs(report[field],False)
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            publish(report,Path(first));publish(report,Path(second))
            for filename in ("op_n1_01_absorption_opportunity.json","op_n1_01_research_opportunity.md"):
                self.assertEqual((Path(first)/filename).read_bytes(),(Path(second)/filename).read_bytes())
            prose=(Path(first)/"op_n1_01_research_opportunity.md").read_text()
            self.assertIn("NO son métricas intercambiables",prose)
            self.assertIn("misma variedad",prose)
if __name__=="__main__":
    unittest.main()

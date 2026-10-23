"""M1-15 tests are entirely synthetic, not claims about CIP phenotypes."""
import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.trial_design_monte_carlo import Design, create, grid, simulate


class HypotheticalTrialPowerTests(unittest.TestCase):
    def test_same_seed_and_model_yield_identical_results(self):
        d = Design(6, 3, 1, 0.6)
        self.assertEqual(simulate(d, draws=900, seed=17),
                         simulate(d, draws=900, seed=17))
        self.assertNotEqual(simulate(d, draws=900, seed=17),
                            simulate(d, draws=900, seed=18))

    def test_known_null_rejection_rate_approximately_five_percent(self):
        for sites in (3, 9):
            d = Design(sites, 3, 1, 1.5, effect_in_plot_sd=0)
            r = simulate(d, draws=10000, seed=20261021)
            self.assertGreater(r["simulated_type_i_error"], 0.035)
            self.assertLess(r["simulated_type_i_error"], 0.065)
            self.assertGreater(r["simulated_power"], 0.035)
            self.assertLess(r["simulated_power"], 0.065)

    def test_more_independent_sites_more_power_in_fixed_hypothetical_scenario(self):
        rows = {n: simulate(Design(n, 3, 1, 1.5),
                            draws=5000, seed=20261021)["simulated_power"]
                for n in (3, 6, 9)}
        self.assertLess(rows[3], rows[6])
        self.assertLess(rows[6], rows[9])

    def test_higher_site_interaction_means_less_power(self):
        low = simulate(Design(9, 3, 1, 0.6), draws=5000, seed=20261021)
        high = simulate(Design(9, 3, 1, 1.5), draws=5000, seed=20261021)
        self.assertGreater(low["simulated_power"], high["simulated_power"])

    def test_lab_repeat_is_not_an_additional_field_site(self):
        r = simulate(Design(9, 3, 3, 0.6), draws=1200)
        self.assertEqual(r["independent_sites"], 9)
        self.assertEqual(r["biological_blocks_per_site"], 3)
        self.assertEqual(r["technical_readings_per_sample"], 3)
        self.assertEqual(r["inferential_units"],
                         "independent_site_contrast_means_not_lab_readings")

    def test_invalid_biology_and_design_rejected(self):
        for d in (Design(2, 3, 1, 0.6), Design(6, 1, 1, 0.6),
                  Design(6, 3, 2, 0.6), Design(6, 3, 1, -0.1),
                  Design(6, 3, 1, float("nan")),
                  Design(6, 3, 1, 0.6, biological_plot_sd=0)):
            with self.subTest(d=d), self.assertRaises(ValueError):
                simulate(d, draws=600)
        with self.assertRaisesRegex(ValueError, "500"):
            simulate(Design(6, 3, 1, 0.6), draws=30)
        with self.assertRaisesRegex(ValueError, "integer"):
            simulate(Design(6, 3, 1, 0.6), seed=3.14)

    def test_grid_contains_18_predeclared_scenarios_only(self):
        records = grid(draws=500, seed=9)
        self.assertEqual(len(records), 18)
        self.assertEqual({r["independent_sites"] for r in records}, {3, 6, 9})
        self.assertEqual({r["genotype_site_contrast_sd"] for r in records},
                         {0.6, 1.5})
        self.assertTrue(all(r["simulation_only_not_empirical_evidence"]
                            for r in records))
        self.assertTrue(all(0 <= r["simulated_power"] <= 1 for r in records))

    def test_derived_files_reproducible_and_never_individual_plot_values(self):
        with tempfile.TemporaryDirectory() as temp:
            out1, out2 = Path(temp)/"first", Path(temp)/"second"
            m1 = create(out1, draws=700, seed=23)
            m2 = create(out2, draws=700, seed=23)
            self.assertEqual(m1["derived_csv_sha256"], m2["derived_csv_sha256"])
            self.assertEqual(m1["status"],
                             "SIMULATION_ONLY_NO_REAL_TRIAL_OR_MINERAL_PHENOTYPES")
            self.assertEqual(m1["designs"], 18)
            path = out1/"synthetic_trial_design_sensitivity.csv"
            self.assertEqual(m1["derived_csv_sha256"],
                             hashlib.sha256(path.read_bytes()).hexdigest())
            with path.open(newline="", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), 18)
            self.assertTrue(all(x["simulation_only_not_empirical_evidence"] ==
                                "True" for x in rows))
            self.assertNotIn("genotype_id", rows[0])
            self.assertNotIn("sample_id", rows[0])
            self.assertNotIn("CIP312", path.read_text())
            self.assertIn("hipotético",
                          (out1/"synthetic_trial_design_report.md").read_text().lower())
            self.assertEqual(json.loads((out1/"synthetic_trial_design_provenance.json")
                                        .read_text())["random_seed"], 23)


if __name__ == "__main__":
    unittest.main()

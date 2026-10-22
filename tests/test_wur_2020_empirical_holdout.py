"""Synthetic test fixtures of a TRUE 2019→2020 temporal prediction baseline.

No original WUR plot identifiers, cultivars or measured yields are bundled.
"""
import copy
import unittest
from datetime import date
from scripts import wur_2020_empirical_holdout as m


def fixture():
    rows=[]
    for year in (2019,2020):
        for site in m.SITES:
            for j,cultivar in enumerate(m.CULTIVARS_BY_SITE[site]):
                for plotnum in (1,2):
                    row={"Year":str(year),"Location":site,
                         "Plotnumber":f"{site}-{cultivar}-{plotnum}",
                         "Cultivar":cultivar,"Nitrogen":"N1","Irrigation":"W1"}
                    for day,value in (
                        (f"{year}-06-01","NA"),
                        (f"{year}-10-01",str(100+10*j+5*(site=="V")+20*(year==2020)+plotnum)),
                    ):
                        rows.append({**row,"Date":day,"tubersDW":value})
    return rows


class TrueWURHoldoutTests(unittest.TestCase):
    def test_real_vs_synthetic_identity_is_explicit(self):
        result=m.benchmark(fixture(),strict=True,counts={"L":6,"V":6})
        self.assertEqual(result["training_unique_physical_plots"],12)
        self.assertEqual(result["heldout_unique_physical_plots"],12)
        self.assertEqual(result["heldout_group_means_not_independent_site_years"],6)
        self.assertEqual(result["different_independent_evaluation_years"],1)
        self.assertTrue(result["no_wofost_predictions_or_calibration"])
        self.assertFalse(result["original_plot_values_exported"])
        self.assertFalse(result["original_plot_ids_exported"])
        self.assertEqual(result["source_csv_sha256"],"SYNTHETIC_TEST_DATA_ONLY")
        self.assertEqual(result["2019_site_by_cultivar_empirical_persistence"]["rmse_kg_dry_ha"],20)
        self.assertEqual(result["2019_site_by_cultivar_empirical_persistence"]["mae_kg_dry_ha"],20)
        self.assertEqual(result["2019_site_by_cultivar_empirical_persistence"]["bias_predicted_minus_observed_kg_dry_ha"],-20)
        self.assertGreater(result["2019_site_only_empirical_persistence"]["rmse_kg_dry_ha"],20)

    def test_last_sample_date_is_not_assumed_formal_harvest(self):
        r=m.benchmark(fixture(),strict=False,counts={"L":6,"V":6})
        self.assertTrue(r["last_measured_date_is_NOT_verified_formal_harvest"])
        self.assertEqual(r["last_sample_day_by_site_year"]["Lelystad 2020"],"2020-10-01")
        self.assertNotIn("S-C",str(r))

    def test_invalid_duplicate_plot_date_refused(self):
        rows=fixture()
        rows.append(dict(rows[0]))
        with self.assertRaisesRegex(ValueError,"Repeated physical plot/date"):
            m.benchmark(rows,strict=True,counts={"L":6,"V":6})

    def test_missing_terminal_plot_measurement_fails_closed(self):
        rows=fixture()
        rows[1]["tubersDW"]="NA"
        with self.assertRaisesRegex(ValueError,"Missing dry tuber"):
            m.benchmark(rows,strict=True,counts={"L":6,"V":6})

    def test_no_2020_year_is_never_fake_validation(self):
        rows=[r for r in fixture() if r["Year"]=="2019"]
        with self.assertRaisesRegex(ValueError,"site-years absent"):
            m.benchmark(rows,strict=True,counts={"L":6,"V":6})

    def test_changed_genotype_in_original_plot_refused(self):
        rows=fixture()
        rows[0]["Cultivar"]="C2"
        with self.assertRaisesRegex(ValueError,"changes cultivar or treatment"):
            m.benchmark(rows,strict=True,counts={"L":6,"V":6})

    def test_changed_management_in_original_plot_refused(self):
        rows=fixture()
        rows[0]["Irrigation"]="W2"
        with self.assertRaisesRegex(ValueError,"changes cultivar or treatment"):
            m.benchmark(rows,strict=True,counts={"L":6,"V":6})

    def test_unexpected_date_or_site_fails(self):
        for mutation, pattern in [
            (("Year","2023"),"Unexpected site/year"),
            (("Location","A"),"Unexpected site/year"),
            (("Date","not-a-date"),"Invalid observed ISO"),
            (("Date","2020-10-01"),"does not match season"),
        ]:
            rows=fixture()
            field,value=mutation
            rows[0][field]=value
            with self.subTest(mutation=mutation),self.assertRaisesRegex(ValueError,pattern):
                m.benchmark(rows,strict=True,counts={"L":6,"V":6})

    def test_duplicate_cultivar_codes_between_sites_refused(self):
        rows=fixture()
        rows[0]["Cultivar"]="C6"
        with self.assertRaisesRegex(ValueError,"Unexpected cultivar"):
            m.benchmark(rows,strict=True,counts={"L":6,"V":6})

    def test_negative_zero_or_nonfinite_dry_mass_refused(self):
        for val,pattern in [("-1","Negative"),("0","positive"),("inf","Nonfinite")]:
            rows=fixture()
            rows[1]["tubersDW"]=val
            with self.subTest(value=val),self.assertRaisesRegex(ValueError,pattern):
                m.benchmark(rows,strict=True,counts={"L":6,"V":6})

    def test_holdout_cannot_leak_2020_results_into_training(self):
        baseline=m.benchmark(fixture(),strict=True,counts={"L":6,"V":6})
        rows=fixture()
        for row in rows:
            if row["Year"]=="2020" and row["tubersDW"].upper()!="NA":
                row["tubersDW"]=str(float(row["tubersDW"])+1000)
        shifted=m.benchmark(rows,strict=True,counts={"L":6,"V":6})
        self.assertNotEqual(
            baseline["2019_site_by_cultivar_empirical_persistence"]["rmse_kg_dry_ha"],
            shifted["2019_site_by_cultivar_empirical_persistence"]["rmse_kg_dry_ha"])
        self.assertEqual(shifted["training_unique_physical_plots"],12)

    def test_not_all_plot_rows_are_independent_outcomes(self):
        rows=fixture()
        self.assertEqual(len(rows),48)
        r=m.benchmark(rows,strict=True,counts={"L":6,"V":6})
        self.assertEqual(r["heldout_group_means_not_independent_site_years"],6)
        self.assertEqual(r["total_original_distinct_physical_plots_site_year"],24)
        self.assertNotIn("plot_data",r)


if __name__=="__main__":
    unittest.main()

"""M1-17 static and model-input contract tests without requiring PCSE or network."""
import csv
import tempfile
import unittest
from pathlib import Path

from scripts import wofost_water_sensitivity as mod
from scripts import wofost_potato_nasa as base


class WaterLimitedAdmissionTests(unittest.TestCase):
    def test_design_has_exactly_48_declared_soil_water_sensitivities(self):
        self.assertEqual(mod.validate_design(),48)
        self.assertEqual(mod.EXPECTED_SCENARIOS,48)
        self.assertEqual(mod.MODEL,"Wofost81_WLP_CWB")
        self.assertIn("UNCALIBRATED",mod.STATUS)
        self.assertEqual(mod.COMMON_SITE["NOTINF"],0.0)

    def test_physical_hydraulic_orderings_accepted(self):
        for soil in mod.SOIL_PROFILES.values():
            for level in mod.INITIAL_AVAILABLE_WATER_CM.values():
                mod.validate_profile(soil,level)

    def test_rejects_nonphysical_hydraulic_properties(self):
        old=mod.SOIL_PROFILES["coarse_assumed"]
        changes=[
            {"SMFCF":0.05},{"SMFCF":0.39},{"SM0":0.9},
            {"CRAIRC":0.8},{"SOPE":0},{"KSUB":-1},
            {"RDMSOL":-1},{"SMW":float("nan")},
        ]
        for mutation in changes:
            with self.subTest(mutation=mutation):
                with self.assertRaises(ValueError):
                    mod.validate_profile({**old,**mutation},8.0)

    def test_rejects_infinite_or_excess_initial_water(self):
        soil=mod.SOIL_PROFILES["medium_assumed"]
        for level in (-0.1,36.0,float("nan"),float("inf")):
            with self.subTest(level=level),self.assertRaises(ValueError):
                mod.validate_profile(soil,level)

    def test_model_outputs_are_declared_dry_not_fresh_or_minerals(self):
        self.assertIn("dry_kg_ha", " ".join(mod.HEADERS))
        self.assertNotIn("iron", " ".join(mod.HEADERS))
        self.assertNotIn("zinc", " ".join(mod.HEADERS))
        self.assertNotIn("fresh_tuber_yield", " ".join(mod.HEADERS))
        self.assertEqual(mod.MODEL,"Wofost81_WLP_CWB")

    def test_rejects_inconsistent_baseline_status_and_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"fake.csv"
            with p.open("w",newline="") as f:
                writer=csv.DictWriter(f,fieldnames=base.SUMMARY_FIELDS)
                writer.writeheader()
                for site in base.SITES:
                    for yr in base.CAMPAIGNS:
                        for m,d in base.START_MONTH_DAYS:
                            writer.writerow({
                                "scenario_id":f"{site}-{yr}-{m:02d}{d:02d}",
                                "site_label":site, "campaign":yr,
                                "interpretation":"UNKNOWN_NON_SCIENTIFIC_SOURCE",
                                "model":"Wofost81_PP","generic_variety":base.VARIETY,
                                "potential_storage_dry_kg_ha":14000,
                                "weather_nasa_power_sha256":base.PINNED_WEATHER_SHA256[site],
                            })
            with self.assertRaisesRegex(ValueError,"baseline source/method"):
                mod.load_baseline(p,base.PINNED_WEATHER_SHA256)

    def test_real_published_potential_reference_has_exact_eight_rows(self):
        path=Path(__file__).resolve().parents[1]/(
            "datasets/wofost_potato_m1_16/model/generic_potato_potential_scenarios.csv")
        if not path.exists():
            self.skipTest("M1-16 references not present in current checkout")
        data=mod.load_baseline(path,base.PINNED_WEATHER_SHA256)
        self.assertEqual(len(data),8)
        self.assertTrue(all(v>0 for v in data.values()))

    def test_reused_nasa_sources_still_have_pinned_digest(self):
        root=Path(__file__).resolve().parents[1]/(
            "datasets/wofost_potato_m1_16/weather")
        if not root.exists():
            self.skipTest("Pinned M1-16 NASA inputs not present")
        _,hashes=base.load_weather(root)
        self.assertEqual(hashes,base.PINNED_WEATHER_SHA256)


if __name__=="__main__":
    unittest.main()

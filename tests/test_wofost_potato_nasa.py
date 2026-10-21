"""Source-only checks. No PCSE dependency, live NASA request or real field claims."""
import json
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch

from scripts import wofost_potato_nasa as mod


def synthetic_power(start=date(2022,1,1), days=7):
    keys = [(start+timedelta(days=i)).strftime("%Y%m%d") for i in range(days)]
    params = {name: {d: 1.0 for d in keys} for name in mod.POWER_VARS}
    for d in keys:
        params["TOA_SW_DWN"][d] = 33.5
        params["ALLSKY_SFC_SW_DWN"][d] = 21.5
        params["T2M"][d] = 16
        params["T2M_MIN"][d] = 9
        params["T2M_MAX"][d] = 24
        params["T2MDEW"][d] = 7
        params["WS2M"][d] = 2.1
        params["PRECTOTCORR"][d] = 4.2
    result = {
        "header":{"fill_value": -999},
        "properties":{"parameter":params},
        "geometry":{"coordinates":[-62.73,-35.97,90]},
    }
    return result, start, start+timedelta(days=days-1)


class ModelWeatherSourceTests(unittest.TestCase):
    def test_complete_hypothetical_weather_is_structurally_valid(self):
        data,start,end = synthetic_power()
        self.assertEqual(mod.validate_power(data,start,end),7)

    def test_missing_day_rejected_without_interpolation(self):
        data,start,end = synthetic_power()
        del data["properties"]["parameter"]["T2M"]["20220103"]
        with self.assertRaisesRegex(ValueError,"missing or extra dates"):
            mod.validate_power(data,start,end)

    def test_missing_or_nonfinite_is_not_assigned_zero(self):
        for changed in (-999, float("nan"), float("inf")):
            with self.subTest(changed=changed):
                data,start,end=synthetic_power()
                data["properties"]["parameter"]["T2M_MIN"]["20220101"]=changed
                with self.assertRaisesRegex(ValueError,"missing/nonfinite"):
                    mod.validate_power(data,start,end)

    def test_extreme_rainfall_is_rejected_not_silently_clipped(self):
        data,start,end=synthetic_power()
        data["properties"]["parameter"]["PRECTOTCORR"]["20220101"]=270.0
        with self.assertRaisesRegex(ValueError,"rainfall"):
            mod.validate_power(data,start,end)

    def test_minimum_cannot_exceed_maximum(self):
        data,start,end=synthetic_power()
        data["properties"]["parameter"]["T2M_MIN"]["20220101"]=50
        with self.assertRaisesRegex(ValueError,"minimum hotter"):
            mod.validate_power(data,start,end)

    def test_extra_and_missing_source_file_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            directory=Path(temp)
            with self.assertRaisesRegex(ValueError,"exactly the two"):
                mod.load_weather(directory)
            (directory/"made_up.json").write_text("{}")
            with self.assertRaisesRegex(ValueError,"exactly the two"):
                mod.load_weather(directory)

    def test_acquisition_never_overwrites_weather_file(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/"trenque_lauquen.json"
            path.write_text("LEGITIMATE_UNTOUCHED_ORIGINAL")
            with self.assertRaisesRegex(ValueError,"Refusing to overwrite"):
                # Acquisition stops before a second network call; force no net access.
                with patch.object(mod,"urlopen",side_effect=AssertionError("network")):
                    mod.acquire_weather(temp)
            self.assertEqual(path.read_text(),"LEGITIMATE_UNTOUCHED_ORIGINAL")

    def test_scenarios_are_explicitly_uncalibrated_and_not_genotypes(self):
        self.assertEqual(mod.CROP,"potato")
        self.assertEqual(mod.VARIETY,"Potato_701")
        self.assertEqual(mod.MODEL,"Wofost81_PP")
        self.assertEqual(mod.PCSE_VERSION,"6.0.13")
        self.assertEqual(len(mod.SITES)*len(mod.CAMPAIGNS)*
                         len(mod.START_MONTH_DAYS),8)
        self.assertNotIn("genotype_id",mod.SUMMARY_FIELDS)
        self.assertNotIn("fresh_tuber_yield",mod.SUMMARY_FIELDS)
        self.assertNotIn("Fe",mod.SUMMARY_FIELDS)
        self.assertNotIn("Zn",mod.SUMMARY_FIELDS)
        self.assertIn("UNCALIBRATED",mod.STATUS)


if __name__ == "__main__":
    unittest.main()

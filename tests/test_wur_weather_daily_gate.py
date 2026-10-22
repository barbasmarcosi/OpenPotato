"""Only entirely imaginary weather rows and local XLSX data in M1-22 tests."""
import importlib.util
import math
import unittest
from datetime import date, timedelta
from unittest.mock import patch
from scripts import wur_weather_daily_gate as mod

UNIT_MAP = {"IRRAD": "kJ/m2/day", "TMIN": "degC", "TMAX": "degC",
            "VAP": "kPa", "RAIN": "mm/day", "WIND": "m/s_at_2m",
            "E0": "mm/day", "ES0": "mm/day", "ET0": "mm/day"}


def fictional_records(days=3):
    return [{
        "DAY": (date(2020, 4, 1) + timedelta(days=i)).isoformat(),
        "IRRAD": 13500, "TMIN": 9, "TMAX": 21, "VAP": 1.1,
        "RAIN": 6, "WIND": 2.5, "E0": 3.5, "ES0": 3.0, "ET0": 3.4,
    } for i in range(days)]


class StrictWeatherUnitTests(unittest.TestCase):
    def test_physical_unit_conversion_and_no_model_admission(self):
        result = mod.normalize_for_pcse(fictional_records(), units=UNIT_MAP)
        self.assertEqual(result["status"], "UNIT_NORMALIZATION_ONLY_NOT_MODEL_ADMISSION")
        row = result["pcse_daily_records_IN_MEMORY_DO_NOT_EXPORT_OR_PUBLISH"][0]
        self.assertEqual(row["IRRAD"], 13500000)
        self.assertAlmostEqual(row["VAP"], 11)
        self.assertAlmostEqual(row["RAIN"], 0.6)
        self.assertAlmostEqual(row["ET0"], 0.34)
        self.assertFalse(result["field_wofost_run_admissible"])

    def test_relative_humidity_not_misrepresented_as_vapour_pressure(self):
        with self.assertRaisesRegex(ValueError, "VAP"):
            mod.normalize_for_pcse(fictional_records(), units={**UNIT_MAP, "VAP": "%RH"})

    def test_wind_height_is_required_not_guessed(self):
        with self.assertRaisesRegex(ValueError,"WIND"):
            mod.normalize_for_pcse(fictional_records(),units={**UNIT_MAP,"WIND":"m/s_at_10m"})

    def test_missing_fao_or_penman_evaporation_variable_is_blocked(self):
        rows=fictional_records()
        del rows[0]["E0"]
        with self.assertRaisesRegex(ValueError,"Missing or extra daily"):
            mod.normalize_for_pcse(rows,units=UNIT_MAP)

    def test_dates_duplicate_gap_or_ambiguous_fail_closed(self):
        for mutate, error in [
            (lambda x: x[1].update(DAY=x[0]["DAY"]), "Duplicate"),
            (lambda x: x[1].update(DAY="2020-04-06"), "Missing daily"),
            (lambda x: x[1].update(DAY="02/04/2020"), "Ambiguous source day"),
        ]:
            with self.subTest(error=error):
                rows=fictional_records()
                mutate(rows)
                with self.assertRaisesRegex(ValueError,error):
                    mod.normalize_for_pcse(rows,units=UNIT_MAP)

    def test_nonfinite_extreme_and_inverted_temperature_rejected(self):
        for field,value,regex in [("IRRAD",float("nan"),"Nonfinite"),("RAIN",-1,"out-of-range"),
                                  ("TMIN",25,"Minimum")]:
            with self.subTest(field=field):
                rows=fictional_records()
                rows[0][field]=value
                with self.assertRaisesRegex(ValueError,regex):
                    mod.normalize_for_pcse(rows,units=UNIT_MAP)

    def test_missing_source_units_rejected(self):
        units=dict(UNIT_MAP)
        del units["IRRAD"]
        with self.assertRaisesRegex(ValueError,"units"):
            mod.normalize_for_pcse(fictional_records(), units=units)

    def test_empty_and_missing_numeric_values_rejected(self):
        with self.assertRaisesRegex(ValueError,"Empty"):
            mod.normalize_for_pcse([],units=UNIT_MAP)
        rows=fictional_records()
        rows[0]["VAP"]=None
        with self.assertRaisesRegex(ValueError,"nonnumeric"):
            mod.normalize_for_pcse(rows,units=UNIT_MAP)

    def test_typed_date_supported_iso_and_excel_serial_not_guessed(self):
        self.assertEqual(mod.parse_day(date(2020,1,2)),date(2020,1,2))
        self.assertIsNone(mod.parse_day(43832))
        self.assertIsNone(mod.parse_day("02/01/2020"))

    @unittest.skipUnless(importlib.util.find_spec("openpyxl"),"Full XLSX tests run in M1-22 dedicated CI")
    def test_original_digest_blocks_fictional_workbooks(self):
        with self.assertRaisesRegex(ValueError,"checksum"):
            mod.inspect_original_weather({"Lelystad":b"invented","Vredepeel":b"invented"})

    def test_date_axis_with_three_years_keeps_2019_and_2020(self):
        # Weather workbook may begin in 2018: not every valid date is in the
        # 2019-2020 experimental holdout; this must not cause false rejection.
        class FictionalSheet:
            def iter_rows(self, min_row, values_only):
                assert min_row == 10 and values_only
                d=date(2018,1,1)
                for i in range(1096):
                    yield (d+timedelta(days=i), 20.0, "INVENTED_NOT_WUR")
        result=mod._date_column(FictionalSheet())
        self.assertEqual(result["date_column_status"],
                         "UNIQUE_DATE_LIKE_COLUMN_UNITS_UNCONFIRMED")
        self.assertEqual(result["parsed_dates_2019"],365)
        self.assertEqual(result["parsed_dates_2020"],366)
        self.assertEqual(result["parsed_dates_other_years"],365)
        self.assertEqual(result["duplicate_date_rows"],0)
        self.assertEqual(result["missing_calendar_days_within_observed_window"],0)
        self.assertFalse(result["date_axis_ready_for_model"])


if __name__=="__main__":
    unittest.main()

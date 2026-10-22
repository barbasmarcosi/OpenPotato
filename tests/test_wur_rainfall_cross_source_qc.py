"""All rainfall/irrigation measurements in these tests are invented."""
import unittest
from collections import Counter
from datetime import date,timedelta
from scripts import wur_rainfall_cross_source_qc as mod

def mocked_rain_sources():
    register={}
    weather={"L":{},"V":{}}
    for (year,site),n in mod.EXPECTED_DATE_COUNTS.items():
        for i in range(n):
            d=date(year,1,1)+timedelta(days=i)
            source_rain=0. if i%2 else 10.
            station_rain=source_rain if i%3 else 0.
            register[year,site,d]=(source_rain,{
                "W1":"unknown_blank" if i%3 else "recorded_positive",
                "W2":"unknown_blank" if i%5 else "recorded_positive",
            })
            weather[site][d]=station_rain
    return register,weather

class CrossWeatherTests(unittest.TestCase):
    def test_aggregation_is_not_implicit_unit_proof(self):
        register,weather=mocked_rain_sources()
        result=mod.compare_indices(register,weather,"AMBIGUOUS_OR_UNSPECIFIED")
        self.assertEqual(len(result["site_year_aggregates"]),4)
        self.assertFalse(result["irrigation_W1_W2_mm_approved"])
        self.assertFalse(result["site_crop_soil_agromanagement_ready"])
        self.assertTrue(result["rainfall_inter_source_agreement_is_NOT_an_unit_conversion"])
        self.assertEqual(sum(r["same_site_same_day_records"] for r in result["site_year_aggregates"]),526)
        self.assertNotIn("2019-01-01",str(result))
        self.assertNotIn("10.0",str(result))
    def test_missing_weather_day_fails_closed(self):
        register,weather=mocked_rain_sources()
        d=date(2019,1,1)
        del weather["L"][d]
        with self.assertRaisesRegex(ValueError,"Missing source weather"):
            mod.compare_indices(register,weather,"unknown")
    def test_water_blanks_stay_unknown_even_when_rain_is_zero(self):
        register,weather=mocked_rain_sources()
        report=mod.compare_indices(register,weather,"unknown")
        self.assertGreater(report["site_year_aggregates"][0]["treatment_source_cell_status_counts"]["W1"]["unknown_blank"],0)
        self.assertFalse(report["blanks_treated_as_zero"])
    def test_non_numeric_and_negative_rain_denied(self):
        for value in (None,True,float("nan"),-1., "5"):
            with self.assertRaises(ValueError):
                mod.valid_number(value,"rain")
    def test_missing_source_files_rejected_without_optional_xlsx(self):
        with self.assertRaisesRegex(ValueError,"All three"):
            mod.audit_originals({"Lelystad":b"bad"})
        with self.assertRaisesRegex(ValueError,"Irrigation original SHA256"):
            mod.audit_originals({"Irrigation.xlsx":b"bad","Lelystad":b"bad","Vredepeel":b"bad"})
    def test_date_year_count_mutation_rejected(self):
        register,weather=mocked_rain_sources()
        key=next(iter(register))
        del register[key]
        with self.assertRaisesRegex(ValueError,"coverage changed"):
            mod.compare_indices(register,weather,"unknown")

if __name__=="__main__":
    unittest.main()

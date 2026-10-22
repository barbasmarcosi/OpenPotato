"""Invented weather records only, no source WUR weather cells."""
import json
import unittest
from datetime import date,timedelta
from scripts import wur_weather_holdout_exposure as mod

class Fixture:
    def __init__(self,broken=None,complete=False):
        self.broken=broken
        self.complete=complete
    def iter_rows(self,*,min_row,values_only):
        assert min_row==1 and values_only
        rows=[("FICTIONAL-PRIVATE-METADATA","invented","SECRET-SENSOR")]
        for year in (2018,2019,2020):
            for offset in range(mod.YEARS[year]):
                day=date(year,1,1)+timedelta(days=offset)
                missing=not self.complete and year==2020 and day.month>=10
                rows.append((day,9.2,None if missing else 14.0))
        if self.broken:self.broken(rows)
        return iter(rows)

class M125Tests(unittest.TestCase):
    def test_conservative_overlap_34_before_endpoint_58_after(self):
        report=mod.audit_sheet(Fixture(),"Lelystad")
        self.assertEqual(report["original_weather_days"],1096)
        c=report["columns_with_missing_or_invalid_cells"][0]
        self.assertEqual(c["source_column_1_based"],3)
        y=c["coverage"]["2020"]
        self.assertEqual(y["non_numeric_from_jan1_through_last_sample"],34)
        self.assertEqual(y["non_numeric_after_last_sample"],58)
        self.assertEqual(y["missing_na"],92)
        self.assertFalse(report["model_ready"])
        for forbidden in ("FICTIONAL-PRIVATE-METADATA","SECRET-SENSOR","2020-11-03","9.2","14.0"):
            self.assertNotIn(forbidden,json.dumps(report))
    def test_complete_source_still_not_model_ready(self):
        report=mod.audit_sheet(Fixture(complete=True),"Vredepeel")
        self.assertEqual(report["columns_with_missing_or_invalid_cells"],[])
        self.assertFalse(report["model_ready"])
    def test_noniso_dates_and_excel_serial_not_guessed(self):
        self.assertIsNone(mod.parse_day("03/11/2020"))
        self.assertIsNone(mod.parse_day(44138))
        self.assertEqual(mod.parse_day("2020-11-03"),date(2020,11,3))
    def test_bool_nan_and_na_classification(self):
        self.assertEqual(mod.value_state(True),"invalid")
        self.assertEqual(mod.value_state(float("nan")),"invalid")
        self.assertEqual(mod.value_state("NA"),"missing")
        self.assertEqual(mod.value_state(-1.0),"numeric")
    def test_repeated_date_denied(self):
        def f(rows):rows[2]=(rows[1][0],9.2,14.0)
        with self.assertRaisesRegex(ValueError,"Repeated"):
            mod.audit_sheet(Fixture(f),"Lelystad")
    def test_nondate_after_series_denied(self):
        def f(rows):rows[15]=(None,9.2,14.0)
        with self.assertRaisesRegex(ValueError,"Undated"):
            mod.audit_sheet(Fixture(f),"Lelystad")
    def test_missing_date_denied(self):
        def f(rows):rows.pop(15)
        with self.assertRaisesRegex(ValueError,"Missing"):
            mod.audit_sheet(Fixture(f),"Lelystad")
    def test_missing_station_or_bad_source_hash_denied_before_excel(self):
        with self.assertRaisesRegex(ValueError,"Both"):
            mod.audit_verified_files({"Lelystad":b"invalid"})
        with self.assertRaisesRegex(ValueError,"SHA-256"):
            mod.audit_verified_files({"Lelystad":b"invalid","Vredepeel":b"invalid"})
    def test_unrecognized_source_site_denied(self):
        with self.assertRaisesRegex(ValueError,"Unknown"):
            mod.audit_sheet(Fixture(),"Bogus")

if __name__=="__main__":unittest.main()

"""M1-24 source-metadata tests: purely fictional cells, no WUR data."""
import unittest
from datetime import date,timedelta
from scripts import wur_weather_semantics_gate as mod

class FakeSheet:
    def __init__(self,modifier=None):self.modifier=modifier
    def iter_rows(self,*,min_row,values_only):
        assert min_row==1 and values_only
        rows=[("notice","radiation MJ/m2","rain mm","unknown header"),
              ("explanation",None,None,None),
              ("column-label","X","Y","Z")]
        begin=date(2019,12,29)
        for i in range(8):
            rows.append((begin+timedelta(days=i),4.0,
                         None if i in (2,3,5) else 7.0,12.0))
        if self.modifier:self.modifier(rows)
        return iter(rows)

class WeatherMetadataTests(unittest.TestCase):
    def test_year_and_quarter_missingness_without_raw_source_values(self):
        r=mod.audit_sheet(FakeSheet(),expected_years={2019:3,2020:5})
        self.assertEqual(r["original_daily_dates"],8)
        self.assertEqual(r["metadata_prefix_row_count"],3)
        c=r["columns"][1]
        self.assertEqual(c["counts_by_year"]["2019"]["missing_na"],1)
        self.assertEqual(c["counts_by_year"]["2020"]["missing_na"],2)
        self.assertEqual(c["counts_by_year"]["2020"]["max_non_numeric_streak"],1)
        self.assertIn("rain",c["candidate_variable_words_NOT_verified"])
        self.assertIn("mm",c["candidate_unit_words_NOT_verified"])
        self.assertFalse(r["pcse_ready"])
        text=str(r)
        for secret in ("unknown header","rain mm","2019-12-29","7.0"):
            self.assertNotIn(secret,text)

    def test_strict_unchanged_calendar(self):
        with self.assertRaisesRegex(ValueError,"date window"):
            mod.audit_sheet(FakeSheet(),expected_years={2019:4,2020:4})

    def test_duplicate_weather_date_rejected(self):
        def duplicate(rows):rows[5]=(rows[4][0],4.0,3.0,12.0)
        with self.assertRaisesRegex(ValueError,"Duplicate"):
            mod.audit_sheet(FakeSheet(duplicate))

    def test_weather_date_gap_rejected(self):
        def gap(rows):rows[6]=(date(2020,1,7),4.0,3.0,12.0)
        with self.assertRaisesRegex(ValueError,"Gap"):
            mod.audit_sheet(FakeSheet(gap))

    def test_out_of_series_text_date_rejected(self):
        def bad(rows):rows[5]=(None,4.0,3.0,12.0)
        with self.assertRaisesRegex(ValueError,"Non-date"):
            mod.audit_sheet(FakeSheet(bad))

    def test_boolean_nonfinite_and_blank_not_numeric(self):
        for x,k in ((True,"untyped"),(float("inf"),"untyped"),
                    (float("nan"),"untyped"),("NA","missing"),(0.0,"numeric")):
            self.assertEqual(mod.classify(x),k)

    def test_unverified_digest_denies_even_without_excel_dependency(self):
        with self.assertRaisesRegex(ValueError,"checksum"):
            mod.audit_originals({"Lelystad":b"fake","Vredepeel":b"fake"})

    def test_missing_weather_station_denied(self):
        with self.assertRaisesRegex(ValueError,"Both"):
            mod.audit_originals({"Lelystad":b"fake"})

if __name__=="__main__":unittest.main()

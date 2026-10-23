"""Original WUR observations never appear: all test rows are invented."""
import unittest
from datetime import timedelta
from scripts import wur_irrigation_trial_window_coverage as mod

def sample():
    data=[]
    for (y,site),plant in mod.PLANT.items():
        end=mod.LAST_SAMPLE[y,site]
        for d in (plant-timedelta(days=1),plant,end):
            data.append(("L" if site=="L" else "V",int(y),d,0.,
                         None if d==plant else 1.,
                         2. if d==end else None))
    return data

class SourceWindowTests(unittest.TestCase):
    def test_blank_and_no_calendar_row_stay_unknown(self):
        r=mod.assess_rows(sample(),strict=False)
        self.assertFalse(r["wofost_irrigation_agromanagement_admissible"])
        self.assertTrue(r["blanks_or_absent_calendar_rows_are_NOT_zero"])
        for group in r["site_year_aggregate_counts"]:
            self.assertEqual(group["windows"]["before_planting"]["recorded_days"],1)
            self.assertEqual(group["registered_calendar_days_within_window"],2)
            self.assertGreater(group["calendar_days_without_register_row_UNKNOWN"],0)
            self.assertEqual(group["windows"]["planting_through_last_sample"]["W1"]["blank_UNKNOWN"],1)
            self.assertEqual(group["windows"]["planting_through_last_sample"]["W2"]["blank_UNKNOWN"],1)
            self.assertEqual(group["windows"]["planting_through_last_sample"]["W1"]["explicit_zero"],0)
        self.assertNotIn("2.0",str(r))
    def test_doubled_site_date_rejected(self):
        r=sample();r.append(r[0])
        with self.assertRaisesRegex(ValueError,"Repeated"):mod.assess_rows(r,strict=False)
    def test_missing_one_site_year_denied(self):
        rows=[x for x in sample() if x[1]==2019]
        with self.assertRaisesRegex(ValueError,"Four experimental"):mod.assess_rows(rows,strict=False)
    def test_source_sha_required_before_optional_excel_import(self):
        with self.assertRaisesRegex(ValueError,"SHA256"):mod.inspect_original(b"fake")
    def test_no_implicit_numeric_imputation(self):
        self.assertEqual(mod.water_state(None),"blank_UNKNOWN")
        self.assertEqual(mod.water_state(0),"explicit_zero")
        self.assertEqual(mod.water_state(1.5),"recorded_positive")
        for v in (-1.,float("nan"),True,"5"):
            with self.assertRaises(ValueError):mod.water_state(v)
    def test_fake_data_rejected_by_original_record_balance(self):
        with self.assertRaisesRegex(ValueError,"Original source record counts"):
            mod.assess_rows(sample(),strict=True)
    def test_wrong_date_year_rejected(self):
        data=sample();site,y,d,r,w1,w2=data[0]
        data[0]=(site,2020 if y==2019 else 2019,d,r,w1,w2)
        with self.assertRaisesRegex(ValueError,"year/date"):mod.assess_rows(data,strict=False)

if __name__=="__main__":unittest.main()

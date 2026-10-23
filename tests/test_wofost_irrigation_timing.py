"""Offline contract tests for irrigation events; no claims about farm outputs."""
import csv
import tempfile
import unittest
from datetime import date,timedelta
from pathlib import Path
from scripts import wofost_irrigation_timing as m
from scripts import wofost_water_sensitivity as w
from scripts import wofost_potato_nasa as b

class IrrigationTests(unittest.TestCase):
    def test_equal_gross_water_for_both_irrigated_strategies(self):
        self.assertEqual(m.validate_schedules(),144)
        start=date(2022,9,1);harvest=date(2023,3,1)
        weekly=m.irrigation_events(start,harvest,"weekly_100mm")
        biweekly=m.irrigation_events(start,harvest,"fortnightly_100mm")
        self.assertEqual(len(weekly),10)
        self.assertEqual(len(biweekly),5)
        self.assertEqual(sum(cm*10 for _,cm,_ in weekly),100)
        self.assertEqual(sum(cm*10 for _,cm,_ in biweekly),100)
        self.assertEqual(sum(cm*10*eff for _,cm,eff in biweekly),80)
        self.assertEqual(sum(cm*10*eff for _,cm,eff in weekly),80)
        self.assertEqual(m.irrigation_events(start,harvest,"none"),[])

    def test_signal_contract_uses_cm_amount_and_efficiency(self):
        start=date(2023,9,1)
        a=m.timed_agromanagement(start,date(2024,3,1),"weekly_100mm")
        event=a[0][start]["TimedEvents"][0]
        self.assertEqual(event["event_signal"],"irrigate")
        first_date,first_args=next(iter(event["events_table"][0].items()))
        self.assertEqual(set(first_args), {"amount","efficiency"})
        self.assertEqual(first_date,start+timedelta(days=14))
        self.assertEqual(first_args,{"amount":1.0,"efficiency":0.8})

    def test_none_control_emits_no_irrigation_signal(self):
        start=date(2022,10,1)
        agro=m.timed_agromanagement(start,date(2023,3,1),"none")
        self.assertIsNone(agro[0][start]["TimedEvents"])

    def test_invalid_schedule_gross_total_fails(self):
        before=dict(m.SCHEDULES["weekly_100mm"])
        try:
            m.SCHEDULES["weekly_100mm"]["gross_mm_per_event"]=11
            with self.assertRaisesRegex(ValueError,"equal gross total"):
                m.validate_schedules()
        finally:
            m.SCHEDULES["weekly_100mm"].update(before)

    def test_irrigation_events_inside_crop_calendar(self):
        with self.assertRaisesRegex(ValueError,"outside crop calendar"):
            m.irrigation_events(date(2022,9,1),date(2022,9,10),"weekly_100mm")

    def test_pinned_control_sources_are_48_unirrigated_cases(self):
        p=Path(__file__).resolve().parents[1]/(
            "datasets/wofost_potato_m1_17/water_limited_scenarios.csv")
        if not p.is_file():
            self.skipTest("M1-17 reference not in checkout")
        rows=m.read_m17(p,b.PINNED_WEATHER_SHA256)
        self.assertEqual(len(rows),48)
        self.assertTrue(all(v>=0 for v in rows.values()))

    def test_bad_control_irrigation_rejected(self):
        original=Path(__file__).resolve().parents[1]/(
            "datasets/wofost_potato_m1_17/water_limited_scenarios.csv")
        if not original.is_file():
            self.skipTest("M1-17 reference unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            file=Path(tmp)/"invalid.csv"
            with original.open(newline="") as fh:
                rdr=csv.DictReader(fh)
                records=list(rdr);columns=rdr.fieldnames
            records[0]["irrigation_mm_assumed"]="99"
            with file.open("w",newline="") as f:
                writer=csv.DictWriter(f,fieldnames=columns)
                writer.writeheader();writer.writerows(records)
            with self.assertRaisesRegex(ValueError,"no-irrigation"):
                m.read_m17(file,b.PINNED_WEATHER_SHA256)

    def test_output_does_not_include_observed_or_nutritional_properties(self):
        joined=" ".join(m.OUTPUT_FIELDS)
        self.assertNotIn("genotype_id",joined)
        self.assertNotIn("iron",joined)
        self.assertNotIn("zinc",joined)
        self.assertNotIn("fresh_tuber_yield",joined)
        self.assertIn("HYPOTHETICAL",m.STATUS)
        self.assertIn("NOT_CALIBRATED",m.STATUS)


if __name__=="__main__":
    unittest.main()

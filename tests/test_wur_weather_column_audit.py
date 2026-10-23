"""Fully fictional 2019/2020 weather cells; never real WUR observations."""
import unittest
from datetime import date, timedelta
from scripts import wur_weather_column_audit as mod


class FictionalSheet:
    def __init__(self, bad=False):
        self.bad=bad
    def iter_rows(self,min_row,max_row=None,values_only=None):
        assert values_only
        if min_row==1:
            for i in range(9):
                yield ("date", "TMIN Celsius", "rain mm/day") if i==0 else (None,None,None)
        elif min_row==10:
            start=date(2019,1,1)
            for i in range(731):
                day=start+timedelta(days=i)
                rain="NA" if i==4 else 0.0
                if self.bad and i==5:rain="corrupt"
                yield (day,10.0,rain)
        else:
            raise AssertionError("Unexpected source access")


class NumericFieldCoverageTests(unittest.TestCase):
    def test_2019_2020_coverage_counts_no_values_or_labels_exported(self):
        report=mod.coverage_of_sheet(FictionalSheet())
        self.assertEqual(report["2019_2020_calendar_rows_with_date"],731)
        self.assertEqual(report["date_axis_source_column_1_based"],1)
        self.assertEqual(len(report["columns"]),2)
        self.assertEqual(report["columns"][1]["finite_numeric_cells"],730)
        self.assertEqual(report["columns"][1]["missing_or_NA_cells"],1)
        self.assertIn("rainfall",report["columns"][1]["tentative_header_patterns_not_validated_mapping"])
        self.assertFalse(report["ready_for_pcse"])
        self.assertNotIn("TMIN Celsius",str(report))

    def test_non_numeric_weather_not_imputed_or_swallowed(self):
        report=mod.coverage_of_sheet(FictionalSheet(bad=True))
        self.assertEqual(report["columns"][1]["untyped_or_nonfinite_cells"],1)
        self.assertEqual(report["columns"][1]["finite_numeric_cells"],729)

    def test_missing_date_axis_keeps_model_denied(self):
        class Undated:
            def iter_rows(self,min_row,max_row=None,values_only=None):
                for _ in range(30):yield (1,2,3)
        report=mod.coverage_of_sheet(Undated())
        self.assertEqual(report["date_axis_status"],"NONE")
        self.assertFalse(report["ready_for_pcse"])

    def test_unverifiable_file_hash_never_processes_weather(self):
        with self.assertRaisesRegex(ValueError,"digest"):
            mod.inspect_originals({"Lelystad":b"fake","Vredepeel":b"fake"})

    def test_missing_original_station_blocks(self):
        with self.assertRaisesRegex(ValueError,"Both"):
            mod.inspect_originals({"Lelystad":b"fake"})


if __name__=="__main__":unittest.main()

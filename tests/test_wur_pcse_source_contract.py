"""M1-26 test: all weather records fabricated, no licensed data."""
import unittest
from datetime import date,timedelta
from scripts import wur_pcse_source_contract as m

class FakeSheet:
    def __init__(self,bad_header=False,bad_sentinel=False):self.bh=bad_header;self.bs=bad_sentinel
    def iter_rows(self,*,min_row,values_only):
        assert min_row==1 and values_only
        rows=[(None,)*10 for _ in range(11)]
        rows[5]=(None,-999.)+(None,)*8
        rows[7]=(5.55,52.54,4.,0.18,0.55,False)+(None,)*4
        h=list(m.FIELDS)+["NOT-PCSE-9","NOT-PCSE-10"]
        if self.bh:h[2]="WRONG"
        rows[9]=tuple(h)
        rows[10]=tuple(m.UNITS)+("irrelevant","irrelevant")
        for y,n in m.DAYS.items():
            for x in range(n):
                d=date(y,1,1)+timedelta(days=x)
                vals=(d,18000.,4.,20.,1.1,-999. if self.bs and y==2020 and x==1 else 2.,
                      5.,0.,8.,None if y==2020 and d.month>=10 else 7.)
                rows.append(vals)
        return iter(rows)

class WeatherContractTests(unittest.TestCase):
    def test_realistic_auxiliary_gap_does_not_block_required_weather(self):
        r=m.audit_sheet(FakeSheet())
        self.assertTrue(r["schema_exact_native_pcse"])
        self.assertTrue(r["mandatory_2019_2020_complete"])
        self.assertEqual(r["unused_extra_field_coverage"][10]["2020"]["missing"],92)
        self.assertEqual(r["unused_source_columns_one_based"],[9,10])
        self.assertFalse(r["wofost_crop_model_field_validated"])
        self.assertNotIn("NOT-PCSE-10",str(r))

    def test_source_field_order_uses_labels_not_unverified_column_positions(self):
        class Swapped(FakeSheet):
            def iter_rows(self, *, min_row, values_only):
                for row in super().iter_rows(min_row=min_row, values_only=values_only):
                    v=list(row)
                    v[7],v[8]=v[8],v[7]
                    yield tuple(v)
        report=m.audit_sheet(Swapped())
        self.assertEqual(report["pcse_source_columns_one_based"]["SNOWDEPTH"],9)
        self.assertEqual(report["unused_source_columns_one_based"],[8,10])
        self.assertTrue(report["mandatory_2019_2020_complete"])
    def test_reject_modified_header(self):
        with self.assertRaisesRegex(ValueError,"Missing or duplicate"):
            m.audit_sheet(FakeSheet(bad_header=True))
    def test_reject_sentinel_in_required_field(self):
        with self.assertRaisesRegex(ValueError,"Mandatory"):
            m.audit_sheet(FakeSheet(bad_sentinel=True))
    def test_reject_changed_source_hash_before_openpyxl(self):
        with self.assertRaisesRegex(ValueError,"SHA256"):
            m.audit_sources({"Lelystad":b"fiction","Vredepeel":b"fiction"})
        with self.assertRaisesRegex(ValueError,"Both"):
            m.audit_sources({"Lelystad":b"fiction"})
    def test_sunshine_boolean_decoding(self):
        for val,expected in [(True,True),(False,False),("=TRUE()",True),("FALSE",False),(1,True),(0,False)]:
            self.assertIs(m.sunshine_flag(val),expected)
        with self.assertRaises(ValueError):m.sunshine_flag("maybe")
    def test_missing_numeric_values(self):
        self.assertTrue(m.is_missing(-999.,-999.))
        self.assertTrue(m.is_missing(float("nan"),-999.))
        self.assertTrue(m.is_missing(None,-999.))
        self.assertFalse(m.is_missing(0.,-999.))
if __name__=="__main__":unittest.main()

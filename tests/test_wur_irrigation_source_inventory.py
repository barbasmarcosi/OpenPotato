"""All source structures made from invented data, no licensed WUR rows."""
import hashlib,io,unittest
from datetime import date
from scripts import wur_irrigation_source_inventory as m
try:
    from openpyxl import Workbook
except ImportError:
    Workbook=None

@unittest.skipUnless(Workbook,"openpyxl only installed in dedicated M1-29 workflow")
class InventoryTests(unittest.TestCase):
    def fake(self):
        w=Workbook();meta=w.active;meta.title="meta"
        meta.append(["treatment","water mm","no real field rows"])
        data=w.create_sheet("data")
        data.append(["date","location","plot","amount mm"])
        data.append([date(2019,5,1),"FAKE-SITE","FAKE-PLOT",20.])
        b=io.BytesIO();w.save(b);w.close();return b.getvalue()
    def test_outputs_only_positional_counts_no_header_or_field_values(self):
        r=m.inspect_irrigation(self.fake())
        self.assertEqual(r["sheet_count"],2)
        self.assertFalse(r["real_wofost_irrigation_schedule_ready"])
        self.assertFalse(r["checksum_independently_pinned_before_publication"])
        self.assertEqual(r["sheet_structures"][1]["typed_or_ISO_2019_2020_dates_found_by_year"]["2019"],1)
        text=str(r)
        for banned in ("FAKE-PLOT","FAKE-SITE","no real field rows","20.0"):
            self.assertNotIn(banned,text)
    def test_sha_must_match_when_pinned(self):
        x=self.fake();sha=hashlib.sha256(x).hexdigest()
        self.assertTrue(m.inspect_irrigation(x,expected_sha=sha)["checksum_independently_pinned_before_publication"])
        with self.assertRaisesRegex(ValueError,"SHA256"):
            m.inspect_irrigation(x,expected_sha="0"*64)
    def test_ambiguous_date_not_guessed(self):
        self.assertIsNone(m.parse_date("01/05/2019"))
        self.assertEqual(m.parse_date("2019-05-01"),date(2019,5,1))
    def test_wrong_bytes_fails_closed(self):
        with self.assertRaisesRegex(ValueError,"invalid"):
            m.inspect_irrigation(b"NOT A VALID XLSX")
if __name__=="__main__":unittest.main()

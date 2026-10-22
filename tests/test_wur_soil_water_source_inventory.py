"""Fictional XLSX cells only; no proprietary original WUR water series."""
import hashlib
import io
import unittest
from datetime import date
from unittest.mock import patch
from scripts import wur_soil_water_source_inventory as mod
try:
    from openpyxl import Workbook
except ImportError:
    Workbook=None

def make_fake():
    book=Workbook()
    meta=book.active;meta.title="meta"
    meta.append(["Groundwater level cm","water potential pF","SECRET-SOURCE-HEADER"])
    data=book.create_sheet("synthetic-data")
    data.append(["date","SITE SECRET","soil depth"])
    data.append([date(2019,5,4),-31.5,"PRIVATE_PLOT_ID"])
    data.append([date(2020,5,2),None,"PRIVATE_PLOT_ID"])
    buf=io.BytesIO();book.save(buf);book.close()
    return buf.getvalue()

@unittest.skipUnless(Workbook is not None,"openpyxl in M1-35 dedicated CI")
class SoilSourceInventoryTests(unittest.TestCase):
    def test_bootstrap_only_reports_safe_sheet_metadata(self):
        data=make_fake()
        with patch.dict(mod.ORIGINALS["groundwater"],{"sha256":hashlib.sha256(data).hexdigest()}):
            report=mod.inspect_workbook(data,"groundwater")
        self.assertEqual(report["number_of_sheets"],2)
        self.assertFalse(report["field_soil_parameters_derived"])
        self.assertTrue(report["source_digest_independently_pinned"])
        self.assertEqual(report["sheet_structures"][1]["typed_or_ISO_date_cells_by_year"],{"2019":1,"2020":1})
        result=str(report)
        for secret in ("PRIVATE_PLOT_ID","SECRET-SOURCE-HEADER","-31.5","2019-05-04"):
            self.assertNotIn(secret,result)
    def test_no_bootstrap_requires_independent_source_checksum(self):
        data=make_fake()
        with patch.dict(mod.ORIGINALS["groundwater"],{"sha256":None}):
            with self.assertRaisesRegex(ValueError,"independently pinned"):
                mod.inspect_workbook(data,"groundwater")
    def test_mismatched_hash_is_rejected_if_pinned(self):
        old=mod.ORIGINALS["groundwater"]["sha256"]
        try:
            mod.ORIGINALS["groundwater"]["sha256"]="0"*64
            with self.assertRaisesRegex(ValueError,"SHA256 mismatch"):
                mod.inspect_workbook(make_fake(),"groundwater")
        finally:
            mod.ORIGINALS["groundwater"]["sha256"]=old
    def test_both_origins_required(self):
        with self.assertRaisesRegex(ValueError,"Both WUR original"):
            mod.assess_sources({"groundwater":make_fake()},allow_bootstrap=True)
    def test_invalid_workbook_bytes_never_accepted(self):
        with patch.dict(mod.ORIGINALS["waterpotential"],{"sha256":hashlib.sha256(b"not excel").hexdigest()}):
            with self.assertRaisesRegex(ValueError,"not valid XLSX"):
                mod.inspect_workbook(b"not excel","waterpotential")
    def test_language_patterns_are_clues_not_units(self):
        tags=mod.metadata_tags("water potential pF from 30 cm")
        self.assertIn("potential",tags)
        self.assertIn("tension_pF",tags)
        self.assertIn("depth_cm",tags)
        self.assertNotIn("SECRET ORIGINAL",str(tags))
    def test_dates_not_guessed_from_local_format(self):
        self.assertEqual(mod.checked_date("2019-05-04"),date(2019,5,4))
        self.assertIsNone(mod.checked_date("04/05/2019"))
    def test_measurements_and_missing_not_mixed(self):
        self.assertEqual(mod.classify(0.0),"numeric")
        self.assertEqual(mod.classify(None),"blank_or_missing")
        self.assertEqual(mod.classify(float("nan")),"invalid_numeric")
        self.assertEqual(mod.classify(date(2019,2,1)),"typed_date")
if __name__=="__main__":unittest.main()

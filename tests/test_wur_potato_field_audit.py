"""M1-19: synthetic-only fixture tests; original WUR plot rows NEVER shipped."""
import csv
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import wur_potato_field_audit as mod

ALL=[
    "Year","Date","Location","Plotnumber","Cultivar","Nitrogen","Irrigation",
    "Yield_gross_t.ha","FWyield","tubersFW","tubersDW","tuberDMpercentage","LAI",
]

def fixture(change=None):
    rows=[]
    for year in ("2019","2020"):
        for location in ("L","V"):
            for index in range(2):
                values={name:"NA" for name in ALL}
                values.update(Year=year,Date=year+"-09-01",
                              Location=location,Plotnumber=str(index+1),
                              Cultivar="SYNTHETIC_CULTIVAR",Nitrogen="fertilized",
                              Irrigation="irrigated",
                              tubersDW="1200.0" if index==0 else "NA",
                              tubersFW="6200.0",FWyield="6.2",
                              tuberDMpercentage="20",
                              LAI="1.0",**{"Yield_gross_t.ha":"NA"})
                rows.append(values)
    if change:
        change(rows)
    dst=io.StringIO()
    writer=csv.DictWriter(dst,fieldnames=ALL)
    writer.writeheader()
    writer.writerows(rows)
    return dst.getvalue().encode()


class WurPotatoSourceTests(unittest.TestCase):
    def test_pinned_source_licence_and_known_original_digest(self):
        self.assertEqual(mod.SOURCE_FILE_ID,10850227)
        self.assertEqual(mod.EXPECTED_ROWS,1824)
        self.assertEqual(mod.SOURCE_SHA256,
                         "8d129262dca38ac98a10f92ccfb1bc46454377020575959fd984c4c5bcab5768")
        self.assertEqual(mod.LICENSE,"CC BY-NC-SA 4.0")
        self.assertEqual(mod.MEASUREMENTS["tubersDW"],"kg_dry_tuber_per_ha")

    def run_fixture(self,raw):
        md5,sha=mod.digest_bytes(raw)
        with patch.object(mod,"EXPECTED_ROWS",8),patch.object(
             mod,"SITE_YEAR_EXPECTED",{(y,s):2 for y in ("2019","2020")
                                        for s in ("L","V")}),patch.object(
             mod,"EXPECTED_NUMERIC",{
                 "tubersDW":4,"tubersFW":8,"tuberDMpercentage":8,
                 "Yield_gross_t.ha":0,"FWyield":8,"LAI":8}):
            return mod.inspect_original(raw,expected_md5=md5,expected_sha256=sha)

    def test_source_metadata_numeric_coverage_na_excluded(self):
        report=self.run_fixture(fixture())
        self.assertEqual(report["total_original_rows_inspected_without_export"],8)
        self.assertEqual(report["observation_rows_exported"],0)
        self.assertEqual(report["source_yield_values_exported"],0)
        self.assertEqual(len(report["year_site_counts"]),4)
        observed={x["original_column"]:x["finite_numeric_entries"]
                  for x in report["measurements_available"]}
        self.assertEqual(observed["tubersDW"],4)
        self.assertEqual(observed["Yield_gross_t.ha"],0)
        for banned in ("SYNTHETIC_CULTIVAR","1200.0","Plotnumber"):
            self.assertNotIn(banned,json.dumps(report))

    def test_reject_unknown_source_hash_and_source_tampering(self):
        raw=fixture()
        with self.assertRaisesRegex(ValueError,"checksum changed"):
            mod.inspect_original(raw)
        good_md5,good_sha=mod.digest_bytes(raw)
        tampered=raw+b" "
        with self.assertRaisesRegex(ValueError,"checksum changed"):
            mod.inspect_original(tampered,expected_md5=good_md5,
                                 expected_sha256=good_sha)

    def test_missing_original_field_rejected(self):
        raw=fixture()
        raw=raw.replace(b"tubersDW",b"notDWTB",1)
        with self.assertRaisesRegex(ValueError,"required fields"):
            self.run_fixture(raw)

    def test_nonfinite_or_negative_observation_must_stop(self):
        for invalid in ("-12","inf","-inf","not-a-number"):
            def change(rows):
                rows[0]["tubersDW"]=invalid
            with self.subTest(invalid=invalid):
                with self.assertRaisesRegex(ValueError,"Nonfinite|Negative|Unparseable"):
                    self.run_fixture(fixture(change))

    def test_extra_row_breaks_verified_original_group_totals(self):
        raw=fixture()
        with self.assertRaisesRegex(ValueError,"row count"):
            self.run_fixture(raw+raw.splitlines(True)[1])

    def test_literal_na_and_blank_values_not_zero(self):
        for value in ("NA","NaN","NULL","  ",""):
            self.assertIsNone(mod.parse_numeric(value))
        self.assertEqual(mod.parse_numeric("0"),0)
        self.assertEqual(mod.parse_numeric("25.4"),25.4)

    def test_complete_real_source_kept_outside_repository(self):
        self.assertTrue(mod.SOURCE_FILENAME.endswith(".csv"))
        self.assertTrue(mod.SOURCE_SHA256.startswith("8d1292"))
        self.assertIn("Noncommercial","Noncommercial".title())
        self.assertNotIn("tubersDW",mod.SITE_NAMES)


if __name__=="__main__":
    unittest.main()

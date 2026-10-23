"""Cross-study clone reconciliation integrity; NO causal G×E inference."""
import csv
import json
import tempfile
import unittest
from pathlib import Path

from scripts.cross_study_clones import A,B,PM_A,PM_B,run


class CrossStudyTests(unittest.TestCase):
    def test_15_shared_accessions_no_yield_unit_mixing(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);audit=run(out=root)
            self.assertEqual(audit["exactly_matching_accessions"],15)
            self.assertEqual(audit["catalogue_accessions"],29)
            self.assertEqual(audit["holetta_accessions"],45)
            with (root/"matched_cip_clones.csv").open() as f:
                rows=list(csv.DictReader(f))
            self.assertEqual(len(rows),15)
            self.assertTrue(all(x["catalogue_yield_unit"]=="kg/plant" for x in rows))
            self.assertTrue(all(x["holetta_yield_unit"]=="kg/m2_fresh" for x in rows))
            self.assertTrue(all(x["comparison_design"]=="non_matched_published_summaries" for x in rows))
            self.assertIn("NO es un ensayo",(root/"matched_cip_report.md").read_text())
    def test_sources_cannot_be_substituted(self):
        with tempfile.TemporaryDirectory() as td:
            f=Path(td)/"fake.csv";f.write_text(A.read_text()+"\n")
            with self.assertRaisesRegex(ValueError,"SHA-256"):
                run(a=f,out=Path(td)/"r")
    def test_reports_missingness_but_does_not_fill_it(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);run(out=root)
            data=list(csv.DictReader((root/"matched_cip_clones.csv").open()))
            unknown=[x for x in data if x["catalogue_vitamin_c_status"]=="not_reported"]
            self.assertTrue(unknown)
            self.assertTrue(all(x["catalogue_vitamin_c_mg_100g_dry"]=="" for x in unknown))

if __name__=="__main__":
    unittest.main()

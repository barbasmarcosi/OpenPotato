"""Header-only intake generator never creates fictional biology."""
import csv
import tempfile
import unittest
from pathlib import Path

from scripts.create_sample_lineage_templates import create
from scripts.validate_sample_lineage import STUDY_COLS, read_csv


class TemplateTests(unittest.TestCase):
    def test_generates_only_empty_headers_for_five_sources(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/"intake"
            self.assertEqual(create(root),5)
            for name,fields in STUDY_COLS.items():
                with (root/(name+".csv")).open(newline="",encoding="utf-8") as f:
                    rdr=csv.reader(f)
                    self.assertEqual(next(rdr),sorted(fields))
                    self.assertEqual(list(rdr),[])
            self.assertIn("SIN observaciones reales",(root/"INTAKE_README.md").read_text())
            self.assertNotIn("PRIVATE_FAKE", "\n".join(
                p.read_text() for p in root.iterdir()))

    def test_cannot_overwrite_partially_filled_authorized_csv(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            existing=root/"samples.csv"
            existing.write_text("SENSITIVE_EXISTING_DATA",encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"refusing to overwrite"):
                create(root)
            self.assertEqual(existing.read_text(),"SENSITIVE_EXISTING_DATA")
            self.assertFalse((root/"plots.csv").exists())

    def test_header_only_csv_not_accepted_as_experimental_observations(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            create(root)
            with self.assertRaisesRegex(ValueError,"empty source table"):
                read_csv(root/"plots.csv",STUDY_COLS["plots"],"plots")


if __name__ == "__main__":
    unittest.main()

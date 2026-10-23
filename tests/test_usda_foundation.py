"""Offline tests for April 2026 USDA Foundation Food ingestion."""
import csv
import io
import tempfile
import unittest
import zipfile
from pathlib import Path
from scripts.usda_foundation import EXPECTED, TARGETS, extract, compare

def make_csv(fields, rows):
    buffer=io.StringIO(newline="")
    writer=csv.DictWriter(buffer,fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()

def fixture(path, *, missing_type=False, duplicate=False, wrong_unit=False, loq=False):
    foods=[{"fdc_id":str(i+2346401),"description":desc,"data_type":"foundation_food"}
           for i,(kind,desc) in enumerate(EXPECTED.items())
           if not (missing_type and kind=="gold")]
    definition=[{"id":str(nid),"unit_name":"g" if wrong_unit and nid==1089
                 else "ug" if unit.startswith("ug_") else unit,"name":name}
                for name,(nid,unit) in TARGETS.items()]
    results=[]
    for row in foods:
        for nid,val in [(2047,"75"),(1089,"0.33"),(1095,"0.22"),(1162,"0")]:
            is_below=loq and nid==1162
            results.append({"fdc_id":row["fdc_id"],"nutrient_id":str(nid),
                            "amount":val,"loq":"0.05" if is_below else "",
                            "data_points":"3"})
    if duplicate: results.append(results[0].copy())
    with zipfile.ZipFile(path,"w") as z:
        z.writestr("foundation/food.csv",make_csv(["fdc_id","description","data_type"],foods))
        z.writestr("foundation/nutrient.csv",make_csv(["id","unit_name","name"],definition))
        z.writestr("foundation/food_nutrient.csv",
                   make_csv(["fdc_id","nutrient_id","amount","loq","data_points"],results))

class FoundationImporterTests(unittest.TestCase):
    def test_extract_three_types_and_unknown_data(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);fixture(root/"data.zip",loq=True)
            meta=extract(root/"data.zip",root/"result")
            self.assertEqual(len(meta["foods"]),3)
            with (root/"result"/"foundation_market_types.csv").open() as handle:
                rows=list(csv.DictReader(handle))
            self.assertEqual(len(rows),3*len(TARGETS))
            indexed={(r["market_type"],r["nutrient"]):r for r in rows}
            self.assertEqual(indexed["red","iron"]["amount_per_100g"],"0.33")
            self.assertEqual(indexed["gold","energy_atwater_general_kcal"]["amount_per_100g"],"75")
            self.assertEqual(indexed["russet","vitamin_c"]["status"],"below_quantification")
            self.assertEqual(indexed["russet","vitamin_c"]["amount_per_100g"],"")
            self.assertEqual(indexed["gold","vitamin_b12"]["status"],"not_reported")
            compare(rows_path:=root/"result"/"foundation_market_types.csv",
                    root/"result"/"comparison.md")
            self.assertIn("<LOQ",(root/"result"/"comparison.md").read_text())
    def test_duplicate_nutrient_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);fixture(root/"data.zip",duplicate=True)
            with self.assertRaisesRegex(ValueError,"Duplicate"):
                extract(root/"data.zip",root/"out")
    def test_missing_market_type_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);fixture(root/"data.zip",missing_type=True)
            with self.assertRaisesRegex(ValueError,"Missing market"):
                extract(root/"data.zip",root/"out")
    def test_wrong_unit_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);fixture(root/"data.zip",wrong_unit=True)
            with self.assertRaisesRegex(ValueError,"unit mismatch"):
                extract(root/"data.zip",root/"out")
    def test_archive_change_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);fixture(root/"data.zip")
            with self.assertRaisesRegex(ValueError,"SHA-256"):
                extract(root/"data.zip",root/"out",expected_sha256="0"*64)
    def test_undefined_not_a_zero(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);fixture(root/"data.zip")
            extract(root/"data.zip",root/"result")
            obs=compare(root/"result"/"foundation_market_types.csv",
                        root/"result"/"comparison.md")
            by_id={r["nutrient"]:r for r in obs}
            self.assertFalse(by_id["vitamin_b12"]["complete"])
            self.assertIsNone(by_id["vitamin_b12"]["min"])
            self.assertTrue(by_id["iron"]["complete"])

if __name__ == "__main__":
    unittest.main()

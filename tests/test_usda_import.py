"""Test importer against synthetic USDA CSV archive without network."""
import csv, io, json, tempfile, unittest, zipfile
from pathlib import Path
from scripts.usda_sr_legacy import FOOD_NAMES, NUTRIENTS, extract

def encode(fields, records):
    stream=io.StringIO(newline="")
    writer=csv.DictWriter(stream,fieldnames=fields)
    writer.writeheader();writer.writerows(records)
    return stream.getvalue()

def fixture(path, wrong_unit=False, duplicate=False, missing=False):
    foods=[{"fdc_id":fid,"description":name,"data_type":"sr_legacy_food"}
           for fid,name in FOOD_NAMES.items() if not (missing and fid=="170440")]
    nutrients=[{"id":str(nid),"name":name,
                "unit_name":"G" if (wrong_unit and nid==1089) else ("UG" if unit.startswith("ug") else unit.upper())}
               for nid,unit,name in NUTRIENTS.values() if nid is not None]
    vals=[{"fdc_id":f["fdc_id"],"nutrient_id":str(nid),"amount":value}
          for f in foods for nid,value in [(1008,"87" if f["fdc_id"]=="170438" else "86"),
                                            (1089,"0.31"),(1178,"0")]]
    if duplicate: vals.append(vals[0])
    with zipfile.ZipFile(path,"w") as zipfile_out:
        zipfile_out.writestr("data/food.csv",encode(["fdc_id","description","data_type"],foods))
        zipfile_out.writestr("data/nutrient.csv",encode(["id","name","unit_name"],nutrients))
        zipfile_out.writestr("data/food_nutrient.csv",encode(["fdc_id","nutrient_id","amount"],vals))

class TestOfficialUSDA(unittest.TestCase):
    def test_valid_two_foods_and_zero_vs_missing(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);fixture(root/"source.zip")
            manifest=extract(root/"source.zip",root/"out")
            self.assertEqual(len(manifest["archive_sha256"]),64)
            self.assertEqual(len(json.loads((root/"out/provenance.json").read_text())["records"]),2)
            for fid in FOOD_NAMES:
                with (root/"out"/f"potato_fdc_{fid}_usda.csv").open() as f:
                    records={r["nutrient"]:r for r in csv.DictReader(f)}
                self.assertEqual(records["vitamin_b12"]["status"],"reported_zero")
                self.assertEqual(records["vitamin_b12"]["amount_per_100g"],"0")
                self.assertEqual(records["linoleic_acid"]["status"],"not_reported")
                self.assertEqual(records["linoleic_acid"]["amount_per_100g"],"")
                self.assertEqual(records["iron"]["unit"],"mg")
    def test_units_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);fixture(root/"bad.zip",wrong_unit=True)
            with self.assertRaisesRegex(ValueError,"unit"):extract(root/"bad.zip",root/"out")
    def test_duplicate_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);fixture(root/"bad.zip",duplicate=True)
            with self.assertRaisesRegex(ValueError,"duplicate"):extract(root/"bad.zip",root/"out")
    def test_missing_food_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);fixture(root/"bad.zip",missing=True)
            with self.assertRaisesRegex(ValueError,"missing"):extract(root/"bad.zip",root/"out")

if __name__=="__main__": unittest.main()

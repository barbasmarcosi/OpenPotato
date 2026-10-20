"""Synthetic full-join checks for USDA Foundation retail sample variability."""
import csv, io, json, tempfile, unittest, zipfile
from decimal import Decimal
from pathlib import Path
from scripts.foundation_variability import analyze, FOCUS
from scripts.usda_foundation import EXPECTED, TARGETS, filehash


def csvtext(fields, rows):
    out=io.StringIO(newline="")
    writer=csv.DictWriter(out,fieldnames=fields)
    writer.writeheader(); writer.writerows(rows)
    return out.getvalue()


def fixture(path, *, missing_lab=False, duplicate_link=False, bad_sample=False):
    root_ids={kind:str(4000+i) for i,kind in enumerate(EXPECTED)}
    foods=[{"fdc_id":root_ids[kind],"description":desc,"data_type":"foundation_food",
            "publication_date":"2022-10-28"} for kind,desc in EXPECTED.items()]
    nutrient_rows=[{"id":nid,"name":key,
                    "unit_name":"ug" if unit.startswith("ug_") else unit}
                   for key,(nid,unit) in TARGETS.items()]
    input_rows=[]; samples=[]; acquire_links=[]; markets=[]; subfoods=[]
    food_nutrients=[]; labs=[]
    nutrient_counter=100000
    for idx,kind in enumerate(EXPECTED):
        base=int(root_ids[kind])
        for n in range(8):
            sid=str(5000+idx*100+n)
            acquire=str(6000+idx*100+n)
            foods.append({"fdc_id":sid,"description":EXPECTED[kind],
                          "data_type":"sample_food","publication_date":"2022-10-28"})
            samples.append({"fdc_id":sid})
            input_rows.append({"fdc_id":str(base),"fdc_of_input_food":sid})
            acquire_links.append({"fdc_id_of_sample_food":sid,"fdc_id_of_acquisition_food":acquire})
            markets.append({"fdc_id":acquire,"acquisition_date":"2022-02-24",
                            "store_city":"SampleTown","store_state":"VA"})
            for m,(label,nid) in enumerate(FOCUS.items()):
                child=str(70000+idx*1000+n*10+m)
                subfoods.append({"fdc_id":child,"fdc_id_of_sample_food":sid})
                nutrient_counter+=1
                amount=str(Decimal(idx+1)+Decimal(n)/10+Decimal(m)/100)
                food_nutrients.append({"id":str(nutrient_counter),"fdc_id":child,
                                       "nutrient_id":str(nid),"amount":amount,
                                       "data_points":"1","min":"","max":"","median":""})
                labs.append({"food_nutrient_id":str(nutrient_counter),
                             "adjusted_amount":amount,"lab_method_id":"1009",
                             "nutrient_name":label})
        for m,(label,nid) in enumerate(FOCUS.items()):
            values=[Decimal(idx+1)+Decimal(n)/10+Decimal(m)/100 for n in range(8)]
            food_nutrients.append({"id":str(200000+idx*10+m),"fdc_id":str(base),
                                   "nutrient_id":str(nid),
                                   "amount":str(sum(values)/8),"data_points":"8",
                                   "min":str(min(values)),"max":str(max(values)),
                                   "median":str((values[3]+values[4])/2)})
    if missing_lab: labs.pop()
    if duplicate_link: input_rows.append(input_rows[0].copy())
    if bad_sample: samples.pop()
    all_files={
        "food.csv":csvtext(["fdc_id","description","data_type","publication_date"],foods),
        "nutrient.csv":csvtext(["id","name","unit_name"],nutrient_rows),
        "food_nutrient.csv":csvtext(["id","fdc_id","nutrient_id","amount","data_points","min","max","median"],food_nutrients),
        "input_food.csv":csvtext(["fdc_id","fdc_of_input_food"],input_rows),
        "sample_food.csv":csvtext(["fdc_id"],samples),
        "acquisition_samples.csv":csvtext(["fdc_id_of_sample_food","fdc_id_of_acquisition_food"],acquire_links),
        "market_acquisition.csv":csvtext(["fdc_id","acquisition_date","store_city","store_state"],markets),
        "sub_sample_food.csv":csvtext(["fdc_id","fdc_id_of_sample_food"],subfoods),
        "sub_sample_result.csv":csvtext(["food_nutrient_id","adjusted_amount","lab_method_id","nutrient_name"],labs),
    }
    with zipfile.ZipFile(path,"w") as z:
        for filename,source in all_files.items():
            z.writestr("dataset/"+filename,source)


class TestVariability(unittest.TestCase):
    def test_happy_path_and_sample_variation(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); source=root/"synthetic.zip"
            fixture(source)
            provenance=analyze(source,root/"result",expected_sha256=filehash(source))
            self.assertEqual(provenance["measurement_rows"],96)
            with (root/"result"/"retail_sample_summary.csv").open() as file:
                rows=list(csv.DictReader(file))
            self.assertEqual(len(rows),12)
            target=next(r for r in rows if r["market_type"]=="russet" and r["nutrient"]=="iron")
            self.assertEqual(Decimal(target["mean"]),Decimal("1.35"))
            self.assertEqual(Decimal(target["range"]),Decimal("0.7"))
            self.assertEqual(target["range_reconciled"],"true")
            self.assertEqual(target["median_reconciled"],"true")
            self.assertGreater(Decimal(target["sample_sd"]),0)
            self.assertIn("NO", (root/"result"/"retail_sample_report.md").read_text().upper())

    def test_missing_lab_measurement_is_not_imputed(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);source=root/"broken.zip";fixture(source,missing_lab=True)
            with self.assertRaisesRegex(ValueError,"Unlinked measurement"):
                analyze(source,root/"out",expected_sha256=filehash(source))

    def test_repeated_input_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);source=root/"broken.zip";fixture(source,duplicate_link=True)
            with self.assertRaisesRegex(ValueError,"Repeated purchase"):
                analyze(source,root/"out",expected_sha256=filehash(source))

    def test_orphan_sample_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);source=root/"broken.zip";fixture(source,bad_sample=True)
            with self.assertRaisesRegex(ValueError,"sample_food"):
                analyze(source,root/"out",expected_sha256=filehash(source))

    def test_checksum_prevents_unverified_release_changes(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);source=root/"broken.zip";fixture(source)
            with self.assertRaisesRegex(ValueError,"checksum"):
                analyze(source,root/"out",expected_sha256="0"*64)


if __name__=="__main__":
    unittest.main()

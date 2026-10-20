"""Comparisons always use SHA-256 verified primary source and remain descriptive."""
import json
import shutil
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from openpotato.compare import compare, DEFAULT_SOURCE
from openpotato.m1 import load_food, DEFAULT_FOOD

class TestPreparations(unittest.TestCase):
    def test_direct_usda_is_default(self):
        self.assertEqual(DEFAULT_FOOD.name,"potato_fdc_170438_usda.csv")
        self.assertEqual(load_food(DEFAULT_FOOD)["vitamin_c"].value,Decimal("13"))

    def test_comparison_has_noncausal_output(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)
            rows=compare(DEFAULT_SOURCE,out)
            indexed={r["nutrient"]:r for r in rows}
            self.assertEqual(indexed["vitamin_c"]["fdc_170438"],"13")
            self.assertEqual(indexed["vitamin_c"]["fdc_170440"],"7.4")
            self.assertEqual(indexed["vitamin_c"]["delta_440_minus_438"],"-5.6")
            self.assertEqual(indexed["linoleic_acid"]["status"],"not_reported")
            self.assertEqual(indexed["linoleic_acid"]["relative_change_pct"],"")
            self.assertIn("No es un experimento controlado", (out/"comparison.md").read_text())
            self.assertTrue((out/"preparation_comparison.csv").is_file())

    def test_tampered_primary_source_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            source=Path(temp)/"source";source.mkdir()
            for name in ("provenance.json","potato_fdc_170438_usda.csv","potato_fdc_170440_usda.csv"):
                shutil.copyfile(DEFAULT_SOURCE/name,source/name)
            with (source/"potato_fdc_170440_usda.csv").open("a") as handle:
                handle.write("\n")
            with self.assertRaisesRegex(ValueError,"SHA-256"):
                compare(source,Path(temp)/"output")

    def test_previous_proxy_values_reconciled(self):
        old=load_food(DEFAULT_SOURCE.parent/"potato_fdc_170438_proxy.csv")
        official=load_food(DEFAULT_FOOD)
        for key, previous in old.items():
            current=official[key]
            self.assertEqual(previous.unit,current.unit,key)
            self.assertEqual(previous.value,current.value,key)
            self.assertEqual(previous.status,current.status,key)

if __name__=="__main__": unittest.main()

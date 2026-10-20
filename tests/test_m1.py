"""Pruebas de propiedades, unidades y trazabilidad para el experimento OP-M1-001."""

import csv
import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from openpotato.m1 import (
    DEFAULT_FOOD, DEFAULT_REFERENCES, compute_rows,
    energy_equivalent_grams, load_food, load_references, run,
)


class BaselineM1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.food = load_food(DEFAULT_FOOD)
        cls.refs = load_references(DEFAULT_REFERENCES)

    def test_real_fixture_loaded(self):
        self.assertEqual(self.food["energy_kcal"].value, Decimal("87"))
        self.assertEqual(self.food["iron"].value, Decimal("0.31"))
        self.assertEqual(self.food["vitamin_b12"].status, "reported_zero")

    def test_scaling_is_linear(self):
        profile = self.refs["adult_male_31_50"]
        a = {r["nutrient"]: r for r in compute_rows(self.food, profile, Decimal(200))}
        b = {r["nutrient"]: r for r in compute_rows(self.food, profile, Decimal(400))}
        self.assertEqual(Decimal(b["iron"]["amount"]), 2 * Decimal(a["iron"]["amount"]))
        self.assertEqual(Decimal(b["zinc"]["coverage_percent"]),
                         2 * Decimal(a["zinc"]["coverage_percent"]))

    def test_iron_reference_depends_on_profile(self):
        male = {r["nutrient"]: r for r in compute_rows(
            self.food, self.refs["adult_male_31_50"], Decimal(400))}
        female = {r["nutrient"]: r for r in compute_rows(
            self.food, self.refs["adult_female_31_50"], Decimal(400))}
        self.assertEqual(Decimal(male["iron"]["amount"]), Decimal("1.24"))
        self.assertEqual(Decimal(male["iron"]["reference"]), Decimal("8"))
        self.assertEqual(Decimal(female["iron"]["reference"]), Decimal("18"))
        self.assertGreater(Decimal(male["iron"]["coverage_percent"]),
                           Decimal(female["iron"]["coverage_percent"]))

    def test_missing_essential_fatty_acids_never_zero(self):
        rows = {r["nutrient"]: r for r in compute_rows(
            self.food, self.refs["adult_male_31_50"], Decimal(400))}
        self.assertEqual(rows["linoleic_acid"]["amount"], "")
        self.assertEqual(rows["linoleic_acid"]["coverage_percent"], "")
        self.assertEqual(rows["linoleic_acid"]["status"], "not_reported")
        self.assertEqual(rows["vitamin_b12"]["amount"], "0")
        self.assertEqual(rows["vitamin_b12"]["food_status"], "reported_zero")

    def test_ai_remains_ai_not_diagnosis(self):
        rows = {r["nutrient"]: r for r in compute_rows(
            self.food, self.refs["adult_male_31_50"], Decimal(400))}
        self.assertEqual(rows["potassium"]["reference_kind"], "AI")
        self.assertEqual(rows["iron"]["reference_kind"], "RDA")

    def test_2000_kcal_math(self):
        equivalent = energy_equivalent_grams(self.food, Decimal(2000))
        self.assertEqual((equivalent * Decimal("87") / 100), Decimal(2000))

    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            compute_rows(self.food, self.refs["adult_male_31_50"], Decimal(-1))
        with self.assertRaises(ValueError):
            energy_equivalent_grams(self.food, Decimal(0))

    def test_mismatching_units_fails_closed(self):
        with tempfile.TemporaryDirectory() as t:
            file = Path(t) / "test.csv"
            with file.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.writer(stream)
                writer.writerow(["profile", "nutrient", "reference_value", "unit", "kind", "source_id"])
                writer.writerow(["test", "iron", "8", "g", "RDA", "source"])
            ref = load_references(file)["test"]
            with self.assertRaisesRegex(ValueError, "Unidades incompatibles"):
                compute_rows(self.food, ref, Decimal(400))

    def test_reject_unknown_finite_numbers(self):
        with tempfile.TemporaryDirectory() as t:
            file = Path(t) / "bad.csv"
            file.write_text(
                "nutrient,unit,amount_per_100g,status,source_id\n"
                "energy_kcal,kcal,87,observed,source\n"
                "iron,mg,NaN,observed,source\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "fuera de rango"):
                load_food(file)

    def test_run_reproducible_artifacts(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            run(food_path=DEFAULT_FOOD, reference_path=DEFAULT_REFERENCES,
                output_dir=Path(a), grams_list=(Decimal(200), Decimal(400)),
                energy_kcal=Decimal(2000))
            run(food_path=DEFAULT_FOOD, reference_path=DEFAULT_REFERENCES,
                output_dir=Path(b), grams_list=(Decimal(200), Decimal(400)),
                energy_kcal=Decimal(2000))
            for filename in ("coverage.csv", "manifest.json", "report.md"):
                self.assertEqual((Path(a) / filename).read_bytes(),
                                 (Path(b) / filename).read_bytes())
            manifest = json.loads((Path(a) / "manifest.json").read_text())
            self.assertIn("sha256", manifest["datasets"]["food"])
            self.assertEqual(len(manifest["profiles"]), 2)


if __name__ == "__main__":
    unittest.main()

"""Synthetic-only M1-14 lineage tests: NO actual CIP participant or plot values."""
import csv
import tempfile
import unittest
from pathlib import Path
from scripts.validate_sample_lineage import STUDY_COLS, audit

PRIVATE = "PRIVATE_FAKE_SOURCE_NEVER_EXPORT"


def fixture():
    tables = {name: [] for name in STUDY_COLS}
    for site in ("SITE-1", "SITE-2"):
        for genotype in ("G1", "G2", "G3"):
            for block in ("B1", "B2"):
                plot = f"{site}-{genotype}-{block}"
                sample = "S-" + plot
                key = dict(trial_id="TEST-TRIAL", site_id=site, season_id="2020",
                           block_id=block, plot_id=plot)
                tables["plots"].append(dict(**key, genotype_id=genotype, plot_area_m2="9.72"))
                tables["samples"].append(dict(
                    sample_id=sample, trial_id="TEST-TRIAL",
                    sample_design="single_plot", tissue="peeled_flesh",
                    processing="raw", sampling_date="2020-08-20", source_id=PRIVATE))
                tables["sample_plots"].append(dict(**key, sample_id=sample))
                for trait in ("iron", "zinc"):
                    tables["assays"].append(dict(
                        assay_id=f"{sample}-{trait}", sample_id=sample,
                        trait=trait, measurement_kind="primary",
                        qualifier="quantified", value="12.5", limit_value="",
                        unit="mg/kg_dry", method="XRF", lab_id=PRIVATE))
                tables["harvest"].append(dict(
                    **key, harvested_kg_fresh="10", harvest_area_m2="9.72"))
    return tables


def run(directory, mutate=None):
    table = fixture()
    if mutate:
        mutate(table)
    paths = {}
    for name, fields in STUDY_COLS.items():
        p = Path(directory) / f"{name}.csv"
        with p.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=sorted(fields))
            writer.writeheader()
            writer.writerows(table[name])
        paths[name] = p
    output = Path(directory) / "report"
    result = audit(paths["plots"], paths["samples"], paths["sample_plots"],
                   paths["assays"], paths["harvest"], output)
    return result, output


class ChainTests(unittest.TestCase):
    def test_valid_custody_only_admits_human_review_and_not_raw_data(self):
        with tempfile.TemporaryDirectory() as td:
            r, out = run(td)
            self.assertEqual(r["status"], "STRUCTURALLY_LINKED_EXPERT_REVIEW_REQUIRED")
            self.assertEqual(r["statistical_model"], "NO_MODEL_FITTED_REVIEW_ONLY")
            self.assertEqual(r["complete_eligible_plot_pairs_with_yield"], 12)
            self.assertEqual(r["physical_plots"], 12)
            self.assertEqual(r["quantified_primary_assays"], 24)
            self.assertEqual(r["site_count"], 2)
            for p in out.iterdir():
                text = p.read_text()
                self.assertNotIn(PRIVATE, text)
                self.assertNotIn("S-SITE-1", text)

    def test_reject_duplicate_physical_plot(self):
        with tempfile.TemporaryDirectory() as td:
            def change(t):
                for k in ("trial_id", "site_id", "season_id", "block_id", "plot_id"):
                    t["plots"][1][k] = t["plots"][0][k]
            with self.assertRaisesRegex(ValueError, "Duplicate physical plot"):
                run(td, change)

    def test_missing_join_is_not_fabricated(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError, "missing an explicit original"):
                run(td, lambda t: t["sample_plots"].pop())

    def test_cross_genotype_pool_refused(self):
        with tempfile.TemporaryDirectory() as td:
            def change(t):
                t["samples"][0]["sample_design"] = "pooled_plots"
                extra = dict(t["sample_plots"][2])
                extra["sample_id"] = t["samples"][0]["sample_id"]
                t["sample_plots"].append(extra)
            with self.assertRaisesRegex(ValueError, "Mixed genotypes"):
                run(td, change)

    def test_homogeneous_pool_blocks_plot_level_inference(self):
        with tempfile.TemporaryDirectory() as td:
            def change(t):
                t["samples"][0]["sample_design"] = "pooled_plots"
                extra = dict(t["sample_plots"][1])
                extra["sample_id"] = t["samples"][0]["sample_id"]
                t["sample_plots"].append(extra)
            r,_ = run(td,change)
            self.assertEqual(r["pooled_sample_records"], 1)
            self.assertTrue(r["status"].startswith("BLOCKED"))
            self.assertEqual(r["complete_eligible_plot_pairs_with_yield"], 11)

    def test_censoring_preserved_and_blocks_complete_paired_observation(self):
        with tempfile.TemporaryDirectory() as td:
            def change(t):
                a=t["assays"][0];a["qualifier"]="below_detection"
                a["value"]="";a["limit_value"]="0.02"
            r,_=run(td,change)
            self.assertEqual(r["censored_assays_without_zero_imputation"],1)
            self.assertEqual(r["complete_eligible_plot_pairs_with_yield"],11)
            self.assertTrue(r["status"].startswith("BLOCKED"))

    def test_censoring_with_imputed_zero_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            def change(t):
                a=t["assays"][0];a["qualifier"]="below_quantification"
                a["value"]="0";a["limit_value"]="0.02"
            with self.assertRaisesRegex(ValueError, "must not impute"):
                run(td,change)

    def test_technical_repeat_is_not_biological_replicate(self):
        with tempfile.TemporaryDirectory() as td:
            def change(t):
                a=dict(t["assays"][0]);a["assay_id"]="TECH-1"
                a["measurement_kind"]="technical_replicate"
                t["assays"].append(a)
            r,_=run(td,change)
            self.assertEqual(r["technical_assays_not_biological_replicates"],1)
            self.assertEqual(r["physical_plots"],12)
            self.assertEqual(r["status"],"STRUCTURALLY_LINKED_EXPERT_REVIEW_REQUIRED")

    def test_technical_without_primary_fails(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError, "without declared primary"):
                run(td,lambda t:t["assays"][0].__setitem__(
                    "measurement_kind","technical_replicate"))

    def test_duplicate_primary_fails(self):
        with tempfile.TemporaryDirectory() as td:
            def change(t):
                a=dict(t["assays"][0]);a["assay_id"]="DUP-NEW"
                t["assays"].append(a)
            with self.assertRaisesRegex(ValueError, "Duplicate primary"):
                run(td,change)

    def test_missing_iron_or_zinc_blocks_statistical_admission(self):
        with tempfile.TemporaryDirectory() as td:
            r,_=run(td,lambda t:t["assays"].pop())
            self.assertEqual(r["incomplete_primary_sample_trait_pairs"],1)
            self.assertTrue(r["status"].startswith("BLOCKED"))

    def test_missing_harvest_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            r,_=run(td,lambda t:t["harvest"].pop())
            self.assertEqual(r["plots_missing_harvest"],1)
            self.assertEqual(r["complete_eligible_plot_pairs_with_yield"],11)
            self.assertTrue(r["status"].startswith("BLOCKED"))

    def test_fresh_basis_mineral_refused(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError, "fresh/dry"):
                run(td,lambda t:t["assays"][0].__setitem__("unit","mg/kg_fresh"))

    def test_harvest_area_greater_than_plot_is_invalid(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError, "exceeds"):
                run(td,lambda t:t["harvest"][0].__setitem__("harvest_area_m2","12"))

    def test_impossible_sample_date_refused(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError, "ISO calendar"):
                run(td,lambda t:t["samples"][0].__setitem__("sampling_date","2020-02-30"))

    def test_second_single_plot_sample_never_averaged(self):
        with tempfile.TemporaryDirectory() as td:
            def change(t):
                s=dict(t["samples"][0]);s["sample_id"]="S-SECOND"
                t["samples"].append(s)
                m=dict(t["sample_plots"][0]);m["sample_id"]=s["sample_id"]
                t["sample_plots"].append(m)
                for base in t["assays"][:2]:
                    a=dict(base);a["assay_id"]="ALT-"+base["trait"];a["sample_id"]=s["sample_id"]
                    t["assays"].append(a)
            r,_=run(td,change)
            self.assertEqual(r["plots_with_multiple_single_plot_samples_no_auto_averaging"],1)
            self.assertTrue(r["status"].startswith("BLOCKED"))

    def test_csv_duplicate_headers_refused(self):
        with tempfile.TemporaryDirectory() as td:
            # Duplicate sample header simulates ambiguous upstream export.
            def change(t): pass
            from scripts.validate_sample_lineage import read_csv
            p=Path(td)/"bad.csv"
            p.write_text("x,x\nA,B\n")
            with self.assertRaisesRegex(ValueError,"duplicate CSV headers"):
                read_csv(p,{"x","y"},"samples")


if __name__ == "__main__":
    unittest.main()

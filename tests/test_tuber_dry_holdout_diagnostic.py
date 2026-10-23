"""Purely synthetic normalized potato dry biomass; no licensed field records."""
import csv
import json
import tempfile
import unittest
from pathlib import Path
from scripts import tuber_dry_holdout_diagnostic as mod

PLOT_MARKER="SECRET_SYNTHETIC_PLOT_"


def test_records():
    obs,pred=[],[]
    for site in ("LELYSTAD","VREDEPEEL"):
        for cultivar in ("FAKE-CULTIVAR-A","FAKE-CULTIVAR-B"):
            common={"trial_id":"SYNTHETIC_TRIAL","site_id":site,"year":"2020",
                    "cultivar_id":cultivar,"management_id":"SYNTHETIC_RAINFED",
                    "observation_date":"2020-09-05",
                    "trait":mod.TRAIT,"unit":mod.UNIT}
            for block,val in (("B1","90"),("B2","100")):
                obs.append({**common,"plot_id":PLOT_MARKER+site+cultivar+block,
                            "observed_value":val})
            pred.append({**common,"predicted_value":"110",
                         "model_name":"Wofost81_WLP_CWB",
                         "model_cultivar_id":cultivar,
                         "model_config_sha256":"a"*64,
                         "source_weather_sha256":"b"*64})
    manifest={
        "source_doi":mod.SOURCE_DOI,
        "source_sha256":mod.SOURCE_SHA,
        "source_license":mod.LICENSE,
        "source_version":"3.0",
        "calibration_years":[2019],
        "heldout_evaluation_years":[2020],
        "split_locked_before_model_tuning":True,
        "prediction_generated_without_evaluation_yields":True,
        "irrigation_soil_weather_provenance_independently_reviewed":False,
    }
    return obs,pred,manifest


def emit(root,observations,predictions,manifest):
    root=Path(root)
    result={}
    for name,fields,records in [
        ("observed",mod.OBS_FIELDS,observations),
        ("predicted",mod.PRED_FIELDS,predictions),
    ]:
        path=root/(name+".csv")
        with path.open("w",newline="",encoding="utf-8") as f:
            writer=csv.DictWriter(f,fieldnames=sorted(fields))
            writer.writeheader();writer.writerows(records)
        result[name]=path
    path=root/"manifest.json"
    path.write_text(json.dumps(manifest),encoding="utf-8")
    result["manifest"]=path
    return result


def sample_run(root,change=None):
    obs,pred,manifest=test_records()
    if change:change(obs,pred,manifest)
    paths=emit(root,obs,pred,manifest)
    return mod.compare(paths["observed"],paths["predicted"],
                       paths["manifest"],Path(root)/"report")


class HoldoutModelDiagnosticTests(unittest.TestCase):
    def test_dry_tuber_descriptive_group_error_never_counts_plot_repeats_as_models(self):
        with tempfile.TemporaryDirectory() as td:
            r=sample_run(td)
            self.assertEqual(r["observed_plot_record_count_NOT_independent_sites"],8)
            self.assertEqual(r["unique_physical_plot_count"],8)
            self.assertEqual(r["compared_group_means_count"],4)
            self.assertEqual(r["site_year_groups_count"],2)
            self.assertEqual(r["plot_group_mae_rmse_descriptive_only"]["rmse_dry_kg_ha"],15)
            self.assertEqual(r["plot_group_mae_rmse_descriptive_only"][
                "signed_bias_model_minus_observed_dry_kg_ha"],15)
            self.assertFalse(r["real_external_field_validation_completed"])
            self.assertEqual(r["source_license"],"CC BY-NC-SA 4.0")
            output=(Path(td)/"report/descriptive_holdout_diagnostic.json").read_text()
            self.assertNotIn(PLOT_MARKER,output)
            self.assertNotIn("FAKE-CULTIVAR-A",output)
            self.assertNotIn("90.0",output)

    def test_duplicate_plot_date_fails_without_pseudoreplication(self):
        with tempfile.TemporaryDirectory() as td:
            def dup(o,p,m):o.append(dict(o[0]))
            with self.assertRaisesRegex(ValueError,"Repeated plot and date"):
                sample_run(td,dup)

    def test_same_physical_plot_cannot_belong_to_two_cultivars(self):
        with tempfile.TemporaryDirectory() as td:
            def collision(o,p,m):
                o[2]["plot_id"]=o[0]["plot_id"]
            with self.assertRaisesRegex(ValueError,"Physical plot assigned"):
                sample_run(td,collision)

    def test_no_training_evaluation_campaign_overlap(self):
        with tempfile.TemporaryDirectory() as td:
            def overlap(o,p,m):m["calibration_years"]=[2019,2020]
            with self.assertRaisesRegex(ValueError,"overlap"):
                sample_run(td,overlap)

    def test_evaluation_file_cannot_contain_training_data(self):
        with tempfile.TemporaryDirectory() as td:
            def leaks(o,p,m):o[0]["year"]="2019"
            with self.assertRaisesRegex(ValueError,"outside declared heldout"):
                sample_run(td,leaks)

    def test_no_unexplained_fresh_to_dry_conversion(self):
        with tempfile.TemporaryDirectory() as td:
            def wrong(o,p,m):o[0]["unit"]="kg_fresh_tuber_per_ha"
            with self.assertRaisesRegex(ValueError,"dry tuber"):
                sample_run(td,wrong)

    def test_generic_potato_parameters_cannot_be_relabelled_cultivar_specific(self):
        with tempfile.TemporaryDirectory() as td:
            def generic(o,p,m):p[0]["model_cultivar_id"]="Potato_701"
            with self.assertRaisesRegex(ValueError,"Generic or mismatched cultivar"):
                sample_run(td,generic)

    def test_missing_prediction_is_not_imputed(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError,"Missing or extra"):
                sample_run(td,lambda o,p,m:p.pop())

    def test_duplicate_model_prediction_is_not_independent(self):
        with tempfile.TemporaryDirectory() as td:
            def duplicate(o,p,m):p.append(dict(p[0]))
            with self.assertRaisesRegex(ValueError,"More than one"):
                sample_run(td,duplicate)

    def test_nonfinite_and_negative_measurements_fail(self):
        for value in ("NaN","-5","inf"):
            with self.subTest(value=value),tempfile.TemporaryDirectory() as td:
                def bad(o,p,m):o[0]["observed_value"]=value
                with self.assertRaisesRegex(ValueError,"nonfinite/negative"):
                    sample_run(td,bad)

    def test_wrong_source_licence_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            def lic(o,p,m):m["source_license"]="CC0"
            with self.assertRaisesRegex(ValueError,"Source DOI, license"):
                sample_run(td,lic)

    def test_missing_weather_sha_in_predictions_fails(self):
        with tempfile.TemporaryDirectory() as td:
            def unknown(o,p,m):p[0]["source_weather_sha256"]="missing"
            with self.assertRaisesRegex(ValueError,"SHA256"):
                sample_run(td,unknown)

    def test_2019_2020_holdout_selection_alone_is_not_external_validation(self):
        with tempfile.TemporaryDirectory() as td:
            r=sample_run(td)
            self.assertEqual(r["calibration_campaigns_declared"],["2019"])
            self.assertEqual(r["heldout_campaigns_declared"],["2020"])
            self.assertEqual(r["status"],mod.STATUS)
            self.assertIn("NOT_EXTERNAL",r["status"])
            self.assertFalse(r["independent_review_of_soil_weather_irrigation_declared_but_not_verified"])


if __name__=="__main__":
    unittest.main()

"""M1-19: conservative dry-tuber heldout comparison contract (LOCAL files).

Prediction and observation MUST match at (trial,site,campaign,cultivar,
management,date,trait), unit kg dry storage organ/ha. Predicted WOFOST
values are GROUP level, not separate biological plot observations. Aggregate
observed plot measurements ONCE per group; report DESCRIPTIVE error only.
No external validity from site-year reuse, leaks, or synthetic fixtures.

Never publish raw licensed potato plot records; output only error summaries
with original CC BY-NC-SA restrictions inherited.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from datetime import date
from pathlib import Path

SOURCE_DOI="10.7910/DVN/1LC6W7"
SOURCE_SHA="8d129262dca38ac98a10f92ccfb1bc46454377020575959fd984c4c5bcab5768"
LICENSE="CC BY-NC-SA 4.0"
TRAIT="tuber_storage_dry_biomass"
UNIT="kg_dry_tuber_per_ha"
STATUS="DESCRIPTIVE_HOLDOUT_DIAGNOSTIC_NOT_EXTERNAL_MODEL_VALIDATION"
OBS_FIELDS={
    "trial_id","site_id","year","plot_id","cultivar_id","management_id",
    "observation_date","trait","unit","observed_value",
}
PRED_FIELDS={
    "trial_id","site_id","year","cultivar_id","management_id",
    "observation_date","trait","unit","predicted_value",
    "model_name","model_cultivar_id","model_config_sha256",
    "source_weather_sha256",
}
KEY_FIELDS=(
    "trial_id","site_id","year","cultivar_id","management_id",
    "observation_date","trait","unit",
)


def sha256(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path,expected,name):
    with Path(path).open(newline="",encoding="utf-8-sig") as f:
        rdr=csv.DictReader(f)
        if not rdr.fieldnames or len(rdr.fieldnames)!=len(set(rdr.fieldnames)) or (
            set(rdr.fieldnames)!=expected
        ):
            raise ValueError(f"{name}: strict CSV source fields or duplicate headers")
        rows=list(rdr)
    if not rows:raise ValueError(f"{name}: empty source")
    for r in rows:
        if None in r or any(v is None or v.strip()=="" for v in r.values()):
            raise ValueError(f"{name}: missing source field or malformed row")
    return rows


def parse_value(raw,name):
    try:
        x=float(raw)
    except ValueError:
        raise ValueError(f"{name}: observation/model amount not a number") from None
    if not math.isfinite(x) or x<0:
        raise ValueError(f"{name}: nonfinite/negative tuber dry mass")
    return x


def observed_key(row):
    return tuple(row[x] for x in KEY_FIELDS)


def check_row(row,name):
    if row["trait"]!=TRAIT or row["unit"]!=UNIT:
        raise ValueError(f"{name}: unit is not measured dry tuber kg/ha; no implicit conversion")
    try:
        date.fromisoformat(row["observation_date"])
    except ValueError:
        raise ValueError(f"{name}: observation date not ISO") from None
    try:
        if not (1980<=int(row["year"])<=2100):
            raise ValueError
    except ValueError:
        raise ValueError(f"{name}: invalid model year") from None


def validate_manifest(manifest):
    expected={
        "source_doi","source_sha256","source_license","source_version",
        "calibration_years","heldout_evaluation_years",
        "split_locked_before_model_tuning",
        "prediction_generated_without_evaluation_yields",
        "irrigation_soil_weather_provenance_independently_reviewed",
    }
    if set(manifest)!=expected:raise ValueError("Incorrect split/source protocol schema")
    if (manifest["source_doi"]!=SOURCE_DOI or manifest["source_sha256"]!=SOURCE_SHA
        or manifest["source_license"]!=LICENSE or manifest["source_version"]!="3.0"):
        raise ValueError("Source DOI, license or original SHA-256 not the verified WUR dataset")
    train=set(map(str,manifest["calibration_years"]))
    heldout=set(map(str,manifest["heldout_evaluation_years"]))
    if not train or not heldout or train&heldout:
        raise ValueError("Training/evaluation campaigns overlap or are absent")
    if not manifest["split_locked_before_model_tuning"]:
        raise ValueError("Evaluation split is not declared prelocked")
    if not manifest["prediction_generated_without_evaluation_yields"]:
        raise ValueError("Predictions contaminated with evaluation labels")
    # Even a declaration does not PROVE independent data/model quality.
    return train,heldout


def metrics(differences):
    if not differences:raise ValueError("No valid paired observations")
    n=len(differences)
    return {
        "n_group_mean_pairs_not_independent_field_trials":n,
        "mae_dry_kg_ha":round(sum(abs(x) for x in differences)/n,6),
        "rmse_dry_kg_ha":round(math.sqrt(sum(x*x for x in differences)/n),6),
        "signed_bias_model_minus_observed_dry_kg_ha":round(sum(differences)/n,6),
    }


def compare(observed_path,predicted_path,manifest_path,out):
    obs=read(observed_path,OBS_FIELDS,"observed")
    pred=read(predicted_path,PRED_FIELDS,"predictions")
    manifest=json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    training,heldout=validate_manifest(manifest)
    groups=defaultdict(list)
    owners={}
    plot_samples=set()
    for row in obs:
        check_row(row,"observed")
        if row["year"] not in heldout:
            raise ValueError("Observed evaluation row outside declared heldout campaigns")
        physical=(row["trial_id"],row["site_id"],row["year"],row["plot_id"])
        owner=(row["cultivar_id"],row["management_id"])
        if physical in owners and owners[physical]!=owner:
            raise ValueError("Physical plot assigned to multiple cultivars or managements")
        owners[physical]=owner
        key=observed_key(row)
        record=physical+(row["observation_date"],)
        if record in plot_samples:
            raise ValueError("Repeated plot and date interpreted as independent biological replicate")
        plot_samples.add(record)
        groups[key].append(parse_value(row["observed_value"],"observed"))
    model={}
    model_versions=set()
    for row in pred:
        check_row(row,"prediction")
        if row["year"] not in heldout:
            raise ValueError("Prediction outside declared heldout campaigns")
        if row["model_cultivar_id"]!=row["cultivar_id"]:
            raise ValueError("Generic or mismatched cultivar model cannot count as validation")
        for field in ("model_config_sha256","source_weather_sha256"):
            value=row[field]
            if len(value)!=64 or any(c not in "0123456789abcdef" for c in value):
                raise ValueError("Missing valid code/weather SHA256 in prediction")
        if row["model_name"]!="Wofost81_WLP_CWB" and row["model_name"]!="Wofost81_PP":
            raise ValueError("Unregistered prediction model")
        key=observed_key(row)
        if key in model:
            raise ValueError("More than one model prediction per observed group")
        model[key]=parse_value(row["predicted_value"],"predicted")
        model_versions.add((row["model_config_sha256"],row["model_name"]))
    if set(model)!=set(groups):
        raise ValueError("Missing or extra model predictions: no imputation or fuzzy joining")
    if len(model_versions)!=1:
        raise ValueError("Mixed model configurations in an evaluation report")
    diffs=[]
    by_siteyear=defaultdict(list)
    biological_plots=0
    for key,observed in groups.items():
        biological_plots+=len(observed)
        # ONE model prediction compared to the mean of independently identified
        # plot replicates, NOT a separate prediction for each plot.
        group_difference=model[key]-sum(observed)/len(observed)
        diffs.append(group_difference)
        by_siteyear[(key[1],key[2])].append(group_difference)
    # Diagnostic environment mean errors; NOT independent across sites/years.
    env_diffs=[sum(errors)/len(errors) for errors in by_siteyear.values()]
    all_m=metrics(diffs)
    env_m=metrics(env_diffs)
    report={
        "status":STATUS,
        "real_external_field_validation_completed":False,
        "source_doi":SOURCE_DOI,
        "source_version":"3.0","source_license":LICENSE,
        "derivative_reuse":"CC BY-NC-SA 4.0, original attribution and noncommercial/SA restrictions",
        "source_file_sha256":SOURCE_SHA,
        "local_normalized_observations_sha256":sha256(observed_path),
        "local_model_predictions_sha256":sha256(predicted_path),
        "local_evaluation_protocol_sha256":sha256(manifest_path),
        "modeled_trait":TRAIT,"measured_unit":UNIT,
        "calibration_campaigns_declared":sorted(training),
        "heldout_campaigns_declared":sorted(heldout),
        "observed_plot_record_count_NOT_independent_sites":len(obs),
        "unique_physical_plot_count":len(owners),
        "compared_group_means_count":len(groups),
        "site_year_groups_count":len(by_siteyear),
        "plot_group_mae_rmse_descriptive_only":all_m,
        "site_year_mean_bias_mae_rmse_descriptive_only":env_m,
        "independent_review_of_soil_weather_irrigation_declared_but_not_verified":bool(
            manifest["irrigation_soil_weather_provenance_independently_reviewed"]),
        "not_external_validation_reasons":[
            "Source values are normalized externally; raw source mapping/units need human audit.",
            "Declared prelock/model fitting input independence is not independently verifiable by this script.",
            "Groups and site-years are correlated; descriptive RMSE is not inference or independent field-trial replication.",
            "Only dry tuber biomass can be compared; fresh yields require measured dry matter and provenance.",
            "WOFOST generic Potato_701 must NOT be silently relabeled as a studied Dutch cultivar.",
            "All user-supplied model soil/weather/management assumptions still need field validation.",
            "No original CC BY-NC-SA potato rows are published by this utility.",
            "No nutritional Fe/Zn or safety inference.",
        ],
    }
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    (out/"descriptive_holdout_diagnostic.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--observed",required=True,type=Path)
    parser.add_argument("--predicted",required=True,type=Path)
    parser.add_argument("--manifest",required=True,type=Path)
    parser.add_argument("--out",required=True,type=Path)
    a=parser.parse_args()
    r=compare(a.observed,a.predicted,a.manifest,a.out)
    print(json.dumps({
        "status":r["status"],"group_means":r["compared_group_means_count"],
        "site_year_groups":r["site_year_groups_count"],"dry_rmse":r[
            "plot_group_mae_rmse_descriptive_only"]["rmse_dry_kg_ha"],
    },ensure_ascii=False))


if __name__=="__main__":
    main()

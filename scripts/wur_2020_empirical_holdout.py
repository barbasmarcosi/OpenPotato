"""M1-20: real 2020 out-of-year prediction BASELINE, NOT WOFOST calibration.

Process byte-verified WUR potato trials under CC BY-NC-SA 4.0. The **only**
predictor is the site x cultivar mean dry tuber biomass on the final sampled
date in 2019; its predictions are evaluated on the same site x cultivar in
2020. A site-only naive comparator uses the 2019 site mean.

This IS a genuine out-of-year empirical benchmark on 2020 field outcomes,
NOT evidence that WOFOST predicts harvests. Do not publish individual plot
rows, plot identifiers, raw tuber masses, cultivar group means or predictions.

No field WOFOST simulation is run here. Field conditions, harvest status,
management differences and same-location temporal dependence are unresolved.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import statistics
from collections import defaultdict
from datetime import date
from pathlib import Path

from scripts import wur_potato_field_audit as source

TRAIN = "2019"
EVALUATION = "2020"
SITES = ("L", "V")
CULTIVARS_BY_SITE = {
    "L": ("C1", "C2", "C3"),
    "V": ("C4", "C5", "C6"),
}
EXPECTED_PLOTS_PER_SITE = {"L": 45, "V": 42}
STATUS = "REAL_WUR_2020_HOLDOUT_EMPIRICAL_BASELINE_NOT_WOFOST_VALIDATION"
CITATION = "https://doi.org/10.7910/DVN/1LC6W7"
MISSING = {"", "NA", "NAN", "NULL"}


def observed_final_rows(rows, counts=EXPECTED_PLOTS_PER_SITE, strict=True):
    """Select last source measurement date per site x year, not 'verified harvest'.

    Each plot must exist on that date with one finite dry value and a stable
    original cultivar, nitrogen and irrigation assignment across all dates.
    These last samples may not be commercially representative final harvests.
    """
    histories = defaultdict(list)
    dates_by_group = defaultdict(set)
    seen = set()
    for r in rows:
        if any(k not in r or r[k] is None for k in (
            "Year", "Date", "Location", "Plotnumber",
            "Cultivar", "Nitrogen", "Irrigation", "tubersDW")):
            raise ValueError("Missing required WUR plot/date/dry biomass source columns")
        year, site = r["Year"].strip(), r["Location"].strip()
        if year not in (TRAIN, EVALUATION) or site not in SITES:
            raise ValueError("Unexpected site/year; fail closed on incomplete study domain")
        try:
            day = date.fromisoformat(r["Date"].strip())
        except ValueError:
            raise ValueError("Invalid observed ISO field date") from None
        if day.year != int(year):
            raise ValueError("Observed field date does not match season label")
        plot = r["Plotnumber"].strip()
        cultivar = r["Cultivar"].strip()
        nitrogen = r["Nitrogen"].strip()
        irrigation = r["Irrigation"].strip()
        if not all((plot, cultivar, nitrogen, irrigation)):
            raise ValueError("Incomplete identity or treatment in original row")
        if cultivar not in CULTIVARS_BY_SITE[site]:
            raise ValueError("Unexpected cultivar codes for site")
        key = (year, site, plot)
        record = (key, day)
        if record in seen:
            raise ValueError("Repeated physical plot/date must not form duplicate biology")
        seen.add(record)
        histories[key].append((day, cultivar, nitrogen, irrigation, r["tubersDW"].strip()))
        dates_by_group[(year, site)].add(day)
    expected_groups = {(y, s) for y in (TRAIN, EVALUATION) for s in SITES}
    if set(dates_by_group) != expected_groups:
        raise ValueError("Required 2019 and 2020 calibration/holdout site-years absent")
    last_dates = {key: max(days) for key, days in dates_by_group.items()}
    selected = defaultdict(list)
    for (year, site, plot), observations in histories.items():
        ownership = {(c, n, w) for d, c, n, w, v in observations}
        if len(ownership) != 1:
            raise ValueError("Original physical plot changes cultivar or treatment between dates")
        latest = [r for r in observations if r[0] == last_dates[(year, site)]]
        if len(latest) != 1:
            raise ValueError("Physical plot missing on final observed field date")
        when, cultivar, nitrogen, irrigation, raw = latest[0]
        if raw.upper() in MISSING:
            raise ValueError("Missing dry tuber observation on terminal observation date")
        value = source.parse_numeric(raw)
        if value is None or value <= 0:
            raise ValueError("Dry storage biomass must be positive and finite on terminal date")
        selected[(year, site, cultivar)].append(value)
    for year,site in expected_groups:
        n=sum(len(selected.get((year,site,c),[])) for c in CULTIVARS_BY_SITE[site])
        if strict and n != counts[site]:
            raise ValueError("Observed final physical plot coverage does not match original")
        if n < len(CULTIVARS_BY_SITE[site]) * 2:
            raise ValueError("Too few plot replicates for descriptive group benchmark")
    if strict and len(histories)!=2*sum(counts.values()):
        raise ValueError("Unexpected unique plot identity count")
    # Return only group value arrays INSIDE process, never as user artifacts.
    return selected, last_dates, len(histories)


def _scores(error):
    if not error: raise ValueError("No held-out comparisons")
    return {
        "mae_kg_dry_ha": round(statistics.mean(abs(v) for v in error), 6),
        "rmse_kg_dry_ha": round(math.sqrt(statistics.mean(v*v for v in error)), 6),
        "bias_predicted_minus_observed_kg_dry_ha": round(statistics.mean(error), 6),
    }


def benchmark(rows, strict=True, counts=EXPECTED_PLOTS_PER_SITE):
    selected, dates, unique_physical = observed_final_rows(
        rows,counts=counts,strict=strict)
    comparison = {}
    for site in SITES:
        train = [v for cultivar in CULTIVARS_BY_SITE[site]
                 for v in selected[TRAIN,site,cultivar]]
        if not train: raise ValueError("No calibration records in declared year")
        for cultivar in CULTIVARS_BY_SITE[site]:
            a=selected[TRAIN,site,cultivar]
            b=selected[EVALUATION,site,cultivar]
            if len(a)<2 or len(b)<2:
                raise ValueError("Missing cultivar-level independent physical plots in split")
            comparison[site,cultivar]={
                "train_n":len(a),"test_n":len(b),
                "site_cultivar_mean_prediction":statistics.mean(a),
                "site_only_mean_prediction":statistics.mean(train),
                "heldout_mean":statistics.mean(b),
            }
    if len(comparison)!=6: raise ValueError("Expected 6 exact site-cultivar heldout groups")
    ordered=[comparison[key] for key in sorted(comparison)]
    site_cultivar_errors=[p["site_cultivar_mean_prediction"]-p["heldout_mean"] for p in ordered]
    site_only_errors=[p["site_only_mean_prediction"]-p["heldout_mean"] for p in ordered]
    if any(not math.isfinite(v) for v in site_cultivar_errors+site_only_errors):
        raise ValueError("Nonfinite observed baseline error")
    assert sum(x["train_n"] for x in ordered) == sum(counts.values()) if strict else True
    assert sum(x["test_n"] for x in ordered) == sum(counts.values()) if strict else True
    return {
        "status":STATUS,
        "evidence_level":"REAL_OBSERVED_FIELD_OUTCOMES_2020; EMPIRICAL_2019_BASELINE_NOT_WOFOST",
        "source_doi":source.DOI,
        "source_version":source.VERSION,
        "source_csv_sha256":source.SOURCE_SHA256 if strict else "SYNTHETIC_TEST_DATA_ONLY",
        "source_license":source.LICENSE,
        "source_license_uri":"https://creativecommons.org/licenses/by-nc-sa/4.0/",
        "derivative_reuse":"Attribution to authors; CC BY-NC-SA 4.0; noncommercial/sharealike",
        "original_plot_values_exported":False,
        "original_plot_ids_exported":False,
        "original_cultivar_group_means_exported":False,
        "training_year":"2019",
        "completely_reserved_evaluation_year":"2020",
        "training_data_used_only_for_predictions":True,
        "holdout_model_was_not_tuned_on_2020":True,
        "predicted_field_trait":"tuber dry storage biomass (published tubersDW) kg/ha",
        "last_measured_date_is_NOT_verified_formal_harvest":True,
        "last_sample_day_by_site_year":{
            (source.SITE_NAMES[s]+" "+y):dates[y,s].isoformat()
            for (y,s) in sorted(dates)},
        "total_original_distinct_physical_plots_site_year":unique_physical,
        "training_unique_physical_plots":sum(x["train_n"] for x in ordered),
        "heldout_unique_physical_plots":sum(x["test_n"] for x in ordered),
        "heldout_group_means_not_independent_site_years":len(comparison),
        "distinct_heldout_sites":len(SITES),
        "different_independent_evaluation_years":1,
        "2019_site_by_cultivar_empirical_persistence":_scores(site_cultivar_errors),
        "2019_site_only_empirical_persistence":_scores(site_only_errors),
        "no_wofost_predictions_or_calibration":True,
        "no_external_validation_claim":True,
        "limits":[
            "These are ACTUAL observed 2020 outcomes versus a simple 2019 observational predictor, NOT WOFOST validation.",
            "Last positive tubersDW per plot on last sampling day does not establish commercial harvest equivalence.",
            "Six site/cultivar group means in just two sites and ONE evaluation year are correlated, not independent experiments.",
            "2019/2020 cultivar codes may encode different fields/varieties; no cultivar genetics are inferred.",
            "Irrigation and N treatment classes vary within groups; using 2019 group means conflates changing management/weather.",
            "The first empirical baseline does not use 2019/2020 weather, management, soil or calibrated crop coefficients.",
            "The 2019/2020 country/site cannot be joined to Argentina 2022-2024 WOFOST outputs.",
            "Descriptive errors use six heldout group MEANS rather than 2020 plots treated as independent models.",
            "Original CC BY-NC-SA data and 2020 group means, cultivar-specific values, plot IDs are not republished.",
            "No dry mass to fresh commercial yield conversion, Fe/Zn, safety or bioavailability.",
        ],
    }


def evaluate_original(source_csv: Path, out: Path):
    # This call enforces both SOURCE SHA-256 and row/trait coverage. It aborts
    # if any upstream original changes before a release can take place.
    blob=Path(source_csv).read_bytes()
    source.inspect_original(blob)
    rows=list(csv.DictReader(io.StringIO(blob.decode("utf-8-sig"))))
    report=benchmark(rows)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    (out/"wur_2020_true_holdout_empirical_baselines.json").write_text(
        json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+"\n",
        encoding="utf-8")
    lines=[
        "# M1-20 — Primer benchmark predictivo REAL con observaciones 2020",
        "",
        "**No es WOFOST. NO se calibró ninguna variedad ni se predijo Fe/Zn.**",
        "",
        "Fuente: ten Den et al. (2024), Harvard Dataverse v3.0.",
        "DOI https://doi.org/10.7910/DVN/1LC6W7",
        "**CC BY-NC-SA 4.0: atribución, uso no comercial y compartir igual.**",
        "",
        f"Entrenamiento observacional: {report['training_year']} con "
        f"{report['training_unique_physical_plots']} parcelas por sitio×año.",
        f"Evaluación temporal reservada: {report['completely_reserved_evaluation_year']} con "
        f"{report['heldout_unique_physical_plots']} parcelas por sitio×año.",
        "Unidades: kg/ha de tubérculo SECO observado; el último muestreo no prueba cosecha comercial.",
        "",
        "| Baseline empírico sobre 6 medias sitio×cultivar | MAE kg seco/ha | RMSE kg seco/ha | Sesgo predicho−observado kg seco/ha |",
        "|---|---:|---:|---:|",
    ]
    for key, label in (
        ("2019_site_only_empirical_persistence","Media 2019 por sitio"),
        ("2019_site_by_cultivar_empirical_persistence","Media 2019 por sitio y cultivar"),
    ):
        m=report[key]
        lines.append(
            f"| {label} | {m['mae_kg_dry_ha']:.2f} | "
            f"{m['rmse_kg_dry_ha']:.2f} | "
            f"{m['bias_predicted_minus_observed_kg_dry_ha']:.2f} |")
    lines+=["","**Este error sí es contra biomasa observada real de 2020**,",
            "pero procede de promedios empíricos de 2019; NO de WOFOST ni simulaciones agronómicas.",
            "Seis medias no son seis ensayos independientes; comparten dos sitios y una campaña reservada.",
            "No se publican datos originales, rendimientos individuales ni valores por cultivar.",
            "Los parámetros de WOFOST para cultivares y suelos de Países Bajos siguen pendientes."]
    (out/"wur_2020_true_holdout_empirical_baselines.md").write_text(
        "\n".join(lines)+"\n",encoding="utf-8")
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    result=evaluate_original(args.source,args.out)
    print(json.dumps({
        "status":result["status"],
        "train_plots":result["training_unique_physical_plots"],
        "heldout_plots":result["heldout_unique_physical_plots"],
        "compared_group_means":result["heldout_group_means_not_independent_site_years"],
        "no_wofost_validation":result["no_wofost_predictions_or_calibration"],
    },ensure_ascii=False))


if __name__=="__main__":
    main()

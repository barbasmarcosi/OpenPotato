"""M1-19: byte-verified Dutch potato OBSERVATIONS; publish SCHEMA/COUNTS ONLY.

Original 2019-2020 WUR/Harvard Dataverse v3.0: CC BY-NC-SA 4.0.
No original records, plot IDs, yield values, rainfall series or field-level
observations are exported from this audit. Not a calibrated WOFOST validation.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

DOI="10.7910/DVN/1LC6W7"
VERSION="3.0"
LICENSE="CC BY-NC-SA 4.0"
SOURCE_FILE_ID=10850227
SOURCE_FILENAME="Plotspecific_processed.csv"
SOURCE_MD5="bdf0f745e2c496868e3285a43df0ff04"
SOURCE_SHA256="8d129262dca38ac98a10f92ccfb1bc46454377020575959fd984c4c5bcab5768"
REFERENCE_META_SHA256="b6bada9e4d9352e2975dbf1159299b114369a36598aa924b3222fa5ce101945c"
REFERENCE_META_ID=10850226
EXPECTED_ROWS=1824
SITE_YEAR_EXPECTED={("2019","L"):495,("2019","V"):504,
                    ("2020","L"):405,("2020","V"):420}
REQUIRED={
    "Year","Date","Location","Plotnumber","Cultivar","Nitrogen","Irrigation",
    "Yield_gross_t.ha","FWyield","tubersFW","tubersDW","tuberDMpercentage","LAI",
}
MEASUREMENTS={"tubersDW":"kg_dry_tuber_per_ha",
              "tubersFW":"kg_fresh_tuber_per_ha",
              "tuberDMpercentage":"percent_tuber_dry_matter",
              "Yield_gross_t.ha":"tonnes_fresh_per_ha_gross_yield",
              "FWyield":"tonnes_fresh_per_ha",
              "LAI":"dimensionless_leaf_area_index"}
EXPECTED_NUMERIC={"tubersDW":1048,"tubersFW":1063,
                  "tuberDMpercentage":454,
                  "Yield_gross_t.ha":87,"FWyield":1063,"LAI":996}
SITE_NAMES={"L":"Lelystad","V":"Vredepeel"}


def digest_bytes(data:bytes)->tuple[str,str]:
    return hashlib.md5(data).hexdigest(),hashlib.sha256(data).hexdigest()


def parse_numeric(value:str):
    value=value.strip()
    if value.upper() in {"","NA","NAN","NULL"}:
        return None
    try:
        n=float(value)
    except ValueError:
        raise ValueError("Unparseable numeric source field in published trial") from None
    if not math.isfinite(n):
        raise ValueError("Nonfinite measured value in published trial")
    if n < 0:
        raise ValueError("Negative numeric measured value requires source review")
    return n


def inspect_original(blob:bytes,*,expected_md5=SOURCE_MD5,expected_sha256=SOURCE_SHA256):
    md5,sha256=digest_bytes(blob)
    if md5!=expected_md5 or sha256!=expected_sha256:
        raise ValueError("WUR source file checksum changed; manual re-verification required")
    try:
        text=blob.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise ValueError("Published source text encoding changed") from None
    reader=csv.DictReader(text.splitlines())
    header=reader.fieldnames
    if not header or len(set(header))!=len(header) or not REQUIRED.issubset(set(header)):
        raise ValueError("Source required fields missing or duplicate CSV header")
    observed=Counter()
    combos=Counter()
    plots_by_siteyear:dict[tuple[str,str],set[str]]=defaultdict(set)
    plot_dates=defaultdict(set)
    rows=0
    for r in reader:
        rows+=1
        if None in r or any(v is None for v in r.values()):
            raise ValueError("Malformed source row")
        year,site=r["Year"].strip(),r["Location"].strip()
        if (year,site) not in SITE_YEAR_EXPECTED:
            raise ValueError("Unexpected source trial-year/site group")
        combos[(year,site)]+=1
        plot=r["Plotnumber"].strip()
        if not plot:
            raise ValueError("Missing original plot identity")
        plots_by_siteyear[(year,site)].add(plot)
        when=r["Date"].strip()
        if not when:raise ValueError("Missing observation date")
        plot_dates[(year,site,plot)].add(when)
        for col in MEASUREMENTS:
            if parse_numeric(r[col]) is not None:
                observed[col]+=1
    if rows!=EXPECTED_ROWS or combos!=SITE_YEAR_EXPECTED:
        raise ValueError("Unexpected original row count or site-year balance")
    if dict(observed)!=EXPECTED_NUMERIC:
        raise ValueError("Measured coverage changed; inspect source before updating")
    report={
        "status":"REAL_FIELD_SOURCE_STRUCTURE_VERIFIED_NOT_WOFOST_CALIBRATION",
        "doi":DOI,"source_dataset_version":VERSION,
        "original_file_id":SOURCE_FILE_ID,"source_file_name":SOURCE_FILENAME,
        "source_md5":md5,"source_sha256":sha256,
        "license":LICENSE,"license_uri":"https://creativecommons.org/licenses/by-nc-sa/4.0/",
        "noncommercial_and_sharealike_restrictions_apply":True,
        "total_original_rows_inspected_without_export":rows,
        "column_count":len(header),
        "year_site_counts":[{"year":year,"site":SITE_NAMES[site],"row_count":n,
                             "distinct_original_plot_identifiers_count":len(plots_by_siteyear[(year,site)])}
                            for (year,site),n in sorted(combos.items())],
        "measurements_available":[
            {"original_column":col,"source_dictionary_unit":unit,
             "finite_numeric_entries":observed[col],
             "non_numeric_or_missing_entries":rows-observed[col]}
            for col,unit in MEASUREMENTS.items()],
        "source_variable_dictionary_file_id":REFERENCE_META_ID,
        "source_variable_dictionary_sha256":REFERENCE_META_SHA256,
        "source_variable_definition_unambiguous_for_tubersDW":"kg/ha, dry weight of the tubers",
        "plot_dates_detected_as_raw_strings_only":True,
        "observation_rows_exported":0,
        "source_yield_values_exported":0,
        "stage":"ADMISSION_GATE_ONLY",
        "important_limits":[
            "1824 source rows are observations collected on various dates, NOT independent harvests.",
            "A tubersDW cell is numerically parseable but harvest-date matching still must be verified.",
            "All numeric availability counts exclude literal NA, NaN, NULL and blank values.",
            "Source license is CC BY-NC-SA 4.0, not CC0 or unrestricted commercial rights.",
            "Comparing these Dutch 2019-2020 observations to Argentinian 2022-2024 modeled weather would be invalid.",
            "Published original site soil/weather/irrigation and real variety coefficients require harmonization.",
            "No Fe or Zn measurements and no nutrition claim may be inferred.",
            "No real model error, predictive accuracy or external validation computed here.",
            "No original row data or plot IDs or individual yields are retained in public derivatives.",
        ],
    }
    return report


def audit_file(source:Path,out:Path):
    report=inspect_original(Path(source).read_bytes())
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    (out/"wur_2019_2020_real_trial_source_admission.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    lines=[
        "# M1-19 — Datos agronómicos observados de papa: admisión documental",
        "",
        "**Fuente real auditada, pero NO calibración ni validación de WOFOST.**",
        f"ten Den et al. (2024), Harvard Dataverse v{VERSION},",
        f"DOI: https://doi.org/{DOI}",
        "",
        "**Licencia original CC BY-NC-SA 4.0: atribución, uso no comercial y compartir igual.**",
        "No se publicaron filas, identificadores individuales ni concentraciones/producciones.",
        "",
        f"- {rows_text(report)}",
        "- Comparaciones nacionales/campañas previas M1-16-18 NO emparejables.",
        "- Un modelo de papa genérica no equivale a cultivar medido.",
        "",
        "| Variable observada | Unidad del diccionario original | Valores numéricos válidos |",
        "|---|---|---:|",
    ]
    for d in report["measurements_available"]:
        lines.append(f"| {d['original_column']} | {d['source_dictionary_unit']} | {d['finite_numeric_entries']} |")
    lines.extend(["", "Los recuentos no son parcelas independientes ni finales de cosecha.",
                  "Para contrastar modelos es obligatorio unir año, lugar, cultivar, tratamiento,",
                  "fecha/estadío, parcela biológica y unidad de peso SECO, sin fuga entre años.",
                  "No se derivan valores de hierro, zinc, rentabilidad o inocuidad."])
    (out/"wur_2019_2020_real_trial_source_admission.md").write_text(
        "\n".join(lines)+"\n",encoding="utf-8")
    return report


def rows_text(report):
    return (f"{report['total_original_rows_inspected_without_export']} filas "
            f"originales revisadas en {len(report['year_site_counts'])} grupos "
            "sitio × campaña; sin redistribuir el CSV original.")


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    report=audit_file(args.source,args.out)
    print(json.dumps({
        "status":report["status"],
        "records":report["total_original_rows_inspected_without_export"],
        "dry_weight_numeric_entries":next(x["finite_numeric_entries"]
            for x in report["measurements_available"] if x["original_column"]=="tubersDW"),
        "original_rows_exported":report["observation_rows_exported"],
    },ensure_ascii=False))


if __name__=="__main__":
    main()

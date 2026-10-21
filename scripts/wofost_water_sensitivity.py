"""M1-17: exploratory WOFOST 8.1 water-limited potato growth, NOT field yields.

Run PCSE Wofost81_WLP_CWB on the EXACT archived NASA POWER 2022-24 inputs.
The soil profiles, initial plant-available water, emergence/harvest dates,
generic Potato_701 cultivar, nutrient sufficiency and lack of irrigation are
explicitly hypothetical. No measured soil/management/phenotypes are inferred.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from datetime import date, timedelta
from pathlib import Path

from scripts import wofost_potato_nasa as base

MODEL = "Wofost81_WLP_CWB"
STATUS = "WOFOST_WATER_LIMITED_SCENARIO_ONLY_UNCALIBRATED"
SOIL_PROFILES = {
    # Units: volumetric water fractions, infiltration/percolation cm/day, root depth cm.
    # Exploratory synthetic contrasts, NOT soil descriptions from either locality.
    "coarse_assumed": {
        "SMW": 0.08, "SMFCF": 0.20, "SM0": 0.38, "CRAIRC": 0.06,
        "SOPE": 6.0, "KSUB": 6.0, "RDMSOL": 100.0,
    },
    "medium_assumed": {
        "SMW": 0.12, "SMFCF": 0.32, "SM0": 0.47, "CRAIRC": 0.06,
        "SOPE": 2.0, "KSUB": 2.0, "RDMSOL": 100.0,
    },
}
# WAV: cm of initial available water in TOTAL 100 cm profile (WOFOST definition).
# These are NOT measurements of a specific day or site.
INITIAL_AVAILABLE_WATER_CM = {"dry": 2.0, "intermediate": 10.0, "wet": 18.0}
COMMON_SITE = {
    "CO2": 410.0, "IFUNRN": 0, "NOTINF": 0.0,
    "SSMAX": 0.0, "SSI": 0.0,
}
EXPECTED_SCENARIOS = len(base.SITES)*len(base.CAMPAIGNS)*len(
    base.START_MONTH_DAYS)*len(SOIL_PROFILES)*len(INITIAL_AVAILABLE_WATER_CM)

HEADERS = [
    "scenario_id", "site_label", "campaign", "assumed_emergence",
    "assumed_harvest", "soil_profile_hypothetical", "initial_water_label",
    "initial_available_water_cm_assumed", "irrigation_mm_assumed",
    "water_limited_storage_dry_kg_ha", "potential_storage_dry_kg_ha",
    "water_limited_to_potential_ratio_descriptive", "days_simulated",
    "average_root_zone_moisture_m3_m3", "total_actual_transpiration_cm",
    "total_potential_transpiration_cm", "total_rainfall_cm",
    "weather_snapshot_sha256", "interpretation",
]
DAILY_HEADERS = [
    "scenario_id", "date", "days_after_emergence", "DVS",
    "SM_root_zone_m3_m3", "LAI",
    "actual_transpiration_cm_day", "potential_transpiration_cm_day",
    "storage_organ_dry_kg_ha", "water_stress_factor",
]


def validate_profile(profile, water_cm):
    expected = {"SMW","SMFCF","SM0","CRAIRC","SOPE","KSUB","RDMSOL"}
    if set(profile)!=expected:
        raise ValueError("Unexpected soil properties schema")
    if any(not isinstance(v,(int,float)) or not math.isfinite(v)
           for v in list(profile.values())+[water_cm]):
        raise ValueError("Nonfinite soil or water assumption")
    if not 0 < profile["SMW"] < profile["SMFCF"] < profile["SM0"] < 0.8:
        raise ValueError("Invalid soil wilting/field-capacity/saturation ordering")
    if not 0 <= profile["CRAIRC"] < profile["SM0"]-profile["SMFCF"]:
        raise ValueError("Unphysical soil critical air content")
    if any(profile[k]<=0 or profile[k]>30 for k in ("SOPE","KSUB")):
        raise ValueError("Soil hydraulic drainage parameter outside sensitivity envelope")
    if not 20 <= profile["RDMSOL"] <= 200:
        raise ValueError("Invalid rootable soil depth")
    available = (profile["SM0"]-profile["SMW"])*profile["RDMSOL"]
    if not 0 <= water_cm <= available:
        raise ValueError("Initial available water exceeds physical soil storage")


def validate_design():
    if len(SOIL_PROFILES)!=2 or len(INITIAL_AVAILABLE_WATER_CM)!=3:
        raise ValueError("Unexpected M1-17 preregistered scenario design")
    if len(set(INITIAL_AVAILABLE_WATER_CM.values()))!=3:
        raise ValueError("Duplicate initial water level")
    for p in SOIL_PROFILES.values():
        for w in INITIAL_AVAILABLE_WATER_CM.values():
            validate_profile(p,w)
    if set(COMMON_SITE)!={"CO2","IFUNRN","NOTINF","SSMAX","SSI"}:
        raise ValueError("Unapproved site assumptions")
    if COMMON_SITE["IFUNRN"]!=0 or COMMON_SITE["NOTINF"]!=0:
        raise ValueError("Rainfall-infiltration assumptions must be explicitly documented")
    return EXPECTED_SCENARIOS


def load_baseline(potential_csv, source_hashes):
    with Path(potential_csv).open(newline="",encoding="utf-8-sig") as f:
        rdr=csv.DictReader(f)
        rows=list(rdr)
    if len(rows)!=8 or not rows:
        raise ValueError("M1-16 potential baseline must contain 8 scenarios")
    result={}
    for r in rows:
        key=r["scenario_id"]
        if key in result or key.split("-")[0] not in ("trenque_lauquen","neuquen"):
            # site label itself has underscore; robustly match declared field.
            if key in result:
                raise ValueError("Duplicate potential baseline scenario")
        if r["interpretation"]!=base.STATUS or r["model"]!="Wofost81_PP" or (
            r["generic_variety"]!=base.VARIETY
        ) or r["weather_nasa_power_sha256"]!=source_hashes.get(r["site_label"]):
            raise ValueError("Potential baseline source/method mismatch")
        value=float(r["potential_storage_dry_kg_ha"])
        if not math.isfinite(value) or value<=0:
            raise ValueError("Bad potential dry biomass")
        result[key]=value
    expected={f"{site}-{year}-{m:02d}{d:02d}"
              for site in base.SITES for year in base.CAMPAIGNS
              for m,d in base.START_MONTH_DAYS}
    if set(result)!=expected:
        raise ValueError("Potential baseline scenarios not exact eight declared designs")
    return result


def run(weather_dir, baseline_csv, out):
    import pcse
    from pcse.base import ParameterProvider
    from pcse.input import NASAPowerWeatherDataProvider, YAMLCropDataProvider
    from pcse.models import Wofost81_WLP_CWB
    if pcse.__version__!=base.PCSE_VERSION:
        raise ValueError("Unreviewed PCSE version")
    validate_design()
    source,hashes=base.load_weather(weather_dir)
    baseline=load_baseline(baseline_csv,hashes)

    class ArchivedWeather(NASAPowerWeatherDataProvider):
        def __init__(self,latitude,longitude,snapshot):
            self.snapshot=snapshot
            super().__init__(latitude=latitude,longitude=longitude,force_update=True)
        def _query_NASAPower_server(self,latitude,longitude):
            return self.snapshot

    url=("https://raw.githubusercontent.com/ajwdewit/WOFOST_crop_parameters/"
         +base.CROP_COMMIT)
    crop=YAMLCropDataProvider(Wofost81_WLP_CWB,repository=url,force_reload=True)
    crop.set_active_crop(base.CROP,base.VARIETY)
    summary,daily=[],[]
    for site,(lat,lon) in base.SITES.items():
        weather=ArchivedWeather(lat,lon,source[site])
        if weather.first_date!=base.WEATHER_FIRST or weather.last_date!=base.WEATHER_LAST:
            raise ValueError("Archived NASA time window changed")
        for year in base.CAMPAIGNS:
            for month,day in base.START_MONTH_DAYS:
                start=date(year,month,day)
                harvest=date(year+1,*base.HARVEST_MONTH_DAY)
                for n in range((harvest-start).days+1):
                    weather(start+timedelta(days=n))
                base_id=f"{site}-{year}-{month:02d}{day:02d}"
                agro=[{start: {"CropCalendar": {
                    "crop_name":base.CROP,"variety_name":base.VARIETY,
                    "crop_start_date":start,"crop_start_type":"emergence",
                    "crop_end_date":harvest,"crop_end_type":"harvest",
                    "max_duration":200,
                },"TimedEvents":None,"StateEvents":None}}]
                for soil_name,soil in SOIL_PROFILES.items():
                    for water_label,wav in INITIAL_AVAILABLE_WATER_CM.items():
                        assumptions={**COMMON_SITE, "WAV":wav,
                                     "SMLIM":soil["SMFCF"]}
                        params=ParameterProvider(
                            cropdata=crop,soildata=dict(soil),sitedata=assumptions)
                        model=Wofost81_WLP_CWB(params,weather,agro)
                        model.run_till_terminate()
                        raw=model.get_summary_output()
                        records=model.get_output()
                        if not raw or not records:
                            raise ValueError("Missing WOFOST water-limited outputs")
                        final=raw[0]
                        storage=float(final["TWSO"])
                        if not math.isfinite(storage) or storage<0:
                            raise ValueError("Invalid WOFOST dry tuber biomass")
                        ratio=storage/baseline[base_id]
                        if not 0<=ratio<2:
                            raise ValueError("Out-of-range WLP/PP comparison; inspect assumptions")
                        identity=base_id+"-"+soil_name+"-"+water_label
                        def value(x):
                            if x is None: return ""
                            y=float(x)
                            return round(y,5) if math.isfinite(y) else ""
                        # RAIN/ET are cm/day in PCSE (POWER raw precipitation mm/day).
                        moistures=[float(r["SM"]) for r in records
                                   if r.get("SM") is not None]
                        if not moistures or any(not 0<=m<=soil["SM0"]+0.02 for m in moistures):
                            raise ValueError("Missing/unphysical root-zone volumetric moisture")
                        waterbalance=final
                        # Totals are WOFOST water-balance state variables (cm).
                        tra=value(waterbalance.get("WTRAT"))
                        rain=value(waterbalance.get("RAINT"))
                        summary.append({
                            "scenario_id": identity,
                            "site_label":site,"campaign":year,
                            "assumed_emergence":start.isoformat(),
                            "assumed_harvest":harvest.isoformat(),
                            "soil_profile_hypothetical":soil_name,
                            "initial_water_label":water_label,
                            "initial_available_water_cm_assumed":wav,
                            "irrigation_mm_assumed":0,
                            "water_limited_storage_dry_kg_ha":value(storage),
                            "potential_storage_dry_kg_ha":baseline[base_id],
                            "water_limited_to_potential_ratio_descriptive":value(ratio),
                            "days_simulated":len(records),
                            "average_root_zone_moisture_m3_m3":value(sum(moistures)/len(moistures)),
                            "total_actual_transpiration_cm":tra,
                            "total_potential_transpiration_cm":"",
                            "total_rainfall_cm":rain,
                            "weather_snapshot_sha256":hashes[site],
                            "interpretation":STATUS,
                        })
                        for rec in records:
                            daily.append({
                                "scenario_id":identity,
                                "date":rec["day"].isoformat(),
                                "days_after_emergence":(rec["day"]-start).days,
                                "DVS":value(rec.get("DVS")),"SM_root_zone_m3_m3":value(rec.get("SM")),
                                "LAI":value(rec.get("LAI")),
                                "actual_transpiration_cm_day":value(rec.get("TRA")),
                                "potential_transpiration_cm_day":value(rec.get("TRAMX")),
                                "storage_organ_dry_kg_ha":value(rec.get("WSO")),
                                "water_stress_factor":value(rec.get("RFTRA")),
                            })
    if len(summary)!=EXPECTED_SCENARIOS:
        raise ValueError("Scenario count changed")
    out=Path(out)
    out.mkdir(parents=True,exist_ok=True)
    hashes_derived={}
    for name,header,rows in [
        ("water_limited_scenarios.csv",HEADERS,summary),
        ("water_limited_daily.csv",DAILY_HEADERS,daily),
    ]:
        path=out/name
        with path.open("w",newline="",encoding="utf-8") as f:
            writer=csv.DictWriter(f,fieldnames=header)
            writer.writeheader()
            writer.writerows(rows)
        hashes_derived[name]=base.sha256(path)
    meta={
        "status":STATUS,"model":MODEL,"pcse_version":pcse.__version__,
        "crop_source_git_commit":base.CROP_COMMIT,"generic_variety":base.VARIETY,
        "weather_snapshot_sha256":hashes,
        "hypothetical_soil_profiles":SOIL_PROFILES,
        "initial_available_water_cm_assumed":INITIAL_AVAILABLE_WATER_CM,
        "other_assumed_site_parameters":COMMON_SITE,
        "no_irrigation":True,"nitrogen_unlimited":True,
        "not_real_soil_or_genotype_prediction":True,
        "simulated_scenarios":len(summary),"simulated_daily_rows":len(daily),
        "scenario_csv_sha256":hashes_derived,
        "potential_baseline_csv_sha256":base.sha256(Path(baseline_csv)),
        "disclaimers":[
            "All soil hydraulic parameters and initial moisture are invented sensitivity cases.",
            "Weather is archived gridded NASA POWER; not farm weather station data.",
            "WOFOST81_WLP_CWB models water limitation, but not nitrogen stress, disease or economic yield.",
            "Both model outputs TWSO represent DRY storage organ biomass kg/ha, not fresh potato harvest.",
            "No estimated Fe Zn bioavailability glycoalkaloids or experimental genotype effects.",
            "Do not infer cultivar/site irrigation recommendations or drought adaptation from these simulations.",
        ],
    }
    (out/"water_limited_provenance.json").write_text(
        json.dumps(meta,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")
    lines=[
        "# OP-M1-17 — WOFOST81 limitado por agua: sensibilidad NO calibrada",
        "",
        "**Datos NASA POWER auténticos; parámetros de suelo y humedad inicial INVENTADOS.**",
        f"Se generaron {len(summary)} escenarios con Wofost81_WLP_CWB, todos SIN riego.",
        "Resultado = materia SECA potencial de órganos de reserva, kg/ha.",
        "Sin predicción varietal, sin nutrición Fe/Zn, sin ensayos de campo.",
        "",
        "| Grilla NASA | Campaña | Fecha inicio | Suelo hipotético | Agua inicial cm | TWSO seca kg/ha | WLP/PP |",
        "|---|---|---|---|---:|---:|---:|",
    ]
    for r in summary:
        lines.append(f"| {r['site_label']} | {r['campaign']} | {r['assumed_emergence']} | "
                     f"{r['soil_profile_hypothetical']} | {r['initial_available_water_cm_assumed']} | "
                     f"{r['water_limited_storage_dry_kg_ha']} | "
                     f"{r['water_limited_to_potential_ratio_descriptive']} |")
    lines += [
        "",
        "No asumir independencia entre temporadas de la misma localidad; el ambiente histórico es grilla NASA.",
        "Las diferencias entre perfiles o humedades son sensibilidad a supuestos, NO predicción observada.",
        "Se necesita medir curvas de retención, humedad, profundidad y manejo para calibrar el modelo.",
        "Lluvia NASA real no implica riego real; no se optimizó calendario de riego ni se aconseja regar.",
    ]
    (out/"water_limited_report.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    return meta


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--weather-dir",required=True,type=Path)
    p.add_argument("--baseline",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    report=run(args.weather_dir,args.baseline,args.out)
    print(json.dumps({
        "status":report["status"],"scenarios":report["simulated_scenarios"],
        "daily_records":report["simulated_daily_rows"],
    },ensure_ascii=False))


if __name__=="__main__":
    main()

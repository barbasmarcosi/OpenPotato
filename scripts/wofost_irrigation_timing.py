"""M1-18: equal-volume hypothetical irrigation schedules under real archived weather.

WOFOST81_WLP_CWB; generic Potato_701; invented soils and initial water.
A paired no-irrigation simulation MUST exactly reproduce the verified M1-17
outputs to be accepted. Five gross 20 mm irrigations (biweekly) versus ten
gross 10 mm irrigations (weekly): both deliver gross 100 mm with efficiency
assumed 0.80, during the first 77 days after emergence only.

Not farm advice, real trials, fresh tuber yield, Fe/Zn or cultivar adaptation.
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
from scripts import wofost_water_sensitivity as water

STATUS="WOFOST_HYPOTHETICAL_IRRIGATION_TIMING_NOT_CALIBRATED"
MODEL=water.MODEL
EVENT_EFFICIENCY_ASSUMED=0.80
SCHEDULES={
    "none": {"interval_days":0,"start_day":0,"events":0,"gross_mm_per_event":0},
    "weekly_100mm": {"interval_days":7,"start_day":14,"events":10,"gross_mm_per_event":10},
    "fortnightly_100mm":{"interval_days":14,"start_day":14,"events":5,"gross_mm_per_event":20},
}
EXPECTED_BASE=48
EXPECTED=len(SCHEDULES)*EXPECTED_BASE
OUTPUT_FIELDS=[
    "scenario_id","base_scenario_id","site_label","campaign",
    "assumed_emergence_date","soil_profile_invented","initial_water_cm_invented",
    "irrigation_timing_strategy_invented","scheduled_events",
    "gross_irrigation_mm_scheduled","effective_irrigation_mm_scheduled",
    "application_efficiency_assumed","storage_organ_dry_kg_ha_modelled",
    "reference_no_irrigation_dry_kg_ha_modelled",
    "difference_from_same_case_no_irrigation_dry_kg_ha",
    "additional_dry_storage_kg_ha_per_gross_irrigation_mm_sensitivity",
    "days_with_RFTRA_lt_0_99","cumulative_model_transpiration_cm",
    "rainfall_NASA_POWER_mm_during_model_days","weather_snapshot_sha256",
    "status",
]
EVENT_FIELDS=[
    "scenario_id","event_date","days_after_emergence",
    "irrigation_amount_cm_gross","irrigation_amount_mm_gross",
    "effective_amount_mm_at_assumed_efficiency",
]
DAILY_FIELDS=[
    "scenario_id","day","days_after_emergence","SM_m3_m3","RFTRA",
    "TRA_cm_day","TWSO_dry_kg_ha",
]


def validate_schedules():
    if set(SCHEDULES)!={"none","weekly_100mm","fortnightly_100mm"}:
        raise ValueError("Unexpected irrigation strategy inventory")
    for name,s in SCHEDULES.items():
        if set(s)!={"interval_days","start_day","events","gross_mm_per_event"}:
            raise ValueError("Schedule has undocumented fields")
        if any(not isinstance(v,int) or v<0 for v in s.values()):
            raise ValueError("Schedules must be nonnegative integers")
        if name=="none":
            if any(s.values()): raise ValueError("Zero-water control must have no events")
        else:
            if s["start_day"]!=14 or s["events"]<=0 or s["interval_days"]<1:
                raise ValueError("Undeclared schedule event design")
            if s["gross_mm_per_event"]*s["events"]!=100:
                raise ValueError("Timed-irrigation scenarios must have equal gross total water")
            last=s["start_day"]+(s["events"]-1)*s["interval_days"]
            if last>80: raise ValueError("Irrigation must stay in early study window")
    if not 0<EVENT_EFFICIENCY_ASSUMED<=1:
        raise ValueError("Invalid irrigation efficiency")
    if water.validate_design()!=EXPECTED_BASE:
        raise ValueError("M1-17 prerequisite design drift")
    return EXPECTED


def irrigation_events(start,harvest,schedule_name):
    """Source WOFOST agromanager uses amounts in cm and efficiency fraction."""
    s=SCHEDULES[schedule_name]
    events=[]
    for index in range(s["events"]):
        when=start+timedelta(days=s["start_day"]+index*s["interval_days"])
        if not start<when<harvest:
            raise ValueError("Event outside crop calendar")
        cm=s["gross_mm_per_event"]/10
        events.append((when,cm,EVENT_EFFICIENCY_ASSUMED))
    if len({v[0] for v in events})!=len(events):
        raise ValueError("Repeated irrigation event date")
    return events


def timed_agromanagement(start,harvest,schedule_name):
    events=irrigation_events(start,harvest,schedule_name)
    return [{start: {
        "CropCalendar":{
            "crop_name":base.CROP,"variety_name":base.VARIETY,
            "crop_start_date":start,"crop_start_type":"emergence",
            "crop_end_date":harvest,"crop_end_type":"harvest",
            "max_duration":200,
        },
        "TimedEvents":([{
            "event_signal":"irrigate",
            "name":"Explicit hypothetical gross cm and 0.8 efficiency",
            "comment":"Input amount in cm, irrigation dose is NOT observed",
            "events_table":[{day:{"amount":amount,"efficiency":eff}}
                            for day,amount,eff in events],
        }] if events else None),
        "StateEvents":None,
    }}]


def read_m17(path,hashes):
    path=Path(path)
    with path.open(newline="",encoding="utf-8-sig") as f:
        rows=list(csv.DictReader(f))
    expected={f"{site}-{year}-{m:02d}{d:02d}-{soil}-{level}"
              for site in base.SITES
              for year in base.CAMPAIGNS
              for m,d in base.START_MONTH_DAYS
              for soil in water.SOIL_PROFILES
              for level in water.INITIAL_AVAILABLE_WATER_CM}
    if len(rows)!=EXPECTED_BASE or {r["scenario_id"] for r in rows}!=expected:
        raise ValueError("M1-17 reference must be 48 unique complete cases")
    out={}
    for r in rows:
        if (r["interpretation"]!=water.STATUS or
                r["weather_snapshot_sha256"]!=hashes.get(r["site_label"]) or
                float(r["irrigation_mm_assumed"])!=0):
            raise ValueError("Reference must be archived M1-17 no-irrigation inputs")
        v=float(r["water_limited_storage_dry_kg_ha"])
        if not math.isfinite(v) or v<0:raise ValueError("Nonphysical M1-17 reference")
        out[r["scenario_id"]]=v
    return out


def run(weather_dir,control_csv,out):
    import pcse
    from pcse.input import NASAPowerWeatherDataProvider,YAMLCropDataProvider
    from pcse.models import Wofost81_WLP_CWB
    from pcse.base import ParameterProvider
    if pcse.__version__!=base.PCSE_VERSION:
        raise ValueError("PCSE model version changed")
    validate_schedules()
    sources,hashes=base.load_weather(weather_dir)
    controls=read_m17(control_csv,hashes)

    class ArchivedWeather(NASAPowerWeatherDataProvider):
        def __init__(self,lat,lon,snapshot):
            self.source_snapshot=snapshot
            super().__init__(latitude=lat,longitude=lon,force_update=True)
        def _query_NASAPower_server(self,lat,lon):
            return self.source_snapshot

    provider_url=("https://raw.githubusercontent.com/ajwdewit/WOFOST_crop_parameters/"
                  +base.CROP_COMMIT)
    crops=YAMLCropDataProvider(Wofost81_WLP_CWB,repository=provider_url,
                               force_reload=True)
    crops.set_active_crop(base.CROP,base.VARIETY)
    scenarios,events_output,daily_output=[],[],[]
    no_irrigation_differences=[]
    for site,(lat,lon) in base.SITES.items():
        weather=ArchivedWeather(lat,lon,sources[site])
        if weather.first_date!=base.WEATHER_FIRST or weather.last_date!=base.WEATHER_LAST:
            raise ValueError("Historical NASA time range changed")
        for year in base.CAMPAIGNS:
            for month,day in base.START_MONTH_DAYS:
                start=date(year,month,day)
                harvest=date(year+1,*base.HARVEST_MONTH_DAY)
                for n in range((harvest-start).days+1):
                    weather(start+timedelta(days=n))
                for soil_name,soil in water.SOIL_PROFILES.items():
                    for initial_label,initial_cm in water.INITIAL_AVAILABLE_WATER_CM.items():
                        base_id=(f"{site}-{year}-{month:02d}{day:02d}-"
                                 f"{soil_name}-{initial_label}")
                        for strategy in SCHEDULES:
                            eventlist=irrigation_events(start,harvest,strategy)
                            gross_mm=sum(x[1]*10 for x in eventlist)
                            effective_mm=sum(x[1]*10*x[2] for x in eventlist)
                            sitevars={**water.COMMON_SITE,"WAV":initial_cm,
                                      "SMLIM":soil["SMFCF"]}
                            params=ParameterProvider(cropdata=crops,
                                                     soildata=dict(soil),
                                                     sitedata=sitevars)
                            model=Wofost81_WLP_CWB(
                                params,weather,timed_agromanagement(start,harvest,strategy))
                            model.run_till_terminate()
                            summaries=model.get_summary_output()
                            records=model.get_output()
                            if not summaries or not records:
                                raise ValueError("Missing water-limited growth outputs")
                            storage=float(summaries[0]["TWSO"])
                            if not math.isfinite(storage) or storage<0:
                                raise ValueError("Bad dry storage biomass from WOFOST")
                            refer=controls[base_id]
                            if strategy=="none":
                                diff=abs(storage-refer)
                                no_irrigation_differences.append(diff)
                                if diff>0.0001:
                                    raise ValueError("Zero-irrigation model does not replay M1-17 biology")
                            if not (0<=storage<2*max(refer,1.0)+25000):
                                raise ValueError("Outside model sensitivity sanity range")
                            def num(v):
                                if not math.isfinite(float(v)):raise ValueError("Nonfinite simulated value")
                                return round(float(v),5)
                            rftra=[float(r["RFTRA"]) for r in records
                                   if r.get("RFTRA") is not None]
                            tra=[float(r["TRA"]) for r in records
                                 if r.get("TRA") is not None]
                            if len(rftra)!=len(records) or len(tra)!=len(records):
                                raise ValueError("Incomplete water stress or transpiration trace")
                            if any(not math.isfinite(x) or x<0 or x>1.001 for x in rftra):
                                raise ValueError("Invalid RFTRA biological state")
                            if any(not math.isfinite(x) or x<0 for x in tra):
                                raise ValueError("Invalid daily transpiration")
                            rains=[float(sources[site]["properties"]["parameter"]
                                         ["PRECTOTCORR"][r["day"].strftime("%Y%m%d")])
                                   for r in records]
                            if any(not math.isfinite(x) or x<0 for x in rains):
                                raise ValueError("Invalid NASA rainfall source")
                            ident=base_id+"-"+strategy
                            gain=storage-refer
                            efficiency=(gain/gross_mm if gross_mm else None)
                            scenarios.append({
                                "scenario_id":ident,"base_scenario_id":base_id,
                                "site_label":site,"campaign":year,
                                "assumed_emergence_date":start.isoformat(),
                                "soil_profile_invented":soil_name,
                                "initial_water_cm_invented":initial_cm,
                                "irrigation_timing_strategy_invented":strategy,
                                "scheduled_events":len(eventlist),
                                "gross_irrigation_mm_scheduled":num(gross_mm),
                                "effective_irrigation_mm_scheduled":num(effective_mm),
                                "application_efficiency_assumed":num(EVENT_EFFICIENCY_ASSUMED) if eventlist else 0,
                                "storage_organ_dry_kg_ha_modelled":num(storage),
                                "reference_no_irrigation_dry_kg_ha_modelled":refer,
                                "difference_from_same_case_no_irrigation_dry_kg_ha":num(gain),
                                "additional_dry_storage_kg_ha_per_gross_irrigation_mm_sensitivity":(
                                    num(efficiency) if efficiency is not None else ""),
                                "days_with_RFTRA_lt_0_99":sum(x<0.99 for x in rftra),
                                "cumulative_model_transpiration_cm":num(sum(tra)),
                                "rainfall_NASA_POWER_mm_during_model_days":num(sum(rains)),
                                "weather_snapshot_sha256":hashes[site],
                                "status":STATUS,
                            })
                            for event_date,amount,eff in eventlist:
                                events_output.append({
                                    "scenario_id":ident,"event_date":event_date.isoformat(),
                                    "days_after_emergence":(event_date-start).days,
                                    "irrigation_amount_cm_gross":num(amount),
                                    "irrigation_amount_mm_gross":num(amount*10),
                                    "effective_amount_mm_at_assumed_efficiency":num(amount*10*eff),
                                })
                            for r in records:
                                date_key=r["day"].isoformat()
                                daily_output.append({
                                    "scenario_id":ident,"day":date_key,
                                    "days_after_emergence":(r["day"]-start).days,
                                    "SM_m3_m3":num(r["SM"]),
                                    "RFTRA":num(r["RFTRA"]),
                                    "TRA_cm_day":num(r["TRA"]),
                                    "TWSO_dry_kg_ha":num(r["WSO"]),
                                })
    if len(scenarios)!=EXPECTED or len(no_irrigation_differences)!=EXPECTED_BASE:
        raise ValueError("Unexpected scenario counts")
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    hashes_derived={}
    for filename,fields,rows in [
        ("irrigation_timing_scenarios.csv",OUTPUT_FIELDS,scenarios),
        ("irrigation_timing_events.csv",EVENT_FIELDS,events_output),
        ("irrigation_timing_daily.csv",DAILY_FIELDS,daily_output),
    ]:
        path=out/filename
        with path.open("w",newline="",encoding="utf-8") as f:
            writer=csv.DictWriter(f,fieldnames=fields)
            writer.writeheader();writer.writerows(rows)
        hashes_derived[filename]=base.sha256(path)
    manifest={
        "schema_version":"1.0","status":STATUS,
        "engine_pcse":base.PCSE_VERSION,"model":MODEL,
        "crop_generic_potato":base.VARIETY,
        "crop_parameters_git_commit":base.CROP_COMMIT,
        "weather_sha256":hashes,"control_m17_csv_sha256":base.sha256(control_csv),
        "soil_profiles_hypothetical":water.SOIL_PROFILES,
        "initial_available_water_cm_hypothetical":water.INITIAL_AVAILABLE_WATER_CM,
        "strategies_hypothetical":SCHEDULES,
        "irrigation_delivery_efficiency_hypothetical":EVENT_EFFICIENCY_ASSUMED,
        "simulated_scenarios":len(scenarios),
        "zero_irrigation_reference_cases_verified":len(no_irrigation_differences),
        "maximum_abs_control_biomass_replay_difference_kg_ha":max(no_irrigation_differences),
        "scheduled_events":len(events_output),
        "daily_records":len(daily_output),
        "derived_sha256":hashes_derived,
        "limitations":[
            "Gross irrigation is scheduled, not metered in a physical field.",
            "Assumed 0.80 effectiveness is not real system efficiency, runoff or application uniformity.",
            "Water response and biomass are WOFOST simulated dry storage organ values, not potato yields observed.",
            "Gain per gross irrigation mm is a descriptive conditional model sensitivity, not farm WUE.",
            "No calibration of soils, crop phenology, irrigation infrastructure or real weather station.",
            "No Fe, Zn, mineral uptake, bioavailability, glycoalkaloids or cultivar recommendation.",
            "All schedules end by day 77 after assumed emergence, but crop maturity may vary among models.",
            "Cannot infer optimal irrigation policy, drought tolerance, economical yield or actual freshwater saving.",
        ],
    }
    (out/"irrigation_timing_provenance.json").write_text(
        json.dumps(manifest,indent=2,sort_keys=True,ensure_ascii=False)+"\n",
        encoding="utf-8")
    lines=[
        "# M1-18 — Simulación de riego de igual volumen: NO CALIBRADA",
        "",
        "**Clima NASA POWER histórico; suelo, dosis, eficacia y fechas hipotéticos.**",
        f"Se ejecutaron {len(scenarios)} modelos WOFOST81_WLP_CWB (48 bases × 3 calendarios).",
        "Riego semanal y quincenal: ambos 100 mm brutos programados, 80 mm",
        "efectivos bajo eficiencia supuesta de 0,80; control: 0 mm.",
        "Todas las simulaciones retornan biomasa SECA de órganos de reserva kg/ha.",
        "",
        "| Grilla | Año | Emergencia | Suelo supuesto | Agua inicial cm | Sin riego | 100 mm semanal | 100 mm quincenal |",
        "|---|---|---|---|---:|---:|---:|---:|",
    ]
    groups={}
    for r in scenarios:
        groups.setdefault(r["base_scenario_id"],{})[r["irrigation_timing_strategy_invented"]]=r
    for base_id,grp in groups.items():
        ctrl=grp["none"]
        lines.append(f"| {ctrl['site_label']} | {ctrl['campaign']} | "
                     f"{ctrl['assumed_emergence_date']} | {ctrl['soil_profile_invented']} | "
                     f"{ctrl['initial_water_cm_invented']} | "
                     f"{ctrl['storage_organ_dry_kg_ha_modelled']} | "
                     f"{grp['weekly_100mm']['storage_organ_dry_kg_ha_modelled']} | "
                     f"{grp['fortnightly_100mm']['storage_organ_dry_kg_ha_modelled']} |")
    lines += ["", "Modelar riego no equivale a recomendar cantidades ni fechas.",
              "Estas respuestas dependen de hipótesis y no están calibradas.",
              "La relación kg seca/kg o mm de agua es SENSIBILIDAD matemática,",
              "no eficiencia productiva observada ni ahorro real de agua."]
    (out/"irrigation_timing_report.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    return manifest


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--weather-dir",required=True,type=Path)
    p.add_argument("--control-csv",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    m=run(args.weather_dir,args.control_csv,args.out)
    print(json.dumps({
        "status":m["status"],"simulated_scenarios":m["simulated_scenarios"],
        "control_replays":m["zero_irrigation_reference_cases_verified"],
        "daily_records":m["daily_records"],
        "scheduled_events":m["scheduled_events"],
    },indent=2))


if __name__=="__main__":
    main()

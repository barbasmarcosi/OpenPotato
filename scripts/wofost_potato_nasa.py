"""M1-16: WOFOST 8.1 generic potato potential dry biomass with real NASA weather.

Observed gridded NASA POWER weather != observed potato yield or tuber minerals.
All agronomy (dates, generic cultivar, unrestricted water/nutrients, soil, CO2)
is ASSUMED and NOT calibrated to a site or to any CIP clone.

PCSE dependency intentionally loaded only when running the model. Existing
offline scientific unit tests do NOT need PCSE or internet.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

PCSE_VERSION = "6.0.13"
CROP_COMMIT = "1ca91d7dbb5aaf6b41462162de03a8254812d3a5"
MODEL = "Wofost81_PP"
CROP = "potato"
VARIETY = "Potato_701"
API = "https://power.larc.nasa.gov/api/temporal/daily/point"
POWER_VARS = (
    "TOA_SW_DWN", "ALLSKY_SFC_SW_DWN", "T2M", "T2M_MIN",
    "T2M_MAX", "T2MDEW", "WS2M", "PRECTOTCORR",
)
SITES = {
    "trenque_lauquen": (-35.97, -62.73),
    "neuquen": (-38.95, -68.06),
}
PINNED_WEATHER_SHA256 = {
    "trenque_lauquen": "32b9404dadf8cf52a59e21a3c3094ea815d7d5485a995704b5b5bfcbd2b07e32",
    "neuquen": "8d0656de76652e14bef10fc1d79a9f19e73055052c889afb11f51959b5fb1d34",
}
WEATHER_FIRST = date(2022, 1, 1)
WEATHER_LAST = date(2024, 4, 1)
HARVEST_MONTH_DAY = (3, 1)
CAMPAIGNS = (2022, 2023)
START_MONTH_DAYS = ((9, 1), (10, 1))
# No measured soil, management, location-specific cultivar or CO2 input.
ASSUMED_SOIL = {"SMFCF": 0.30, "CRAIRC": 0.06, "SM0": 0.45,
                "SMW": 0.10, "RDMSOL": 100.0}
ASSUMED_SITE = {"CO2": 410.0}
STATUS = "WOFOST_POTENTIAL_DRY_STORAGE_BIOMASS_UNCALIBRATED"
SUMMARY_FIELDS = [
    "scenario_id", "site_label", "latitude", "longitude", "campaign",
    "assumed_emergence_date", "assumed_harvest_date",
    "model", "generic_variety", "potential_storage_dry_kg_ha",
    "potential_total_aboveground_dry_kg_ha",
    "max_leaf_area_index", "simulated_maturity_date",
    "weather_nasa_power_sha256", "interpretation",
]
DAILY_FIELDS = [
    "scenario_id", "date", "day_after_emergence", "DVS", "LAI",
    "storage_organ_dry_kg_ha", "total_aboveground_dry_kg_ha",
]


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def day_strings(start, end):
    for n in range((end-start).days+1):
        yield (start+timedelta(days=n)).strftime("%Y%m%d")


def validate_power(data, start=WEATHER_FIRST, end=WEATHER_LAST):
    if not isinstance(data, dict) or not isinstance(data.get("properties"), dict):
        raise ValueError("Invalid NASA POWER source structure")
    params = data["properties"].get("parameter")
    if not isinstance(params, dict):
        raise ValueError("NASA POWER missing parameter dictionary")
    expected = set(day_strings(start, end))
    if len(expected) < 2:
        raise ValueError("Meteorological period must include multiple days")
    fill = float(data.get("header", {}).get("fill_value", -999))
    for name in POWER_VARS:
        series = params.get(name)
        if not isinstance(series, dict) or set(series) != expected:
            raise ValueError("NASA POWER missing or extra dates for " + name)
        for key, raw in series.items():
            if not isinstance(raw, (int, float)):
                raise ValueError("NASA POWER nonnumeric observation in " + name)
            v = float(raw)
            if not math.isfinite(v) or v == fill or v <= -900:
                raise ValueError("NASA POWER missing/nonfinite weather value in " + name)
            if name in ("ALLSKY_SFC_SW_DWN", "TOA_SW_DWN") and not 0 <= v <= 55:
                raise ValueError("NASA POWER solar MJ/m²/day out of physical envelope")
            if name == "PRECTOTCORR" and not 0 <= v <= 250:
                raise ValueError("NASA POWER rainfall mm/day incompatible with PCSE bound")
            if name == "WS2M" and not 0 <= v <= 50:
                raise ValueError("NASA POWER wind m/s out of physical envelope")
            if name.startswith("T2M") and not -65 <= v <= 65:
                raise ValueError("NASA POWER temperature °C out of envelope")
    min_t = params["T2M_MIN"]
    max_t = params["T2M_MAX"]
    if any(min_t[d] > max_t[d] for d in expected):
        raise ValueError("NASA POWER daily minimum hotter than daily maximum")
    elevation = data.get("geometry", {}).get("coordinates")
    if not isinstance(elevation, list) or len(elevation) < 3:
        raise ValueError("NASA POWER missing elevation metadata")
    if not -500 <= float(elevation[2]) <= 9000:
        raise ValueError("NASA POWER elevation invalid")
    return len(expected)


def nasa_url(lat, lon):
    query = urlencode({
        "parameters": ",".join(POWER_VARS),
        "latitude": lat, "longitude": lon,
        "start": WEATHER_FIRST.strftime("%Y%m%d"),
        "end": WEATHER_LAST.strftime("%Y%m%d"),
        "community": "AG", "format": "JSON",
    })
    return API + "?" + query


def acquire_weather(weather_dir):
    """Explicit network operation; never run implicitly during modeling."""
    weather_dir = Path(weather_dir)
    weather_dir.mkdir(parents=True, exist_ok=True)
    for label, (lat, lon) in SITES.items():
        target = weather_dir/(label+".json")
        if target.exists():
            raise ValueError("Refusing to overwrite existing source weather snapshot")
        req = Request(nasa_url(lat, lon), headers={
            "User-Agent": "OpenPotato-M1-16-reproducible-weather/1.0"})
        with urlopen(req, timeout=90) as response:
            if response.status != 200:
                raise ValueError("NASA POWER HTTP request failed")
            payload = response.read()
        data = json.loads(payload)
        validate_power(data)
        target.write_bytes(payload)
    return sorted(p.name for p in weather_dir.glob("*.json"))


def load_weather(weather_dir):
    """Require named, complete locally stored source snapshots; never fetch."""
    root = Path(weather_dir)
    if {x.name for x in root.glob("*.json")} != {k+".json" for k in SITES}:
        raise ValueError("Expected exactly the two named NASA source JSON snapshots")
    sources, hashes = {}, {}
    for label in SITES:
        path = root/(label+".json")
        if sha256(path) != PINNED_WEATHER_SHA256[label]:
            raise ValueError("Historical NASA weather snapshot SHA-256 changed: manual rebaseline required")
        data = json.loads(path.read_bytes())
        validate_power(data)
        if (abs(float(data["geometry"]["coordinates"][0])-SITES[label][1]) > 0.02
                or abs(float(data["geometry"]["coordinates"][1])-SITES[label][0]) > 0.02):
            raise ValueError("NASA weather source coordinates do not match declared research site")
        sources[label] = data
        hashes[label] = sha256(path)
    return sources, hashes


def run_model(weather_sources, source_hashes, out):
    import pcse
    from pcse.base import ParameterProvider
    from pcse.input import NASAPowerWeatherDataProvider, YAMLCropDataProvider
    from pcse.models import Wofost81_PP

    if pcse.__version__ != PCSE_VERSION:
        raise ValueError("PCSE version changed: refusing unreviewed results")

    class PinnedWindowPower(NASAPowerWeatherDataProvider):
        """Reuse PCSE's conversion and evapotranspiration, never query the web."""
        def __init__(self, latitude, longitude, snapshot):
            self._snapshot = snapshot
            super().__init__(latitude=latitude, longitude=longitude, force_update=True)
        def _query_NASAPower_server(self, latitude, longitude):
            return self._snapshot

    provider_url = ("https://raw.githubusercontent.com/ajwdewit/"
                    "WOFOST_crop_parameters/"+CROP_COMMIT)
    crops = YAMLCropDataProvider(Wofost81_PP, repository=provider_url,
                                force_reload=True)
    crops.set_active_crop(CROP, VARIETY)
    if len(crops) < 60:
        raise ValueError("Missing published potato crop coefficients")
    scenario_rows, daily_rows = [], []
    for label, (lat, lon) in SITES.items():
        weather = PinnedWindowPower(lat, lon, weather_sources[label])
        if weather.first_date != WEATHER_FIRST or weather.last_date != WEATHER_LAST:
            raise ValueError("Weather provider's actual dates differ from pinned snapshots")
        for year in CAMPAIGNS:
            for mon, day in START_MONTH_DAYS:
                start = date(year, mon, day)
                harvest = date(year+1, *HARVEST_MONTH_DAY)
                # Force complete DAILY meteorology throughout campaign.
                for n in range((harvest-start).days+1):
                    weather(start+timedelta(days=n))
                agro = [{start: {"CropCalendar": {
                    "crop_name": CROP, "variety_name": VARIETY,
                    "crop_start_date": start, "crop_start_type": "emergence",
                    "crop_end_date": harvest, "crop_end_type": "harvest",
                    "max_duration": 200,
                }, "TimedEvents": None, "StateEvents": None}}]
                params = ParameterProvider(cropdata=crops,
                                           soildata=ASSUMED_SOIL.copy(),
                                           sitedata=ASSUMED_SITE.copy())
                model = Wofost81_PP(params, weather, agro)
                model.run_till_terminate()
                summaries = model.get_summary_output()
                if not summaries or not isinstance(summaries[0].get("TWSO"), (int, float)):
                    raise ValueError("WOFOST summary missing storage organ dry biomass")
                result = summaries[0]
                storage = float(result["TWSO"])
                if not math.isfinite(storage) or storage <= 0:
                    raise ValueError("WOFOST biomass missing or nonphysical")
                scenario_id = f"{label}-{year}-{mon:02d}{day:02d}"
                def fmt(x):
                    return "" if x is None else round(float(x), 4)
                scenario_rows.append({
                    "scenario_id": scenario_id,
                    "site_label": label,
                    "latitude": lat, "longitude": lon,
                    "campaign": year,
                    "assumed_emergence_date": start.isoformat(),
                    "assumed_harvest_date": harvest.isoformat(),
                    "model": MODEL, "generic_variety": VARIETY,
                    "potential_storage_dry_kg_ha": fmt(storage),
                    "potential_total_aboveground_dry_kg_ha": fmt(result["TAGP"]),
                    "max_leaf_area_index": fmt(result.get("LAIMAX")),
                    "simulated_maturity_date": (result.get("DOM") or "").isoformat()
                                              if result.get("DOM") else "",
                    "weather_nasa_power_sha256": source_hashes[label],
                    "interpretation": STATUS,
                })
                days = model.get_output()
                if not days or days[-1]["day"] > harvest:
                    raise ValueError("WOFOST daily output inconsistent with scenario period")
                for rec in days:
                    wso = rec.get("WSO")
                    tagp = rec.get("TAGP")
                    daily_rows.append({
                        "scenario_id": scenario_id,
                        "date": rec["day"].isoformat(),
                        "day_after_emergence": (rec["day"]-start).days,
                        "DVS": fmt(rec.get("DVS")),
                        "LAI": fmt(rec.get("LAI")),
                        "storage_organ_dry_kg_ha": fmt(wso),
                        "total_aboveground_dry_kg_ha": fmt(tagp),
                    })
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    paths = {}
    for filename, columns, records in (
        ("generic_potato_potential_scenarios.csv", SUMMARY_FIELDS, scenario_rows),
        ("generic_potato_potential_daily.csv", DAILY_FIELDS, daily_rows),
    ):
        path = out/filename
        with path.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=columns)
            w.writeheader()
            w.writerows(records)
        paths[filename] = sha256(path)
    manifest = {
        "status": STATUS,
        "model": MODEL,
        "pcse_version": PCSE_VERSION,
        "crop_parameters_source_commit": CROP_COMMIT,
        "crop_source": "https://github.com/ajwdewit/WOFOST_crop_parameters",
        "crop": CROP, "variety": VARIETY,
        "nasa_power_api": API,
        "weather_gridded_observations_not_field_station_data": True,
        "weather_date_window": [WEATHER_FIRST.isoformat(), WEATHER_LAST.isoformat()],
        "site_coordinates": {label: {"lat": lat, "lon": lon}
                             for label, (lat, lon) in SITES.items()},
        "weather_json_sha256": source_hashes,
        "pinned_nasa_weather_sha256_verified": source_hashes == PINNED_WEATHER_SHA256,
        "assumed_soil_not_measured": ASSUMED_SOIL,
        "assumed_co2_ppm_not_observed": ASSUMED_SITE["CO2"],
        "assumed_planting_dates_not_recorded_field_dates": True,
        "unlimited_water_and_nutrients": True,
        "does_not_simulate_water_stress": True,
        "scenarios": len(scenario_rows),
        "daily_output_records": len(daily_rows),
        "derived_csv_sha256": paths,
        "limits": [
            "Generic published potato variety is NOT a CIP or locally calibrated cultivar.",
            "WOFOST81_PP models potential production; historical rainfall DOES NOT cause drought stress.",
            "TWSO is storage organ DRY mass kg/ha, not observed or fresh tuber yield.",
            "No calibrated soil properties, irrigation, local management, disease or weather-station validation.",
            "Weather is historical gridded NASA POWER data, not a field observation.",
            "No observed potato yields, no genotype contrasts or GxE genetic inference.",
            "No Fe/Zn concentrations, glycoalkaloid safety, bioavailability or nutrition per hectare inferred.",
            "Crop emergence and harvest dates are researcher ASSUMPTIONS, not planting records.",
        ],
    }
    (out/"potential_model_provenance.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True)+"\n",
        encoding="utf-8")
    lines = [
        "# M1-16 — Modelo de papa WOFOST 8.1 con meteorología NASA POWER",
        "",
        "**MODELO POTENCIAL NO CALIBRADO. No son rendimientos observados.**",
        "Resultados en **kg/ha de MATERIA SECA de órganos de reserva** (TWSO),",
        "**nunca toneladas de tubérculo fresco**.",
        "Sin limitación de agua/nutrientes, con un clon genérico Potato_701;",
        "No se modela déficit hídrico ni hierro o zinc.",
        "",
        "| Sitio de grilla NASA | Campaña | Emergencia supuesta | TWSO potencial seco (kg/ha) |",
        "|---|---|---|---:|",
    ]
    for r in scenario_rows:
        lines.append(f"| {r['site_label']} | {r['campaign']} | "
                     f"{r['assumed_emergence_date']} | "
                     f"{float(r['potential_storage_dry_kg_ha']):,.0f} |")
    lines += [
        "", "Estas cifras son contrafácticos computacionales con parámetros genéricos,",
        "no recomendaciones productivas ni evidencia nutricional para cultivares.",
        "El cambio entre fechas o sitios refleja este modelo particular y los supuestos.",
        "",
        "NASA POWER: https://power.larc.nasa.gov/docs/services/api/temporal/daily/",
        "PCSE/WOFOST: https://pcse.readthedocs.io/",
        "Parámetros fijados al commit de catálogo: "+CROP_COMMIT,
    ]
    (out/"potential_model_report.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    return manifest


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--weather-dir", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--acquire", action="store_true",
                   help="Explicitly obtain public NASA weather if no pinned files exist")
    args = p.parse_args()
    if args.acquire:
        acquire_weather(args.weather_dir)
    sources, hashes = load_weather(args.weather_dir)
    results = run_model(sources, hashes, args.out)
    print(json.dumps({
        "status": results["status"],
        "scenarios": results["scenarios"],
        "days": results["daily_output_records"],
        "weather_source_sha256": results["weather_json_sha256"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

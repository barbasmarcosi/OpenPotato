"""M1-27: run official PCSE ExcelWeatherDataProvider against ephemeral WUR XLSX.

Source: ten Den et al 2024, doi:10.7910/DVN/1LC6W7, CC BY-NC-SA.
No field crop-model run. Never export or print weather values or XLSX.
"""
import argparse
from datetime import datetime,time,date,timedelta
import hashlib
import io
import json
import math
import tempfile
from pathlib import Path
from scripts.wur_pcse_source_contract import FIELDS,UNITS,HASHES,audit_sheet,day

PCSE_VERSION="6.0.13"

def build_private_pcse_xlsx(source_sheet):
    """Convert observed ORIGINAL into PCSE Excel layout, in-memory only."""
    from openpyxl import Workbook
    audit=audit_sheet(source_sheet)
    rows=list(source_sheet.iter_rows(min_row=1,values_only=True))
    idx={k:v-1 for k,v in audit["pcse_source_columns_one_based"].items()}
    out=Workbook()
    ws=out.active
    ws.title="Weather"
    ws["A1"]="Site Characteristics"
    for line,label,original_row in [
        (2,"Country",2),(3,"Station",3),(4,"Description",4),
        (5,"Source",5),(6,"Contact",6)]:
        ws.cell(line,1,label)
        ws.cell(line,2,rows[original_row-1][1])
    ws.cell(7,1,"Missing values")
    ws.cell(7,2,rows[5][1])
    for i,label in enumerate(("Longitude","Latitude","Elevation",
                              "AngstromA","AngstromB","HasSunshine"),1):
        ws.cell(8,i,label)
        ws.cell(9,i,rows[7][i-1])
    ws.cell(10,1,"Observed data")
    for i,(field,unit) in enumerate(zip(FIELDS,UNITS),1):
        ws.cell(11,i,field)
        ws.cell(12,i,unit)
    for nr,row in enumerate(rows[11:],13):
        for i,field in enumerate(FIELDS,1):
            value=row[idx[field]]
            if field=="DAY":
                parsed=day(value)
                if parsed is None:raise ValueError("Non-dated source row")
                value=datetime.combine(parsed,time.min)
            ws.cell(nr,i,value)
    buffer=io.BytesIO()
    out.save(buffer);out.close()
    return buffer.getvalue(),audit

def assert_all_days(provider):
    """Provider is known to SKIP invalid rows: read and verify every day."""
    start=date(2018,1,1)
    end=date(2020,12,31)
    count=0
    failures=[]
    while start<=end:
        try:
            weather=provider(start)
            for field in ("IRRAD","TMIN","TMAX","VAP","WIND","RAIN","E0","ES0","ET0"):
                v=getattr(weather,field)
                if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v):
                    raise ValueError("Nonfinite numeric output from PCSE "+field)
            count+=1
        except Exception:
            failures.append(start)
        start+=timedelta(days=1)
    if failures:
        raise ValueError("PCSE weather data provider omitted or rejected "+
                         str(len(failures))+" original daily observations")
    return count

def process_originals(inputs):
    if set(inputs)!=set(HASHES):
        raise ValueError("Both original stations mandatory")
    for site,expected in HASHES.items():
        if hashlib.sha256(inputs[site]).hexdigest()!=expected:
            raise ValueError("Unknown original source XLSX bytes")
    import pcse
    from openpyxl import load_workbook
    from pcse.input import ExcelWeatherDataProvider
    if pcse.__version__!=PCSE_VERSION:
        raise ValueError("PCSE version unpinned; comparison invalid")
    summaries=[]
    with tempfile.TemporaryDirectory(prefix="m1-27-weather-ephemeral-") as path:
        for site in HASHES:
            book=load_workbook(io.BytesIO(inputs[site]),read_only=True,data_only=True)
            try:
                private_bytes,audit=build_private_pcse_xlsx(book.worksheets[0])
            finally:book.close()
            tmp=Path(path)/("internal_original_"+site+".xlsx")
            tmp.write_bytes(private_bytes)
            # Never upload or print the temporary file or daily values.
            provider=ExcelWeatherDataProvider(str(tmp),force_reload=True)
            records=assert_all_days(provider)
            summaries.append({
                "site":site,
                "original_source_sha256":HASHES[site],
                "source_pcse_required_fields_complete":audit["mandatory_2019_2020_complete"],
                "source_extra_non_pcse_columns":audit["unused_source_columns_one_based"],
                "pcse_daily_calendar_days_retrievable":records,
                "pcse_weather_daily_records_exported":0,
                "pcse_observed_weather_values_exported":0,
                "pcse_crop_model_executed":False,
            })
    return {
        "status":"OFFICIAL_PCSE_WEATHER_PROVIDER_IMPORTED_WUR_NOT_CROP_VALIDATION",
        "pcse_version":PCSE_VERSION,
        "source_doi":"10.7910/DVN/1LC6W7",
        "license":"CC BY-NC-SA 4.0",
        "original_workbooks_uploaded":False,
        "model_prediction_heldout_performed":False,
        "agronomic_model_calibration_approved":False,
        "sites":summaries,
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--lelystad",type=Path,required=True)
    p.add_argument("--vredepeel",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    result=process_originals({"Lelystad":args.lelystad.read_bytes(),
                              "Vredepeel":args.vredepeel.read_bytes()})
    args.out.mkdir(parents=True,exist_ok=True)
    (args.out/"m1_27_pcse_provider_verified_days_only.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],
                      "site_days":[{"site":x["site"],
                                    "complete_days":x["pcse_daily_calendar_days_retrievable"]}
                                   for x in result["sites"]],
                      "field_wofost_validated":False},sort_keys=True))
if __name__=="__main__":main()

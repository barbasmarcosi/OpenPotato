"""M1-34: fail-closed physical irrigation evidence contract.

Reports contain counts only. Verified rainfall conversion DOES NOT prove W1/W2
units or blank-row meanings. Never emits crop simulations or daily water events.
"""
import argparse
import json
import re
from pathlib import Path
from scripts.wur_irrigation_source_inventory import EXPECTED_SHA256
from scripts import wur_potato_field_audit as plot_source

DOI="10.7910/DVN/1LC6W7"
CLAIMS=("W1_physical_unit","W2_physical_unit","W1_blank_meaning",
        "W2_blank_meaning","absent_calendar_row_meaning",
        "field_area_or_water_depth_definition","application_efficiency_definition")
UNIT_CODES={"mm","cm","L_per_m2","L_per_plot","m3_per_field"}
BLANK_CODES={"NO_APPLICATION","NOT_MEASURED","NOT_APPLICABLE","MIXED_BY_SOURCE"}
OTHER_CODES={"DEPTH_PER_UNIT_AREA","VOLUME_PER_DECLARED_PLOT",
             "OBSERVED_APPLICATION","GROSS_APPLICATION_WITH_EFFICIENCY"}

def verify_reports(treatment,window):
    if treatment.get("irrigation_file_sha256")!=EXPECTED_SHA256:
        raise ValueError("Original irrigation source hash changed")
    if treatment.get("plots_file_sha256")!=plot_source.SOURCE_SHA256:
        raise ValueError("Original plot source hash changed")
    if window.get("original_sha256")!=EXPECTED_SHA256 or not window.get("source_sha_checked"):
        raise ValueError("Window original SHA256 not verified")
    if treatment.get("source_licence")!="CC BY-NC-SA 4.0" or window.get("source_license")!="CC BY-NC-SA 4.0":
        raise ValueError("Source license does not match")
    if not treatment.get("all_site_year_treatment_labels_reconciled"):
        raise ValueError("Physical plot W1/W2 codes not verified")
    if window.get("blanks_or_absent_calendar_rows_are_NOT_zero") is not True:
        raise ValueError("Source blanks were recoded")
    if window.get("wofost_irrigation_agromanagement_admissible") is not False:
        raise ValueError("Source falsely admitted WOFOST")
    groups=window.get("site_year_aggregate_counts")
    if not isinstance(groups,list) or len(groups)!=4:
        raise ValueError("Four original site-years required")
    total={"days":0,"recorded":0,"no_row":0,"W1_unknown":0,"W2_unknown":0,
           "W1_positive":0,"W2_positive":0}
    for g in groups:
        calendar=g["conservative_calendar_days_including_both_anchors"]
        days=g["registered_calendar_days_within_window"]
        no_row=g["calendar_days_without_register_row_UNKNOWN"]
        during=g["windows"]["planting_through_last_sample"]
        if calendar!=days+no_row or during["recorded_days"]!=days:
            raise ValueError("Calendar coverage misbalanced")
        total["days"]+=calendar
        total["recorded"]+=days
        total["no_row"]+=no_row
        for name in ("W1","W2"):
            cells=during[name]
            if cells.get("explicit_zero")!=0:
                raise ValueError("Manufactured irrigation zero from original blank")
            if cells["blank_UNKNOWN"]+cells["recorded_positive"]!=days:
                raise ValueError("Original treatment balance changed")
            unk=g[name+"_unknown_total_blanks_plus_unrecorded_days"]
            if unk!=cells["blank_UNKNOWN"]+no_row:
                raise ValueError("Original blank/absent UNKNOWN count changed")
            total[name+"_unknown"]+=unk
            total[name+"_positive"]+=cells["recorded_positive"]
    if total!={"days":746,"recorded":526,"no_row":220,
               "W1_unknown":565,"W2_unknown":496,
               "W1_positive":181,"W2_positive":250}:
        raise ValueError("Pinned M1-33 source study counts changed")
    return total

def inspect_claims(ledger):
    if not isinstance(ledger,dict) or set(ledger)!={
            "schema_version","dataset_doi","irrigation_source_sha256","claims"}:
        raise ValueError("Evidence ledger schema malformed")
    if (ledger["schema_version"]!=1 or ledger["dataset_doi"]!=DOI
        or ledger["irrigation_source_sha256"]!=EXPECTED_SHA256):
        raise ValueError("Evidence ledger wrong original source")
    claims=ledger["claims"]
    if not isinstance(claims,dict) or set(claims)!=set(CLAIMS):
        raise ValueError("Evidence ledger must contain exactly seven independent claims")
    pending=[]
    reviewed=[]
    for name in CLAIMS:
        item=claims[name]
        keys={"status","value","primary_source_url","primary_source_sha256","independent_review_reference"}
        if not isinstance(item,dict) or set(item)!=keys:
            raise ValueError("Evidence claim schema changed")
        if item["status"]=="UNVERIFIED":
            if any(item[k] is not None for k in keys-{"status"}):
                raise ValueError("Unverified claim contains an invented value or evidence")
            pending.append(name)
            continue
        if item["status"]!="PRIMARY_SOURCE_REVIEWED":
            raise ValueError("Unsupported source verification state")
        allowed=(UNIT_CODES if name.endswith("_physical_unit") else
                 BLANK_CODES if name.endswith("_meaning") else OTHER_CODES)
        if item["value"] not in allowed:
            raise ValueError("Unsupported physical evidence value")
        uri=item["primary_source_url"]
        digest=item["primary_source_sha256"]
        review=item["independent_review_reference"]
        if not isinstance(uri,str) or not re.fullmatch(r"https://[A-Za-z0-9][A-Za-z0-9.-]+/\S+",uri):
            raise ValueError("Primary evidence URL absent")
        if not isinstance(digest,str) or not re.fullmatch("[0-9a-f]{64}",digest):
            raise ValueError("Primary evidence SHA256 absent")
        if not isinstance(review,str) or not re.fullmatch("#[1-9][0-9]*",review):
            raise ValueError("Independent review issue link absent")
        reviewed.append(name)
    return pending,reviewed

def make_report(treatment,window,ledger):
    totals=verify_reports(treatment,window)
    pending,reviewed=inspect_claims(ledger)
    return {
       "status":"BLOCKED_M1_34_PRIMARY_WATER_SEMANTICS_MISSING" if pending else
                "EVIDENCE_LISTED_REQUIRES_SEPARATE_PHYSICAL_QA",
       "dataset_doi":DOI,"source_license":"CC BY-NC-SA 4.0",
       "irrigation_original_sha256":EXPECTED_SHA256,
       "original_plot_sha256":plot_source.SOURCE_SHA256,
       "original_aggregate_balance":totals,
       "unresolved_claims":pending,"listed_reviewed_claims":reviewed,
       "rainfall_factor_ten_NOT_evidence_for_W1_W2_units":True,
       "unrecorded_and_blank_doses_remain_UNKNOWN":True,
       "source_daily_measurements_exported":0,
       "plot_ids_or_field_yields_exported":0,
       "2020_biomass_holdout_used_for_calibration":False,
       "W1_W2_schedule_generation_permitted":False,
       "field_WOFOST_simulation_admissible":False,
       "separate_soil_cultivar_fenology_review_required":True,
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--m1-31",type=Path,required=True)
    p.add_argument("--m1-33",type=Path,required=True)
    p.add_argument("--evidence",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    result=make_report(json.loads(a.m1_31.read_text()),
                       json.loads(a.m1_33.read_text()),
                       json.loads(a.evidence.read_text()))
    a.out.mkdir(parents=True,exist_ok=True)
    (a.out/"m1_34_irrigation_evidence_blockers_ONLY.json").write_text(
       json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],"pending":result["unresolved_claims"],
                      "calendar":result["original_aggregate_balance"],
                      "WOFOST_admissible":False},sort_keys=True))
if __name__=="__main__":
    main()

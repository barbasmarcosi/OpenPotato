"""M1-28: verified WUR planting calendar vs actual plot treatment history.
Sources: ten Den et al. 2024, ODjAR Table 3, Harvard Dataverse v3,
CC BY-NC-SA 4.0. Only anonymous site-year COUNTS are exportable.
This is NOT a field simulation, nor an agromanagement model.
"""
import argparse,csv,io,json
from collections import Counter,defaultdict
from datetime import date
from pathlib import Path
from scripts import wur_potato_field_audit as source

PLANT={
 ("2019","L"):date(2019,4,25),("2020","L"):date(2020,4,20),
 ("2019","V"):date(2019,4,18),("2020","V"):date(2020,4,21),
}
LAST_SAMPLE={
 ("2019","L"):date(2019,10,31),("2020","L"):date(2020,11,3),
 ("2019","V"):date(2019,10,10),("2020","V"):date(2020,10,19),
}
COLUMNS=("Year","Location","Plotnumber","Date","Cultivar","Nitrogen","Irrigation","tubersDW")

def inspect_rows(rows,strict=False):
    plots=defaultdict(list); dates=defaultdict(set); observed=Counter(); used=set()
    for row in rows:
        if not set(COLUMNS).issubset(row) or None in row or any(row[k] is None for k in COLUMNS):
            raise ValueError("Malformed plot source record")
        key=(row["Year"].strip(),row["Location"].strip())
        if key not in PLANT:raise ValueError("Unknown year or location")
        plot=row["Plotnumber"].strip()
        cultivar=row["Cultivar"].strip()
        nitrogen=row["Nitrogen"].strip()
        irrigation=row["Irrigation"].strip()
        if not all((plot,cultivar,nitrogen,irrigation)):
            raise ValueError("Missing cultivar/management/plot identity")
        try: d=date.fromisoformat(row["Date"].strip())
        except ValueError as exc:raise ValueError("Invalid plot observation date") from exc
        if row["Date"].strip()!=d.isoformat() or d.year!=int(key[0]):
            raise ValueError("Observation year/date does not match")
        if d<PLANT[key]:raise ValueError("Observation before published planting date")
        if d>LAST_SAMPLE[key]:raise ValueError("Observation after verified latest sample")
        identity=(key,plot,d)
        if identity in used:raise ValueError("Duplicate physical plot/date")
        used.add(identity)
        plots[key,plot].append((d,cultivar,nitrogen,irrigation,row["tubersDW"].strip()))
        dates[key].add(d);observed[key]+=1
    if set(observed)!=set(PLANT):raise ValueError("Missing site-year")
    if strict and observed!=source.SITE_YEAR_EXPECTED:raise ValueError("Original source row totals changed")
    memberships=defaultdict(lambda:{"plots":set(),"cultivars":set(),"N":set(),"I":set(),"triples":set()})
    for (siteyear,plot),history in plots.items():
        protocol={(c,n,i) for d,c,n,i,dry in history}
        if len(protocol)!=1:raise ValueError("Physical plot changed management or cultivar")
        cultivar,nitrogen,irrigation=next(iter(protocol))
        final=[dry for d,c,n,i,dry in history if d==LAST_SAMPLE[siteyear]]
        if len(final)!=1:raise ValueError("Missing terminal plot measurement")
        dry=source.parse_numeric(final[0])
        if dry is None or dry<=0:raise ValueError("Terminal dry biomass missing or invalid")
        a=memberships[siteyear]
        a["plots"].add(plot);a["cultivars"].add(cultivar)
        a["N"].add(nitrogen);a["I"].add(irrigation);a["triples"].add((cultivar,nitrogen,irrigation))
    if strict:
        if any(len(memberships[y,s]["plots"])!=({"L":45,"V":42}[s]) for y,s in PLANT):
            raise ValueError("Unexpected distinct physical plot count")
        if sum(len(x["plots"]) for x in memberships.values())!=174:
            raise ValueError("Physical train/holdout split changed")
    report=[]
    for year,site in sorted(PLANT):
        k=(year,site);a=memberships[k]
        if max(dates[k])!=LAST_SAMPLE[k]:raise ValueError("Source last sampled date changed")
        report.append({
          "year":year,"site":source.SITE_NAMES[site],
          "article_table3_planting_date":PLANT[k].isoformat(),
          "last_sample_date_NOT_verified_commercial_harvest":LAST_SAMPLE[k].isoformat(),
          "days_planting_to_last_sample":(LAST_SAMPLE[k]-PLANT[k]).days,
          "original_observation_rows":observed[k],
          "unique_physical_plots":len(a["plots"]),
          "unique_sampling_days":len(dates[k]),
          "cultivar_label_count":len(a["cultivars"]),
          "nitrogen_treatment_label_count":len(a["N"]),
          "irrigation_treatment_label_count":len(a["I"]),
          "cultivar_N_irrigation_combinations":len(a["triples"]),
          "plots_with_terminal_dry_tuber_observation":len(a["plots"]),
        })
    return {
      "status":"REAL_PLANTING_AND_PLOT_ASSIGNMENT_AUDIT_NOT_WOFOST_READY",
      "source_doi":source.DOI,"article_doi":"10.18174/odjar.v10i0.18680",
      "original_csv_sha256":source.SOURCE_SHA256 if strict else "NOT_AN_ORIGINAL_SOURCE",
      "licensed_source_verified":strict,"source_license":source.LICENSE,
      "training_year":"2019","untouched_holdout_year":"2020",
      "site_year_aggregates":report,"original_plot_ids_exported":0,
      "original_biomass_values_exported":0,"individual_management_rows_exported":0,
      "planting_is_not_emergence":True,
      "irrigation_class_is_not_measured_water_amount":True,
      "nitrogen_class_is_not_kgN_dose":True,
      "last_sample_is_not_formal_harvest":True,
      "cultivar_specific_parameters_approved":False,
      "soil_hydraulic_profile_approved":False,
      "real_irr_event_join_approved":False,
      "emergence_date_by_source_cultivar_approved":False,
      "training_may_consume_2020_data":False,
      "real_wofost_field_simulation_admissible":False,
      "real_wofost_prediction_errors_computed":False,
      "limitations":[
        "Planting dates are site-year-level observed values from ODjAR Table 3, not inferred emergence.",
        "Plot irrigation and nitrogen columns represent treatments, not dated applications.",
        "Cultivar C1-C6 mapping to named varieties still needs a source dictionary.",
        "The final observed sample need not be the physical harvest or haulm kill.",
        "No plot values, original records, WOFOST outputs, Fe/Zn or safety metrics released.",
      ],
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    blob=a.source.read_bytes()
    source.inspect_original(blob)
    rows=list(csv.DictReader(io.StringIO(blob.decode("utf-8-sig"))))
    result=inspect_rows(rows,strict=True)
    a.out.mkdir(parents=True,exist_ok=True)
    (a.out/"m1_28_wur_plot_management_aggregate.json").write_text(
       json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],"verified":result["licensed_source_verified"],
       "sites":[{"site":x["site"],"year":x["year"],"plots":x["unique_physical_plots"],
       "n_classes":x["nitrogen_treatment_label_count"],
       "irrigation_classes":x["irrigation_treatment_label_count"],
       "management_combinations":x["cultivar_N_irrigation_combinations"]}
       for x in result["site_year_aggregates"]],
       "WOFOST_admissible":False},sort_keys=True))
if __name__=="__main__":main()

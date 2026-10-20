"""Fail-closed admission gate for a future Fe/Zn multi-environment POTATO plot dataset.

This module VALIDATES hypothetical/imported external files; it does not
generate plot observations and does not fit G×E models.

One plot carries yield and paired raw edible-flesh Fe/Zn assays. A different
sampling hierarchy (e.g., pooled lab samples) needs a separately preregistered
design: never fabricate plot-level results from genotype means.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path

TRAITS = {
    "iron": ("mg/kg_dry", "raw", "peeled_flesh"),
    "zinc": ("mg/kg_dry", "raw", "peeled_flesh"),
    "tuber_yield": ("kg/plot_fresh", "raw", "whole_tuber"),
}
FIELDS = {
    "trial_id","genotype_id","location_id","season_id","block_id",
    "plot_id","trait","value","unit","processing","tissue",
    "plot_area_m2","source_id",
}


def positive(raw, label):
    try:
        v=Decimal(raw)
    except (ValueError,InvalidOperation) as exc:
        raise ValueError(f"{label}: invalid number") from exc
    if not v.is_finite() or v<=0:
        raise ValueError(f"{label}: expected positive finite value")
    return v


def inspect(path: Path) -> dict:
    path=Path(path)
    with path.open(newline="",encoding="utf-8") as f:
        reader=csv.DictReader(f)
        if set(reader.fieldnames or ())!=FIELDS:
            raise ValueError("Unapproved plot-level schema; never infer columns from names")
        records=list(reader)
    if not records:
        raise ValueError("Empty dataset")
    trials={r["trial_id"] for r in records}
    if len(trials)!=1 or not next(iter(trials)):
        raise ValueError("Exactly one declared trial_id is required")
    plots=defaultdict(dict)
    meta={}
    env_gen=defaultdict(set)
    plot_source=set()
    for index,r in enumerate(records,2):
        if any(not str(r[field]).strip() for field in FIELDS):
            raise ValueError(f"Missing value at CSV line {index}: empty cannot become zero")
        if r["trait"] not in TRAITS:
            raise ValueError(f"Unknown trait at line {index}: {r['trait']}")
        units,processing,tissue=TRAITS[r["trait"]]
        if (r["unit"],r["processing"],r["tissue"])!=(units,processing,tissue):
            raise ValueError(f"Incompatible units/basis/processing in {r['trait']} at line {index}")
        observed=positive(r["value"],f"line {index}, value")
        area=positive(r["plot_area_m2"],f"line {index}, area")
        if not r["genotype_id"].strip() or not r["location_id"].strip() or not r["season_id"].strip():
            raise ValueError("Missing genotype or environment")
        key=(r["trial_id"],r["location_id"],r["season_id"],r["genotype_id"],r["block_id"],r["plot_id"])
        if r["trait"] in plots[key]:
            raise ValueError(f"Duplicate plot-trait analytical value at line {index}")
        plots[key][r["trait"]]=observed
        if key in meta and meta[key]!=(area,r["source_id"]):
            raise ValueError("Inconsistent plot area or source within biological plot")
        meta[key]=(area,r["source_id"])
        env_gen[(r["location_id"],r["season_id"])].add(r["genotype_id"])
        plot_source.add((key,r["source_id"]))
    if any(set(values)!=set(TRAITS) for values in plots.values()):
        raise ValueError("Incomplete paired Fe/Zn/yield per plot: cannot invent biological pairs")
    locations={x[0] for x in env_gen}
    if len(locations)<2 or len(env_gen)<2:
        raise ValueError("At least two distinct locations/environments needed for cross-location validation")
    genotype_sets=list(env_gen.values())
    all_genotypes=set.union(*genotype_sets)
    if len(all_genotypes)<3:
        raise ValueError("Need at least three identified genotypes for this quality gate")
    if any(s!=all_genotypes for s in genotype_sets):
        raise ValueError("Unbalanced genotype × environment design; analyze missingness separately")
    biological=defaultdict(set)
    for key in plots:
        biological[(key[1],key[2],key[3])].add((key[4],key[5]))
    if any(len(items)<2 for items in biological.values()):
        raise ValueError("Each genotype/environment needs >=2 distinct biological plot replicates")
    if any(len(items)!=(len({x[0] for x in items})) for items in biological.values()):
        raise ValueError("Repeated block IDs within genotype/environment; review design")
    p=hashlib.sha256(path.read_bytes()).hexdigest()
    return {
        "status":"admissible_for_expert_design_review_only",
        "source_sha256":p,
        "trial_id":next(iter(trials)),
        "genotypes":len(all_genotypes),
        "locations":len(locations),
        "environments":len(env_gen),
        "biological_plots":len(plots),
        "numeric_observations":len(records),
        "nutrient_unit":"mg/kg_dry",
        "yield_unit":"kg/plot_fresh",
        "plot_area_recorded":True,
        "no_statistical_model_fitted":True,
        "notes":[
            "Passing schema checks does NOT validate randomization, analytical assay or independence.",
            "Missing and censored values require separate models; never encode ND as zero.",
            "Plot area must be used before comparing yield across sites with different plot sizes.",
            "Converted fresh-weight nutrient concentration requires matched dry matter and edible fraction.",
            "Do not pool or fake Fe/Zn values from papers reporting genotype means only.",
            "Do not infer causality, genotype effect or G×E significance without expert model review.",
        ],
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--csv",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    result=inspect(args.csv)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()

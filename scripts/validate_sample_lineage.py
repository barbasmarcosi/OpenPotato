"""M1-14: fail-closed chain of custody for future AUTHORISED plot mineral data.

This audit handles source files ON THE LOCAL MACHINE ONLY. It never emits
raw plots, sample IDs, names, GPS, individual assays or biological estimates.
Reports are metadata-only, insufficient to perform GxE or varietal ranking.
Rights, ethics, laboratory calibration and experimental independence still
require expert inspection even when structures are internally consistent.

Inputs: plots.csv, samples.csv, sample_plots.csv, assays.csv, harvest.csv.
NO source rows from the restricted CIP datasets are bundled or downloaded.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

PLOT_COLS = {
    "trial_id", "site_id", "season_id", "block_id", "plot_id",
    "genotype_id", "plot_area_m2",
}
SAMPLE_COLS = {
    "sample_id", "trial_id", "sample_design", "tissue", "processing",
    "sampling_date", "source_id",
}
MEMBERSHIP_COLS = {
    "sample_id", "trial_id", "site_id", "season_id", "block_id", "plot_id",
}
ASSAY_COLS = {
    "assay_id", "sample_id", "trait", "measurement_kind", "qualifier",
    "value", "limit_value", "unit", "method", "lab_id",
}
HARVEST_COLS = {
    "trial_id", "site_id", "season_id", "block_id", "plot_id",
    "harvested_kg_fresh", "harvest_area_m2",
}
STUDY_COLS = {
    "plots": PLOT_COLS, "samples": SAMPLE_COLS,
    "sample_plots": MEMBERSHIP_COLS, "assays": ASSAY_COLS,
    "harvest": HARVEST_COLS,
}
TRAITS = {"iron", "zinc"}
MEASUREMENT_KINDS = {"primary", "technical_replicate"}
QUALIFIERS = {"quantified", "below_detection", "below_quantification"}
SAMPLE_DESIGNS = {"single_plot", "pooled_plots"}
METHODS = {"XRF", "ICP-MS"}
UNIT = "mg/kg_dry"
NO_MODEL = "NO_MODEL_FITTED_REVIEW_ONLY"


def fingerprint(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path, expected: set[str], name: str) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        if len(fields) != len(set(fields)) or set(fields) != expected:
            raise ValueError(f"{name}: unapproved, missing or duplicate CSV headers")
        out = []
        for row in reader:
            if None in row or any(row.get(k) is None for k in fields):
                raise ValueError(f"{name}: malformed CSV row")
            # Blank is acceptable ONLY for assay value/limit fields with a
            # documented qualifier; all IDs and metadata must be nonblank.
            optional = {"value", "limit_value"} if name == "assays" else set()
            if any(not row[k].strip() for k in fields if k not in optional):
                raise ValueError(f"{name}: missing required identifier or metadata")
            out.append({k: v.strip() for k, v in row.items()})
    if not out:
        raise ValueError(f"{name}: empty source table")
    return out


def positive(value: str, label: str) -> Decimal:
    try:
        d = Decimal(value)
    except (InvalidOperation, ValueError):
        raise ValueError(f"{label}: invalid decimal") from None
    if not d.is_finite() or d <= 0:
        raise ValueError(f"{label}: expected positive finite value")
    return d


def plot_key(row: dict[str, str]) -> tuple[str, ...]:
    return tuple(row[k] for k in (
        "trial_id", "site_id", "season_id", "block_id", "plot_id"
    ))


def audit(plots_path: Path, samples_path: Path, membership_path: Path,
          assays_path: Path, harvest_path: Path, out: Path) -> dict:
    inputs = {
        "plots": Path(plots_path), "samples": Path(samples_path),
        "sample_plots": Path(membership_path), "assays": Path(assays_path),
        "harvest": Path(harvest_path),
    }
    # Do not parse rows into report/logs; messages intentionally omit source IDs.
    tables = {name: read_csv(path, STUDY_COLS[name], name)
              for name, path in inputs.items()}
    trial_ids = {row["trial_id"] for name in ("plots", "samples", "sample_plots", "harvest")
                 for row in tables[name]}
    if len(trial_ids) != 1:
        raise ValueError("Declared trial identity is inconsistent")

    plots: dict[tuple[str, ...], dict[str, str]] = {}
    env_gen: defaultdict[tuple[str, str], set[str]] = defaultdict(set)
    biological_reps: defaultdict[tuple[str, str, str], set[str]] = defaultdict(set)
    for row in tables["plots"]:
        key = plot_key(row)
        if key in plots:
            raise ValueError("Duplicate physical plot (including conflicting genotype)")
        positive(row["plot_area_m2"], "plot area")
        plots[key] = row
        env = (row["site_id"], row["season_id"])
        env_gen[env].add(row["genotype_id"])
        rep_key = (row["site_id"], row["season_id"], row["genotype_id"])
        if row["block_id"] in biological_reps[rep_key]:
            raise ValueError("Same genotype appears multiple times in an environment block")
        biological_reps[rep_key].add(row["block_id"])

    samples: dict[str, dict[str, str]] = {}
    for row in tables["samples"]:
        if row["sample_id"] in samples:
            raise ValueError("Duplicate sample identifier")
        if row["sample_design"] not in SAMPLE_DESIGNS:
            raise ValueError("Undeclared or unknown sampling hierarchy")
        if row["tissue"] != "peeled_flesh" or row["processing"] != "raw":
            raise ValueError("Incompatible tuber tissue or processing for this audit")
        try:
            date.fromisoformat(row["sampling_date"])
        except ValueError:
            raise ValueError("Sample date is not a valid ISO calendar date") from None
        samples[row["sample_id"]] = row

    sample_plots: defaultdict[str, set[tuple[str, ...]]] = defaultdict(set)
    for row in tables["sample_plots"]:
        sid = row["sample_id"]
        if sid not in samples:
            raise ValueError("Sample-to-plot record without registered sample")
        if row["trial_id"] != samples[sid]["trial_id"]:
            raise ValueError("Sample trial inconsistent with physical plot trial")
        key = plot_key(row)
        if key not in plots:
            raise ValueError("Sample membership references unknown physical plot")
        if key in sample_plots[sid]:
            raise ValueError("Repeated membership does not make a biological replicate")
        sample_plots[sid].add(key)
    if set(sample_plots) != set(samples):
        raise ValueError("Sample missing an explicit original plot membership")

    pooled = set()
    plot_single_samples: defaultdict[tuple[str, ...], set[str]] = defaultdict(set)
    for sid, record in samples.items():
        members = sample_plots[sid]
        if record["sample_design"] == "single_plot":
            if len(members) != 1:
                raise ValueError("Single-plot sample has more than one source plot")
            plot_single_samples[next(iter(members))].add(sid)
        else:
            if len(members) < 2:
                raise ValueError("Pooled sample requires two or more actual plots")
            pooled.add(sid)
            # Never accept cross-genotype or cross-environment mixing as one
            # biological observation even if the assay looks numerically valid.
            environments_genotypes = {
                (plots[k]["site_id"], plots[k]["season_id"], plots[k]["genotype_id"])
                for k in members
            }
            if len(environments_genotypes) != 1:
                raise ValueError("Mixed genotypes/environments in pooled chemical sample")

    primary: dict[tuple[str, str], dict[str, str]] = {}
    all_assay_ids: set[str] = set()
    technical: Counter[tuple[str, str]] = Counter()
    censored: Counter[str] = Counter()
    for row in tables["assays"]:
        if row["sample_id"] not in samples:
            raise ValueError("Assay references unknown biological sample")
        if row["assay_id"] in all_assay_ids:
            raise ValueError("Duplicate analytical assay ID")
        all_assay_ids.add(row["assay_id"])
        if row["trait"] not in TRAITS or row["measurement_kind"] not in MEASUREMENT_KINDS:
            raise ValueError("Unknown mineral trait or analytic replicate kind")
        if row["method"] not in METHODS or not row["lab_id"]:
            raise ValueError("Unknown laboratory method or missing lab provenance")
        if row["unit"] != UNIT or row["qualifier"] not in QUALIFIERS:
            raise ValueError("Unknown fresh/dry basis or censored-value qualifier")
        qualifier = row["qualifier"]
        if qualifier == "quantified":
            positive(row["value"], "quantified assay")
            if row["limit_value"] != "":
                raise ValueError("Quantified assay cannot have censoring limit in this schema")
        else:
            if row["value"] != "":
                raise ValueError("Censored assay must not impute a numeric concentration")
            positive(row["limit_value"], "censoring detection/quantification bound")
            censored[qualifier] += 1
        key = (row["sample_id"], row["trait"])
        if row["measurement_kind"] == "primary":
            if key in primary:
                raise ValueError("Duplicate primary sample-trait assay")
            primary[key] = row
        else:
            technical[key] += 1
    # A technical repeat must not substitute for the original primary assay.
    if set(technical) - set(primary):
        raise ValueError("Technical assay repeat without declared primary measurement")

    harvest = {}
    for row in tables["harvest"]:
        key = plot_key(row)
        if key not in plots:
            raise ValueError("Harvest references unknown physical plot")
        if key in harvest:
            raise ValueError("Duplicate harvested yield for one physical plot")
        area = positive(row["harvest_area_m2"], "harvest area")
        if area > positive(plots[key]["plot_area_m2"], "registered plot area"):
            raise ValueError("Harvested area exceeds registered plot area")
        positive(row["harvested_kg_fresh"], "fresh harvest mass")
        harvest[key] = row

    missing_yields = len(set(plots) - set(harvest))
    no_single_sample = len(set(plots) - set(plot_single_samples))
    multi_single_samples = sum(len(sids) > 1 for sids in plot_single_samples.values())
    complete_pairs = sum(
        len(sids) == 1 and all(
            (next(iter(sids)), trait) in primary
            and primary[(next(iter(sids)), trait)]["qualifier"] == "quantified"
            for trait in TRAITS
        )
        for plot, sids in plot_single_samples.items()
        if plot in harvest
    )
    incomplete_assays = sum(
        sum((sid, trait) not in primary for trait in TRAITS)
        for sid in samples for _ in (0,)
    )
    distinct_sites = {site for site, season in env_gen}
    all_genotypes = set().union(*env_gen.values()) if env_gen else set()
    balanced = bool(env_gen) and all(s == all_genotypes for s in env_gen.values())
    enough_reps = all(len(v) >= 2 for v in biological_reps.values())
    structural_candidate = (
        len(distinct_sites) >= 2 and len(all_genotypes) >= 3 and
        balanced and enough_reps and missing_yields == 0 and
        no_single_sample == 0 and multi_single_samples == 0 and not pooled and
        complete_pairs == len(plots) and incomplete_assays == 0 and
        not censored and len(primary) == 2 * len(plots)
    )
    # This remains a review-only gate regardless of apparent completeness:
    # rights, assay validity, pooled biology, calibration and randomisation
    # cannot be established by tabular internal consistency alone.
    status = ("STRUCTURALLY_LINKED_EXPERT_REVIEW_REQUIRED"
              if structural_candidate else "BLOCKED_INCOMPLETE_OR_NONINDEPENDENT_EVIDENCE")

    report = {
        "status": status,
        "statistical_model": NO_MODEL,
        "raw_records_exported": False,
        "authorisation_and_licence_verification": "NOT_DONE_BY_SOFTWARE",
        "source_sha256": {name: fingerprint(path) for name, path in inputs.items()},
        "source_row_counts": {name: len(rows) for name, rows in tables.items()},
        "trial_count": len(trial_ids),
        "site_count": len(distinct_sites),
        "site_year_environments": len(env_gen),
        "genotypes": len(all_genotypes),
        "physical_plots": len(plots),
        "sample_records": len(samples),
        "single_plot_samples": len(samples) - len(pooled),
        "pooled_sample_records": len(pooled),
        "plot_membership_rows": len(tables["sample_plots"]),
        "quantified_primary_assays": sum(r["qualifier"] == "quantified"
                                         for r in primary.values()),
        "technical_assays_not_biological_replicates": sum(technical.values()),
        "censored_assays_without_zero_imputation": sum(censored.values()),
        "incomplete_primary_sample_trait_pairs": incomplete_assays,
        "plots_missing_harvest": missing_yields,
        "plots_without_single_plot_sample": no_single_sample,
        "plots_with_multiple_single_plot_samples_no_auto_averaging": multi_single_samples,
        "complete_eligible_plot_pairs_with_yield": complete_pairs,
        "balanced_genotype_coverage": balanced,
        "at_least_two_biological_blocks_per_genotype_environment": enough_reps,
        "limitations": [
            "No source rows or source IDs retained in output/logs.",
            "Biological independence, field randomisation and assessor calibration unverified.",
            "Technical replicates never counted as biological samples or environmental replications.",
            "A pooled sample is not back-projected onto its individual source plots.",
            "No censored assay value is treated as zero or numeric data.",
            "An uncalibrated or unauthorized dataset may not be analysed despite passing structural checks.",
            "No GxE fit, hypothesis test, heritability, nutritional ranking or safety claim.",
            "Yield is fresh kg/plot; Fe/Zn are dry mg/kg. No basis conversion or nutritional yield inferred.",
        ],
    }
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "sample_lineage_readiness.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    (out / "sample_lineage_readiness.md").write_text(
        "# OP-M1-14 — Validación de procedencia de muestras minerales\n\n"
        f"**Estado:** \`{status}\` — NO se ajustó ningún modelo G×E.\n\n"
        f"- {len(plots)} parcelas físicas registradas, {len(samples)} muestras identificadas.\n"
        f"- {len(pooled)} muestras agrupadas; {sum(technical.values())} réplicas técnicas "
        "no tratadas como observaciones biológicas.\n"
        f"- {sum(censored.values())} ensayos censurados conservados sin imputar cero.\n"
        f"- {complete_pairs} parcelas con un enlace singular a Fe/Zn cuantificados y cosecha, "
        "**todavía sin verificar independencia ni calibración**.\n\n"
        "Nunca se exportan filas de participantes, IDs de muestras o datos de parcelas.\n"
        "Hace falta revisar diseño, origen de claves, derechos, ética y QC de laboratorio.\n",
        encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in STUDY_COLS:
        parser.add_argument("--" + name.replace("_", "-"), required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    report = audit(args.plots, args.samples, args.sample_plots,
                   args.assays, args.harvest, args.out)
    # Standard output contains *counts and status only*. No sensitive IDs.
    print(json.dumps({
        "status": report["status"],
        "physical_plots": report["physical_plots"],
        "sample_records": report["sample_records"],
        "statistical_model": report["statistical_model"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()

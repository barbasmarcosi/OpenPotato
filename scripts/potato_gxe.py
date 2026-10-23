"""Multi-environment potato trial: descriptive G × E decomposition.

Demonstration based on Tai (1971), redisplayed as agridat::tai.potato
through Rdatasets. Data are GENOTYPE-ENVIRONMENT MEANS of kg/plot yield,
not individual plots, and contain NO mineral concentrations.

No p-values/heritability/BLUPs or individual experimental errors inferred.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from decimal import Decimal, InvalidOperation, getcontext
from itertools import combinations
from pathlib import Path

getcontext().prec = 32
SOURCE_COMMIT = "1dcc2bf5f955cc1224a3e1307256e1fe86b68dae"
SOURCE_URL = (f"https://raw.githubusercontent.com/vincentarelbundock/Rdatasets/"
              f"{SOURCE_COMMIT}/csv/agridat/tai.potato.csv")
DOI = "10.2135/cropsci1971.0011183X001100020006x"
FIELDS = {"rownames", "yield", "gen", "variety", "env", "loc", "year"}
GENOTYPE_COUNT = 8
ENVIRONMENT_COUNT = 6
EXPECTED_LOCATIONS = {"NB", "NS", "PEI"}
EXPECTED_YEARS = {"65", "66"}


def filehash(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def decimal(raw: str, *, label: str) -> Decimal:
    try:
        d = Decimal(raw)
    except (InvalidOperation, ValueError) as error:
        raise ValueError(f"Invalid numeric {label}: {raw!r}") from error
    if not d.is_finite() or d <= 0:
        raise ValueError(f"Nonpositive/nonfinite {label}: {raw!r}")
    return d


def read_matrix(path: Path) -> tuple[dict[tuple[str, str], Decimal], dict, dict]:
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if set(reader.fieldnames or ()) != FIELDS:
            raise ValueError("Unexpected tai.potato schema")
        rows = list(reader)
    if len(rows) != GENOTYPE_COUNT * ENVIRONMENT_COUNT:
        raise ValueError("Expected 48 genotype-environment aggregate means")
    data = {}
    gen_to_variety = {}
    env_to_location_year = {}
    row_ids = set()
    for r in rows:
        number = r["rownames"]
        if not number.isdigit() or number in row_ids:
            raise ValueError("Missing or repeated source row IDs")
        row_ids.add(number)
        genotype, environment = r["gen"], r["env"]
        if not genotype or not environment or not r["variety"]:
            raise ValueError("Missing genotype/environment/variety")
        if r["loc"] not in EXPECTED_LOCATIONS or r["year"] not in EXPECTED_YEARS:
            raise ValueError(f"Unknown location or year: {r['loc']} / {r['year']}")
        key = (genotype, environment)
        if key in data:
            raise ValueError(f"Duplicated genotype/environment: {key}")
        data[key] = decimal(r["yield"], label=str(key))
        if genotype in gen_to_variety and gen_to_variety[genotype] != r["variety"]:
            raise ValueError(f"Contradictory genotype identity: {genotype}")
        gen_to_variety[genotype] = r["variety"]
        meta = (r["loc"], r["year"])
        if environment in env_to_location_year and env_to_location_year[environment] != meta:
            raise ValueError(f"Environment {environment} has inconsistent location/year")
        env_to_location_year[environment] = meta
    if row_ids != {str(i) for i in range(1,49)}:
        raise ValueError("Unexpected row ID coverage")
    if len(gen_to_variety) != GENOTYPE_COUNT or len(env_to_location_year) != ENVIRONMENT_COUNT:
        raise ValueError("Unbalanced numbers of genotypes and environments")
    if set(env_to_location_year.values()) != {
        (loc, year) for loc in EXPECTED_LOCATIONS for year in EXPECTED_YEARS
    }:
        raise ValueError("Expected each location × year combination exactly once")
    if set(data) != {
        (gen, env) for gen in gen_to_variety for env in env_to_location_year
    }:
        raise ValueError("Unbalanced matrix; no imputation allowed")
    return data, gen_to_variety, env_to_location_year


def analyze(path: Path, output: Path, *, pinned_sha256: str | None = None) -> dict:
    source_hash = filehash(path)
    if pinned_sha256 is not None and source_hash != pinned_sha256:
        raise ValueError("Dataset SHA-256 changed; refusing new source release")
    data, genmeta, envmeta = read_matrix(path)
    genotypes = sorted(genmeta)
    environments = sorted(envmeta)
    n_gen, n_env = len(genotypes), len(environments)
    values = list(data.values())
    overall = sum(values) / Decimal(len(values))
    gmean = {g: sum(data[g,e] for e in environments)/Decimal(n_env) for g in genotypes}
    emean = {e: sum(data[g,e] for g in genotypes)/Decimal(n_gen) for e in environments}

    # Exact algebraic identity for one aggregate mean per G×E cell.
    gss = Decimal(n_env) * sum((x-overall)**2 for x in gmean.values())
    ess = Decimal(n_gen) * sum((x-overall)**2 for x in emean.values())
    iss = sum((data[g,e]-gmean[g]-emean[e]+overall)**2
              for g in genotypes for e in environments)
    totalss = sum((x-overall)**2 for x in values)
    if abs((gss+ess+iss)-totalss) > Decimal("0.0000000000000000000001"):
        raise ValueError("G + E + interaction identity did not balance")
    # No residual error estimate: input is one mean per genotype × environment.
    winner_by_environment = {}
    for e in environments:
        top = max(data[g,e] for g in genotypes)
        winner_by_environment[e] = sorted(g for g in genotypes if data[g,e]==top)
    crossovers = []
    for a,b in combinations(genotypes,2):
        wins_a = sum(data[a,e] > data[b,e] for e in environments)
        wins_b = sum(data[b,e] > data[a,e] for e in environments)
        if wins_a and wins_b:
            crossovers.append({"genotype_a":a,"genotype_b":b,
                               "environments_a_higher":wins_a,
                               "environments_b_higher":wins_b,
                               "tied":n_env-wins_a-wins_b})
    records=[]
    for g in genotypes:
        residuals=[data[g,e]-gmean[g]-emean[e]+overall for e in environments]
        records.append({
            "genotype":g, "variety":genmeta[g],
            "mean_yield_kg_per_plot":str(gmean[g]),
            "min_yield_kg_per_plot":str(min(data[g,e] for e in environments)),
            "max_yield_kg_per_plot":str(max(data[g,e] for e in environments)),
            "interaction_rms_kg_per_plot":
                str((sum(x*x for x in residuals)/Decimal(n_env)).sqrt()),
            "environment_wins":str(sum(g in winners for winners in winner_by_environment.values())),
            "n_environments":str(n_env), "observation_level":"published_aggregate_means",
        })
    output=Path(output)
    output.mkdir(parents=True,exist_ok=True)
    summarycsv=output/"yield_stability.csv"
    with summarycsv.open("w",encoding="utf-8",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    crosscsv=output/"rank_crossovers.csv"
    with crosscsv.open("w",encoding="utf-8",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=[
            "genotype_a","genotype_b","environments_a_higher",
            "environments_b_higher","tied"
        ])
        writer.writeheader();writer.writerows(crossovers)
    # Published data are aggregate means. Their residual differences are G×E
    # descriptors; they cannot estimate within-plot experimental error.
    summary = {
        "source":SOURCE_URL,"source_project":"Rdatasets / agridat::tai.potato",
        "original_study_doi": DOI,
        "source_sha256":source_hash,
        "derived_files":{
            "yield_stability.csv":filehash(summarycsv),
            "rank_crossovers.csv":filehash(crosscsv),
        },
        "genotypes":n_gen,"environments":n_env,
        "locations":sorted(EXPECTED_LOCATIONS),
        "years":["1965","1966"],
        "one_mean_per_genotype_environment":True,
        "trait":"tuber yield, kg/plot (NO Fe/Zn values)",
        "total_sum_squares":str(totalss),
        "genotype_sum_squares":str(gss),
        "environment_sum_squares":str(ess),
        "interaction_sum_squares":str(iss),
        "genotype_share_of_total":str(gss/totalss),
        "environment_share_of_total":str(ess/totalss),
        "interaction_share_of_total":str(iss/totalss),
        "pairwise_rank_crossovers":len(crossovers),
        "pairs_of_genotypes":len(genotypes)*(len(genotypes)-1)//2,
        "no_residual_variance_estimate":True,
        "limitations":[
            "Historical multienvironment YIELD ONLY trial, not nutritional biofortification.",
            "One published mean per G×E cell from originally 4-rep design; plot-level values unavailable here.",
            "Sum-of-squares breakdown describes point estimates, NOT ANOVA F-tests or heritability.",
            "Interaction RMS and crossover counts are descriptive, not genetic stability certification.",
            "kg/plot lacks fixed published plot-area here; never convert to tonnes/hectare.",
            "Data redistribution license must be checked before copying source CSV into repository."
        ],
    }
    manifest=output/"gxE_provenance.json"
    manifest.write_text(json.dumps(summary,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    lines=[
        "# OP-M1-05 — Ensayo multientorno de papa: validación del método",
        "",
        "**Fuente real: Tai (1971), agridat::tai.potato. Solo RENDIMIENTO (kg/parcela), no minerales.**",
        "**Datos disponibles: 8 genotipos × 6 ambientes = 48 medias publicadas, 3 localidades × 2 años.**",
        "El diseño original tuvo cuatro repeticiones; aquí NO existen las mediciones por parcela.",
        "",
        "## Descomposición descriptiva de los valores publicados",
        "",
        f"- Total SC: {totalss:.4f}",
        f"- Genotipo: {gss:.4f} ({100*gss/totalss:.1f}% de SC total)",
        f"- Ambiente: {ess:.4f} ({100*ess/totalss:.1f}%)",
        f"- Interacción genotipo × ambiente: {iss:.4f} ({100*iss/totalss:.1f}%)",
        f"- Cambios de orden entre genotipos: {len(crossovers)} de {summary['pairs_of_genotypes']} pares",
        "",
        "Las fracciones de suma de cuadrados **no** son porcentajes de heredabilidad ni causalidad;",
        "no se calculan valores p, F-tests, componentes de varianza de error ni predicciones de minerales.",
        "",
        "## Promedios y respuesta a ambientes (kg/parcela)",
        "",
        "| Genotipo | Nombre | Media | Mínimo–máximo | RMS interacción | Ambientes ganados |",
        "|---|---|---:|---|---:|---:|",
    ]
    for row in sorted(records,key=lambda r:Decimal(r["mean_yield_kg_per_plot"]),reverse=True):
        lines.append(
            f'| {row["genotype"]} | {row["variety"]} | '
            f'{Decimal(row["mean_yield_kg_per_plot"]):.3f} | '
            f'{row["min_yield_kg_per_plot"]}–{row["max_yield_kg_per_plot"]} | '
            f'{Decimal(row["interaction_rms_kg_per_plot"]):.3f} | {row["environment_wins"]} |'
        )
    lines += [
        "",
        "## Límite innegociable",
        "",
        "Esta validación sirve para comprobar análisis multientorno de **rendimiento**,",
        "pero no permite decir nada sobre G×E de hierro y zinc.",
        "Para M1-05 nutricional faltan archivos primarios genotipo × ambiente × bloque/parcela",
        "con Fe/Zn, método analítico, materia seca y rendimiento compatible.",
        "",
        f"Artículo original: https://doi.org/{DOI}",
        f"Dataset reproducible: {SOURCE_URL}",
        f"SHA-256 fuente: {source_hash}",
        "",
    ]
    (output/"gxE_report.md").write_text("\n".join(lines),encoding="utf-8")
    return summary


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--sha256",help="Pinned source SHA256 (required for CI)",required=True)
    args=parser.parse_args()
    print(json.dumps(analyze(args.csv,args.out,pinned_sha256=args.sha256),ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()

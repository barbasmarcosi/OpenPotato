"""M1-15: prospective design simulation; not measured potato genetics or nutrition.

Compare two hypothetical genotypes in paired randomized blocks. An environmental
contrast has genotype-by-environment variation plus independent biological plot
error and technical assay error. Only the mean contrast of each INDEPENDENT SITE
is a statistical test unit (Student two-sided 5% t-test with df=n_sites-1).

This script DOES NOT fit to CIP data; all effect sizes and SDs are ASSUMPTIONS.
Yearly repeats at the same location may be correlated and require another model.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import random
from dataclasses import asdict, dataclass
from pathlib import Path

T975 = {2: 4.3026527299, 5: 2.5705818356, 8: 2.3060041352}


@dataclass(frozen=True)
class Design:
    independent_sites: int
    biological_blocks_per_site: int
    technical_readings_per_sample: int
    genotype_site_contrast_sd: float
    effect_in_plot_sd: float = 1.0
    biological_plot_sd: float = 1.0
    technical_assay_sd: float = 0.35

    def check(self):
        if self.independent_sites - 1 not in T975:
            raise ValueError("Only 3, 6 or 9 hypothetical independent sites supported")
        if self.biological_blocks_per_site not in (2, 3):
            raise ValueError("Only two or three biological blocks per site supported")
        if self.technical_readings_per_sample not in (1, 3):
            raise ValueError("Only one or three technical readings supported")
        if any(not math.isfinite(x) or x < 0 for x in (
            self.genotype_site_contrast_sd, self.effect_in_plot_sd,
            self.biological_plot_sd, self.technical_assay_sd)):
            raise ValueError("Effect and SD parameters must be finite and nonnegative")
        if self.biological_plot_sd == 0:
            raise ValueError("Nonzero biological variation scale required")


def site_contrast(rng, d, difference):
    # Gaussian mean contrast after paired block design, without invented field
    # plot data. Only biological blocks lower the plot-error term.
    environmental_difference = rng.gauss(0, d.genotype_site_contrast_sd)
    field_sd = math.sqrt(2 / d.biological_blocks_per_site) * d.biological_plot_sd
    assay_sd = math.sqrt(2 / (d.biological_blocks_per_site *
                              d.technical_readings_per_sample)) * d.technical_assay_sd
    return difference + environmental_difference + rng.gauss(0, field_sd) + rng.gauss(0, assay_sd)


def reject_ttest(site_means):
    n = len(site_means)
    mean = sum(site_means) / n
    sample_var = sum((x - mean)**2 for x in site_means) / (n - 1)
    if sample_var <= 0:
        return False   # zero error is not proof of infinite precision
    return abs(mean) / math.sqrt(sample_var / n) > T975[n - 1]


def simulate(d, draws=5000, seed=20261021):
    d.check()
    if not isinstance(draws, int) or draws < 500:
        raise ValueError("At least 500 Monte Carlo draws needed")
    if not isinstance(seed, int):
        raise ValueError("Random seed must be an integer")
    rng = random.Random(seed)
    significant = false_positive = 0
    for _ in range(draws):
        under_null = [site_contrast(rng, d, 0.0) for _ in range(d.independent_sites)]
        under_effect = [site_contrast(rng, d, d.effect_in_plot_sd)
                        for _ in range(d.independent_sites)]
        false_positive += reject_ttest(under_null)
        significant += reject_ttest(under_effect)
    power = significant / draws
    return {
        **asdict(d),
        "simulated_power": round(power, 5),
        "simulated_type_i_error": round(false_positive / draws, 5),
        "power_monte_carlo_se": round(math.sqrt(power * (1-power) / draws), 5),
        "inferential_units": "independent_site_contrast_means_not_lab_readings",
        "nominal_two_sided_alpha": 0.05,
        "draws": draws, "random_seed": seed,
        "simulation_only_not_empirical_evidence": True,
    }


def grid(draws=5000, seed=20261021):
    # Each magnitude is an invented sensitivity condition, NOT estimated
    # from CIP sample n, genotype means, pooled SDs or other measured trials.
    return [simulate(Design(sites, blocks, tech, gx), draws=draws, seed=seed)
            for gx in (0.6, 1.5)
            for sites in (3, 6, 9)
            for blocks, tech in ((2, 1), (3, 1), (3, 3))]


def create(out, draws=5000, seed=20261021):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    rows = grid(draws, seed)
    path = out/"synthetic_trial_design_sensitivity.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    manifest = {
        "status": "SIMULATION_ONLY_NO_REAL_TRIAL_OR_MINERAL_PHENOTYPES",
        "designs": len(rows),
        "draws_per_design": draws,
        "effect_assumed_in_plot_sd_units": 1.0,
        "biological_plot_sd_assumed": 1.0,
        "technical_assay_sd_assumed": 0.35,
        "GxE_site_contrast_sd_assumed": [0.6, 1.5],
        "random_seed": seed,
        "derived_csv_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "limitations": [
            "All biological effects and GxE variance are hypothetical; no real potato genotype is predicted.",
            "Site-year repetitions at the same site are correlated until proven otherwise.",
            "Technical repeats reduce assay error only; they never increase biological replication.",
            "Prospective power requires independent pilot estimates and an expert-designed model.",
            "The simulated two-genotype contrast cannot rank real cultivars.",
            "No mineral GxE results, nutritional yield, safety, bioavailability or field validation.",
        ],
    }
    (out/"synthetic_trial_design_provenance.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True)+"\n",
        encoding="utf-8")
    high = [r for r in rows if r["genotype_site_contrast_sd"] == 1.5
            and r["biological_blocks_per_site"] == 3
            and r["technical_readings_per_sample"] == 1]
    lines = [
        "# M1-15 — Simulación de sensibilidad experimental",
        "",
        "**Todo el efecto nutricional y su variación se SUPONEN para esta prueba.**",
        "No hay datos nuevos del CIP ni predicción de una variedad verdadera.",
        "",
        "Modelo: contraste de dos genotipos por bloques físicos emparejados,",
        "variación genotipo×sitio e imprecisión de parcela y laboratorio.",
        "Se calcula una prueba t de dos colas sobre contrastes de SITIOS independientes.",
        "",
        "Escenario hipotético de alta variación genotipo×sitio (SD = 1,5 veces",
        "la SD biológica de parcela) con tres bloques y una lectura por muestra:",
        "",
        "| Sitios independientes | Potencia simulada | Falsos positivos simulados |",
        "|---|---:|---:|",
    ]
    for r in high:
        lines.append(f"| {r['independent_sites']} | {r['simulated_power']:.1%} | "
                     f"{r['simulated_type_i_error']:.1%} |")
    lines += [
        "",
        "Otros 15 escenarios están en el CSV. Estos porcentajes no son ",
        "recomendaciones de tamaño de muestra para un cultivar real, porque no",
        "hemos medido ni calibrado la dispersión biológica, G×E o los errores.",
        "Las réplicas técnicas no se cuentan como sitios o parcelas.",
        "",
        "Se trata de simulación de diseño, NO de predicción de Fe/Zn, causalidad,",
        "rendimiento agronómico, seguridad o validación experimental.",
    ]
    (out/"synthetic_trial_design_report.md").write_text(
        "\n".join(lines)+"\n", encoding="utf-8")
    return manifest


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--draws", type=int, default=5000)
    p.add_argument("--seed", type=int, default=20261021)
    args = p.parse_args()
    print(json.dumps(create(args.out, args.draws, args.seed), indent=2))


if __name__ == "__main__":
    main()

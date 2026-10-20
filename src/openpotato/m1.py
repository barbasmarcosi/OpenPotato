"""OP-M1-001: cobertura dietaria exploratoria de papa hervida.

No prescribe dietas ni evalúa suficiencia clínica; calcula únicamente la razón
aporte de alimento / referencia dietaria documentada. Datos faltantes != cero.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FOOD = ROOT / "datasets" / "official" / "potato_fdc_170438_usda.csv"
DEFAULT_REFERENCES = ROOT / "datasets" / "adult_references_31_50.csv"
ALLOWED_UNITS = {"kcal", "g", "mg", "ug", "ug_RAE", "ug_DFE"}
OBSERVATION_STATUS = {"observed", "reported_zero", "not_reported"}
REFERENCE_KINDS = {"RDA", "AI"}


@dataclass(frozen=True)
class Observation:
    nutrient: str
    unit: str
    value: Decimal | None
    status: str
    source_id: str


@dataclass(frozen=True)
class Reference:
    profile: str
    nutrient: str
    value: Decimal
    unit: str
    kind: str
    source_id: str


def _number(raw: str, *, location: str, allow_zero: bool = True) -> Decimal:
    try:
        value = Decimal(raw)
    except (InvalidOperation, ValueError) as error:
        raise ValueError(f"{location}: número inválido: {raw!r}") from error
    if not value.is_finite() or value < 0 or (not allow_zero and value == 0):
        raise ValueError(f"{location}: número fuera de rango: {raw!r}")
    return value


def load_food(path: Path) -> dict[str, Observation]:
    result: dict[str, Observation] = {}
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        expected = {"nutrient", "unit", "amount_per_100g", "status", "source_id"}
        if set(reader.fieldnames or ()) != expected:
            raise ValueError(f"{path}: esquema de composición incorrecto")
        for line, row in enumerate(reader, 2):
            nutrient = row["nutrient"].strip()
            unit = row["unit"].strip()
            status = row["status"].strip()
            raw = row["amount_per_100g"].strip()
            source = row["source_id"].strip()
            if not nutrient or nutrient in result or not source:
                raise ValueError(f"{path}:{line}: identificador duplicado/vacío o fuente ausente")
            if unit not in ALLOWED_UNITS or status not in OBSERVATION_STATUS:
                raise ValueError(f"{path}:{line}: unidad/estado no admitido")
            if status == "not_reported":
                if raw:
                    raise ValueError(f"{path}:{line}: dato faltante no puede tener cantidad")
                value = None
            else:
                if not raw:
                    raise ValueError(f"{path}:{line}: cantidad ausente sin marca de faltante")
                value = _number(raw, location=f"{path}:{line}")
                if status == "reported_zero" and value != 0:
                    raise ValueError(f"{path}:{line}: reported_zero exige valor cero")
            result[nutrient] = Observation(nutrient, unit, value, status, source)
    energy = result.get("energy_kcal")
    if not energy or energy.value is None or energy.value <= 0 or energy.unit != "kcal":
        raise ValueError("Se necesita energía positiva por 100 g en kcal")
    return result


def load_references(path: Path) -> dict[str, dict[str, Reference]]:
    result: dict[str, dict[str, Reference]] = {}
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        expected = {"profile", "nutrient", "reference_value", "unit", "kind", "source_id"}
        if set(reader.fieldnames or ()) != expected:
            raise ValueError(f"{path}: esquema de requerimientos incorrecto")
        for line, row in enumerate(reader, 2):
            profile = row["profile"].strip()
            nutrient = row["nutrient"].strip()
            unit = row["unit"].strip()
            kind = row["kind"].strip()
            source = row["source_id"].strip()
            if not profile or not nutrient or not source or kind not in REFERENCE_KINDS or unit not in ALLOWED_UNITS:
                raise ValueError(f"{path}:{line}: requerimiento inválido")
            table = result.setdefault(profile, {})
            if nutrient in table:
                raise ValueError(f"{path}:{line}: requerimiento duplicado")
            value = _number(row["reference_value"], location=f"{path}:{line}", allow_zero=False)
            table[nutrient] = Reference(profile, nutrient, value, unit, kind, source)
    if not result:
        raise ValueError("No hay perfiles en requerimientos")
    return result


def compute_rows(food: dict[str, Observation], refs: dict[str, Reference], grams: Decimal) -> list[dict[str, str]]:
    if not grams.is_finite() or grams <= 0:
        raise ValueError("La cantidad de papa debe ser positiva y finita")
    records = []
    for nutrient in sorted(set(food) | set(refs)):
        item = food.get(nutrient)
        reference = refs.get(nutrient)
        if item and reference and item.unit != reference.unit:
            raise ValueError(f"Unidades incompatibles en {nutrient}: {item.unit} vs {reference.unit}")
        unit = item.unit if item else reference.unit
        amount = (item.value * grams / 100) if item and item.value is not None else None
        pct = (amount / reference.value * 100) if amount is not None and reference else None
        if amount is None:
            state = "not_reported"
        elif not reference:
            state = "no_reference"
        elif pct >= 100:
            state = "at_or_above_reference"
        else:
            state = "below_reference"
        records.append({
            "nutrient": nutrient,
            "unit": unit,
            "amount": str(amount) if amount is not None else "",
            "reference": str(reference.value) if reference else "",
            "reference_kind": reference.kind if reference else "",
            "coverage_percent": str(pct) if pct is not None else "",
            "status": state,
            "food_status": item.status if item else "not_reported",
            "food_source_id": item.source_id if item else "",
            "reference_source_id": reference.source_id if reference else "",
        })
    return records


def energy_equivalent_grams(food: dict[str, Observation], energy_kcal: Decimal) -> Decimal:
    if not energy_kcal.is_finite() or energy_kcal <= 0:
        raise ValueError("El objetivo energético debe ser positivo")
    return energy_kcal * Decimal(100) / food["energy_kcal"].value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(*, food_path: Path, reference_path: Path, output_dir: Path,
        grams_list: tuple[Decimal, ...], energy_kcal: Decimal) -> dict:
    food = load_food(food_path)
    references = load_references(reference_path)
    for grams in grams_list:
        if not grams.is_finite() or grams <= 0:
            raise ValueError("Cantidad inválida")
    equivalent = energy_equivalent_grams(food, energy_kcal)
    scenarios = list(grams_list) + [equivalent]
    rows: list[dict[str, str]] = []
    for profile, profile_refs in sorted(references.items()):
        for index, grams in enumerate(scenarios):
            name = f"{grams}g" if index < len(grams_list) else f"equivalente_{energy_kcal}kcal"
            for row in compute_rows(food, profile_refs, grams):
                rows.append({
                    "profile": profile,
                    "scenario": name,
                    "grams": str(grams),
                    **row,
                })
    output_dir.mkdir(parents=True, exist_ok=True)
    cols = ["profile", "scenario", "grams", "nutrient", "unit", "amount",
            "reference", "reference_kind", "coverage_percent", "status",
            "food_status", "food_source_id", "reference_source_id"]
    out_csv = output_dir / "coverage.csv"
    with out_csv.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=cols)
        writer.writeheader()
        writer.writerows(rows)
    manifest = {
        "experiment_id": "OP-M1-001",
        "state": "exploratory_reanalysis_not_clinical",
        "food_id": food["energy_kcal"].source_id,
        "energy_equivalent_grams": str(equivalent),
        "energy_target_kcal_is_hypothetical": str(energy_kcal),
        "profiles": sorted(references),
        "grams_scenarios": [str(v) for v in grams_list],
        "datasets": {
            "food": {"filename": food_path.name, "sha256": digest(food_path)},
            "references": {"filename": reference_path.name, "sha256": digest(reference_path)},
        },
        "limitations": [
            "No es una dieta recomendada ni una evaluación clínica.",
            "Consultar la procedencia en el CSV y datasets/official/provenance.json; fuente SR Legacy histórica, no medidas actuales por cultivar.",
            "Comparación dietaria con RDA/AI no mide biodisponibilidad, déficit individual ni seguridad.",
            "Por debajo de AI no prueba insuficiencia; superar RDA no prueba seguridad ni cobertura completa.",
            "Cero informado no garantiza ausencia química; falta de dato no equivale a cero.",
            "No se modelan ácidos grasos esenciales sin identificación analítica inequívoca.",
            "No se modelan UL, variación varietal, glicoalcaloides ni pérdidas poscosecha.",
            "El escenario energético es matemático; no significa que se pueda vivir solo de papa.",
        ],
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    selected = ("iron", "zinc", "calcium", "vitamin_a_rae", "vitamin_b12",
                "vitamin_d", "vitamin_e", "vitamin_c", "potassium", "fiber",
                "linoleic_acid", "alpha_linolenic_acid")
    lines = [
        "# OP-M1-001 — reporte exploratorio reproducible",
        "",
        "**No es una dieta recomendada, una estimación de deficiencia clínica ni una variedad creada.**",
        "",
        f"Papa hervida, pulpa sin sal: {food['energy_kcal'].value} kcal/100 g.",
        f"Para alcanzar matemáticamente {energy_kcal} kcal con esta papa se requieren "
        f"{equivalent.quantize(Decimal('0.1'))} g de alimento preparado; "
        "no equivale a una dieta equilibrada.",
        "",
        "## Cobertura de referencias para 400 g (no predice absorción)",
        "",
        "| Perfil | Nutriente | Aporte | Referencia | Cobertura | Estado |",
        "|---|---|---:|---:|---:|---|",
    ]
    for profile, profile_refs in sorted(references.items()):
        lookup = {r["nutrient"]: r for r in compute_rows(food, profile_refs, Decimal(400))}
        for nutrient in selected:
            r = lookup.get(nutrient)
            if r is None:
                continue
            coverage = f"{Decimal(r['coverage_percent']):.1f}%" if r["coverage_percent"] else "ND"
            amount = f"{Decimal(r['amount']):.3f} {r['unit']}" if r["amount"] else "ND"
            ref = f"{r['reference']} {r['unit']} {r['reference_kind']}" if r["reference"] else "—"
            lines.append(f"| {profile} | {nutrient} | {amount} | {ref} | {coverage} | {r['status']} |")
    lines += [
        "",
        "## Interpretación y límites",
        "",
        "- Una cobertura <100% de RDA en **un alimento** no diagnostica déficit nutricional; "
        "una dieta completa aporta nutrientes de otros alimentos.",
        "- AI (ingesta adecuada) no es un umbral diagnóstico: quedar debajo no prueba carencia.",
        "- ND = no reportado/identificación insuficiente, **nunca** cero supuesto.",
        "- La composición transcrita de una fuente secundaria será sustituida o auditada "
        "contra descarga directa oficial de FDC.",
        "- Ver manifest.json para checksums y todas las limitaciones.",
        "",
    ]
    (output_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="OpenPotato M1: análisis no clínico y reproducible")
    parser.add_argument("--food", type=Path, default=DEFAULT_FOOD)
    parser.add_argument("--references", type=Path, default=DEFAULT_REFERENCES)
    parser.add_argument("--output", type=Path, default=ROOT / "reports" / "m1-001")
    parser.add_argument("--grams", nargs="+", default=["200", "400", "800"])
    parser.add_argument("--energy-kcal", default="2000")
    args = parser.parse_args()
    result = run(food_path=args.food, reference_path=args.references,
                 output_dir=args.output,
                 grams_list=tuple(Decimal(v) for v in args.grams),
                 energy_kcal=Decimal(args.energy_kcal))
    print(f"OP-M1-001 listo: {args.output} | perfiles={len(result['profiles'])}")


if __name__ == "__main__":
    main()

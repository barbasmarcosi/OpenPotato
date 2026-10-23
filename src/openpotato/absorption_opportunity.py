"""OP-N1-01: evidence-led joint Fe/Zn opportunity, not a new variety.

Uses primary 2023 human stable-isotope *group summaries* in two distinct
trials, alongside separately sourced USDA SR Legacy cooked-potato baseline.
No pooling, no per-person outcomes, no RDA comparison to absorbed milligrams.
All amounts remain on their original meal size and preparation.
"""
from __future__ import annotations

import argparse
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

from openpotato.m1 import ROOT, load_food, load_references, digest

DEFAULT_STUDIES=ROOT/"datasets"/"evidence"/"human_potato_fe_zn_absorption_2023.json"
DEFAULT_USDA=ROOT/"datasets"/"official"
DEFAULT_REFERENCES=ROOT/"datasets"/"adult_references_31_50.csv"
EXPECTED={"PERU_FE_2023":("iron","10.1016/j.tjnut.2023.04.010",28,Decimal("460")),
          "PERU_ZN_2023":("zinc","10.1016/j.tjnut.2023.08.028",37,Decimal("500"))}
# Published abstract headline group summaries, independently verified by DOI.
# These anchors detect accidental edits to curated endpoint transcription.
PRIMARY_ABSTRACT_ANCHORS={
    "PERU_FE_2023":{
        "control":("0.31","16.6","0.24"),
        "biofortified":("0.63","12.1","0.35"),
    },
    "PERU_ZN_2023":{
        "control":("0.32","25.5","0.40"),
        "biofortified":("0.48","20.8","0.49"),
    },
}
USDA_FOODS={"170438","170440"}
SIDES=("control","biofortified")

def number(x,label,positive=False):
    if not isinstance(x,str):
        raise ValueError(label+": decimal strings required for verifiable precision")
    try:v=Decimal(x)
    except (InvalidOperation,ValueError) as exc:raise ValueError(label+": invalid number") from exc
    if not v.is_finite() or (v<=0 if positive else v<0):
        raise ValueError(label+": nonfinite/negative/zero where prohibited")
    return v

def validate_studies(raw):
    if not isinstance(raw,dict) or raw.get("schema_version")!=1:
        raise ValueError("Unknown evidence registry version")
    if raw.get("register_type")!="published_summary_manually_transcribed_not_individual_patient_data":
        raise ValueError("Source population status changed")
    if raw.get("same_genotype_both_minerals_measured_in_humans") is not False:
        raise ValueError("Joint Fe/Zn identical genotype NOT demonstrated")
    if raw.get("individual_participant_data_available") is not False:
        raise ValueError("Published group summaries are not individual participant data")
    if raw.get("field_yield_and_safety_assessed_for_trial_materials") is not False:
        raise ValueError("No verified matching yield or safety trials")
    if raw.get("clinical_anemia_reduction_tested") is not False:
        raise ValueError("No anemia incidence effect established")
    studies=raw.get("studies")
    if not isinstance(studies,list) or len(studies)!=2:
        raise ValueError("Two distinct nutrient trials required")
    if {x.get("id") for x in studies if isinstance(x,dict)}!=set(EXPECTED):
        raise ValueError("Original trial identity mismatch")
    outputs=[]
    for study in studies:
        key=study["id"]
        nutrient,doi,participants,serving=EXPECTED[key]
        if (study.get("nutrient")!=nutrient or study.get("doi")!=doi
           or study.get("participants")!=participants
           or study.get("published_year")!=2023
           or study.get("primary_url")!=
            ("https://pmc.ncbi.nlm.nih.gov/articles/PMC10308245/" if nutrient=="iron"
             else "https://pmc.ncbi.nlm.nih.gov/articles/PMC10613720/")):
            raise ValueError("Published original trial provenance mismatch")
        if study.get("unit_absorbed")!="mg_per_serving" or study.get("unit_intake")!="mg_per_100g_as_published":
            raise ValueError("Unapproved endpoint unit")
        if number(study["meal_g"],"meal_g",True)!=serving:
            raise ValueError("Different meal mass; no dose-equivalence extrapolation")
        if not study.get("material_linkage", "").endswith("_not_verified_same_genotype_as_"+("Zn" if nutrient=="iron" else "Fe")+"_study"):
            raise ValueError("Do not pretend studies evaluate same genotype")
        pairs={}
        for side in SIDES:
            item=study.get(side)
            if not isinstance(item,dict):raise ValueError("Missing trial arm")
            c=number(item["intake_mg_per_100g"],"mineral concentration",True)
            f=number(item["fractional_absorption_pct"],"fractional absorption",True)
            a=number(item["absorbed_mg_per_meal"],"absorbed meal mass",True)
            if f>100:raise ValueError("Fractional absorption greater than 100%")
            expected_from_rounded=c*serving/100*f/100
            # Allow effect of averaging/rounding published group means; never
            # equate a product of means with the original paired estimate.
            if abs(expected_from_rounded-a)>Decimal("0.035"):
                raise ValueError("Published concentration/fraction/absorption numerically inconsistent")
            if nutrient=="iron":
                if "absorbed_group_sd_mg" in item:raise ValueError("Mixing iron CI with zinc SD")
                ci=item.get("absorbed_group_ci95_mg")
                if not isinstance(ci,list) or len(ci)!=2:raise ValueError("Iron study group CI required")
                lower,upper=[number(x,"group CI",True) for x in ci]
                if not lower<=a<=upper:raise ValueError("Group CI does not bracket published mean")
            else:
                if "absorbed_group_ci95_mg" in item:raise ValueError("Mixing zinc SD with iron CI")
                sd=number(item.get("absorbed_group_sd_mg"),"group SD",True)
            original=PRIMARY_ABSTRACT_ANCHORS[key][side]
            if (c,f,a)!=tuple(Decimal(x) for x in original):
                raise ValueError("Curated primary abstract endpoint changed; review published source")
            pairs[side]=(c,f,a)
        cc,cf,ca=pairs["control"];bc,bf,ba=pairs["biofortified"]
        if not (bc>cc and bf<cf and ba>ca):
            raise ValueError("Original published nutrient/fraction/absorption directions changed")
        outputs.append({
          "study_id":key,"nutrient":nutrient,"primary_doi":doi,
          "participants_women_peru":participants,"meal_g":str(serving),
          "control_concentration_mg_per_100g":str(cc),
          "biofortified_concentration_mg_per_100g":str(bc),
          "control_fractional_absorption_pct":str(cf),
          "biofortified_fractional_absorption_pct":str(bf),
          "control_absorbed_mg_per_study_meal":str(ca),
          "biofortified_absorbed_mg_per_study_meal":str(ba),
          "absorbed_absolute_difference_mg_per_study_meal":str(ba-ca),
          "absorbed_difference_pct_based_on_rounded_group_means":str((ba-ca)/ca*100),
          "source_uncertainty_type":"group_95pct_CI" if nutrient=="iron" else "group_SD",
          "paired_difference_uncertainty_computed":False,
          "independent_crossover_trial_not_joint_genotype":True,
        })
    return sorted(outputs,key=lambda x:x["nutrient"])

def usda_baseline(directory, reference_path):
    directory=Path(directory)
    provenance=json.loads((directory/"provenance.json").read_text(encoding="utf-8"))
    if provenance.get("no_imputation") is not True or set(provenance.get("records",{}))!=USDA_FOODS:
        raise ValueError("USDA official original inventory missing")
    if provenance.get("archive_sha256")!="b80817294b8850530aaedf2e515c02593b1824f763a0ff356e5c2081643e6fd0":
        raise ValueError("USDA SR Legacy archive identity changed")
    food={}
    refs=load_references(reference_path)
    for fdc_id in sorted(USDA_FOODS):
        record=provenance["records"][fdc_id]
        if record["filename"]!=f"potato_fdc_{fdc_id}_usda.csv":
            raise ValueError("USDA food source file mismatch")
        file=directory/record["filename"]
        if digest(file)!=record["sha256"]:
            raise ValueError("USDA official record SHA256 mismatch")
        food[fdc_id]=load_food(file)
    observations=[]
    for fdc_id in sorted(USDA_FOODS):
        for nutrient in ("iron","zinc","vitamin_c","vitamin_b12","linoleic_acid","alpha_linolenic_acid"):
            value=food[fdc_id].get(nutrient)
            if value is None:raise ValueError("USDA selected nutrient row missing")
            observations.append({
                "fdc_id":fdc_id,"nutrient":nutrient,"unit":value.unit,
                "food_report_status":value.status,
                "amount_mg_per_400g_prepared_food":(
                    str(value.value*4) if value.value is not None and value.unit=="mg" else None),
                "amount_per_100g_raw_FDC_unit":str(value.value) if value.value is not None else None,
                "amount_unit":value.unit,
            })
    coverage=[]
    for fdc_id in sorted(USDA_FOODS):
        for profile in sorted(refs):
            for nutrient in ("iron","zinc"):
                value=food[fdc_id][nutrient];ref=refs[profile][nutrient]
                if value.unit!=ref.unit or value.value is None or ref.kind!="RDA":
                    raise ValueError("USDA/reference harmonization failed")
                coverage.append({
                    "fdc_id":fdc_id,"profile":profile,"nutrient":nutrient,
                    "dietary_amount_mg_per_400g":str(value.value*4),
                    "reference_type":"RDA","reference_mg_daily":str(ref.value),
                    "dietary_amount_over_reference_pct":str(value.value*4/ref.value*100),
                    "absorption_adjustment_applied":False,
                })
    return {
      "usda_source_archive_sha256":provenance["archive_sha256"],
      "official_food_ids":sorted(food),
      "form":"boiled potato flesh prepared; NOT Peruvian absorption-trial material",
      "portion_g":400,
      "targeted_observations":observations,
      "adult_RDA_context_not_clinical_requirement_or_bioavailability":coverage,
      "directly_comparable_to_peruvian_human_isotope_trial":False,
    }

def compile_opportunity(study_path=DEFAULT_STUDIES, usda=DEFAULT_USDA, refs=DEFAULT_REFERENCES):
    trials=json.loads(Path(study_path).read_text(encoding="utf-8"))
    comparisons=validate_studies(trials)
    baseline=usda_baseline(usda,refs)
    return {
        "id":"OP-N1-01",
        "title":"Absorbed Fe and Zn jointly in ONE traceable genotype, with processing and agronomic constraints",
        "status":"TESTABLE_RESEARCH_OPPORTUNITY_NOT_DEMONSTRATED_FOR_SAME_GENOTYPE",
        "human_isotope_studies":comparisons,
        "usda_cooked_baseline_separate_population_and_preparation":baseline,
        "scientific_gap_to_test":"paired Fe+Zn absorption in the same genetically traceable potato material with matched control, preparation, safety and field performance",
        "first_primary_endpoint":"difference in absorbed Fe mg per prespecified meal for the same genotype vs control",
        "second_primary_endpoint_requires_multiplicity_plan":"difference in absorbed Zn mg per prespecified meal for that same genotype vs control",
        "can_claim_joint_fe_zn_improvement":False,
        "can_compare_USDA_dietary_RDA_to_absorbed_mg":False,
        "can_claim_iron_deficiency_or_anemia_reduction":False,
        "can_claim_first_in_world_or_prior_work_absent":False,
        "can_claim_potato_variety_developed_by_openpotato":False,
        "can_claim_yield_or_glycoalkaloid_safety":False,
        "unresolved_dependencies":[
            "genotype identity and availability for a genuinely joint Fe/Zn trial",
            "same-meal isotope evidence for both minerals; primary endpoint multiplicity/precision plan",
            "phytate, ascorbate, chlorogenic acid and cooking/processing retention",
            "validated farmer yield, field stability and glycoalkaloid/safety limits",
            "locally relevant comparator, meal sizes, dietary patterns and affordability",
            "expert ethics approvals and independent replication before any health claim",
        ],
    }

def publish(output, out_dir):
    out_dir=Path(out_dir);out_dir.mkdir(parents=True,exist_ok=True)
    (out_dir/"op_n1_01_absorption_opportunity.json").write_text(
        json.dumps(output,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")
    lines=[
      "# OP-N1-01 — Una oportunidad concreta y falsable para OpenPotato","",
      "**HIPÓTESIS CANDIDATA, NO DESCUBRIMIENTO NI VARIEDAD NUEVA.**",
      "Ensayos humanos independientes evaluaron hierro y zinc por separado; no hay prueba aquí de una variedad que optimice ambos mineral absorbidos a la vez.","",
      "| Estudio | Porción | Concentración (conv→biofortificada, mg/100 g) | Absorción fraccional (conv→biof) | Total absorbido por comida (conv→biof) | Diferencia de medias publicadas |",
      "|---|---|---|---|---|---|",
    ]
    for study in output["human_isotope_studies"]:
        lines.append(
            f'| {study["nutrient"].upper()} (n={study["participants_women_peru"]}) | '
            f'{study["meal_g"]} g | {study["control_concentration_mg_per_100g"]}→{study["biofortified_concentration_mg_per_100g"]} | '
            f'{study["control_fractional_absorption_pct"]}%→{study["biofortified_fractional_absorption_pct"]}% | '
            f'{study["control_absorbed_mg_per_study_meal"]}→{study["biofortified_absorbed_mg_per_study_meal"]} mg | '
            f'+{Decimal(study["absorbed_difference_pct_based_on_rounded_group_means"]):.1f}% |')
    lines.extend([
        "","**Porcentajes calculados con medias REDONDEADAS; no reproducen la inferencia pareada del artículo.**",
        "No sumamos hierro y zinc entre diferentes estudios ni extrapolamos de mujeres peruanas a otras poblaciones.",
        "Los intervalos de hierro se publicaron como CI de grupo y los de zinc como SD; ninguna inferencia del efecto pareado se recalculó.",
        "","## Comparación separada — USDA cocida, 400 g, aporte dietario NO absorbido","",
        "| Preparación USDA | Hierro total dietario (mg) | Zinc total dietario (mg) |",
        "|---|---:|---:|",
    ])
    baseline=output["usda_cooked_baseline_separate_population_and_preparation"]
    for fid in baseline["official_food_ids"]:
        obs={r["nutrient"]:r for r in baseline["targeted_observations"] if r["fdc_id"]==fid}
        lines.append(f'| {fid} | {obs["iron"]["amount_mg_per_400g_prepared_food"]} | {obs["zinc"]["amount_mg_per_400g_prepared_food"]} |')
    lines.extend([
        "","Son otros materiales, otra preparación y datos históricos USDA SR Legacy 2018. No se usan para calcular absorción humana en ensayos peruanos.",
        "Ácidos grasos esenciales no identificados en la fuente permanecen ND; ceros reportados para vitaminas B12/D son registros históricos, no pruebas de ausencia absoluta.",
        "","## Hipótesis prioritaria para contraste independiente",
        "En una **misma variedad genéticamente identificada** y con preparación, ambiente y comparador armonizados, ¿podemos lograr mejoras demostrables de Fe y Zn **absorbidos por comida** sin deterioro verificable de rendimiento, seguridad ni asequibilidad?",
        "La originalidad de esta combinación debe verificarse en una revisión sistemática posterior; no afirmamos ser los primeros.",
        "","## Puertas que impiden declaraciones prematuras",
        "- El diseño debe identificar material, procesamiento, dosis, población, contrafactual y control de multiplicidad.",
        "- Los resultados humanos previos NO prueban mejora clínica ni seguridad de un genotipo nuevo.",
        "- No hay datos de rendimiento/inocuidad del material experimental equivalente; no existe validación WOFOST por parcela.",
        "- Datos de nutrición total USDA y mg absorbidos de isótopos NO son métricas intercambiables.",
        "","Fuentes primarias:",
        "- Hierro: https://doi.org/10.1016/j.tjnut.2023.04.010",
        "- Zinc: https://doi.org/10.1016/j.tjnut.2023.08.028",
        "- USDA: https://fdc.nal.usda.gov/download-datasets/","",
    ])
    (out_dir/"op_n1_01_research_opportunity.md").write_text("\n".join(lines),encoding="utf-8")

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--studies",type=Path,default=DEFAULT_STUDIES)
    p.add_argument("--usda",type=Path,default=DEFAULT_USDA)
    p.add_argument("--references",type=Path,default=DEFAULT_REFERENCES)
    p.add_argument("--output",type=Path,default=ROOT/"reports"/"op-n1-01")
    args=p.parse_args()
    output=compile_opportunity(args.studies,args.usda,args.references)
    publish(output,args.output)
    print(json.dumps({
        "id":output["id"],
        "study_ids":[r["study_id"] for r in output["human_isotope_studies"]],
        "joint_genotype_benefit_validated":output["can_claim_joint_fe_zn_improvement"],
        "usda_official_records":output["usda_cooked_baseline_separate_population_and_preparation"]["official_food_ids"]
    },sort_keys=True))
if __name__=="__main__":main()

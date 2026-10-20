"""Compare official USDA food records descriptively; NEVER infer peeling causality."""
from __future__ import annotations
import argparse, csv, json
from decimal import Decimal
from pathlib import Path
from openpotato.m1 import ROOT, load_food, digest

DEFAULT_SOURCE = ROOT / "datasets" / "official"

def compare(directory: Path, output: Path) -> list[dict[str,str]]:
    directory=Path(directory)
    provenance=json.loads((directory/"provenance.json").read_text(encoding="utf-8"))
    records=provenance["records"]
    expected_ids=("170438","170440")
    food={}
    for fid in expected_ids:
        meta=records[fid]
        path=directory/meta["filename"]
        if digest(path)!=meta["sha256"]:
            raise ValueError(f"SHA-256 no coincide con manifiesto oficial: {fid}")
        food[fid]=load_food(path)
    result=[]
    for nutrient in sorted(set(food["170438"]) | set(food["170440"])):
        left,right=food["170438"].get(nutrient),food["170440"].get(nutrient)
        if left is None or right is None or left.unit!=right.unit:
            raise ValueError(f"Datos incompatibles: {nutrient}")
        is_known=left.value is not None and right.value is not None
        difference=(right.value-left.value) if is_known else None
        relative=(difference/left.value*100) if difference is not None and left.value!=0 else None
        result.append({
            "nutrient":nutrient,"unit":left.unit,
            "fdc_170438":str(left.value) if left.value is not None else "",
            "fdc_170440":str(right.value) if right.value is not None else "",
            "delta_440_minus_438":str(difference) if difference is not None else "",
            "relative_change_pct":str(relative) if relative is not None else "",
            "status":"comparable" if is_known else "not_reported",
        })
    output=Path(output)
    output.mkdir(parents=True,exist_ok=True)
    cols=list(result[0].keys())
    with (output/"preparation_comparison.csv").open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=cols);writer.writeheader();writer.writerows(result)
    lines=[
        "# Comparación descriptiva: papa hervida USDA SR Legacy 2018",
        "",
        "**No es un experimento controlado de pelado, ni representa una comparación genética.**",
        "",
        "FDC 170438: pulpa de papa cocida con piel. FDC 170440: pulpa de papa cocida sin piel.",
        "Ambas cifras expresan composición publicada por **100 g de alimento preparado**.",
        "",
        "| Nutriente | 170438 | 170440 | Diferencia (440−438) |",
        "|---|---:|---:|---:|",
    ]
    keys={"energy_kcal","iron","zinc","vitamin_c","folate_dfe","potassium","protein",
          "vitamin_a_rae","vitamin_e","vitamin_b12","linoleic_acid"}
    for r in result:
        if r["nutrient"] in keys:
            def show(value):
                return value if value!="" else "ND"
            lines.append(f'| {r["nutrient"]} ({r["unit"]}) | {show(r["fdc_170438"])} | '
                         f'{show(r["fdc_170440"])} | {show(r["delta_440_minus_438"])} |')
    lines += [
        "",
        "La diferencia entre fichas **no identifica la causa**: posibles cambios de muestreo,",
        "variedad, retención, método analítico y otras variables no controladas.",
        "Ceros publicados son ceros del registro; ND no equivale a cero.",
        "Sin medición de biodisponibilidad, glicoalcaloides, rendimiento ni incertidumbre varietal.",
        "",
        "Fuente primaria: https://fdc.nal.usda.gov/download-datasets/",
        f'Archivo original SHA-256: {provenance["archive_sha256"]}',
        "Método y trazabilidad: datasets/official/provenance.json",
        "",
    ]
    (output/"comparison.md").write_text("\n".join(lines),encoding="utf-8")
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir",type=Path,default=DEFAULT_SOURCE)
    parser.add_argument("--output",type=Path,default=ROOT/"reports"/"m1-preparations")
    args=parser.parse_args()
    result=compare(args.source_dir,args.output)
    print(f"Comparación validada: {len(result)} nutrientes; salida {args.output}")

if __name__=="__main__": main()

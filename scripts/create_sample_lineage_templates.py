"""Write HEADER-ONLY chain-of-custody intake templates, never mock observations.

Copying templates or passing schema validation is not permission to access,
publish, or model confidential CIP, grower or laboratory records.
"""
import argparse
import csv
from pathlib import Path

from scripts.validate_sample_lineage import STUDY_COLS

INSTRUCTIONS = """# OpenPotato M1-14 — plantilla vacía, SIN observaciones reales

Estos cinco CSV son plantillas con ENCABEZADOS, no datasets ni evidencia
de biología de la papa. Completar exclusivamente con datos autorizados,
respetando condiciones de privacidad y uso. No subir microdatos protegidos
a GitHub, Issues, Actions, PR o artefactos públicos.

plots.csv: una fila por parcela física; identidad ensayo/sitio/campaña/
bloque/parcela, genotipo y área total m2.
samples.csv: una fila por muestra biológica; sample_design = single_plot o
pooled_plots. tissue = peeled_flesh, processing = raw, sampling_date ISO.
sample_plots.csv: relación explícita N:M entre muestra(s) y parcela(s)
de origen. Nunca inventar vínculos ausentes.
assays.csv: un valor principal por muestra × iron/zinc; unit = mg/kg_dry,
method = XRF o ICP-MS; qualifier = quantified, below_detection o
below_quantification; measurement_kind = primary o technical_replicate.
Si quantified: valor numérico >0, limit_value vacío. Si censurado:
value vacío, limit_value positivo; no imputar cero.
harvest.csv: una fila de cosecha por parcela, harvested_kg_fresh y
harvest_area_m2 no mayor que plot_area_m2.

El validador falla si falta procedencia y NO transforma unidades.
La salida es solo un reporte de estructura y recuentos sin datos de personas,
localizaciones, muestras, análisis individuales o resultados biológicos.
La decisión final requiere revisión humana de diseño, consentimiento,
derechos de reutilización, calibraciones y procedencia.
"""

def create(out):
    out=Path(out)
    out.mkdir(parents=True,exist_ok=True)
    target=[out/(name+".csv") for name in STUDY_COLS]+[out/"INTAKE_README.md"]
    if any(path.exists() for path in target):
        raise ValueError("An intake target already exists: refusing to overwrite input data")
    for name,fields in STUDY_COLS.items():
        with (out/(name+".csv")).open("x",newline="",encoding="utf-8") as stream:
            csv.writer(stream).writerow(sorted(fields))
    (out/"INTAKE_README.md").write_text(INSTRUCTIONS,encoding="utf-8")
    return len(STUDY_COLS)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    n=create(args.out)
    print(f"Created {n} header-only CSV templates; NO biological observations")

if __name__ == "__main__":
    main()

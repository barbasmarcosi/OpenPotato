# M1 — Evidencia primaria USDA y comparación de dos preparaciones

**Estado al 20-10-2026:** extracción oficial **ejecutada y verificada** en [GitHub Actions #39432690346](https://github.com/barbasmarcosi/OpenPotato/actions/runs/39432690346), con 14 pruebas aprobadas. Datos extraídos versionados en [datasets/official](../datasets/official). Esto valida la **procedencia y el pipeline**, no la aplicabilidad clínica de los cálculos.

## Fuente exacta, reproducción y auditoría

USDA FoodData Central, **SR Legacy, descarga final de abril de 2018**: https://fdc.nal.usda.gov/download-datasets/

Archivo: https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_sr_legacy_food_csv_2018-04.zip

SHA-256 del ZIP original:

    b80817294b8850530aaedf2e515c02593b1824f763a0ff356e5c2081643e6fd0

Identificadores verificados:
- **FDC 170438**: "Potatoes, boiled, cooked in skin, flesh, without salt": papa hervida *con piel durante cocción*, **pulpa consumida**, sin sal.
- **FDC 170440**: "Potatoes, boiled, cooked without skin, flesh, without salt": papa hervida *sin piel*, **pulpa consumida**, sin sal.

Ficheros permanentes:
- [170438](../datasets/official/potato_fdc_170438_usda.csv), SHA-256: 5ebd6b64e1f9a8e692e31b2bb8576c9ab2b1c805fe084cbfa4804a452a90dabd
- [170440](../datasets/official/potato_fdc_170440_usda.csv), SHA-256: e700a845c89a1e2e1da9ad29b20be80f32682e9eddf8b9853908ef8d0b940017
- [Manifest de procedencia](../datasets/official/provenance.json)

El importador verifica nombre, tipo de alimento, identificador **entero** de cada nutriente, unidad oficial, duplicados y valores inválidos. Conserva los datos faltantes como **ND**, no como cero. La comprobación del espejo anterior para la ficha 170438 permanece en tests, pero **ya no es fuente primaria ni entrada por defecto**.

## Resultados oficiales por 100 g de pulpa hervida preparada

| Variable | FDC 170438 | FDC 170440 | Diferencia 440 − 438 |
|---|---:|---:|---:|
| Energía | 87 kcal | 86 kcal | -1 kcal |
| Proteína total | 1,87 g | 1,71 g | -0,16 g |
| Grasas totales | 0,10 g | 0,10 g | 0 g |
| Calcio | 5 mg | 8 mg | +3 mg |
| Hierro | 0,31 mg | 0,31 mg | 0 mg |
| Zinc | 0,30 mg | 0,27 mg | -0,03 mg |
| Potasio | 379 mg | 328 mg | -51 mg |
| Vitamina C | 13 mg | 7,4 mg | -5,6 mg |
| Folato DFE | 10 µg | 9 µg | -1 µg |
| Vitamina A RAE | 0 µg publicado | 0 µg publicado | 0 µg |
| Vitamina B12 | 0 µg publicado | 0 µg publicado | 0 µg |
| Vitamina D | 0 µg publicado | 0 µg publicado | 0 µg |
| Ácidos grasos linoleico y alfa-linolénico | ND | ND | No calculable |

**No extrapolar**: la diferencia de vitamina C es real entre las dos fichas USDA, pero el dataset NO es un ensayo con muestras emparejadas y controles. No se puede atribuir causalidad al pelado: pueden intervenir variedad, lote, método, tiempo de cocción y muestreo.

**No diagnosticar:** porcentajes de ingesta dietaria frente a RDA/AI no determinan absorción ni estado nutricional individual. La tabla no es una recomendación para comer principalmente papa. No contiene ensayos de glicoalcaloides, toxicidad, rendimiento, costos, perfil de aminoácidos o estabilidad de biofortificación.

## Reproducir sin claves ni internet

Requiere Python >=3.11. Con los datos primarios ya versionados:

    PYTHONPATH=src python -m unittest discover -s tests -v
    PYTHONPATH=src python -m openpotato.m1 --output reports/m1-001
    PYTHONPATH=src python -m openpotato.compare --output reports/m1-preparations

Para **reconstruir** desde el archivo fuente:

    curl -fL https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_sr_legacy_food_csv_2018-04.zip -o /tmp/sr-legacy.zip
    PYTHONPATH=.:src python -m scripts.usda_sr_legacy --zip /tmp/sr-legacy.zip --output-dir /tmp/usda-reproduced

Comparar hashes con [provenance.json](../datasets/official/provenance.json) y analizar diferencias antes de sustituir datos. La workflow [USDA primary validation](../.github/workflows/usda-official.yml) ejecuta el flujo completo con fuente oficial y publica artefactos temporales. La workflow [M1 reproducibility](../.github/workflows/m1-tests.yml) valida que el motor y la comparación funcionen offline.

## Lo que falta para cerrar M1

1. Fuentes regionales y variedades con mediciones específicas (la ficha USDA es agregada/histórica).
2. Segunda revisión de referencias nutricionales y cobertura de todos los nutrientes indispensables.
3. Incertidumbre y variabilidad real por cultivar, preparación y análisis.
4. Biodisponibilidad/retención con evidencia apropiada, no factores inventados.
5. Revisión experta de interpretación e inocuidad antes de hablar de dietas o nuevas variedades.

**Resultado científico legítimo del hito parcial:** existe una línea base nutricional auditable para dos preparaciones, pero todavía no hay prueba de biofortificación, mejora genética ni suficiencia dietaria.

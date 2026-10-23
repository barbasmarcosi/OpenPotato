# M1 — Comparación exploratoria de tres tipos comerciales de papa con USDA Foundation Foods

**Fecha de ejecución:** 2026-10-20. **Estado:** datos oficiales descargados, normalizados y versionados; análisis descriptivo no causal.

## 1. Fuente primaria y procedencia

USDA FoodData Central **Foundation Foods abril de 2026**, ZIP oficial: https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_foundation_food_csv_2026-04-30.zip

- SHA-256 original: `70457ee9d9342f43bda2010318c85f04210c689fdeb9cd2da4c513b0e8dbc655`
- [USDA: descargas](https://fdc.nal.usda.gov/download-datasets/)
- [USDA: metodología de Foundation](https://fdc.nal.usda.gov/Foundation_Foods_Documentation/)
- [Datos normalizados](../datasets/foundation/foundation_market_types.csv)
- [Comparación reproducible](../datasets/foundation/foundation_comparison.md)
- [Metadatos y hashes](../datasets/foundation/foundation_provenance.json)
- [Pipeline usado](../.github/workflows/usda-foundation.yml)

**Registros originales:**
- *Russet*, cruda sin piel: **FDC 2346401**, publicada el 28-10-2022.
- *Red*, cruda sin piel: **FDC 2346402**, publicada el 28-10-2022.
- *Gold*, cruda sin piel: **FDC 2346403**, publicada el 28-10-2022.

La descarga abril 2026 incluye estos registros publicados en 2022. **«Tipo comercial» no identifica necesariamente un cultivar genético específico.** Todos representan pulpa cruda sin piel; no equivalen a las fichas SR Legacy de papa hervida.

## 2. Resultados por 100 g de alimento CRUDO, sin piel

| Indicador | Russet | Roja | Dorada | Unidad |
|---|---:|---:|---:|---|
| Energía Atwater general (ID 2047) | 83,42 | 75,56 | 73,47 | kcal |
| Energía Atwater específico (ID 2048) | 80,95 | 73,37 | 71,58 | kcal |
| Proteínas calculadas | 2,274 | 2,063 | 1,813 | g |
| Grasas | 0,360 | 0,248 | 0,264 | g |
| Hierro | 0,3835 | 0,3911 | 0,3728 | mg |
| Zinc | 0,3781 | 0,3923 | 0,3739 | mg |
| Potasio | 450,1 | 472,0 | 445,8 | mg |
| Vitamina C | 10,90 | 21,29 | 23,30 | mg |

**Observación descriptiva:** el contenido registrado de vitamina C en la categoría dorada es ~2,14 veces el de russet. Zinc y hierro varían mucho menos entre las tres fichas. Estas son cifras de composición publicadas, no de nuevos experimentos.

La energía Atwater general/específico utiliza métodos de cálculo **distintos** (no promediar o combinar). En Foundation Foods, la proteína puede calcularse a partir del nitrógeno medido y de factores de conversión; la palabra «proteína» no supone que se hayan medido todos los aminoácidos esenciales. Ver [metodología USDA](https://fdc.nal.usda.gov/Foundation_Foods_Documentation/).

## 3. Evidencia que NO tenemos

- Causalidad genética de las diferencias, o identificación de cultivares individuales.
- Variables de suelo, clima, manejo agronómico, madurez, almacenamiento o cosecha emparejadas.
- Comparaciones de micronutrientes después de cocinar las tres categorías.
- Estimación del error estándar, varianza y significancia estadística de las diferencias. El valor `data_points=8` aparece en varias concentraciones, pero **no es por sí solo una estimación de dispersión**.
- Fibra, B12, D, provitamina A RAE, folato DFE y vitamina E dentro de esta selección Foundation: aparecen **ND** (no reportados), **no cero**. Algunos tienen valores en otras fuentes o preparaciones, pero no se deben trasladar sin estudio.
- Medición de absorción humana, glicoalcaloides, productividad, costo, rendimiento de semillas ni tolerancia a enfermedades.

Las cantidades deben interpretarse como **puntos de partida para comparar composición alimentaria**, nunca como evidencia de que un tipo comercial puede curar deficiencias o como resultado de una intervención genética.

## 4. Distinción clave de diseños

| Conjunto | Fuente | Compara | Puede responder | NO puede responder |
|---|---|---|---|---|
| USDA SR Legacy | 2018 | 2 preparaciones de pulpa **hervida** | Aportes dietarios bajo supuestos | Causalidad por pelado o genética |
| USDA Foundation | descarga 2026, fichas 2022 | 3 tipos de papa **cruda sin piel** | Diferencias de composición descriptiva | Causalidad genética o cambios tras hervido |
| Futuro programa genético | aún sin datos propios | cultivares y ambientes replicados | Interacción genotipo × ambiente | Por anticipado, nada |

## 5. Próximo experimento recomendado: variabilidad dentro de cada grupo

Ahora el paso más informativo es examinar los **valores individuales de las muestras y metadatos** de Foundation Foods, cuando estén disponibles. La documentación USDA explica que se incluyen observaciones subyacentes y, a veces, procedencia agrícola.

Antes de afirmar superioridad de un tipo comercial necesitamos:
1. Reconstruir de la fuente primaria las observaciones por muestra y nutriente, identificando las relaciones entre muestras y submuestras.
2. Comprobar independencia, método analítico, fechas y región; no contar submuestras técnicas como réplicas biológicas.
3. Cuantificar dispersión y posibles confusores; no calcular significancia sin un diseño justificable.
4. Separar la variabilidad dentro de cada tipo de las diferencias entre tipos, y evaluar cómo se modifica la prioridad nutricional.
5. Buscar después conjuntos de cultivares **genéticamente identificados**, idealmente experimentos multisitio (por ejemplo CIP y literatura académica).

## 6. Reproducir

El dataset normalizado ya está versionado. Para reconstruirlo con la descarga oficial:

```bash
curl -fL https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_foundation_food_csv_2026-04-30.zip -o /tmp/foundation.zip
PYTHONPATH=.:src python -m scripts.usda_foundation --zip /tmp/foundation.zip --output-dir /tmp/foundation-check --expected-sha256 70457ee9d9342f43bda2010318c85f04210c689fdeb9cd2da4c513b0e8dbc655
PYTHONPATH=.:src python -m unittest discover -s tests -v
```

El importador valida identificadores, tipos Foundation, unidades, duplicados, límites de cuantificación y registra las fechas de publicación. Si aparece una nueva versión histórica para el mismo tipo, aplica un criterio explícito de fecha más reciente y **rechaza empates ambiguos**.

## 7. Implicación para OpenPotato

La nueva evidencia confirma que **no debemos optimizar únicamente sobre una papa genérica**: existen diferencias de composición entre grupos comerciales. Sin embargo, **todavía no sabemos cuánto de esas diferencias es hereditario**, si se conserva tras cocinar, ni cuál es su impacto nutricional real. El hito M1 continúa abierto y necesita un análisis adecuado de variabilidad y datos por cultivar.

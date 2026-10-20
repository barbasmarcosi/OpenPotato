# OP-M1-03 — Variabilidad de muestras comerciales de papa: evidencia primaria reconstruida

**Fecha:** 20-10-2026. **Estado:** análisis descriptivo por muestra ejecutado y auditable. **No constituye evidencia causal genética.**

## Pregunta

¿Las diferencias que encontramos entre las medias de tipos comerciales de papa exceden la variación observada entre productos adquiridos del mismo tipo? ¿Qué evidencia es válida para priorizar futuros estudios genéticos?

## Fuente y cadena de datos

USDA FoodData Central **Foundation Foods, descarga abril de 2026**: https://fdc.nal.usda.gov/download-datasets/

- Datos de compras y análisis **realizados en 2022**; no confundir fecha de adquisición con fecha de publicación de la descarga.
- SHA-256 del ZIP oficial: `70457ee9d9342f43bda2010318c85f04210c689fdeb9cd2da4c513b0e8dbc655`.
- FDC de grupos de papa cruda sin piel: russet `2346401`, red `2346402`, gold `2346403`.
- 24 muestras comerciales adquiridas: **8 por tipo comercial**. Las 24 se vinculan con registros de adquisición comerciales; todas las ubicaciones registradas corresponden al **estado de Virginia (EE. UU.)**, en Blacksburg, Christiansburg o Wytheville.
- Cuatro analitos por muestra: hierro, zinc, potasio y vitamina C. **96 resultados analíticos enlazados**.
- Procedencia enlazada por identificadores USDA reales:

```text
Foundation food (fdc_id)
  -> input_food (fdc_id, fdc_of_input_food)
  -> sample_food (fdc_id)
  -> sub_sample_food (fdc_id_of_sample_food, fdc_id)
  -> food_nutrient (id, fdc_id, nutrient_id)
  -> sub_sample_result (food_nutrient_id, adjusted_amount, lab_method_id)

sample_food -> acquisition_samples -> market_acquisition
```

No se asignan resultados de submuestras directamente a una planta individual; la unidad de agregación es el producto/muestra de adquisición documentada. Se exige una única medición válida del analito por muestra de adquisición para estos 4 nutrientes. Otros analitos y muestras no se analizan en esta entrega.

## Resultados observados por cada 100 g CRUDOS sin piel

Los intervalos mostrados son **mínimo–máximo de las ocho muestras** por grupo; NO son intervalos de confianza.

| Nutriente | Tipo | Media de 8 compras | Mínimo–máximo | Desv. estándar muestral |
|---|---|---:|---:|---:|
| Vitamina C (mg) | Russet | 10,8975 | 7,44–19,8 | 3,921 |
| Vitamina C (mg) | Roja | 21,2875 | 14,2–29,6 | 5,705 |
| Vitamina C (mg) | Dorada | 23,3000 | 16,6–30,3 | 4,860 |
| Hierro (mg) | Russet | 0,3835 | 0,259–0,519 | 0,0935 |
| Hierro (mg) | Roja | 0,391125 | 0,295–0,645 | 0,1063 |
| Hierro (mg) | Dorada | 0,37275 | 0,267–0,617 | 0,1131 |
| Zinc (mg) | Russet | 0,378125 | 0,173–0,523 | 0,1187 |
| Zinc (mg) | Roja | 0,39225 | 0,305–0,473 | 0,0672 |
| Zinc (mg) | Dorada | 0,373875 | 0,289–0,465 | 0,0775 |
| Potasio (mg) | Russet | 450,125 | 407–530 | 45,599 |
| Potasio (mg) | Roja | 472 | 427–516 | 30,524 |
| Potasio (mg) | Dorada | 445,75 | 342–539 | 65,694 |

### Hallazgos metodológicos

1. Las medias de vitamina C entre grupos se distinguen descriptivamente, pero las distribuciones **se superponen**: el máximo russet (19,8 mg) es superior al mínimo dorado (16,6 mg), y hay mayor superposición entre roja y dorada.
2. Para hierro, zinc y potasio, la variación dentro de grupos es considerable. Una jerarquía de tipos comerciales a partir de una sola media sería incompleta.
3. Todas las compras proceden de tiendas de Virginia, en fechas de 2022; por tanto **no representan un muestreo mundial** de genotipos o ambientes.
4. Los metadatos no identifican necesariamente cultivar o secuencia genética. Además, tiendas próximas podrían vender productos de proveedores o lotes compartidos. **No se considera cada observación una réplica genética independiente.**
5. No hay evaluación de cocción, biodisponibilidad, glicoalcaloides, rendimiento, suelo ni costos. Tampoco se infiere evolución o modificación hereditaria a partir de esta tabla.

### Validación independiente dentro de las fuentes USDA

Se reconstruyeron las medias desde resultados de laboratorio enlazados y se contrastaron con `food_nutrient` de las fichas agregadas. Para los 12 pares (3 tipos × 4 nutrientes):
- **Los mínimos y máximos coinciden exactamente**.
- **Las medianas coinciden exactamente**.
- Las diferencias de medias son compatibles con precisión/redondeo del dato publicado: de 0 a 0,05 en las respectivas unidades, con el máximo en potasio.

No se alteraron los valores originales para hacer coincidir el promedio. Se conservaron esas diferencias en los CSV de auditoría.

## Archivos y reproductibilidad

- [Observaciones vinculadas](../datasets/variability/retail_sample_measurements.csv) — 96 mediciones con sus IDs y metadatos de compra.
- [Resumen por grupo](../datasets/variability/retail_sample_summary.csv) — 12 filas y estadística descriptiva.
- [Reporte generado](../datasets/variability/retail_sample_report.md) — números calculados desde datos de muestra.
- [Hashes y relaciones](../datasets/variability/retail_sample_provenance.json).
- [Código de reconstrucción](../scripts/foundation_variability.py) y [pruebas](../tests/test_variability_snapshot.py).
- [GitHub Actions Foundation](../.github/workflows/usda-foundation.yml) — descarga ZIP oficial, reconstrucción, QA y artefactos.

Para reconstruir desde la versión oficial fijada:

```bash
curl -fL https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_foundation_food_csv_2026-04-30.zip -o /tmp/foundation.zip
PYTHONPATH=.:src python -m scripts.foundation_variability --zip /tmp/foundation.zip --output-dir /tmp/reconstruccion
PYTHONPATH=.:src python -m unittest discover -s tests -v
```

El programa comprueba SHA-256 oficial, relaciones entre tablas, ausencia de duplicados, exactitud de cantidades analíticas y presencia de 8 muestras por grupo para este conjunto concreto. Si la publicación cambia, falla y requiere revisión explícita.

## Decisión: qué NO debemos hacer todavía

**No calcular valores p ni proclamar diferencias significativas genéticas.** La variación por compra no es equivalente a variación de cultivares en condiciones controladas, y las ubicaciones/fechas no permiten identificar efectos independientes de suelo, temporada y cadena de distribución.

## Próximo paso científico

Pasar de «tipos comerciales» a datos de **cultivares genéticamente identificados**, idealmente en ensayos agrícolas multisitio y multicampaña:
- Identidad del cultivar y ploidía, lugar/año, métodos analíticos, tratamiento, número de réplicas biológicas.
- Rendimiento por área y concentración nutricional en una misma campaña.
- Materia seca, cocción y absorción de nutrientes con unidades comparables.
- Estimación de efectos genotipo × ambiente y controles de glicoalcaloides.

Esta investigación reduce la incertidumbre **descriptiva** en un conjunto concreto; no demuestra aún cuál modificación genética deberíamos realizar.

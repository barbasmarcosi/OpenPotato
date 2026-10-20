# OP-M1-09/M1-10 — Trazabilidad de Tabla 16, suelos públicos y agenda genómica

**Fecha:** 2026-10-20. **Estado:** las dos extracciones públicas de CIP se ejecutaron en GitHub Actions con verificación de SHA-256; los resultados son documentos derivados de fuentes públicas, **NO** nuevos experimentos.

## M1-09 — De la estadística publicada a su fila fuente exacta

Fuente: [CIP Dataverse DOI 10.21223/N11QJS](https://doi.org/10.21223/N11QJS), archivo público **6979** (Tabla 16, exportación TSV con SHA-256 `39843e2d1cea114ee18f32e9cd40219c14a8ff32a70ea737bb6438ee609e9dc8`).

El módulo [cip_peru_row_lineage.py](../scripts/cip_peru_row_lineage.py):

- Confronta por igualdad decimal **exacta** los 28 resúmenes derivados de Fe y Zn con las cifras del archivo original (sin redondear ni aceptar tolerancias numéricas arbitrarias).
- Identifica la línea TSV real, código fuente original, descripción original y línea del CSV derivado para cada estadístico. **La línea técnica de un archivo no es un identificador de parcela**.
- Conserva en un archivo aparte las tres filas estadísticas finales globales (`Mean/Prom`, `Max/Max`, `Min/Min`): no son materiales, pero tampoco se borran de la cadena de auditoría.
- Rechaza manipulación de hash, cambios de unidades, resúmenes huérfanos, identificadores duplicados de material donde la estructura de esta tabla requiere exactamente una fila por material, y diferencias en media/SD/mín/máx/n.
- Conserva los **14 materiales**, dos nutrientes por material y la semántica de agregados publicados, no de observaciones biológicas replicadas.

**Validación real:** [GitHub Actions M1-09](https://github.com/barbasmarcosi/OpenPotato/actions/runs/39480710086) ejecutó **99 tests** y validó 28 estadísticas + 3 pies de tabla; generó `peru_row_lineage.csv`, `peru_source_footer_ledger.csv` y manifiesto de procedencia.

La regla contra duplicados solo se aplica a la semántica **específica** de Tabla 16, no es una regla general de datasets agronómicos: un mismo genotipo **sí puede y debe repetirse** en distintos sitios, bloques, tratamientos o años cuando la fuente lo documenta.

## M1-10 — Contexto ambiental real de nueve suelos peruanos

Fuente: mismo Dataverse CIP, archivo público **6970**, *Tabla 01a. Análisis de suelos de nueve localidades del Perú*. Exportación TSV autenticada por SHA-256 `bd64f98a69694dd057b0f808308acc080eeca7b839875c3fd583a5d2f40bc158`.

El módulo [cip_peru_soil_context.py](../scripts/cip_peru_soil_context.py) produce **27 entradas sitio × rasgo**: nueve localidades, cada una con **pH, Zn del suelo (columna ppm) y Fe del suelo (columna ppm)**. Los valores de otras columnas no se reinterpretan. El campo altitud se conserva en su forma textual porque el encabezado no confirma la unidad.

En la fuente real se registraron 27 medias presentes y 24 SD numéricas más tres SD marcadas con `*`. El origen de los asteriscos no se presupone; se conservan como `asterisk_placeholder_source_meaning_unverified`. El parser sabe representar valores censurados como `<0.02` preservando el límite e impidiendo imputaciones, aunque **no se encontraron medias censuradas entre los 27 rasgos seleccionados en esta versión de la tabla**.

**Validación real:** [GitHub Actions M1-10](https://github.com/barbasmarcosi/OpenPotato/actions/runs/39481197872) ejecutó **105 tests** y el importador de 9 sitios; archivó CSV, manifiesto y reporte con hashes.

### Límite de comparabilidad crucial

| Dato | Observación biológica | ¿Se puede incorporar a G×E nutricional ahora? |
|---|---|---|
| CIP Tabla 16 (6979) | Media + SD + n + rango publicados por clon y mineral | **No:** agregados sin clave de parcela, laboratorio y ambiente por medición |
| CIP Tabla 01a (6970) | Estadísticas fisicoquímicas agrupadas por localidad | **No:** no están enlazadas a parcelas/fechas de los clones |
| CIP catálogo 29 clones | Resúmenes por clon del programa | **No:** sin matriz de replicación × ambiente |
| Holetta 2019 | Medias por genotipo de un único sitio y año | **No:** no hay observaciones multientorno por genotipo importadas |

**Fe y Zn del suelo en ppm no son Fe y Zn del tubérculo en mg/kg seco.** Las concentraciones no son equivalentes, aunque algunas unidades puedan ser dimensionalmente similares. No vincular `Locality` a un clon si no existe clave de ensayo/fecha/parcela original. Las estadísticas de dispersión tampoco demuestran réplicas biológicas independientes.

## Nueva línea primaria: genómica tetraploide 2026

Singh et al. (2026), [DOI 10.1038/s41598-026-52419-5](https://doi.org/10.1038/s41598-026-52419-5), evaluó **288 accesiones tetraploides** durante **dos ciclos en la misma estación experimental de Modipuram, India**, y aplicó GWAS con genotipado GBS para Fe, Zn, Cu y Mn. Reporta **16 asociaciones marcador-rasgo** entre los minerales estudiados y propone genes candidatos ligados a transporte y regulación de metales.

- Este resultado **no valida causalidad molecular**. Un locus asociado o un candidato localizado cerca de un marcador no demuestra que su modificación eleve Fe/Zn sin penalización agronómica.
- Dos campañas en un lugar **no equivalen a replicación geográfica**; el estudio no aporta automáticamente validación de materiales de CIP Perú.
- La sección *Data availability* del artículo indica el proyecto de secuenciación NCBI **PRJNA850159**, mientras que los genotipos/fenotipos completos se indican como disponibles por solicitud. **No se ha importado aquí una matriz de fenotipos ni de SNPs.**
- El artículo indica licencia **CC BY-NC-ND 4.0**, con restricciones sobre obras derivadas; no se redistribuyen sus materiales suplementarios sin analizar derechos específicos y permiso cuando corresponda.

### Una vía de validación adecuada

1. Pedir formalmente a titulares de datos de CIP ensayos con Fe/Zn, rendimiento, base fresca/seca, ambiente, bloque, parcela, año, unidades originales y método analítico. No solicitar saltar restricciones.
2. Verificar si el GWAS 2026 permite disponer bajo licencia de la matriz de fenotipos (idealmente por accesión × año × réplica), las asociaciones y los detalles de imputación/control poblacional.
3. Modelar por separado efectos experimentales, sitio-año, cosecha y laboratorio. Con suficientes réplicas reales ajustar modelos jerárquicos *después* de especificar el diseño.
4. Cruzar nutrición con rendimiento, tizón tardío, materia seca, glicoalcaloides, biodisponibilidad, procesamiento y costos solo cuando existan datos comparables y se respeten escalas.
5. Validar marcadores genéticos funcionalmente en materiales relevantes **antes** de usar predicciones para recomendar materiales a agricultores.

## Reproducibilidad

```sh
PYTHONPATH=.:src python -m unittest discover -s tests -v
# En CI se descargan únicamente archivos públicos con SHA fijado:
PYTHONPATH=.:src python -m scripts.cip_peru_row_lineage --tsv /tmp/cip-peru-6979.tab --out /tmp/m1-09
PYTHONPATH=.:src python -m scripts.cip_peru_soil_context --tsv /tmp/cip-soils-6970.tab --out /tmp/m1-10
```

Los workflows [M1-09](../.github/workflows/cip-peru-row-lineage.yml) y [M1-10](../.github/workflows/cip-peru-soil-context.yml) no requieren paquetes externos de Python y solo tienen permisos GitHub `contents: read`. Los artefactos reproducibles se almacenan temporalmente en Actions; no se confunden con una población de observaciones de parcela.

**Conclusión:** mejora sustancial de auditoría, incorporación de covariables ambientales de fuente pública y una nueva hipótesis genómica documentada. **No** hay todavía identificación causal de genes, experimentación propia ni estimación válida de G×E nutricional.

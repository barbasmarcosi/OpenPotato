# OP-M1-20 — Primer benchmark predictivo sobre mediciones REALES de papa de 2020

**Fecha:** 21-10-2026. **Estado:** cálculo auténtico de error temporal contra observaciones reales de campo, con entrenamiento en 2019 y evaluación reservada en 2020. **NO ES LA VALIDACIÓN DE WOFOST.** Los únicos pronósticos evaluados son promedios históricos empíricos muy simples.

## Fuente primaria y derechos

**Tamara ten Den et al.**, *Agronomic dataset on potato growth and yield in the Netherlands*, **Harvard Dataverse v3.0**, DOI [10.7910/DVN/1LC6W7](https://doi.org/10.7910/DVN/1LC6W7), archivo 10850227 \`Plotspecific_processed.csv\` y diccionario publicado \`Plotspecific_processed_meta.xlsx\`.

**Licencia de la fuente: CC BY-NC-SA 4.0**, con atribución, requisito no comercial y compartir adaptaciones bajo condiciones compatibles. La licencia se verificó de nuevo por la API antes de descargar; el original **no se subió al repositorio** ni se incluyó en artifacts. Los resultados agregados y el informe se distribuyen con identificación de origen y la restricción CC BY-NC-SA 4.0; revisar compatibilidad antes de reuso, especialmente comercial.

SHA-256 original **\`8d129262dca38ac98a10f92ccfb1bc46454377020575959fd984c4c5bcab5768\`** y versión 3.0 bloquean sustituciones silenciosas. La ejecución científica cotejó el checksum y los 1.824 registros y sus disponibilidades documentadas antes de analizar.

## Por qué se puede comparar 2019 con 2020

El archivo contiene observaciones repetidas en diferentes fechas, pero el último **día de observación** por localidad y campaña tiene una medición numérica de \`tubersDW\` para cada una de sus parcelas físicas. \`tubersDW\` significa **peso seco de tubérculo en kg/ha**, según el diccionario de los autores, compatible dimensionalmente con la biomasa seca de órganos de reserva de WOFOST.

| Campaña | Lelystad: fecha final de medición | Parcelas | Vredepeel: fecha final de medición | Parcelas |
|---|---|---:|---|---:|
| 2019 | 31/10/2019 | 45 | 10/10/2019 | 42 |
| 2020 | 03/11/2020 | 45 | 19/10/2020 | 42 |

**La última fecha con mediciones no equivale automáticamente a una fecha de cosecha comercial**, y no se asume que diferencias de temperatura, fertilización o manejo hayan quedado controladas. Las 1.048 celdas numéricas de \`tubersDW\` de toda la serie no son 1.048 cosechas finales independientes: muchas corresponden a *las mismas* parcelas en sucesivas fechas.

Se tomó **2019 completo como año de entrenamiento**, usando una única medición terminal por parcela, **87 parcelas** en total (45+42). Se dejó **2020 completo como año de evaluación**, con otras **87 parcelas** en total. La llave física es año × lugar × parcela y debe conservar cultivar, nitrógeno y tratamiento hídrico estables a lo largo de la serie; cualquier duplicación o cambio se rechaza. El proceso exige que todas las parcelas tengan el valor final numérico válido: no elimina individuos silenciosamente ni reemplaza faltantes.

## Dos referencias empíricas predefinidas

Ambas predicen una media observada de **biomasa seca** usando solamente 2019:

1. **Media histórica por localidad:** un predictor constante para las variedades evaluadas dentro de Lelystad o Vredepeel.
2. **Media histórica por localidad y cultivar:** un predictor por cada uno de los seis grupos sitio × cultivar presentes en ambos años.

El comparador observa en 2020 la media por **cada uno de los mismos seis grupos**, calcula la diferencia predicción−observación y comunica MAE, RMSE y sesgo. Las parcelas originales no se publican y no se estima el error de cada individuo como una predicción independiente. No se seleccionaron parámetros del predictor en función del año de evaluación.

### Resultado cuantitativo (REAL, no sintético)

| Benchmark para seis grupos sitio×cultivar | MAE (kg seco/ha) | RMSE (kg seco/ha) | Sesgo predicho−observado (kg seco/ha) |
|---|---:|---:|---:|
| Media de 2019 por sitio | **1.333,40** | 1.776,12 | −450,06 |
| Media de 2019 por sitio y cultivar | 1.516,04 | **1.702,31** | −478,15 |

Son **errores reales frente a las mediciones publicadas de 2020**, pero los predictores son promedios de 2019, **no WOFOST**. Incluir cultivar mejora el RMSE del ejemplo, pero empeora MAE; no puede afirmarse una ganancia consistente. El sesgo negativo indica subpredicción de la media de los seis contrastes bajo ambos métodos, no un efecto genético causal.

**Limitación crítica:** seis medias corresponden a **dos sitios y un único año reservado**. No constituyen seis ambientes independientes ni sostienen intervalos inferenciales sobre validez fuera de Países Bajos. Ambas técnicas mezclan tratamientos de riego y nitrógeno dentro de los grupos, por lo que el cambio 2019→2020 refleja una combinación desconocida de clima, manejo, variación biológica y otros factores. No se atribuye por separado un efecto genético, de año, suelo o tratamiento.

## Implementación auditada

- [\`scripts/wur_2020_empirical_holdout.py\`](../scripts/wur_2020_empirical_holdout.py): fuente verificada doblemente por hash, comprobación de cobertura/fechas/tratamientos por parcela, entrenamiento exclusivo 2019, evaluación exclusiva 2020, agregación por grupo y reporte sin mediciones individuales. Solo el entrypoint de fuente SHA-verificada declara los resultados como evidencia de campo, evitando etiquetar un fixture como real.
- [\`tests/test_wur_2020_empirical_holdout.py\`](../tests/test_wur_2020_empirical_holdout.py): pruebas con datos expresamente **ficticios**, que detectan duplicación de parcela/fecha, faltantes terminales, cambios de cultivar/riego, fechas imposibles, fuentes no verificadas y contaminación temporal.
- [CI M1-20](https://github.com/barbasmarcosi/OpenPotato/actions/runs/39708654617): suite completa (215 pruebas en la primera ejecución verde), descarga temporal del CSV original público bajo licencia CC BY-NC-SA 4.0, validación de versión 3.0 y SHA256, cálculo de errores observados y publicación **solo** de reportes agregados.
- [Métricas y manifiesto de procedencia](../research/real_holdout_m1_20/wur_2020_true_holdout_empirical_baselines.json) y [reporte de los dos errores](../research/real_holdout_m1_20/wur_2020_true_holdout_empirical_baselines.md) con fuentes y licencia.
- [Auditor de acceso M1-19](../scripts/wur_potato_field_audit.py) preserva trazabilidad de los 1.824 registros originales y de la definición de \`tubersDW\`.

Para procesar legalmente una copia de la fuente fuera del repositorio:

\`\`\`bash
PYTHONPATH=.:src python -m scripts.wur_2020_empirical_holdout \
  --source /ruta/privada/Plotspecific_processed.csv \
  --out /ruta/privada/metricas-CC-BY-NC-SA
\`\`\`

El procesamiento genera **solo recuentos, seis errores agregados convertidos en MAE/RMSE/sesgo y hashes de procedencia**, no \`Plotnumber\`, valores \`tubersDW\` por parcela ni medias por variedad. Un fichero mutado, incluso con idéntico encabezado, falla por SHA-256 antes del cálculo.

## Lo pendiente para medir errores de WOFOST reales

**NO se utilizó el WOFOST de Argentina 2022–2024 para Holanda 2019–2020.** Eso habría creado emparejamientos imposibles entre sitios y campañas. Los resultados de M1-16/M1-18, incluyendo supuestos de 100 mm de riego, tampoco deben compararse con las observaciones WUR sin rediseño.

El próximo paso real exige:

1. **Interpretar los dos libros originales de clima** de Lelystad/Vredepeel 2019–2020 (\`Weatherfile_lelystad.xlsx\`, \`Weatherfile_vredepeel.xlsx\`), su unidad diaria/estación de referencia, radiación, lluvia, humedad y fechas.
2. **Documentar manejo real** de irrigación, calendario de emergencia/cosecha, textura/propiedades hidráulicas del suelo y tratamientos experimentales; reconstruir solo joins originales comprobables. Respetar la licencia CC BY-NC-SA de los archivos.
3. **Representar cultivares medidos**, cuyos coeficientes propios no se han validado. No renombrar \`Potato_701\` como \`C1\`–\`C6\` para producir un falso ajuste.
4. Mantener 2019 para cualquier calibración/autorización legítima y **2020 excluido de los ajustes**, usando las referencias empíricas anteriores como comparación mínima. Si faltan insumos esenciales, publicar un reporte **NO_ADMISSIBLE** en vez de estimar parámetros arbitrarios.
5. Contrastar biomasa seca simulada y \`tubersDW\` observado en **igual sitio, año, cultivar, fecha, manejo y unidad**, reportando errores descriptivos, sensibilidad y eventual incertidumbre; dos sitios/una campaña reservada **no prueban transferencia agronómica universal**.

La biofortificación nutricional sigue bloqueada por ausencia de Fe/Zn por muestra vinculada a parcela y verificación de seguridad, materia seca y bioaccesibilidad. Una validación agronómica no equivale a desarrollar una variedad de papa nueva.

**Decisión M1-20:** ya hay una referencia predictiva basada en **datos verdaderos**, numérica y reproducible. La siguiente inversión útil es habilitar modelos WOFOST con fuentes neerlandesas reales y parámetros justificables para superar esa referencia. Si no se pueden reunir, no inventar una validación mecanística.

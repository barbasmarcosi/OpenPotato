# M1-30 — Auditoría de las columnas originales de irrigación WUR

**Origen:** ten Den et al. (2024), Harvard Dataverse v3.0 DOI 10.7910/DVN/1LC6W7, Irrigation.xlsx ID 10284791; SHA-256 original 3def99dfb0643abe4d524431702a224bf62abd9489b306fbb89d54fdb3c9f109, CC BY-NC-SA 4.0.

El artículo científico (DOI 10.18174/odjar.v10i0.18680, tabla 7) caracteriza el archivo como riego diario por tratamiento y lluvia diaria. Los regímenes W1 (objetivo pF ~3,2) y W2 (objetivo pF ~2,4) no son en sí mismos aplicaciones observadas de agua.

El auditor scripts/wur_irrigation_schema_probe.py, ligado a SHA y versión de la fuente, examina la planilla real en un runner temporal, con las dos hojas meta (17 filas) y data (527 filas, seis columnas), detecta inequívocamente la columna de fechas con 258 registros de 2019 y 268 de 2020, e inventaría tipos de datos por columna/año y pistas de encabezados usando un vocabulario cerrado. Los resultados publicados son **exclusivamente conteos y etiquetas genéricas**; nunca valores de irrigación, fechas individuales, filas, identificadores de parcela ni texto original.

Este diagnóstico aún no prueba la columna de volumen de riego en mm, su diferencia frente a lluvia ni la clave de unión sitio × tratamiento × día. Una fila fechada puede corresponder a un tratamiento/sitio y no necesariamente a un evento físico independiente. Debe validarse antes de crear los schedules de PCSE y se preserva el holdout 2020. La ingestión PCSE de meteorología M1-27 fue correcta, pero ni suelo/cultivar ni WOFOST han sido calibrados para el campo; este hito no demuestra productividad, Fe/Zn ni inocuidad.


## Evidencia real de M1-30 — originales SHA-pinneados

La [ejecución real M1-30](https://github.com/barbasmarcosi/OpenPotato/actions/runs/39719253843) y la [suite general](https://github.com/barbasmarcosi/OpenPotato/actions/runs/39719259920) resultaron satisfactorias. Con el archivo de origen de integridad verificada, el auditor reconoció la columna física 1 como localidad, la 2 como año y la 3 como fecha tipada. Confirmó **526 claves únicas localidad × año × día**, sin duplicados ni desacuerdos año/fecha.

| Localidad | Año | Fechas únicas | Columna 4 numérica | Columna 5 numérica / ausente | Columna 6 numérica / ausente |
|---|---|---:|---:|---:|---:|
| Lelystad | 2019 | 127 | 127 | 11 / 116 | 41 / 86 |
| Vredepeel | 2019 | 131 | 131 | 74 / 57 | 77 / 54 |
| Lelystad | 2020 | 134 | 134 | 9 / 125 | 30 / 104 |
| Vredepeel | 2020 | 134 | 134 | 87 / 47 | 102 / 32 |

Las 526 observaciones de columna 4 son valores numéricos, incluyendo cero; las columnas 5 y 6 solo presentaron valores positivos o ausencias en los días auditados. **NO se ha demostrado en código que la columna 4 sea efectivamente lluvia, que 5/6 equivalgan respectivamente a W1/W2 o que su unidad sea milímetros.** El artículo describe lluvia y riego por tratamiento, lo cual apoya investigar ese mapeo, pero no autoriza hacerlo por mera posición.

La comprobación de fechas por sitio/año es un avance de integridad e identidad **que no une todavía riego con una parcela del CSV experimental** ni da fechas reales de aplicación con unidad validada. Nunca convierte celdas ausentes en cero. La fuente de irrigación y las mediciones de biomasa del holdout 2020 pueden examinarse para auditoría de cobertura, pero no se usan para estimar parámetros agronómicos de 2019.

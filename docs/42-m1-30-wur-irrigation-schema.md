# M1-30 — Auditoría de las columnas originales de irrigación WUR

**Origen:** ten Den et al. (2024), Harvard Dataverse v3.0 DOI 10.7910/DVN/1LC6W7, Irrigation.xlsx ID 10284791; SHA-256 original 3def99dfb0643abe4d524431702a224bf62abd9489b306fbb89d54fdb3c9f109, CC BY-NC-SA 4.0.

El artículo científico (DOI 10.18174/odjar.v10i0.18680, tabla 7) caracteriza el archivo como riego diario por tratamiento y lluvia diaria. Los regímenes W1 (objetivo pF ~3,2) y W2 (objetivo pF ~2,4) no son en sí mismos aplicaciones observadas de agua.

El auditor scripts/wur_irrigation_schema_probe.py, ligado a SHA y versión de la fuente, examina la planilla real en un runner temporal, con las dos hojas meta (17 filas) y data (527 filas, seis columnas), detecta inequívocamente la columna de fechas con 258 registros de 2019 y 268 de 2020, e inventaría tipos de datos por columna/año y pistas de encabezados usando un vocabulario cerrado. Los resultados publicados son **exclusivamente conteos y etiquetas genéricas**; nunca valores de irrigación, fechas individuales, filas, identificadores de parcela ni texto original.

Este diagnóstico aún no prueba la columna de volumen de riego en mm, su diferencia frente a lluvia ni la clave de unión sitio × tratamiento × día. Una fila fechada puede corresponder a un tratamiento/sitio y no necesariamente a un evento físico independiente. Debe validarse antes de crear los schedules de PCSE y se preserva el holdout 2020. La ingestión PCSE de meteorología M1-27 fue correcta, pero ni suelo/cultivar ni WOFOST han sido calibrados para el campo; este hito no demuestra productividad, Fe/Zn ni inocuidad.

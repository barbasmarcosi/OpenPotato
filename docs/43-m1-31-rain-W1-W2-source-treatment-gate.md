# M1-31 — Diccionario de irrigación y unión de tratamientos experimentales

**Fuentes:** ten Den et al. (2024), Harvard Dataverse v3 DOI https://doi.org/10.7910/DVN/1LC6W7, **CC BY-NC-SA 4.0**. Fuentes originales byte-locked: Irrigation.xlsx (file ID 10284791, SHA-256 3def99dfb0643abe4d524431702a224bf62abd9489b306fbb89d54fdb3c9f109) y Plotspecific_processed.csv (file ID 10850227, SHA-256 8d129262dca38ac98a10f92ccfb1bc46454377020575959fd984c4c5bcab5768). El artículo científico DOI https://doi.org/10.18174/odjar.v10i0.18680 Table 7 describe lluvia diaria y riego por tratamiento.

## Qué implementa

El módulo scripts/wur_irrigation_event_admission.py valida los **encabezados físicos originales y el diccionario de la hoja meta por separado**, exigiendo correspondencia de lluvia en la columna 4, riego W1 en la 5 y riego W2 en la 6, con metadatos de origen de las filas 15–17. Verifica integridad de fecha, sitio, año y valores no negativos en los 526 registros del Excel.

Contrasta las clases W1 y W2 con la columna Irrigation del CSV original de 1.824 observaciones, **sin usar ni ajustar la biomasa de 2020**: solo comprueba identidad de parcela y estabilidad del código de riego en las visitas repetidas. El reporte exporta cantidades de **días con valores positivos, celdas explícitamente cero, ausencias y número de parcelas por tratamiento y sitio-año**. Los datos diarios, cantidades de agua, IDs de parcela, filas originales y nombres completos de metadatos NO se exportan.

### Puerta de admisión de unidades

El reconocimiento de columna NO valida automáticamente la unidad física. Se buscan unidades literales declaradas en las etiquetas originales (mm o litros/m²) y se rechazan unidades conflictivas/no documentadas. Aunque haya unidades declaradas, un campo WOFOST también necesita suelo, agua disponible, distribución temporal, emergencia, variedad y agronómica real.

**Ninguna ausencia equivale a cero**. Una celda W1/W2 vacía se mantiene UNKNOWN, por lo que no se puede generar un calendario completo mediante relleno automático. Se puede acreditar el conjunto observado de aplicaciones positivas, sin publicarlas ni convertirlas en WOFOST input hasta superar las puertas de unidades y calibración. 2019 es solo desarrollo; 2020 queda reservado para evaluación final. Sin pruebas de biofortificación Fe/Zn ni seguridad.

## Evidencia reproducible

CI dedicated M1-31: verificar versión/licencia, hashes originales, el diccionario de fuente y las claves de tratamiento, ejecutar tests de datos ficticios, retirar archivos transitorios y publicar únicamente recuentos por sitio/año y campo. Un fallo de etiqueta, tipo o vínculo debe marcar la admisión como fallida, no inferir automáticamente valores.

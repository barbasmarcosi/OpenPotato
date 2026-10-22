M1-33 — Fuente original WUR: calendario de riego y UNKNOWN

El archivo Irrigation.xlsx es el original verificado de ten Den et al. (2024), Harvard Dataverse v3, DOI https://doi.org/10.7910/DVN/1LC6W7, licencia CC BY-NC-SA 4.0. La siembra procede de la tabla 3 del artículo DOI https://doi.org/10.18174/odjar.v10i0.18680. Los últimos muestreos provienen de M1-20/28; NO se asume que sean cosechas comerciales.

El módulo scripts/wur_irrigation_trial_window_coverage.py computa únicamente resúmenes por localidad y campaña para antes de la siembra, desde siembra hasta última medición, y después de ésta. Separa días con fuente, días del calendario sin fila, celdas W1/W2 positivas, ceros explícitos y blancos UNKNOWN. Días sin registro son también UNKNOWN; no se imputan cero aplicaciones ni cantidades de agua. No se publican dosis, registros originales, fechas individuales ni parcelas. La salida deja WOFOST inadmisible por falta de unidad, significado del blanco, suelo, cultivar, emergencia y parámetros reales.

M1-32 verificó lluvia del registro frente a Weatherfile con relación diaria 10x en 526/526 días. Ese hecho no confirma unidad de los campos W1/W2. El artículo sólo describe riego por goteo controlado por potencial de agua del suelo y dos regímenes pF. Se requiere documentación del laboratorio o aclaración de autores sobre unidad de W1/W2 (mm, cm o volumen por superficie) y qué representa ausencia de valor, antes de autorizar un evento físico en PCSE. No usar biomasa 2020 para calibración.


## M1-33: resultado real contra Harvard Dataverse v3.0

El [workflow de originales WUR, M1-33](https://github.com/barbasmarcosi/OpenPotato/actions/runs/39827359295) verificó la licencia, el SHA-256 y la geometría original de Irrigation.xlsx, y ejecutó 7 tests ficticios adicionales.

| Sitio | Año | Calendario desde plantación hasta última medición | Días con fila del registro | Sin fila: UNKNOWN | W1 UNKNOWN total | W2 UNKNOWN total |
|---|---:|---:|---:|---:|---:|---:|
| Lelystad | 2019 | 190 | 127 | 63 | 179 | 149 |
| Vredepeel | 2019 | 176 | 131 | 45 | 102 | 99 |
| Lelystad | 2020 | 198 | 134 | 64 | 189 | 168 |
| Vredepeel | 2020 | 182 | 134 | 48 | 95 | 80 |
| **Totales** | | **746** | **526** | **220** | **565** | **496** |

El total UNKNOWN de un tratamiento incluye días sin ninguna fila de registro más celdas de ese tratamiento vacías dentro de las filas existentes. En esas ventanas se registran 181 celdas positivas para W1 y 250 para W2, sin ningún 0 literal W1/W2. **Estos conteos NO son dosis en milímetros ni prueba de que los días UNKNOWN no se regaron.** Todos los 526 días registrados quedan dentro de los períodos conservadores de siembra a último muestreo, sin filas externas.

**Decisión operacional:** no construir un calendario WOFOST rellenando 565 (W1) o 496 (W2) días como cero; la incertidumbre de 220 fechas sin fila afecta ambos tratamientos por igual. La ventana siembra→último muestreo no debe presentarse como fenología precisa del cultivo.

Se abrió la [issue #8 — M1-34, definición de unidades y celdas vacías](https://github.com/barbasmarcosi/OpenPotato/issues/8) con preguntas específicas para aclaración mediante el diccionario original o los autores. La issue no es una consulta enviada a los autores; el proyecto mantiene bloqueadas las conversiones.

# OP-M1-23 — Auditoría numérica de columnas meteorológicas reales WUR

**Propósito:** comprobar cobertura y ausentes de variables de las dos estaciones originales, no producir un modelo WOFOST. Continuación del control de fechas M1-22: 2018=365 días, 2019=365, 2020=366 por estación; no hay fechas duplicadas en los dos archivos auditados.

Fuente: ten Den et al. (2024), Harvard Dataverse v3.0, [DOI 10.7910/DVN/1LC6W7](https://doi.org/10.7910/DVN/1LC6W7). Derechos **CC BY-NC-SA 4.0**, atribución/no comercial/compartir igual. Checksums fijados para Weatherfile_lelystad.xlsx y Weatherfile_vredepeel.xlsx como en M1-21/M1-22.

## Qué aporta M1-23

El módulo [wur_weather_column_audit.py](../scripts/wur_weather_column_audit.py) trabaja exclusivamente con los dos XLSX originales temporales, verifica SHA-256 antes de abrirlos y reconoce el eje temporal sin asumir que una columna numérica indica una unidad determinada. Por columna y estación, calcula el número de entradas finitas, faltantes tipo NA y no numéricas/no finitas en 2019–2020. Emite además categorías **tentativas** de etiquetas/unidades desde las nueve filas originales de metadatos, sin redistribuir el encabezado literal o los valores de mediciones. Todas las pruebas usan hojas ficticias.

La variable date y sus 731 días de 2019–2020 son información estructural; no se publica ni una fecha individual de medición de campo, coordenada, serie meteorológica, XLSX, hoja original ni valor de clima por sitio/día.


## Resultado auténtico de los XLSX — 21 de octubre de 2026

[CI M1-23 con originales auditados](https://github.com/barbasmarcosi/OpenPotato/actions/runs/39710932948):

| Sitio | Fechas auditadas 2019–2020 | Columnas físicas con 731/731 numéricos | Otras columnas |
|---|---:|---:|---|
| Lelystad | 731 | 8 de 9 (posiciones 2–9) | **Posición 10: 639 numéricos y 92 ausentes/NA** |
| Vredepeel | 731 | 9 de 9 (posiciones 2–10) | Sin ausentes numéricos detectados |

Las posiciones de columna son índices del XLSX fuente, no nombres de variables validados. El hecho de que 92 registros de la columna 10 en Lelystad sean ausentes **no autoriza identificar el fenómeno, su causa ni su método de imputación**. Tampoco significa que todas las otras columnas tengan unidades compatibles con WOFOST. El identificador de columna, en lugar del encabezado original o dato diario, es lo que se publica.

Las series y encabezados originales permanecen bajo CC BY-NC-SA 4.0 en el runner transitorio, no en GitHub. Esta auditoría valida únicamente cobertura numérica y trazabilidad de archivo; **no calibración ni validación de WOFOST**.

## Puerta científica

- Los conteos físicos completos NO acreditan el sensor, altura del anemómetro, unidades de irradiación, presión de vapor real ni definición de ET0/E0/ES0. ETref Makkink no puede equipararse silenciosamente a todas las necesidades de PCSE.
- No convertir porcentaje de humedad relativa a presión de vapor sin temperatura y metodología explícita.
- Sin mapeo de unidades verificadas, entradas diarias alineadas y suelo/cultivares/riego emparejados, **field_wofost_run_admissible=false**, incluso cuando todas las celdas sean numéricas.
- No se introducen Fe/Zn ni se afirma una variedad mejorada; issue #7 continúa como bloqueo.

## Próximo M1-24

Revisión física de la tabla de metadatos y método de cada sensor, normalización de humedad/vapor y meteorología compatible PCSE (E0,ES0,ET0), y verificación de entradas de manejo y suelo de los dos experimentos, sin usar 2020 para ajustar parámetros. Solo después se podrá probar WOFOST frente a la referencia empírica del holdout 2020. Los resultados negativos y los estados NO_ADMISSIBLE son resultados válidos de investigación.

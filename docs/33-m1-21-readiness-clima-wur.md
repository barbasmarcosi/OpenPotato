# OP-M1-21 — Auditoría de originales meteorológicos WUR antes de ejecutar WOFOST

**Entrega:** módulo reutilizable, cinco pruebas offline sobre XLSX inventados y pipeline de extracción de metadatos, con dos fuentes primarias verificadas por su SHA-256. **No constituye calibración o validación WOFOST.**

## Razón científica

El benchmark [M1-20](32-m1-20-errores-reales-holdout.md) calcula errores descriptivos reales contra 2020 para **promedios empíricos entrenados en 2019**, no para WOFOST. Para comparar WOFOST necesitamos reconstruir fuentes coherentes de clima diario por sitio, manejo real, variedad y suelo; tomar meteorología argentina 2022–2024 es metodológicamente inadmisible.

## Archivos legítimos y restricciones

La fuente es ten Den et al., **Harvard Dataverse v3.0**, [DOI 10.7910/DVN/1LC6W7](https://doi.org/10.7910/DVN/1LC6W7), **CC BY-NC-SA 4.0**, sin licencia comercial general. Los originales declarados en M1-19 son:

| Ubicación | Archivo WUR | ID Dataverse | SHA-256 |
|---|---|---:|---|
| Lelystad | Weatherfile_lelystad.xlsx | 10284792 | ad66a23468a969b5795a656fb6989499e790a3e18179b9e3158f203b12ab8636 |
| Vredepeel | Weatherfile_vredepeel.xlsx | 10284786 | 0bb40a5aa91ae6bfd02a8e8b4f825e4d834207884c1f2f44caa12fd0e88a1fd6 |

El pipeline consulta la metadata pública vigente, impide cambios silenciosos de versión o licencia, exige archivos no restringidos y coteja SHA-256 del XLSX descargado. Trabaja en /tmp y no exporta ningún Excel original ni valores diarios. El artefacto disponible contiene por libro exclusivamente **número y dimensiones declaradas de hojas y conteos de coincidencias aproximadas de encabezados meteorológicos**, con atribución y restricciones NC-SA explícitas.

## Qué NO significa detectar una columna meteorológica

Una etiqueta que contiene “rain”, “temp”, “radiation”, etc. **no demuestra** que existan todas las variables diarias necesarias, que la unidad esté validada ni que el libro represente las observaciones de sitio/campaña. Por ello el programa mantiene siempre **ready_to_run_field_wofost = false** y **model_driver_units_and_daily_frequency_confirmed = false**. La detección de cadenas no transforma ni interpola valores y no da lugar a pronósticos ni inferencia nutricional.

## Próxima puerta verificable: normalizar clima real 2019–2020

1. Verificar con el diccionario fuente las hojas y columnas exactas, frecuencia temporal, faltantes, convenciones de fecha, radiación, temperatura mínima/máxima, lluvia, viento y vapor, junto con las conversiones exigidas por PCSE/WOFOST; fijar un contrato explícito y pruebas de unidades.
2. Comparar la cobertura de las fechas con el periodo de crecimiento observado por sitio. Rechazar fechas faltantes o incoherentes sin imputaciones no documentadas.
3. Obtener suelo e irrigación de los mismos ensayos y parametrización de variedades científicamente defendible; nunca renombrar la papa genérica Potato_701 como un cultivar WUR.
4. Si no hay trazabilidad completa, el siguiente gate debe devolver NO_ADMISSIBLE. Únicamente después ajustar modelo en 2019 y evaluar en 2020 reservado contra los benchmarks reales existentes, con unidades de biomasa seca, reportando dependencia entre grupos y limitaciones.
5. No atribuir al crecimiento modelado mejoras en Fe/Zn, inocuidad, bioaccesibilidad ni nuevas variedades. El bloqueo de datos CIP por parcela continúa en el issue #7.

**Uso local (fuentes originales bajo licencia):** ejecutar Python 3.12 con openpyxl 3.1.5 e invocar python -m scripts.wur_weather_readiness --lelystad ... --vredepeel ... --out /tmp/estructura. No subir el original al repositorio.

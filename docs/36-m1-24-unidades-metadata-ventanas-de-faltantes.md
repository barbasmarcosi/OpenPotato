# M1-24 — Metadatos de columnas y períodos de ausencia del clima original

**Estado:** auditoría implementada. No calibra WOFOST ni constituye validación agronómica.

## Fuente y derechos
ten Den et al. (2024), Agronomic dataset on potato growth and yield in the Netherlands, Harvard Dataverse versión 3.0, DOI https://doi.org/10.7910/DVN/1LC6W7, licencia **CC BY-NC-SA 4.0**. El pipeline verifica en GitHub Actions identidad, versión, licencia y SHA-256 de Weatherfile_lelystad.xlsx y Weatherfile_vredepeel.xlsx antes de procesarlos, y elimina originales transitorios. No se distribuyen Excel, datos diarios ni encabezados originales.

## Qué analiza la etapa
El programa scripts/wur_weather_semantics_gate.py verifica cronología ordenada y sin brechas 2018–2020, distingue el prefijo de metadatos de las observaciones diarias y calcula por columna los recuentos finitos, ausentes/no numéricos por año y trimestre, y la mayor racha de ausencias. Solo emite pistas de un vocabulario propio a partir de metadatos; no son correspondencias aprobadas con campos de PCSE. Tests con observaciones inventadas, sin usar resultados publicados.

## Puertas de calidad
El contrato de PCSE exige IRRAD en J/m²/día, TMIN/TMAX en °C, VAP en hPa, WIND a 2 m, RAIN en cm/día, E0, ES0 y ET0 en cm/día. Ver la referencia de PCSE: https://github.com/ajwdewit/pcse/blob/master/doc/reference_guide.rst y su referencia de cálculo de evapotranspiración https://pcse.readthedocs.io/en/5.5.6/code.html.

**No** equiparar humedad relativa (%) con VAP (hPa), ni evapotranspiración Makkink con los tres componentes de referencia exigidos por PCSE. Antes de derivar E0/ES0/ET0 hay que aprobar coordenadas y elevación de estación, definiciones de viento/radiación y método reference_ET/coeficientes. No es correcto imputar automáticamente las 92 celdas que faltan en la columna 10 de Lelystad: primero hay que identificar su significado y su patrón de ausencia.

Aun completando meteorología, siguen pendientes suelo, riego, cultivar y fenología del ensayo original para calibración específica, así como un protocolo de evaluación 2019 entrenamiento / 2020 reservado que no filtre datos. Ninguna de estas auditorías demuestra calidad nutricional, Fe/Zn o inocuidad: issue #7 permanece abierto.

## Próxima ejecución
Ejecutar la puerta sobre ambos originales bajo licencia, registrar el patrón por año/trimestre, revisar las pistas de unidades y precisar los obstáculos de mapeo. Mantener siempre field_wofost_run_admissible = false hasta revisión original y comprobaciones de manejo/variedades. No producir estadísticas de error WOFOST sin predicciones emparejadas.

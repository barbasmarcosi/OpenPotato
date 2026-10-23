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


## Resultado original reproducido — campo WUR (M1-24)

En [GitHub Actions M1-24](https://github.com/barbasmarcosi/OpenPotato/actions/runs/39712232552), las dos fuentes SHA-pinneadas confirmaron los 1.096 días diarios por estación sin duplicados. En **2020**, la **columna física 10 de Lelystad** contiene 92 faltantes consecutivos, exactamente **todos los días de octubre, noviembre y diciembre**; en 2019 no tiene ausentes. Vredepeel no tiene ausentes en las nueve columnas meteorológicas analizadas durante 2019–2020. Los recuentos trimestrales confirman esta distribución sin publicar ningún valor meteorológico.

El archivo original tiene **11 filas de prefijo antes de la primera fecha** (incluidas anotaciones/encabezados). El artículo contiene una discrepancia documental que debe conservarse: el texto del apartado 4 menciona **seis filas** de metadatos para archivos meteorológicos, mientras la tabla 7 menciona **nueve filas**; ninguna de esas cifras debe sustituir el detector basado en las fechas originales sin una conciliación del diseño. La columna 10 no tuvo una asociación semántica ni una unidad aprobada por la clasificación automatizada. En los reportes, vacío de vocabulario NO significa que una variable no esté definida en el original: significa que nuestro parser aún no la ha identificado inequívocamente.

### Interpretación de la cobertura del holdout

El archivo de observaciones del ensayo documenta última fecha de medición en Lelystad 2020 el 3 de noviembre. Por tanto, el bloque meteorológico ausente coincide con parte del período hasta el último muestreo. **No corresponde asumir que todos los 92 días son indispensables para un ciclo WOFOST**: el límite de simulación depende de fenología, fecha efectiva de finalización y objetivo (biomasa en último muestreo vs cosecha comercial). Sin aprobación del campo físico de columna 10 ni el calendario de modelo, NO se pueden tratar esos 92 días como datos válidos, ni descartar la variable como irrelevante.

### Documentación externa verificada

El artículo primario [ten Den et al., 2024](https://doi.org/10.18174/odjar.v10i0.18680), sección 3.3, identifica estación **DACOM** cercana al campo para temperaturas mínima y máxima en °C, viento en m/s, lluvia en mm y evapotranspiración ETo/Etref por **Makkink** en mm/día. La irradiación y humedad en % proceden de estaciones **KNMI** (Volkel para Vredepeel, aeropuerto de Lelystad para Lelystad). Este detalle describe categorías de variables **a nivel de publicación**, NO asigna un campo físico concreto a las posiciones 2–10 de cada XLSX ni prueba altura del anemómetro, fórmula de humedad o unidades definitivas de radiación. Se debe documentar el mapeo exacto antes de ejecutar PCSE.

## Próxima ejecución
Ejecutar la puerta sobre ambos originales bajo licencia, registrar el patrón por año/trimestre, revisar las pistas de unidades y precisar los obstáculos de mapeo. Mantener siempre field_wofost_run_admissible = false hasta revisión original y comprobaciones de manejo/variedades. No producir estadísticas de error WOFOST sin predicciones emparejadas.

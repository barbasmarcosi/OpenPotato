# OP-M1-22 — Meteorología diaria WUR: continuidad, unidades y bloqueo de acceso a WOFOST

**Etapa implementada:** auditor de cronología real de Excel y convertidor estricto de unidades para datos DIARIOS **ficticios/autorizados**. NO se generaron predicciones agronómicas ni se ajustó WOFOST a WUR.

## Fuente primaria y método
- ten Den et al. (2024), *Agronomic dataset on potato growth and yield in the Netherlands*. DOI [10.7910/DVN/1LC6W7](https://doi.org/10.7910/DVN/1LC6W7) y artículo [10.18174/odjar.v10i0.18680](https://doi.org/10.18174/odjar.v10i0.18680).
- La publicación describe termometría, viento, precipitaciones y evapotranspiración de estaciones próximas DACOM, e irradiación/humedad obtenidas de KNMI. Indica metadatos en las primeras nueve filas de los archivos Weatherfile_lelystad.xlsx y Weatherfile_vredepeel.xlsx. **Sus encabezados no constituyen por sí mismos un diccionario de conversión aprobado.**
- Dataset Harvard Dataverse **v3.0, CC BY-NC-SA 4.0**. Los originales se cotejan con los SHA-256 anclados en M1-21. Las filas originales y datos meteorológicos NO se incorporan al repositorio.

## Contrato técnico PCSE 6
Referencia de campos/unidades: [PCSE weather reference](https://pcse.readthedocs.io/en/6.0.5/_modules/pcse/base/weather.html). Se exigen registros diarios consecutivos, sin duplicados ni ausentes rellenados. Campos: DAY, IRRAD en J/m²/día, TMIN/TMAX en °C, VAP en hPa, RAIN/E0/ES0/ET0 en cm/día y WIND en m/s **a 2 m**. El convertidor solo admite transformaciones declaradas por campo (kJ o MJ a J; mm a cm; kPa a hPa). No transforma humedad relativa %RH en presión de vapor, no asume altura de viento, no finge que ET0 Makkink garantiza E0/ES0 Penman. Rechaza entradas faltantes, no finitas, físicamente imposibles y fechas ambiguas. Un CSV sin procedencia de unidades no pasa.

## Qué se audita de los XLSX VERDADEROS
Se identifica —sin exportar valores— si después de las nueve filas de metadatos existe un posible eje de fechas de 2019/2020. Solo se emiten por libro/hoja: dimensiones, número de registros con fecha inequívoca por año, fechas distintas, duplicados y brechas de días dentro del periodo observado. Las fechas individuales, coordenadas, nombres de hojas, medidas y valores diarios quedan en memoria.

**Ninguna columna se considera meteorología validada por detección de nombres.** Las fechas Excel sin formato temporal y los estilos regionales ambiguos se rechazan. Este diagnóstico de fechas no identifica todavía variables físicas: field_wofost_run_admissible **siempre es false**. La salida de conversión local, aunque supere consistencia física, continúa marcada UNIT_NORMALIZATION_ONLY_NOT_MODEL_ADMISSION. Ningún reporte registra rendimientos medidos ni inventa Fe/Zn.

## Puertas restantes (M1-23)
1. Resolver el mapeo original exacto de hoja, columna, unidad, método instrumental y estación mediante el artículo, metadatos Excel y revisión humana; producir matriz de correspondencias aprobada, versionada y contrastada con datos originales bajo licencia.
2. Verificar diariamente sitio/año y las fechas del ciclo del cultivo; justificar E0, ES0, ET0, VAP y WIND2 antes de crear un WeatherDataProvider PCSE válido (derivar humedad de %RH requiere temperatura/convenio de cálculo, no sustitución directa).
3. Identificar riego, suelo, fertilización y cultivares realmente medidos; modelo genérico Potato_701 no demuestra calibración para C1-C6.
4. Mantener holdout temporal 2019→2020, sin ajuste en 2020; contrastar WOFOST contra benchmarks empíricos M1-20 solo con pares exactos de sitio, fecha, cultivar, manejo y biomasa seca kg/ha.
5. No interpretar estos resultados como biofortificación: Fe/Zn por parcela y seguridad todavía bloqueados, issue #7.

**Seguridad/licencia:** las fuentes originales de Harvard son CC BY-NC-SA 4.0; los artefactos públicos contienen exclusivamente conteos estructurales y preservan atribución. En CI no se guardan archivos XLSX originales ni meteorología diaria extraída.

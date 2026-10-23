# M1-26 — Fuente WUR y esquema de entrada PCSE reconocido

Estudio: ten Den et al. (2024), DOI https://doi.org/10.7910/DVN/1LC6W7, versión 3.0, CC BY-NC-SA 4.0. Se respetan los hashes SHA-256 originales de las estaciones Lelystad/Vredepeel; los Excel y valores diarios no se publican.

## Hallazgo de reutilización

La implementación pública https://github.com/ronvree/diffwofost-tutorial ya implementa la importación de **estos mismos originales** a PCSE, bajo licencia EUPL-1.1. También está disponible https://github.com/WUR-AI/diffWOFOST. Se estudió únicamente el esquema de interoperabilidad, sin copiar su código ni reutilizar pesos de entrenamiento.

El notebook público contempla la fila 10 como encabezado y 11 como unidades; entradas DAY, IRRAD, TMIN, TMAX, VAP, WIND, RAIN, SNOWDEPTH, en posiciones 1–8. PCSE ExcelWeatherDataProvider acepta irradiación kJ/m²/día u horas de sol, temperaturas °C, VAP kPa, WIND m/s, RAIN mm, nieve cm; convierte a unidades internas y calcula las tres evaporaciones de referencia E0/ES0/ET0. Documentación oficial: https://pcse.readthedocs.io/en/stable/_modules/pcse/input/excelweatherdataprovider.html .

El nuevo archivo scripts/wur_pcse_source_contract.py comprueba las correspondencias por NOMBRE exacto, las unidades de entrada y la disponibilidad directamente en los Excel originales de hash fijado. No infiere el significado de las columnas auxiliares 9 y 10 y no redistribuye su información. Si el original contradice el contrato, detiene la CI. Las ausencias detectadas en la columna 10 no prueban falta de una de las seis variables obligatorias del lector Excel; sólo cuando la fuente hash-verificada concuerde podemos concluir que es un campo no consumido por este adaptador.

## Resultado verificado con la fuente primaria

[Action original M1-26/M1-27 exitosa](https://github.com/barbasmarcosi/OpenPotato/actions/runs/39715050232): seis campos meteorológicos obligatorios de PCSE completos en 2019 y 2020 para ambas estaciones; campos no utilizados en posiciones **8 y 10**, en ambos libros. La posición 10 es la que registra los 92 faltantes de Lelystad; esto no afecta la cobertura de las variables obligatorias del adaptador verificado.

[Suite general](https://github.com/barbasmarcosi/OpenPotato/actions/runs/39715052748): exitosa. El extractor de metadatos mantiene aviso de no validación agronómica.

## Limitaciones y próxima etapa

Una entrada legible no demuestra la altura medida del viento (se requieren datos a 2 m), validez experimental de reference_ET, manejo, suelo, cultivar, fenología o rendimiento. Tampoco demuestra Fe/Zn ni seguridad. Mantener entrenamiento 2019 / evaluación 2020 sin contaminar el holdout.

M1-27: construir y comprobar el proveedor ExcelWeatherDataProvider real en una carpeta transitoria, verificando exactitud del número de días finalmente admitidos, sin reportar ni publicar ninguna observación meteorológica ni ejecutar el modelo agronómico. Si falla en cualquier día de 2019–2020, la etapa debe señalar la discrepancia. Después investigar el emparejamiento agronómico y la parametrización de las variedades.

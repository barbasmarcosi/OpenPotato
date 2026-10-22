# M1-32 — Comparación entre lluvia del registro de riego y estación meteorológica

**Tipo:** control de coherencia entre fuentes originales, no calibración WOFOST, no inferencia automática de unidades.

**Fuentes**: ten Den et al. (2024), Harvard Dataverse v3.0, DOI https://doi.org/10.7910/DVN/1LC6W7, licencia CC BY-NC-SA 4.0, tres archivos originales SHA-256 fijados: Irrigation.xlsx (ID 10284791), Weatherfile_lelystad.xlsx (ID 10284792) y Weatherfile_vredepeel.xlsx (ID 10284786). El artículo científico https://doi.org/10.18174/odjar.v10i0.18680 documenta experimentos en Lelystad/Vredepeel y sensores locales; **no prueba equivalencia exacta** entre la lluvia del registro de riego y el pluviómetro de las estaciones.

## Hipótesis contrastable, no una conversión aprobada

M1-31 identificó con evidencia de diccionario la columna 4 como lluvia, 5 como W1 y 6 como W2, pero las unidades de W1/W2 siguen sin declararse inequívocamente. El clima PCSE original incluye una columna RAIN etiquetada en milímetros. M1-32 cruza ambas fuentes únicamente por sitio×año×fecha (526 claves en las cuatro combinaciones), calculando dentro del runner:

- cuántos días ambas fuentes dicen lluvia positiva o ambas registran cero;
- días discordantes para la presencia de lluvia (lluvia positiva solo en una de las fuentes);
- coincidencia numérica exacta y diferencia numérica media **condicional** a comparar números en sus escalas originales;
- cociente de sumas de lluvia **condicional**, que no demuestra igualdad de unidad;
- conteo por tratamiento de positivos, ceros literales o blancos de riego W1/W2, conservando el blanco como UNKNOWN.

Las únicas salidas son estadísticos **agregados por sitio y campaña**, jamás fechas individuales, cantidades diarias, eventos, celdas originales, parcela o coordenadas. Se auditan los tres archivos originales y su integridad antes de procesarlos; la meteorología debe tener exactamente 1.096 días por localidad. La comprobación de archivo original prevalece sobre ejemplos de modelos y supuestos.

## Criterio científico

Incluso una comparación con correlación o igualdad alta NO atribuye automáticamente las unidades físicas de las aplicaciones de W1/W2. Ambas fuentes pueden proceder de instrumentos distintos, mediciones a escalas diferentes o transformaciones previas. Los blancos de W1/W2 no son ceros sin documentación.

La siguiente etapa deberá documentar formalmente la fuente de unidad, el significado de las celdas vacías y las tasas de aplicación. Hasta entonces el estado de agromanejo WOFOST y las predicciones de campo sigue bloqueado; 2020 permanece reservado como año de evaluación de rendimiento y ningún valor nutricional Fe/Zn o seguridad queda establecido.

# M1-27 — Prueba del lector meteorológico oficial PCSE sobre WUR

Fase de interoperabilidad, no de validación agronómica. Fuente: ten Den et al. (2024), Harvard Dataverse 3.0, https://doi.org/10.7910/DVN/1LC6W7, CC BY-NC-SA 4.0. El esquema y las convenciones se comprobaron contra https://github.com/ronvree/diffwofost-tutorial (licencia EUPL-1.1); el código de OpenPotato es independiente.

El programa scripts/wur_pcse_weather_provider_smoke.py parte de los dos Excel originales SHA-verificados, comprueba nombres reales de columna (no posiciones supuestas), metadatos de estación, valores obligatorios y fechas. Reconstruye un libro meteorológico compatible con la especificación ExcelWeatherDataProvider dentro de una carpeta temporal y utiliza PCSE 6.0.13 para recuperar **cada uno de los 1.096 días originales por estación** (2018, 2019, 2020), incluidos E0/ES0/ET0 derivados por reference_ET. Ningún valor de meteorología sale del proceso; se guardan solo recuentos de días y hashes de fuente.

El lector PCSE puede ignorar filas inválidas con advertencia: el chequeo posterior de cobertura exacta evita afirmar compatibilidad sobre una importación parcial. El proceso no ejecuta WOFOST, no entrena coeficientes, no publica observaciones ni prueba Fe/Zn, inocuidad, rendimiento o estabilidad. **La verificación del método de E0/ES0/ET0 y de la altura del viento sigue pendiente antes de hablar de una simulación de campo calibrada.**

Queda pendiente construir joins de suelo/agua/variedades y mantener 2020 exclusivamente reservado para validación del modelo, sin ajuste a posteriori.

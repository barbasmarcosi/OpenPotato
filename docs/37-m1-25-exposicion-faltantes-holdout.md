# OpenPotato M1-25 — Meteorología WUR: intersección de ausencias con el holdout

**Estado:** auditor desarrollado, con nueve pruebas sintéticas. No constituye ajuste, evaluación ni validación de WOFOST.

## Fuente y protección
Tamara ten Den et al. (2024), *Agronomic dataset on potato growth and yield in the Netherlands*, Harvard Dataverse v3.0, DOI https://doi.org/10.7910/DVN/1LC6W7, **CC BY-NC-SA 4.0**. Los dos originales Weatherfile_lelystad.xlsx y Weatherfile_vredepeel.xlsx se comprueban contra hashes ya anclados. El pipeline valida identidad/versión/licencia y procesa los libros solo temporalmente, sin guardar series, etiquetas originales ni variables medidas.

## Alcance de la comparación
La etapa previa M1-24 demostró 92 ausencias consecutivas en el **cuarto trimestre de 2020**, exclusivamente en la **posición física 10** del libro de Lelystad. M1-25 separa estos faltantes tomando como límite de interés el **último día de medición de biomasa** ya auditado en M1-20 (Lelystad 2020-11-03 y Vredepeel 2020-10-19).

**Advertencia:** la ventana de cómputo comienza el **1 de enero** como criterio conservador de exposición y termina en la **última fecha de muestreo**. No supone que el cultivo emergiera el 1 de enero ni que la última observación fuera la cosecha comercial. Antes de construir WOFOST se necesitan fechas agronómicas auténticas y una definición objetiva del endpoint comparado.

### Resultado verdadero de los archivos originales
Se guardan únicamente recuentos por lugar, año y **posición física de columna**, nunca días ni mediciones individuales. El resultado de M1-25 debe confirmar en Lelystad durante 2020: 92 ausentes en la columna 10, **34 anteriores o coincidentes con el último muestreo** (octubre + primeros tres días de noviembre) y **58 posteriores**. Vredepeel 2019–2020 no presenta faltantes de valor numérico en las nueve columnas físicas revisadas. La columna 10 no tiene asignación semántica/PCSE revisada, así que la utilidad de estas 34 ausencias para simulación permanece desconocida.

## Puerta de aptitud científica
- Datos de fecha íntegros y fuentes con checksum son necesarios, pero insuficientes.
- PCSE requiere campos de radiación, TMIN, TMAX, vapor en hPa, lluvia, viento a 2 m y E0/ES0/ET0 con conversiones justificadas, como documenta https://pcse.readthedocs.io/en/6.0.4/code.html.
- No reemplazar humedad relativa con VAP ni evapotranspiración Makkink con E0/ES0/ET0 sin método de derivación validado.
- Parametrización de suelo, riego, fechas de emergencia y cultivares observados siguen sin validarse; el escenario de papa genérica no representa C1–C6.
- Una simulación sobre clima neerlandés no acredita productividad observada, estabilidad genotípica, Fe/Zn o inocuidad.

El módulo scripts/wur_weather_holdout_exposure.py mantiene explícitamente **field_wofost_run_admissible=false**; ninguna entrada se completa automáticamente. El siguiente hito M1-26 debe buscar y aprobar diccionarios instrumentales/variables del estudio e incorporar el protocolo real de suelo/riego/fenología, antes de calcular cualquier MAE/RMSE de WOFOST frente al benchmark empírico 2020.

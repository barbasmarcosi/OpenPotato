# M1-35 — Datos originales de potencial hídrico y nivel freático WUR

**Fuente:** ten Den et al. (2024), [Harvard Dataverse v3](https://doi.org/10.7910/DVN/1LC6W7), licencia CC BY-NC-SA 4.0. Archivos primarios: `Groundwaterlevel.xlsx` ID 10284788 y `Waterpotential.xlsx` ID 10284794. El artículo de [Open Data Journal for Agricultural Research](https://doi.org/10.18174/odjar.v10i0.18680) distingue el suelo arcilloso en Lelystad y el arenoso en Vredepeel.

## Objetivo y estado científico

Contrastar la disponibilidad efectiva de mediciones de potencial hídrico del suelo y niveles freáticos durante 2019/2020, antes de parametrizar WOFOST. Es incorrecto interpretar mediciones de estado hídrico como una curva de retención suelo-agua o como la conductividad hidráulica saturada.

El script `scripts/wur_soil_water_source_inventory.py` audita los originales de forma temporal, distingue hojas meta/datos por posición, cuantifica clases de celda y fechas tipadas y detecta indicios de profundidad, potencial, nivel freático, pF, kPa y unidades **solo como etiquetas controladas**. No se redistribuyen archivos, encabezados originales, valores medidos ni filas.

Para habilitar un proveedor físico de suelo se necesitarán perfiles por horizonte, relación contenido hídrico–potencial matricial, parámetros de conductividad, profundidad radicular, contenido inicial y condiciones de borde, con unidades y sitios verificables. El potencial hídrico observado puede ser valioso en una validación posterior, pero no es por sí solo el parámetro constitutivo del suelo.

Se mantienen las restricciones: las unidades y blancos del riego W1/W2 permanecen sin resolver en [issue #8](https://github.com/barbasmarcosi/OpenPotato/issues/8); biomasa 2020 se preserva para evaluación; WOFOST no se considera validado. La investigación sigue sujeta a revisión de licencia para eventuales reutilizaciones. No se han demostrado resultados de Fe/Zn ni inocuidad.

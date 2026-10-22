# M1-35 — Datos originales de potencial hídrico y nivel freático WUR

**Fuente:** ten Den et al. (2024), [Harvard Dataverse v3](https://doi.org/10.7910/DVN/1LC6W7), licencia CC BY-NC-SA 4.0. Archivos primarios: `Groundwaterlevel.xlsx` ID 10284788 y `Waterpotential.xlsx` ID 10284794. El artículo de [Open Data Journal for Agricultural Research](https://doi.org/10.18174/odjar.v10i0.18680) distingue el suelo arcilloso en Lelystad y el arenoso en Vredepeel.

## Objetivo y estado científico

Contrastar la disponibilidad efectiva de mediciones de potencial hídrico del suelo y niveles freáticos durante 2019/2020, antes de parametrizar WOFOST. Es incorrecto interpretar mediciones de estado hídrico como una curva de retención suelo-agua o como la conductividad hidráulica saturada.

El script `scripts/wur_soil_water_source_inventory.py` audita los originales de forma temporal, distingue hojas meta/datos por posición, cuantifica clases de celda y fechas tipadas y detecta indicios de profundidad, potencial, nivel freático, pF, kPa y unidades **solo como etiquetas controladas**. No se redistribuyen archivos, encabezados originales, valores medidos ni filas.

Para habilitar un proveedor físico de suelo se necesitarán perfiles por horizonte, relación contenido hídrico–potencial matricial, parámetros de conductividad, profundidad radicular, contenido inicial y condiciones de borde, con unidades y sitios verificables. El potencial hídrico observado puede ser valioso en una validación posterior, pero no es por sí solo el parámetro constitutivo del suelo.

Se mantienen las restricciones: las unidades y blancos del riego W1/W2 permanecen sin resolver en [issue #8](https://github.com/barbasmarcosi/OpenPotato/issues/8); biomasa 2020 se preserva para evaluación; WOFOST no se considera validado. La investigación sigue sujeta a revisión de licencia para eventuales reutilizaciones. No se han demostrado resultados de Fe/Zn ni inocuidad.

## Resultado real de fuentes originales — 22 de octubre de 2026

La [ejecución M1-35](https://github.com/barbasmarcosi/OpenPotato/actions/runs/39831288748) obtuvo los Excel originales de Harvard Dataverse v3, verificó versión, licencia, nombre, estado de acceso y MD5 original. Los siguientes SHA-256 independientes quedaron anclados en script y CI:

- Groundwaterlevel.xlsx (ID 10284788): 7c546ba5493fa28bb073073071ff44be562e89d4401467caefe73b82911f65de.
- Waterpotential.xlsx (ID 10284794): 7a6924d01eff020215a1aca9c7de36fa4d97b33a0e99cfcf330127bedcfdec15.

| Origen | Hoja | Filas | Columnas | Celdas fecha 2019 / 2020 |
|---|---:|---:|---:|---|
| Groundwaterlevel | Meta #1 | 5 | 3 | — |
| Groundwaterlevel | Datos #2 | 141 | 4 | 100 / 40 |
| Waterpotential | Meta #1 | 187 | 7 | — |
| Waterpotential | Datos #2 | 8.237 | 38 | 7.666 / 0 |
| Waterpotential | Datos #3 | 8.078 | 35 | 7.708 / 0 |
| Waterpotential | Datos #4 | 7.470 | 26 | 0 / 6.894 |
| Waterpotential | Datos #5 | 6.672 | 24 | 0 / 6.671 |

Los conteos de fechas corresponden a **celdas reconocibles**, no a días calendario independientes, ni a parcelas o sensores inequívocamente mapeados. Pueden existir marcas temporales repetidas por sensor. El emparejamiento hoja ↔ localidad todavía no está aprobado.

Las etiquetas de metadatos presentan indicios de profundidad en cm, potencial hídrico en kPa y pF, y nivel freático; **no se han validado unidades para cada columna**. No podemos generar curvas de retención, conductividad hidráulica o parámetros físicos WOFOST únicamente por estas pistas. En particular, el perfil arenoso de Vredepeel y el arcilloso de Lelystad requieren validación sitio-específica.

La CI ahora exige los hashes originales, 2 y 5 hojas respectivamente, sus dimensiones y los recuentos tipados de fechas por año. Los archivos, mediciones y encabezados originales no se publican.

**Siguiente M1-36:** validar identidad de hoja sitio×año, frecuencia, sensores, profundidad, unidad física por campo y controles de series temporales; comprobar si existen pares de potencial y contenido hídrico antes de inferir curvas hidráulicas. En paralelo, volver a los criterios de cierre de M1 nutricional: USDA, perfil poblacional, nutrientes ausentes, biodisponibilidad y revisión crítica. La [issue #8](https://github.com/barbasmarcosi/OpenPotato/issues/8) mantiene pendiente el riego W1/W2.

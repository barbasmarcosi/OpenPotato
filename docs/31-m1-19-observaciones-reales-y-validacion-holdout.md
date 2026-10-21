# M1-19 — Observaciones agronómicas REALES y puerta de evaluación WOFOST

**Fecha:** 21-10-2026. **Resultado:** fuente experimental verificada, contenido tabular y unidades auditados, protocolo de contraste implementado. **NO se ha calibrado ni validado WOFOST contra las observaciones originales todavía.** Solo se probó el comparador con fixtures ficticios.

## 1. Datos originales auditados

Fuente primaria: **Tamara ten Den y colaboradores (2024)**, «Agronomic dataset on potato growth and yield in the Netherlands», Harvard Dataverse versión **3.0**, DOI https://doi.org/10.7910/DVN/1LC6W7. Artículo descriptivo: https://doi.org/10.18174/odjar.v10i0.18680.

Ensayos de **Lelystad y Vredepeel**, Países Bajos, en **2019 y 2020**, con variedades, nitrógeno, tratamientos hídricos y observaciones de crecimiento y biomasa. Se verificaron 13 archivos públicos mediante la API de Harvard Dataverse y las huellas exactas de los siguientes cinco:

| Archivo original | Dataverse file ID | SHA-256 |
|---|---:|---|
| Plotspecific_processed.csv | 10850227 | 8d129262dca38ac98a10f92ccfb1bc46454377020575959fd984c4c5bcab5768 |
| Plotspecific_processed_meta.xlsx | 10850226 | b6bada9e4d9352e2975dbf1159299b114369a36598aa924b3222fa5ce101945c |
| Irrigation.xlsx | 10284791 | 3def99dfb0643abe4d524431702a224bf62abd9489b306fbb89d54fdb3c9f109 |
| Weatherfile_lelystad.xlsx | 10284792 | ad66a23468a969b5795a656fb6989499e790a3e18179b9e3158f203b12ab8636 |
| Weatherfile_vredepeel.xlsx | 10284786 | 0bb40a5aa91ae6bfd02a8e8b4f825e4d834207884c1f2f44caa12fd0e88a1fd6 |

**Licencia real del dataset: CC BY-NC-SA 4.0, no CC0.** Requiere atribución, permite usos bajo condición no comercial y compartir adaptaciones bajo las mismas condiciones. **No convertirla silenciosamente en datos de uso comercial sin restricciones.** Los originales no se incorporaron al repo. Los archivos se descargaron temporalmente para verificar origen y cobertura; solo se publican metadatos agregados con atribución y aviso de licencia.

El libro original de metadatos confirma específicamente estas unidades:
- **tubersDW:** peso SECO de tubérculos, **kg/ha**, físicamente comparable a la salida TWSO de WOFOST tras verificar cultivo, fecha y tratamiento.
- **tubersFW:** peso fresco de tubérculos, **kg/ha**.
- **FWyield:** rendimiento fresco, **t/ha**.
- **Yield_gross_t.ha:** rendimiento bruto, **t/ha**.
- **tuberDMpercentage:** porcentaje de materia seca del tubérculo.
- **LAI:** índice de área foliar.

No se pueden mezclar peso fresco y seco sin materia seca medida y conversiones auditadas. La unidad física es un requisito, pero **no demuestra** que la predicción y la medición correspondan al mismo ambiente, cultivar o momento.

## 2. Resultado real de la inspección (sin publicar observaciones)

Archivo Plotspecific_processed.csv, original verificado: **1.824 registros**. La distribución es:

| Año | Sitio | Registros de distintas fechas/rasgos | Parcela física identificada, recuento |
|---|---|---:|---:|
| 2019 | Lelystad | 495 | 45 |
| 2019 | Vredepeel | 504 | 42 |
| 2020 | Lelystad | 405 | 45 |
| 2020 | Vredepeel | 420 | 42 |

Se distinguieron los números reales de literales de ausencia NA, NaN y NULL:

| Campo original | Registros con medición numérica | Sin medición numérica |
|---|---:|---:|
| tubersDW, kg/ha materia seca | **1.048** | 776 |
| tubersFW, kg/ha materia fresca | 1.063 | 761 |
| FWyield, t/ha materia fresca | 1.063 | 761 |
| tuberDMpercentage | 454 | 1.370 |
| LAI | 996 | 828 |
| Yield_gross_t.ha | 87 | 1.737 |

**1.048 no es el número de cosechas finales independientes**: hay registros de las mismas parcelas en distintas fechas. Los valores de observaciones y los identificadores de cada parcela no se exportaron. Los contadores son metadatos sanitizados de disponibilidad, NO un ensayo de validación.

Código: [auditor de fuente real](../scripts/wur_potato_field_audit.py), [pruebas](../tests/test_wur_potato_field_audit.py), [inventario y recuentos anónimos](../research/field_observations_m1_19/wur_2019_2020_real_trial_source_admission.json) y [reporte](../research/field_observations_m1_19/wur_2019_2020_real_trial_source_admission.md).

## 3. Comparador científico, sin falsa independencia

Nuevo [comparador de biomasa seca observado/modelado](../scripts/tuber_dry_holdout_diagnostic.py), para usar **localmente** con datos normalizados que hayan sido obtenidos y tratados bajo permiso legítimo:

1. Identifica exactamente **ensayo, sitio, campaña, cultivar, manejo, fecha, rasgo y unidad**. No permite unir datos por nombre aproximado ni imputar predicciones ausentes.
2. Solo acepta **kg de biomasa seca de tubérculo por hectárea**. Prohíbe asumir que toneladas de rendimiento fresco o la biomasa aérea equivalen a TWSO.
3. Verifica unicidad de **parcela física × fecha** y asignación única de cultivar/manejo. Si una parcela se repite, **no** se cuenta como una nueva réplica biológica.
4. El modelo aporta **una predicción por grupo**, comparada con la media descriptiva de parcelas físicas observadas en el grupo, no una predicción independiente por cada parcela.
5. Exige un manifiesto de campañas de **calibración y evaluación separadas**, división predeclarada y declaración explícita de que el modelo no fue ajustado usando los resultados reservados. Esto controla coherencia documental, pero **no prueba por sí solo** que nunca hubo fuga durante el trabajo humano.
6. Rechaza sustituir parámetros del cultivar medido con el perfil genérico Potato_701 como si fueran específicos de la variedad original. Exige hashes completos para modelo y clima.
7. Si los datos se admiten, calcula **MAE, RMSE y sesgo únicamente descriptivos**, sobre grupos y medias sitio×año; **no** infiere intervalos de confianza ni independencia de los grupos dentro del mismo ensayo.

**Importante:** el reporte siempre se identifica como DIAGNOSTIC, no como VALIDATED. El error de predicción que prueban los fixtures de CI es **SINTÉTICO**, no la precisión real de WOFOST para Wageningen.

## 4. Evidencia de ejecución

La [Action M1-19](https://github.com/barbasmarcosi/OpenPotato/actions/runs/39614030031) finalizó correctamente. Ejecutó **203 pruebas** (incluidas 8 sobre procedencia/licencia y 13 sobre las barreras del comparador), descargó solamente el CSV original público exacto, verificó MD5/SHA-256, licencia/versionado y recuentos de observaciones reales, realizó una prueba end-to-end **sintética** de comparación y publicó **únicamente el resumen agregado**, sin filas individuales, ni producciones por parcela.

La [Action de investigación original](https://github.com/barbasmarcosi/OpenPotato/actions/runs/39612388230) verificó además los 13 nombres originales y la metadata de los cinco archivos principales, incluyendo los libros de riego y clima.

## 5. M1-20 — primer error de predicción sobre observaciones verdaderas

Para pasar de la trazabilidad a la **validación cuantitativa auténtica**, hace falta:

1. Normalizar temporalmente el CSV original sin inventar que cada registro de tubersDW es el rendimiento final: separar etapas de crecimiento, cosecha final, área, unidad biológica, tratamiento y cultivar.
2. Interpretar los libros meteorológicos 2019/2020 de **los propios sitios**, sus fechas y unidades, y verificar el calendario de siembra/emergencia y la transpiración/irrigación registradas.
3. Calibrar o justificar parámetros de variedades **reales** de la fuente, con perfil de suelo documentado; no etiquetar Potato_701 como otro cultivar ni usar clima argentino 2022/24 para experimentos neerlandeses 2019/20.
4. Elegir **un año de calibración** y **otro año reservado para evaluación** antes del ajuste; nunca seleccionar retrospectivamente la división de mejor resultado.
5. Producir salidas WOFOST con hashes de parámetros, clima y código, y recién entonces comparar contra kg/ha SECO observado. Reportar MAE/RMSE/sesgo con unidades físicas y límites de correlación dentro de ensayo y sitio/año.
6. Para demostrar transferencia fuera de este dominio, buscar un **tercer ensayo externo**. Dos sitios y dos campañas no justifican generalización mundial ni extrapolación a Argentina.

Esta fuente real es **agronómica**, no de Fe/Zn. Nuestro bloqueo científico para biofortificación de tubérculos CIP, inocuidad y biodisponibilidad se mantiene: los modelos de crecimiento no pueden sustituir análisis químicos primarios.

**Decisión M1-19:** tenemos evidencia agronómica verdadera, licencia/huellas/mediciones documentadas y el comparador listo para la próxima etapa. **No afirmar todavía calibración, validez agronómica externa ni mejoras nutricionales comprobadas.**

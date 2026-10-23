# OP-M1-16 — Crecimiento mecanístico de papa con WOFOST 8.1 y clima NASA POWER

**Fecha:** 21-10-2026. **Estado:** ocho simulaciones auténticas del modelo WOFOST con meteorología histórica pública, validación técnica en Actions y conservación del origen. **Ningún dato de rendimiento, composición nutricional o cultivar fue medido por OpenPotato.**

## Alcance, sin sobreinterpretar

Se ejecuta [PCSE 6.0.13](https://pypi.org/project/pcse/6.0.13/) con **WOFOST 8.1 en modo PP (potential production)**, no un modelo ajustado a una variedad del CIP. La parametrización agronómica es la variedad genérica publicada `Potato_701` de [WOFOST_crop_parameters, commit fijado `1ca91d7dbb5aaf6b41462162de03a8254812d3a5`](https://github.com/ajwdewit/WOFOST_crop_parameters/tree/1ca91d7dbb5aaf6b41462162de03a8254812d3a5).

Los **únicos datos observacionales de entrada** son las variables meteorológicas diarias de [NASA POWER](https://power.larc.nasa.gov/docs/services/api/temporal/daily/), sobre una **grilla**, no una estación meteorológica instalada en las parcelas. El archivo conserva las respuestas originales para evitar revisiones silenciosas de una API histórica. Los lugares evaluados son Trenque Lauquen (−35,97; −62,73) y Neuquén (−38,95; −68,06); las coordenadas son referencias geográficas de consulta de una celda meteorológica, **no** mediciones ni recomendaciones para un establecimiento real.

**El resultado central `TWSO` es masa seca de órganos de reserva modelada en kg/ha**, NO producción cosechada de papa fresca, NO el rendimiento comercial, y NO nutrientes por hectárea. La simulación idealizada **no representa estrés hídrico ni limitación de nitrógeno**, aunque POWER incluye lluvia histórica. No pueden inferirse sequías ni respuestas a fertilización con este modelo `Wofost81_PP`.

## Escenarios y supuestos explícitos

Cada lugar se simula en dos campañas (2022/23 y 2023/24) y dos fechas **supuestas de emergencia**, 1 de septiembre y 1 de octubre; se presume cosecha el 1 de marzo siguiente. Son ocho escenarios; no ocho ensayos agrícolas ni ocho variedades.

Se reutiliza el **mismo** conjunto genérico de coeficientes de `Potato_701` y **los mismos** supuestos de suelo `SMFCF=0,30`, `CRAIRC=0,06`, `SM0=0,45`, `SMW=0,10`, `RDMSOL=100 cm` y `CO2=410 ppm` para ambas grillas y campañas. Estos números no provienen de muestreos de suelo ni medidas de CO₂ en Argentina. El agua y los nutrientes no restringen el crecimiento. Los cambios entre celdas/fechas/campañas describen únicamente el comportamiento de **este modelo particular bajo estos supuestos**, no superioridad de variedades ni adaptación genética.

## Resultados reproducidos

| Grilla NASA | Campaña | Emergencia asumida | TWSO potencial seco (kg/ha) |
|---|---|---|---:|
| Trenque Lauquen | 2022/23 | 1 sep. | 14.156 |
| Trenque Lauquen | 2022/23 | 1 oct. | 12.154 |
| Trenque Lauquen | 2023/24 | 1 sep. | 15.835 |
| Trenque Lauquen | 2023/24 | 1 oct. | 15.044 |
| Neuquén | 2022/23 | 1 sep. | 15.689 |
| Neuquén | 2022/23 | 1 oct. | 14.215 |
| Neuquén | 2023/24 | 1 sep. | 18.198 |
| Neuquén | 2023/24 | 1 oct. | 16.340 |

Todos son **salidas numéricas de un modelo PP sin calibración** y solo ilustran sensibilidad al clima y a la fecha. No son estimaciones fiables de toneladas/ha de papas reales. No se ha validado la respuesta de `Potato_701` con datos de campo locales.

### Rastro de procedencia y modelo

- [`scripts/wofost_potato_nasa.py`](../scripts/wofost_potato_nasa.py): obtiene datos públicos solo cuando se pide explícitamente `--acquire`. Para modelar utiliza las dos respuestas JSON **locales** fijadas y **jamás consulta NASA en el paso de simulación**.
- [Fuentes NASA POWER originales](../datasets/wofost_potato_m1_16/weather/) con cobertura **2022-01-01 a 2024-04-01**, parámetros diarios `TOA_SW_DWN`, `ALLSKY_SFC_SW_DWN`, `T2M`, `T2M_MIN`, `T2M_MAX`, `T2MDEW`, `WS2M` y `PRECTOTCORR`.
- SHA-256 del JSON original Trenque Lauquen: `32b9404dadf8cf52a59e21a3c3094ea815d7d5485a995704b5b5bfcbd2b07e32`.
- SHA-256 del JSON original Neuquén: `8d0656de76652e14bef10fc1d79a9f19e73055052c889afb11f51959b5fb1d34`.
- [Manifiesto completo](../datasets/wofost_potato_m1_16/model/potential_model_provenance.json), [CSV de ocho escenarios](../datasets/wofost_potato_m1_16/model/generic_potato_potential_scenarios.csv), [CSV de 1.340 valores diarios de crecimiento](../datasets/wofost_potato_m1_16/model/generic_potato_potential_daily.csv) y [reporte automático](../datasets/wofost_potato_m1_16/model/potential_model_report.md). Ambas tablas de salida contienen su propio hash en el manifiesto.

El código valida cobertura diaria sin huecos, unidades y rangos físicos; comprueba que los JSON conservan exactamente sus bytes fijados y sus coordenadas de origen. No rellena lluvia ni temperatura faltantes. Los coeficientes de cultivo se leen de una revisión Git fija y el motor exige **PCSE 6.0.13**.

### Hallazgo de ingeniería: el proveedor NASA histórico tiene un límite interno

El proveedor estándar de PCSE intenta descargar la serie desde 1983 hasta hoy y falló al detectar al menos un día **histórico** con lluvia que excedía su rango permitido de 25 cm/día. **No** se truncó la precipitación ni se corrigió el dato: la integración de OpenPotato pasó a solicitar exclusivamente el período 2022–2024 realmente necesario para los escenarios, procesándolo mediante las conversiones originales de PCSE. La ventana publicada pasó sin datos fuera de rango. Si un valor excepcional real de la ventana excediera el contrato, el modelo **debe fallar y motivar revisión**, no alterarlo silenciosamente. Esto no permite afirmar que NASA POWER sea una medición pluviométrica de campo ni que el proveedor no pueda presentar otros límites.

## Reproducibilidad

Para recalcular sobre la **versión de clima ya almacenada**:

```bash
python -m pip install "pcse==6.0.13"
PYTHONPATH=.:src python -m scripts.wofost_potato_nasa \
  --weather-dir datasets/wofost_potato_m1_16/weather \
  --out /tmp/openpotato-modelo-potencial
```

La [Action M1-16](https://github.com/barbasmarcosi/OpenPotato/actions/runs/39546324609) ejecuta la suite completa offline (164 tests al completar el primer pipeline), corre WOFOST y publica solo en la rama de investigación. Los siguientes cambios utilizan el clima *commiteado* y verifican **reproducción exacta de los CSV mediante SHA-256**, sin volver a descargar clima. No se distribuyen datos privados ni archivos XRF restringidos.

## Qué falta para hacer predicciones útiles y verificables

1. **Estrés hídrico:** pasar a WOFOST 8.1 `Wofost81_WLP_CWB` únicamente con suelo, capacidad de retención de agua, profundidad efectiva, humedad inicial e irrigación razonablemente documentados. De otra forma solo sería un nuevo experimento de sensibilidad, no una predicción real de sequía.
2. **Calibración y validación local:** fechas observadas de emergencia/cosecha, cultivar real conocido, peso fresco/seco, materia seca y rendimiento medido por parcela, suelo, manejo y meteorología de campo. Separar campañas de ajuste y de evaluación externa.
3. **Nutrición:** Fe/Zn en tubérculos por muestra vinculada a parcela y procesamiento, biodisponibilidad y concentración en base seca/fresca; **WOFOST no calcula Fe/Zn** por sí mismo. La comparación genética y G×E nutricional continúa bloqueada hasta obtener los datos apropiados y con permisos.
4. **Seguridad:** glicoalcaloides con unidad, tejido, protocolo y umbrales aplicables; estos resultados no certifican inocuidad, productividad rentable ni nueva variedad.

**Decisión M1-16:** mantener abierto el laboratorio virtual y ampliar escenarios con métodos bien identificados, sin confundir biomasa potencial de órganos de reserva con rendimiento fresco medido o calidad nutricional humana.

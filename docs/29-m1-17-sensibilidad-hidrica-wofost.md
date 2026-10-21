# OP-M1-17 — Sensibilidad a disponibilidad de agua: WOFOST81_WLP_CWB

**21 de octubre de 2026. Estado: modelo físico ejecutado, resultados contrafácticos NO calibrados.** Este hito **no contiene** ensayos de campo, datos de suelo medidos, cultivares CIP específicos, Fe/Zn, seguridad alimentaria, recomendaciones de riego ni pronóstico de rendimiento comercial.

## Diferencia con M1-16

[M1-16](28-m1-16-modelo-climatico-wofost.md) usó \`Wofost81_PP\`: crecimiento **potencial** sin estrés de agua ni nitrógeno. M1-17 utiliza la variante publicada de PCSE \`Wofost81_WLP_CWB\` con **balance hídrico clásico**: la lluvia diaria NASA POWER puede entrar al perfil supuesto de suelo y la transpiración puede limitarse cuando el agua disponible es insuficiente. El nitrógeno continúa sin ser limitante. Un modelo de **agua limitada** no es un modelo de **nutrientes, fertilización o acumulación de hierro y zinc**.

Referencias de documentación técnica:
- [PCSE 6, modelos Wofost81_PP y Wofost81_WLP_CWB](https://pcse.readthedocs.io/en/stable/_modules/pcse/models.html).
- [PCSE balance hídrico clásico y parámetros, unidades y limitaciones](https://github.com/ajwdewit/pcse/blob/master/pcse/soil/classic_waterbalance.py).
- [NASA POWER Daily](https://power.larc.nasa.gov/docs/services/api/temporal/daily/).

## Inputs y procedencia

Se reutilizan los **mismos dos archivos JSON originales** de [NASA POWER archivados en M1-16](../datasets/wofost_potato_m1_16/weather/) con dos hashes SHA-256 inmutables, el mismo motor **PCSE 6.0.13** y la misma revisión de coeficientes publicada de papa genérica **Potato_701**, commit \`1ca91d7dbb5aaf6b41462162de03a8254812d3a5\`.

Se comparan los ocho escenarios previos de **dos puntos de grilla** (Trenque Lauquen y Neuquén), dos campañas (2022–2023 y 2023–2024) y dos **fechas supuestas de emergencia** (1 de septiembre y 1 de octubre). No hay estaciones ni parcelas medidas aquí. No se han generado archivos meteorológicos artificiales ni manipulado la lluvia NASA.

### Perfiles de suelo COMPLETAMENTE supuestos

Las unidades del motor PCSE para agua son **centímetros de lámina** y para humedad son **fracciones volumétricas m³/m³**.

| Parámetro | Perfil hipotético de baja retención | Perfil hipotético medio | Significado |
|---|---:|---:|---|
| \`SMW\` | 0,08 | 0,12 | Humedad en punto de marchitez |
| \`SMFCF\` | 0,20 | 0,32 | Humedad en capacidad de campo |
| \`SM0\` | 0,38 | 0,47 | Humedad de saturación |
| \`CRAIRC\` | 0,06 | 0,06 | Aire crítico para anegamiento |
| \`SOPE\` | 6 | 2 | Percolación máxima zona radicular (cm/día) |
| \`KSUB\` | 6 | 2 | Percolación máxima subsuelo (cm/día) |
| \`RDMSOL\` | 100 | 100 | Profundidad máxima enraizable (cm) |

Condiciones iniciales \`WAV\`: **2, 10 o 18 cm de agua disponible en todo el perfil** por encima de la referencia del punto de marchitez. El comportamiento de la humedad **dentro de la zona radicular al comienzo** se calcula internamente con \`SMLIM=SMFCF\` y las reglas de inicialización de PCSE; \`WAV=2\` **no** significa uniformemente 2 cm distribuidos en una zona radicular fija ni que cada perfil comience con el mismo porcentaje de capacidad de campo. En este estudio se los llama \`dry\`, \`intermediate\` y \`wet\` como **etiquetas comparativas del experimento**, no categorías de campo. CO₂=410 ppm supuesto; infiltración de lluvia sin fracción no infiltrada (\`NOTINF=0\`), almacenamiento superficial 0, **sin eventos de riego** y **nitrógeno ilimitado**.

El diseño es por tanto **8 campañas/fechas/grillas × 2 suelos inventados × 3 aguas iniciales inventadas = 48 corridas de sensibilidad**, no 48 ensayos, localidades o variedades.

## Qué medimos computacionalmente

- \`TWSO\` **kg/ha de biomasa seca modelada de órganos de reserva**, no rendimiento de tubérculos frescos ni kg comercializables; relación exploratoria \`WLP/PP\` contra el caso potencial M1-16 idéntico en grilla, campaña y fecha.
- Humedad volumétrica \`SM\` del volumen de suelo ocupado por raíces, crecimiento \`LAI\`, \`DVS\`, \`TRA\` transpiración real diaria (cm/día), \`RFTRA\` factor de estrés del modelo; si \`RFTRA<0,99\`, se contabiliza un **día modelado con limitación hídrica**.
- La precipitación acumulada se toma exclusivamente de \`PRECTOTCORR\` de los archivos JSON originales NASA POWER (**mm/día, dividido por 10 para expresarla en cm**), únicamente en las fechas modeladas. Nunca es un pluviómetro de campo.
- La transpiración real acumulada se obtiene **sumando los valores diarios \`TRA\` efectivamente exportados**. No se inventa un acumulado cuando la salida del balance hídrico no lo trae.

### Hallazgo exploratorio, sin recomendación productiva

La primera ejecución muestra que, **bajo estos supuestos de suelo y ausencia total de riego**, el modelo de agua limitada puede reducir considerablemente la biomasa seca frente al modelo PP. En escenarios extremos puede acercarse a cero, en particular en la grilla de Neuquén. Es una respuesta del **modelo bajo condiciones hipotéticas de secano** y **no** significa que un cultivo de papa real en Neuquén vaya a fracasar: el riego, el suelo, la fecha, el cultivar y la profundidad en fincas reales pueden ser radicalmente distintos.

La tabla completa de [48 resultados](../datasets/wofost_potato_m1_17/water_limited_report.md) está etiquetada sin confundirla con resultados observados. Comparar directamente una celda irrigada o no descrita de Neuquén con nuestro caso **sin riego** sería metodológicamente incorrecto.

## Ingeniería y replicación

- [Código M1-17](../scripts/wofost_water_sensitivity.py) lee **solo** datos meteorológicos archivados validados con hash y las ocho filas de biomasa potencial de M1-16. Rechaza conjuntos de escenarios alterados, perfiles físicos inconsistentes, atributos faltantes y versiones PCSE no fijadas.
- [Tests científicos](../tests/test_wofost_water_sensitivity.py) incluyen orden de humedades \`SMW < SMFCF < SM0\`, caudales hidráulicos, rangos de agua inicial, línea base con la versión exacta y fuentes NASA inalteradas.
- [Workflow M1-17](../.github/workflows/m1-17-water-limited.yml) ejecuta la suite general, luego las 48 corridas con \`Wofost81_WLP_CWB\`, verifica integridad y después publica **solo derivados etiquetados** en la rama de investigación. Compara SHA-256 de resultados en posteriores ejecuciones para detectar deriva.
- [CSV de sensibilidad](../datasets/wofost_potato_m1_17/water_limited_scenarios.csv), [serie diaria](../datasets/wofost_potato_m1_17/water_limited_daily.csv), [manifiesto](../datasets/wofost_potato_m1_17/water_limited_provenance.json), [reporte](../datasets/wofost_potato_m1_17/water_limited_report.md).

Para reproducir:

\`\`\`bash
python -m pip install "pcse==6.0.13"
PYTHONPATH=.:src python -m scripts.wofost_water_sensitivity \
  --weather-dir datasets/wofost_potato_m1_16/weather \
  --baseline datasets/wofost_potato_m1_16/model/generic_potato_potential_scenarios.csv \
  --out /tmp/openpotato-water-limited
\`\`\`

## Qué falta antes de dar recomendaciones agronómicas

Para interpretar resultados de finca hacen falta **perfiles medidos** de textura/retención, profundidad, humedad inicial, manejo e irrigación, datos de estación local, cultivar y fenología, producción fresca/seca real por parcela, y validación externa entre años. Solo entonces tendría sentido evaluar políticas de riego o diferencias de adaptación entre materiales.

Para medir nuestro objetivo final —**papas nutricionalmente mejoradas**— siguen faltando Fe/Zn por muestra real y trazable, bioaccesibilidad, materia seca y glicoalcaloides con protocolos/verificación. Ningún rendimiento virtual aumenta el número de muestras biológicas del CIP ni demuestra cambios nutricionales.

**Decisión:** M1-17 es una prueba de sensibilidad y un control de capacidad del laboratorio virtual. La agricultura real sigue siendo el criterio de validación; no se postulan clones mejorados ni consejos de riego.

# OP-M1-18 — Calendarios de riego con igual cantidad total de agua

**Fecha:** 21 de octubre de 2026. **Estatus:** WOFOST ejecutado y evaluado; los 144 resultados son **simulaciones exploratorias NO CALIBRADAS**, no rendimientos observados, no consejos de riego, no estudios de Fe/Zn ni adaptaciones de una nueva variedad.

## Propósito

Comparar *la distribución en el tiempo de una misma dosis bruta hipotética de riego*, sin confundir mayor frecuencia con mayor volumen de agua. Se mantiene constante **el mismo clima histórico NASA POWER, suelo supuesto, humedad inicial supuesta y coeficientes genéricos** de papa \`Potato_701\` dentro de cada comparación emparejada.

Continuamos de [M1-17](29-m1-17-sensibilidad-hidrica-wofost.md), que ya había modelado 48 casos sin riego con \`Wofost81_WLP_CWB\`. Ese modelo sí permite que la precipitación influya en el crecimiento mediante el balance hídrico clásico. El nuevo módulo añade eventos \`irrigate\` a la agenda del cultivo, usando los contratos publicados de PCSE: \`amount\` **en cm** y \`efficiency\` como fracción.

## Diseño exacto, predefinido y estrictamente contrafáctico

| Tratamiento | Eventos | Dosis bruta por evento | Total bruto programado | Total nominal tras eficiencia supuesta 0,80 |
|---|---:|---:|---:|---:|
| Control sin riego | 0 | 0 mm | 0 mm | 0 mm |
| Semanal | 10 | 10 mm | 100 mm | 80 mm |
| Quincenal | 5 | 20 mm | 100 mm | 80 mm |

El primer evento irrigado ocurre **14 días después de la emergencia hipotética**. El calendario semanal aplica el siguiente cada siete días hasta el día 77; el quincenal aplica cada catorce hasta el día 70. **No necesariamente coinciden las fechas finales de ambos calendarios**: ésa es parte de la intervención modelada y es imposible atribuir una diferencia únicamente a la frecuencia ignorando la distribución estacional. Ninguna de esas fechas es una recomendación para un lote.

La aplicación efectiva nominal (80 mm) resulta de multiplicar 100 × 0,80 en el evento. **No** afirma que 80 mm hayan ingresado efectivamente a la zona radicular de un campo: el modelo calcula a partir de sus supuestos la infiltración, almacenamiento, pérdidas y estrés, sin haber calibrado infraestructura o suelo. En particular, la relación de biomasa por mm bruto **no** es una medida observada de eficiencia de uso de agua o ahorro neto.

Cada combinación conserva:
- Dos puntos de grilla meteorológica NASA POWER: **Trenque Lauquen y Neuquén**.
- Dos campañas históricas: **2022/23 y 2023/24**.
- Dos emergencias inventadas: **1 de septiembre y 1 de octubre**.
- Dos perfiles de suelo hidráulico inventados: \`coarse_assumed\` / \`medium_assumed\`.
- Tres estados iniciales de agua disponible en el perfil: \`WAV=2, 10 y 18 cm\`, todos hipotéticos.

Son **48 combinaciones de base × tres calendarios = 144 corridas**, con **720 eventos** exclusivamente sintéticos y **24.120 salidas diarias**. Los parámetros publicados de cultivo (commit \`1ca91d7dbb5aaf6b41462162de03a8254812d3a5\`) y el modelo **PCSE 6.0.13, \`Wofost81_WLP_CWB\`** son comunes a los 144 casos. El nitrógeno se supone ilimitado; no se simula Fe/Zn, glicoalcaloides, producción fresca ni rentabilidad.

## Verificación de origen y equivalencia experimental

[El motor](../scripts/wofost_irrigation_timing.py) hace **de nuevo las 48 simulaciones sin riego** y compara cada biomasa seca contra las 48 filas de la tabla pública derivada [M1-17](../datasets/wofost_potato_m1_17/water_limited_scenarios.csv).

La diferencia máxima absoluta entre controles repetidos y originales fue **0,000004914 kg/ha**, explicada por el redondeo del CSV fijado a cinco decimales. La validación **rechaza** cualquier discrepancia mayor de \`0,0001 kg/ha\`. Además, cada repetición utiliza los **mismos bytes** de meteorología NASA POWER protegidos con SHA-256 y la identidad original suelo/campaña/muestra sintética.

Esto es evidencia de **reproducibilidad numérica del software**, no de que sus parámetros sean válidos para un lote real.

## Resultado exploratorio

Los resultados muestran una respuesta diversa a la distribución de la misma dosis bruta:

- **35/48** condiciones simuladas resultaron con biomasa seca mayor bajo la estrategia quincenal respecto de la semanal.
- **13/48** resultaron con biomasa seca mayor bajo la estrategia semanal.
- Ninguna de las dos estrategias produjo en estas 48 condiciones una biomasa seca modelada inferior a su correspondiente control sin riego.

Estos conteos **no son réplicas independientes, ni contrastes estadísticos entre técnicas reales de riego**: reutilizan los mismos lugares y años, y varían parámetros inventados del suelo. No se infiere significancia, superioridad agronómica ni certeza predictiva. Que el quincenal “gane” más veces bajo estos supuestos **no significa que sea mejor** en Argentina.

Ejemplo descriptivo que mantiene fijas grilla, campaña, fecha, suelo y agua inicial:

| Grilla y condiciones hipotéticas | Sin riego | Semanal 100 mm | Quincenal 100 mm |
|---|---:|---:|---:|
| Trenque Lauquen, octubre 2023, suelo medio, WAV=18 cm | 10.100 | 12.511 | 12.610 |
| Neuquén, octubre 2023, suelo medio, WAV=18 cm | 1.798 | 3.021 | 3.052 |

Cifras en **kg/ha de biomasa SECA modelada de órganos de reserva** (\`TWSO\`), no rendimiento de papa fresca ni biomasa realmente cosechada. La desviación fuerte entre grillas refleja **el clima diario y los supuestos de secano y suelos inventados**, no un ranking de localidades agrícolas.

## Archivos publicados y reproducibilidad

- [Simulador con eventos PCSE y balance hídrico](../scripts/wofost_irrigation_timing.py): incluye estado explícito de cada evento \`amount\` en **cm** y \`efficiency\` como supuesto; emite tres CSV con hashes de salida.
- [Pruebas de unidades y calendario](../tests/test_wofost_irrigation_timing.py): 100 mm totales en ambos tratamientos, conversión mm↔cm, eficiencia, señal \`irrigate\`, control sin eventos, eventos dentro de cultivo, procedencia 48 casos originales.
- [144 resultados emparejados](../datasets/wofost_potato_m1_18/irrigation_timing_scenarios.csv), [720 eventos con fecha](../datasets/wofost_potato_m1_18/irrigation_timing_events.csv), [24.120 filas diarias](../datasets/wofost_potato_m1_18/irrigation_timing_daily.csv), [reporte reproducible](../datasets/wofost_potato_m1_18/irrigation_timing_report.md) y [manifiesto con SHA-256](../datasets/wofost_potato_m1_18/irrigation_timing_provenance.json).
- [Action M1-18](https://github.com/barbasmarcosi/OpenPotato/actions/runs/39607807871): corre toda la suite (182 pruebas al cierre inicial), realiza las 144 simulaciones, verifica procedencia y **48 controles originales** antes de publicar. Las ejecuciones posteriores tienen guardia de reproducción por hash que bloquea cambios inesperados en entradas o salidas.

Para reproducir con el repositorio actual:

\`\`\`bash
python -m pip install "pcse==6.0.13"
PYTHONPATH=.:src python -m scripts.wofost_irrigation_timing \
  --weather-dir datasets/wofost_potato_m1_16/weather \
  --control-csv datasets/wofost_potato_m1_17/water_limited_scenarios.csv \
  --out /tmp/m1-18-irrigacion
\`\`\`

## Límites científicos y próximos pasos

Este experimento es un **laboratorio de comportamiento de software y sensibilidad agronómica**, no un diseño de irrigación listo para usar. La misma cantidad bruta no garantiza la misma fracción de agua retenida en raíces; la simulación no representa calibración de emisores, escorrentía real, evaporación de tubérculos, salinidad, variación microclimática, dinámica de nutrientes, enfermedades, genotipos CIP específicos ni incertidumbre de parámetros.

**Para comparar irrigación real** hacen falta textura, curva de retención, profundidad efectiva, humedad inicial medida, precipitación de estación de campo, riego registrado, sistema y uniformidad reales, calendario del cultivo, transpiración/evapotranspiración verificadas y rendimiento fresco/seco medido por parcelas con repeticiones independientes. Para el propósito nutricional OpenPotato aún necesitamos Fe/Zn genuinos por muestra y los controles de seguridad y biodisponibilidad establecidos en M1-14.

**Decisión M1-18:** es posible seguir probando estrategias como investigación computacional, pero cualquier propuesta de “mejor calendario”, “ahorro de agua” o variedad resistente a sequía **requiere primero calibración y validación externa**. M1-19 debería construir un protocolo de calibración con fuentes de campo públicas o pilotos legítimos antes de aumentar indiscriminadamente la complejidad del modelo.

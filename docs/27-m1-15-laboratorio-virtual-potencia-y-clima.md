# OP-M1-15 — Laboratorio virtual: potencia estadística y diseño de ensayos nutricionales

**Fecha:** 21-10-2026. **Estado:** simulador ejecutable de diseños de ensayo, CI pública y resultados claramente **SINTÉTICOS**. Esto **NO** modela mineralogía real de papa, ni pronostica Fe/Zn de accesiones CIP. No hay nuevos microdatos experimentales.

## Por qué simular antes de sembrar

En el [dataset del CIP Perú](https://doi.org/10.21223/N11QJS), el diseño de campo describe nueve ensayos y tres réplicas por sitio, pero **no** tenemos correspondencia verificable entre parcela, muestra de tubérculo y ensayo químico. No sería defendible reutilizar el "n" de los agregados como réplicas biológicas ni ajustar un G×E mineral.

Sí podemos plantear hipótesis explícitas sobre **cuántas unidades experimentales harían falta para distinguir dos genotipos**, e investigar cómo cambian las posibilidades de detectar una diferencia cuando la variabilidad genotipo×ambiente es alta. Esto tiene utilidad para decidir qué datos piloto solicitar o generar y no diseñar ensayos estadísticamente débiles.

## Implementación real

[Motor reproducible](../scripts/trial_design_monte_carlo.py) y [pruebas](../tests/test_trial_design_monte_carlo.py): solo biblioteca estándar Python, generador aleatorio con semilla fija, hipótesis de contraste emparejado entre **dos genotipos anónimos**, dos colas y error nominal del 5 %. Un dato inferencial es la **media del contraste de un SITIO independiente**; nunca se cuentan las lecturas XRF repetidas como sitios o parcelas adicionales.

En cada sitio virtual la diferencia observada entre genotipos se calcula de forma equivalente a un diseño en bloques biológicos emparejados:

\[
D_s = \delta + U_s +
\varepsilon_{\mathrm{parcela},s}+\varepsilon_{\mathrm{laboratorio},s}
\]

Donde \(\delta\) es una **diferencia verdadera supuesta** (no estimada), \(U_s\) es la desviación aleatoria específica de cada ambiente, la dispersión de parcelas se reduce con más bloques **biológicos**, y la del laboratorio puede reducirse con lecturas **técnicas**. Cada escenario se evalúa bajo \(\delta=0\) para contar falsos positivos y bajo \(\delta=1\) para estimar potencia de detección con **5000 repeticiones simuladas** por diseño y semilla 20261021.

El test t contrasta medias de sitios independientes (grados de libertad = número de sitios menos uno). Se usa esta prueba únicamente como ilustración predefinida de diseño. **Campañas repetidas en la misma localidad pueden estar correlacionadas y no deben contarse automáticamente como sitios independientes.** Tampoco constituye una modelización jerárquica completa con respuesta genotipo×sitio×año.

### Matriz de escenarios: todos hipotéticos

- **3, 6 o 9 sitios independientes**.
- **2 o 3 bloques biológicos** por sitio.
- **1 o 3 lecturas técnicas** por muestra.
- Desviación estándar del contraste genotipo×sitio **0,6 o 1,5**, medida en unidades de desviación estándar biológica de parcela; desviación de parcela = 1, ruido analítico = 0,35.
- Diferencia real supuesta entre genotipos = **1** desviación de parcela, **idéntica en promedio** para todos los sitios.

Son **18 diseños** (3 × 3 configuraciones de bloque/lectura × 2 condiciones ambientales), no 18 variedades ni 18 ensayos de campo. Los SD y efectos verdaderos son inventados para análisis de sensibilidad, **no** derivados de la Tabla 12 del CIP ni de Holetta.

## Resultado reproducible (únicamente conceptual)

En el escenario de variación entre sitios **alta** (SD = 1,5) y tres bloques biológicos con una lectura por muestra:

| Número de sitios supuestamente independientes | Potencia para detectar el efecto inventado | Falsos positivos (comprobación del 5 %) |
|---:|---:|---:|
| 3 | 9,4 % | ≈5 % |
| 6 | 22,4 % | ≈5 % |
| 9 | 34,5 % | ≈5 % |

En el escenario de variación entre sitios **más baja** (SD = 0,6), también con tres bloques y una lectura técnica, nueve sitios producen una potencia simulada del orden de **72 %**. **Las diferencias entre escenarios son sensibilidad matemática a los supuestos, no efectos medidos de una papa en otro clima.**

**Interpretación:** un programa que basa toda su inferencia en pocas localidades puede pasar por alto un efecto real cuando el contraste genotipo×ambiente varía ampliamente. Subir de una a tres mediciones del mismo material en laboratorio reduce ruido técnico, pero no equivale a sembrar tres veces más plantas ni crear ambientes nuevos. En estas configuraciones, ampliar el número de sitios independientes puede ser mucho más relevante para la detección.

No se pretende recomendar **9 localidades como número óptimo real**. El tamaño definitivo solo se puede calcular con variabilidad biológica, correlación espacial/temporal, precisión analítica, costo de muestreo y magnitud mínima clínicamente/agronómicamente relevante **calibrados o justificados por pilotos independientes**.

## Ejecutar y auditar

\`\`\`bash
PYTHONPATH=.:src python -m scripts.trial_design_monte_carlo \
  --out /tmp/openpotato-m1-15-simulacion \
  --draws 5000 \
  --seed 20261021
PYTHONPATH=.:src python -m unittest discover -s tests -v
\`\`\`

Los resultados se publican expresamente en el directorio [\`datasets/hypothetical_trial_design/\`](../datasets/hypothetical_trial_design/) y constan de:

- \`synthetic_trial_design_sensitivity.csv\`: 18 combinaciones de supuestos, tasa de rechazo y error Monte Carlo.
- \`synthetic_trial_design_provenance.json\`: seed, número de simulaciones, valores hipotéticos, checksum y límites.
- \`synthetic_trial_design_report.md\`: explicación legible de los resultados; siempre con etiqueta de simulación.

[Action M1-15](https://github.com/barbasmarcosi/OpenPotato/actions/runs/39544792808): se ejecutan todos los tests y se verifica que cada fila declara ser sintética y no incluye ID ni observaciones de ningún genotipo. La CI **no descarga** datos XRF restringidos ni abre archivos de participantes.

## Qué herramientas externas permiten llegar más lejos sin campo inmediato

La **segunda pista computacional** es un modelo de crecimiento de papa que use datos meteorológicos observados:

1. [**DSSAT SUBSTOR-Potato**](https://dssat.net/substor-potato/): simula agua, nitrógeno, biomasa, desarrollo y rendimiento de tubérculos. Requiere versión, parámetros, suelos y calibración apropiados; no modela automáticamente Fe/Zn o glicoalcaloides.
2. [**PCSE/WOFOST**](https://pcse.readthedocs.io/en/stable/) junto con [parámetros de papa publicados](https://github.com/ajwdewit/WOFOST_crop_parameters): alternativa abierta en Python. Antes de adoptarla verificar adaptabilidad al sitio, suelo y cultivar, licencia y validaciones; **no generar por cuenta propia coeficientes que pretendan representar clones CIP**.
3. [**NASA POWER**](https://power.larc.nasa.gov/docs/services/api/temporal/daily/): clima diario histórico de radiación, temperaturas, lluvia y otros parámetros. Una grilla meteorológica no reemplaza lluvia/suelo/manejo medidos en cada parcela.

Con modelado de rendimiento calibrado se podrían comparar **escenarios agronómicos** y riesgos climáticos; la nutriente concentración debería llegar **como parámetro explícitamente observado o de sensibilidad**, no como salida supuestamente validada de estos modelos. Para nutrición por hectárea es imprescindible combinar base seca/fresca y materia seca medida de modo compatible; para nutrición humana real, bioaccesibilidad, procesamiento y aceptabilidad.

**Decisión científica:** seguir con laboratorio virtual y modelos mecanísticos existentes **en paralelo con** el acceso legítimo a microdatos CIP y la planificación de un piloto. Aún **no** se requiere inventar variedades ni construir inmediatamente un invernadero. La futura fase de campo es necesaria para confirmar estabilidad, genética, inocuidad y valor nutricional real.

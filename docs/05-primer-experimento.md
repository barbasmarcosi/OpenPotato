# Experimento computacional OP-M1-001 — línea base de nutrición

**Estado:** preregistro de diseño, **no ejecutado**. **Fecha:** 2026-10-19.

## Pregunta precisa

En perfiles poblacionales bien definidos, ¿qué nutrientes cubre una papa convencional en diferentes cantidades y formas de preparación, y cuáles constituyen los cuellos de botella? ¿Cuánto cambiarían los resultados bajo escenarios explícitos y puramente hipotéticos de biofortificación?

Esta primera investigación es **computacional y observacional**. No produce papas modificadas ni permite concluir resultados clínicos.

## Fuentes mínimas que habrá que fijar antes de correr

1. USDA FoodData Central: ID(s) de alimento seleccionado, publicación, fecha, variedad si se conoce, preparación (cruda, hervida, con/sin cáscara), unidades y datos faltantes: https://fdc.nal.usda.gov/download-datasets/
2. Valores de referencia nutricional: institución emisora, edición, población y tipo de referencia (EAR/RDA/AI/UL); p. ej. https://ods.od.nih.gov/HealthInformation/nutrientrecommendations.aspx
3. Evidencia de pérdidas por procesamiento y biodisponibilidad solo cuando sea válida para el alimento, el nutriente y el escenario.
4. Estudios de biofortificación del registro con **resultados medidos** para caracterizar plausibilidad, **no** para fabricar datos de variedades combinadas.
5. Metadatos de rendimiento, agua y costos: quedan **fuera de M1** hasta que haya fuentes y unidades homologables; se incluyen en M2.

## Poblaciones y condiciones de ejemplo

Crear perfiles **no clínicos** separados, con requerimientos documentados por edad y circunstancia fisiológica (p. ej. persona adulta no gestante, mujer adulta no gestante, niño/a según guías correspondientes). No combinar valores de diferentes perfiles ni asumir 2.000 kcal como requerimiento universal.

Escenarios:
- Consumo de papa preparada: 200, 400, 800 g/día (exploración nutricional; **no** recomendación de ingesta).
- Escenario matemático de «energía aportada primordialmente por papa»: calcular cantidad necesaria según calorías por 100 g; etiquetar **no aconsejable como dieta**.
- Preparaciones: comparar solo si existen entradas confiables en la base para cocción y cáscara.
- Incertidumbre: definir al menos escenario conservador y favorable, sin asignar confianza numérica arbitraria a datos desconocidos.
- No comparar directamente bioavailability aparente contra una RDA ya ajustada por absorción.

## Variables mínimas

Energía (kcal), proteína total (g), perfil de aminoácidos si disponible, lípidos totales (g), ácidos grasos esenciales (g), fibra (g), potasio, calcio, hierro, zinc, folato, vitaminas A, B12, C, D y E; además sodio, otros micronutrientes con datos y posibles límites superiores de seguridad.

**Prohibido:** interpretar campos ausentes como ceros reales; interpretar analitos medidos como biodisponibles al 100 %; interpretar «proteínas totales» como cobertura completa de aminoácidos.

## Cálculos auditables

### Aporte dietario por nutriente

Para n, perfil p y preparación a:
- gramos de alimento = g
- concentración medida = c[n,a] por 100 g preparados
- aporte dietario = g × c[n,a] / 100
- referencia específica = R[n,p] con unidades compatibles
- cociente de referencia = aporte dietario / R[n,p], con etiquetas del tipo EAR/RDA/AI que impidan interpretaciones incorrectas

### Energía

Si c[kcal] > 0: gramos para energía escenario E = 100 × E / c[kcal]. Mostrar masa resultante y limitaciones de volumen, monotonicidad dietaria y nutrición, **sin** presentarlo como consejo de alimentación.

### Retención y absorción

- Si FoodData Central ya representa alimento cocinado, **no** aplicar otra vez una retención genérica.
- Si se usan factores externos, conservar población, método, matriz, incertidumbre y fuente; reportar cobertura dietaria y absorción **en métricas separadas** y solo con comparadores coherentes.
- Si faltan datos, marcar «desconocido» y comparar rangos únicamente cuando estén justificados.

### Mejora hipotética

Escenario S[n] = c[n] × m[n] o c[n] + delta[n], **nunca ambos sin especificación**. Multiplicadores de exploración (por ejemplo 1,25×, 1,5×, 2×) son **supuestos matemáticos sin afirmación de viabilidad biológica**. Reportar el origen de cada parámetro y marcar combinaciones no ensayadas.

## Salidas esperadas

- Matriz reproducible perfil × preparación × cantidad × nutriente, con unidades y fuente.
- Brechas separadas por **datos ausentes**, **aporte inferior a la referencia** y **excesos potenciales**.
- Gráficos de cobertura sin promedios engañosos; mostrar todos los nutrientes esenciales relevantes.
- Sensibilidad: cantidad, cocción, perfil poblacional y supuestos de retención.
- «Lista corta» de nutrientes prioritarios, ordenada por relevancia social, gravedad de déficit, evidencia de mejora y riesgos conocidos.
- Comparación transparente con alternativas dietarias en M2, **no** en la conclusión definitiva de M1.

## Control de calidad predefinido

1. Test de unidades: mg ≠ µg ≠ g; errores deben producir fallos visibles.
2. Test de escala: con concentración fija, duplicar g duplica aporte dietario.
3. Test de cocción: una entrada de papa cocida no recibe reducción adicional sin explicación.
4. Test de faltantes: falta de B12 reportada como ND no se sustituye sin evidencia por 0.
5. Test de perfiles: ningún requerimiento aparece sin fuente ni grupo.
6. Test de reproducibilidad: mismo dataset+config+versión produce la misma tabla.
7. Revisión manual de al menos tres nutrientes (hierro, provitamina A, lípidos) y un dato ausente.
8. Revisión por tercero antes de compartir conclusiones públicas.

## Criterio para cerrar M1

El código, fuente/versiones de datos, configuración, pruebas, reporte y limitaciones están disponibles y son reproducibles. Se pueden responder las preguntas para los **escenarios definidos**, **no** para «toda la humanidad». Si faltan datos críticos, se documenta y el hito puede cerrarse como estudio de factibilidad con pendientes.

## Fase posterior condicionada

M2 agregaría combinación de alimentos, costos, rendimientos por hectárea y métricas multiobjetivo; M3 bibliografía funcional sobre genes/rutas. Un laboratorio sólo entraría en fases autorizadas y con expertos.


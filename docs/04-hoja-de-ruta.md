# Hoja de ruta por hitos y puertas de calidad

**Plan original fechado 2026-10-19; estado operativo revisado 2026-10-22.** Los criterios iniciales y el alcance de fases M0–M6 se conservan abajo; el avance comprobado y los bloqueos actuales se registran en el anexo final. No se prometen fechas ni resultados biológicos.

| Fase | Objetivo | Entregables | Puerta de calidad |
|---|---|---|---|
| **M0 — Fundamentos** | Definir misión y límites | Visión, preguntas, bibliografía inicial, ética, protocolo computacional | Contradicciones y supuestos visibles; fuentes verificables; sin afirmaciones de descubrimientos propios |
| **M1 — Línea base nutricional** | Medir las carencias bajo escenarios definidos | Dataset con procedencia, notebook/scripts reproducibles, matriz de cobertura por nutriente, pruebas y reporte | Comparación independiente con cálculos manuales; datos faltantes explícitos; población y preparación identificadas |
| **M2 — Optimización comparativa** | Explorar mejoras hipotéticas vs. combinaciones de alimentos | Algoritmo multiobjetivo, escenarios de sensibilidad, frente Pareto, reporte de tradeoffs | Ninguna mejora hipotética presentada como real; restricciones de seguridad y disponibilidad |
| **M3 — Mapa biológico** | Priorizar rutas, genes y mecanismos existentes | Inventario de evidencia genética, vínculos a estudios funcionales, lista de riesgos y oportunidades | Anotaciones rastreables; sin inferir causalidad de expresión o estructura |
| **M4 — Revisión experta** | Someter hipótesis a nutricionistas y especialistas vegetales | Dossier, preguntas de validación, revisión independiente y riesgos | Revisión registrada con objeciones, sin exagerar certidumbre |
| **M5 — Programa experimental externo** | Diseñar validación, *solo si hay socios, instalaciones y autorizaciones* | Propuesta de protocolo de laboratorio/campo, resultados bajo custodia profesional | Permisos, regulación, ensayos de composición, rendimiento e inocuidad; publicación incluso de resultados negativos |
| **M6 — Transferencia social** | Evaluar posibilidad de impacto real | Estrategia de acceso y costos, plan de producción e independencia tecnológica | Evidencia en contextos reales, evaluación agroecológica y mecanismos de distribución ética |

## Próximos pasos priorizados

**P0 — Ahora**
1. Completar registro de evidencia con fuente primaria, año, método, comparador y limitaciones.
2. Elegir una papa de referencia en FoodData Central y un perfil poblacional de ejemplo no clínico.
3. Definir nutrientes, unidades, preparación y versión de requerimientos.
4. Redactar pruebas de consistencia para el modelo antes de ejecutar simulaciones.

**P1 — M1**
5. Importar datos sin dependencias propietarias y anotar vacíos.
6. Calcular cobertura por nutriente (no un puntaje que esconda deficiencias).
7. Comparar con una verificación manual y explorar sensibilidad por cocción y cantidad.
8. Publicar reporte reproducible con fuentes y advertencias.

**P2 — M2**
9. Añadir escenarios de biofortificación **hipotéticos** parametrizados y claramente rotulados.
10. Incorporar comparación con combinaciones de alimentos.
11. Evaluar área, costos, rendimientos, pérdidas y otros impactos cuando haya datos consistentes.

**P3 — M3 y M4**
12. Crear registro de características hereditarias con evidencia funcional y fenotipo medido.
13. Distinguir mecanismo bioquímico de prueba experimental de resultados en campo.
14. Preparar un dossier de revisión externa y consultar instituciones pertinentes.

## Riesgos de proyecto y mitigación

- **Datos incompletos / incompatibles:** conservar procedencia, unidades y desconocidos; rechazar comparaciones no homologables.
- **Falsa precisión:** bandas de sensibilidad, cautela en estadísticas y distinción entre hechos y supuestos.
- **Objetivo nutricional mal definido:** perfiles de población explícitos; revisión por especialistas en nutrición.
- **Intercambio por menor rendimiento o mayor toxicidad:** métricas agronómicas y controles de inocuidad obligatorios.
- **Dependencia de un solo cultivo:** referencia de dietas diversas y resiliencia varietal.
- **Licencias de datos/modelos restrictivas:** revisión antes de importaciones masivas o redistribución.
- **«Mucho plan, poca evidencia»:** hitos con entregables, criterios de aceptación y resultados verificables.

## Decisión de dirección

Se prioriza M1 frente a simulaciones moleculares: primero demostrar qué nutriente necesita mejorar, cuánto y en qué contexto; después investigar si existe mecanismo biológico viable. M1 puede demostrar que una vía genética no es la alternativa más adecuada, y eso también sería un resultado útil.



---

## Corte de avance verificado — 22 de octubre de 2026

**Regla:** el número de commits, documentos y subhitos M1-xx **NO** mide la proporción de avance científico. Un módulo que falla explícitamente por falta de evidencia es una entrega de *control de calidad*, no la consecución del objetivo agrícola/nutricional.

| Fase original | Estado operativo | Evidencia existente | Qué falta para cerrar |
|---|---|---|---|
| **M0 — Fundamentos** | **Sustancialmente implementada** | Visión, preguntas, límites, ética, arquitectura, plan y fuentes bibliográficas versionadas | Revisión formal de consistencia y decisiones por expertos cuando haya colaboración; no afirmar validación externa |
| **M1 — Línea base nutricional** | **Implementación relevante, cierre científico pendiente** | Dos preparaciones **originales USDA** FDC 170438 y 170440, extracción fijada por SHA y CI; escenarios por ración/perfil, cálculos y controles manuales; fuentes CIP y revisiones secundarias con cautela | Matriz suficientemente completa de nutrientes esenciales, referencias/perfiles independientes, incertidumbre por preparación/variedad, biodisponibilidad separada y revisión crítica externa; informar ausencia de datos cuando no se disponga |
| **M2 — Optimización comparativa** | **No ejecutada como fase integral** | Pruebas preliminares de fronteras Pareto/casos de estudio y escenarios hipotéticos en M1, sin comparar alimentos alternativos a iguales restricciones | Implementar optimización multiobjetivo nutrición/costo/agua/superficie con referencias alimentarias alternativas, seguridad, sensibilidad y comparación justa |
| **M3 — Mapa biológico** | **Exploración de fuentes, no mapa mecanístico completo** | Literatura genética y clones de CIP, Holetta y Perú; documentación y accesiones coincidentes | Vincular rutas de nutrientes, genes, evidencia funcional, fenotipos y riesgos con fuentes independientes y causalidad claramente separada |
| **M4 — Revisión experta** | **No iniciada formalmente** | Dossier y preguntas preparatorios; [issue #8](https://github.com/barbasmarcosi/OpenPotato/issues/8) sobre datos originales (NO contacto experto) | Colaboración efectiva de nutrición, agronomía, genética y seguridad; objeciones y decisiones registradas |
| **M5 — Programa experimental externo** | **No iniciado** | Propuestas y contratos de datos de muestra/parcela, sin mediciones experimentales propias | Socios, permisos, laboratorio, protocolos, Fe/Zn por muestra y parcela, estabilidad/rendimiento, control de glicoalcaloides e inocuidad |
| **M6 — Transferencia social** | **No iniciada** | Principios de accesibilidad y costo definidos | Prueba de impacto nutricional/agronómico/económico, producción y distribución en contextos reales |

### Dos pistas de trabajo, para evitar deriva de alcance

**Pista N — nutrición y viabilidad de biofortificación** (corresponde a M1→M2→M3). Prioridad crítica para la pregunta madre. La línea base USDA es reproducible, pero *no demuestra* que los materiales con más Fe/Zn mejoren absorción o salud, ni que sean variedades producidas por OpenPotato. Los resultados CIP disponibles se hallan agregados y sin vínculo parcela–muestra Fe/Zn verificable. Las mediciones originales XRF de más detalle todavía requieren acceso legítimo. El cierre M1-N no depende de ejecutar WOFOST: depende del contrato nutricional original, de una evaluación de vacíos y de revisión externa.

**Pista A — productividad y respuesta ambiental** (M1-16→M1-35, investigación complementaria que alimentará M2/M5). Se desarrollaron 144 corridas reales del motor WOFOST bajo **supuestos sintéticos** de agua, suelo/cultivar y clima NASA, más un benchmark **empírico independiente** 2019→2020 de los ensayos originales WUR. **No hay** validación predictiva de WOFOST contra parcelas holandesas. Weatherfile fue importado íntegramente en PCSE (1.096 días por estación); parcelas y tratamientos W1/W2 fueron cruzados. La lluvia entre fuentes mantiene factor diez verificado día por día, pero **unidad física W1/W2 y semántica de celdas vacías están sin resolver**. M1-33 confirmó 746 días de ventanas de estudio, 526 filas fuente, 220 días sin registro y UNKNOWN: W1 565 / W2 496. [M1-34](46-m1-34-irrigation-evidence-gate.md) impide inferir cero o unidades.

La línea A **no debe consumir presupuestos/iteraciones indefinidamente sin volver al objetivo nutricional**; revisar su prioridad después de comprobar suelo/fenología original y el alcance científico real del modelo.

### Próximas puertas objetivas, ordenadas por valor

1. **N1 — Cierre evaluable de M1 nutricional:** ejecutar batería USDA oficial de dos preparaciones, construir matriz de nutrientes indispensables completos/incompletos, identificar referencias poblacionales y revisión independiente de la interpretación. Cerrar como *línea base/factibilidad condicionada* si faltan nutrientes; nunca como resultado clínico.
2. **A1 — M1-35 suelo e hidrología original:** auditar Waterpotential.xlsx y Groundwaterlevel.xlsx (ambos de Harvard Dataverse v3), verificar formato, fechas, licencias y unidades/profundidades. Identificar disponibilidad, **no** fabricar curvas de retención ni parámetros WOFOST.
3. **A2 — Recuperar evidencia sobre W1/W2:** [issue #8](https://github.com/barbasmarcosi/OpenPotato/issues/8). Resolver unidad por tratamiento, significado de blanco y de día sin fila, eficiencia/superficie de aplicación; no sustituir autores por correlaciones.
4. **A3 — Parametrización y pruebas independientes:** sólo con datos reales de suelo, cultivar, emergencia, N, riego y condiciones iniciales verificadas se podrá correr y calibrar 2019; reservar biomasa observada de 2020 como evaluación genuina. No ajustar hiperparámetros basándose en errores de 2020.
5. **M2 y M3 tras estabilizar M1-N:** optimización de dietas/comparadores y priorización de mecanismos funcionales. Una papas más productiva pero de mejora nutricional no demostrada **no** cierra las preguntas nutricionales del proyecto.

### Semáforo científico, no de ingeniería

- **Verde (reproducible):** USDA oficial para dos preparaciones, ingesta y QA, código, algunas comparaciones descriptivas; meteorología WUR original legible PCSE y estructura temporal/agronómica source-pinned.
- **Amarillo (exploratorio/condicional):** rangos Fe/Zn publicados a nivel agregado, potenciales genotipos y escenarios WOFOST parametrizados de forma hipotética; no atribuir efectos a parcelas/genotipos individuales por cruce indirecto.
- **Rojo (NO demostrado):** aumento propio de Fe/Zn bioavailable, seguridad y glicoalcaloides de nuevas variedades, ensayo propio aprobado, validación WOFOST de campo, parametrización hidrológica de suelo, riego W1/W2 en mm con blancos resueltos, impacto real en costo/salud.

La etapa M1 se puede cerrar documentalmente como **estudio de factibilidad bien delimitado** solo tras comprobar sus criterios originales y dejar pendientes explícitos. Esto no significa completar M2–M6, ni producir una nueva papa nutritiva.

## Prioridad nutricional ejecutada — OP-N1-01 (22 de octubre de 2026)

Tras M1-35 se vuelve al problema central: **nutriente que realmente alcanza al organismo**, no únicamente concentración en el tubérculo. Este hito no incrementa artificialmente el porcentaje de M1 cerrado, pero convierte la pregunta madre en una hipótesis con medidas verificables.

**Resultado verificable:** las publicaciones primarias de dos ensayos de 2023 muestran Fe absorbido 0,35 vs 0,24 mg por 460 g (n=28 mujeres), y Zn absorbido 0,49 vs 0,40 mg por 500 g (n=37 mujeres). En ambos ensayos desciende la fracción absorbida, aunque aumente la masa total absorbida. Es evidencia EXTERNA, no ensayo de OpenPotato, y no demuestra los dos beneficios en un mismo genotipo.

**Entregables implementados:** [registro cuantitativo de evidencia](../datasets/evidence/human_potato_fe_zn_absorption_2023.json), [motor reproducible](../src/openpotato/absorption_opportunity.py), [criterios científicos](48-n1-01-hipotesis-fe-zn-absorbidos.md), pruebas de coherencia y separación de ensayos y [GitHub Actions](../.github/workflows/m1-tests.yml). El USDA oficial histórico FDC 170438/170440 se presenta por separado como nutrientes dietarios por peso cocido, no como mg absorbidos en un experimento peruano. [CI verificada](https://github.com/barbasmarcosi/OpenPotato/actions/runs/39879262443), sin datos clínicos individuales ni material vegetal nuevo.

**Siguiente puerta N1-02** ([issue #9](https://github.com/barbasmarcosi/OpenPotato/issues/9)): revisión bibliográfica con búsqueda y criterios explícitos para identificar, o descartar provisionalmente, ensayos de **hierro y zinc absorbidos en una misma variedad/clon genéticamente caracterizado**, con procesamiento/comparador armonizados, y analizar fitatos/ascorbato, rendimiento, glicoalcaloides y asequibilidad. La novedad de ese enfoque todavía NO ha sido demostrada.

**Regla de decisión:** si una revisión revela que otro centro ya resolvió el mismo problema con evidencia sólida, reproducir/colaborar o pivotar hacia una incertidumbre específica; no reclamar ser pioneros. Una mejora de contenido mineral, un rendimiento hipotético de WOFOST o un perfil USDA no se puede sustituir por una medición isotópica de absorción humana.

# Hoja de ruta por hitos y puertas de calidad

**Estado al 2026-10-19:** documentación inicial. Los hitos son **planes**, no entregas terminadas. No se prometen fechas ni resultados biológicos.

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


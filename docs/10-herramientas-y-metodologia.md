# Evaluación técnica y selección de herramientas (OP-ADR-010)

**Fecha:** 2026-10-20 · **Estado:** decisión inicial parcialmente aceptada, con criterios de reevaluación. **No hay pipeline ejecutado ni genes candidatos validados a la fecha de esta evaluación.**

## 0. Conclusión ejecutiva

**No fijar una pila biotecnológica monolítica antes de tener preguntas bioquímicas concretas.** Sí fijar desde ahora el proceso de investigación, las herramientas para bibliografía, nutrición, cálculo, QA y proveniencia. Genómica, simulación metabólica y predicción estructural serán **módulos condicionales** disparados por evidencia, no por entusiasmo tecnológico.

### Reglas de elección

Preferir herramientas con: datos relevantes para papa; respaldo científico; trazabilidad hasta fuente; reproducibilidad; licencias compatibles; funcionamiento sin dependencia exclusiva de pagos; mantenimiento activo; costo/beneficio real. Una técnica avanzada sin datos adecuados se **rechaza** por el momento. Comparar contra métodos clásicos y baselines sencillos.

## 1. Inventario de recursos y selección

| Problema | Preferido ahora | Alternativas/complementos | Cuándo usar | Decisión |
|---|---|---|---|---|
| Descubrir artículos y registrar evidencia | **Europe PMC REST** + PubMed/NCBI; DOI con Crossref | Zotero manual, literatura CIP/FAO | M0-M4, solo metadatos/textos legalmente accesibles | **Adoptar** |
| Composición nutricional | **USDA FoodData Central** Foundation, FNDDS o SR Legacy según alimento y cobertura | **FAO/INFOODS**, Argentina **SARA 2/ArgenFoods**, otras tablas regionales | M1; comparar calidad, versiones, preparación y regiones | **Adoptar, selección de registros pendiente** |
| Requerimientos humanos | **NIH ODS / DRI** y fuentes nacionales/WHO-FAO apropiadas | EFSA, otras instituciones reconocidas | M1; por edad, fisiología y contexto | **Adoptar metodología, estándares exactos por seleccionar** |
| Datos de investigaciones con papas | Estudios primarios y tablas suplementarias | CIP / programas públicos de mejoramiento y germoplasma | M0-M4 | **Adoptar con licencia/verificación** |
| Genomas y expresión en papa | **SpudDB** (genomas y RNA-seq específicos) | NCBI GEO/SRA, UniProt, otras anotaciones | M3 para hipótesis genética respaldada | **Reservar** |
| Rutas metabólicas | **PotatoCyc** en Plant Metabolic Network | PlantCyc, MetaCyc, KEGG si licencia y datos permiten | M3 para investigar acumulación/metabolismo de nutrientes | **Reservar** |
| Estructuras ya predichas | **AlphaFold Protein Structure Database (EMBL-EBI)** | PDB experimental; AlphaFold 2, herramientas locales si hacen falta | Solo ante proteínas identificadas y preguntas estructurales | **Preferir consulta a generación** |
| Predicciones nuevas de estructura/complejos | **Evaluar caso por caso** | AlphaFold 2 / AlphaFold 3 Server (restricciones), alternativas verificadas | Solo si las estructuras existentes no responden la pregunta | **No adoptar como base** |
| Modelo nutricional reproducible | **Python + NumPy + pandas + SciPy**; validación de unidades, esquemas y pruebas | polars, DuckDB y Parquet si el volumen lo requiere | M1 | **Adoptar** |
| Restricciones y optimización | **SciPy linprog/milp** para modelos lineales; **pymoo** para Pareto/no lineales si necesario | CVXPY/HiGHS, otros algoritmos con justificación | M2 tras definir problema verificable | **Adoptar condicionalmente** |
| Simular flujos metabólicos | **COBRApy** SOLO con modelo estequiométrico de papa/tubérculo verificado | Análisis de rutas dirigido y estudios empíricos | M3 si existe modelo apropiado y datos para restringirlo | **Condicional; no construir de cero por defecto** |
| IA para síntesis y recuperación | LLM con **RAG de fuentes verificables** y control de afirmaciones | revisión humana y extracción bibliográfica estructurada | Desde M0; cada afirmación ligada a cita primaria y contexto | **Adoptar con supervisión y auditoría** |
| Infraestructura y QA | GitHub repositorio, Python, pytest, dependencias fijadas, entornos locales, CI ligera | DuckDB, contenedores, DVC si crecen los datos | M1 | **Adoptar minimalista** |

Fuentes de herramientas y licencia al final del documento. No se ha verificado la precisión o actualidad de cada **dato biológico individual** simplemente por seleccionar un portal.

## 2. Por qué cambiar respecto al plan inicial

### 2.1 El foco es el fenotipo, no los genes por sí solos

Una papa con mejores nutrientes requiere considerar **concentración real en tubérculo, retención en cocción, biodisponibilidad, rendimiento, seguridad, estabilidad entre ambientes y costo**. Mutar un gen o hallar una estructura plausible no prueba ninguno de esos objetivos de forma automática.

Los minerales **no se sintetizan** en las células: el hierro y zinc deben estar disponibles y ser absorbidos/distribuidos por la planta. Sus concentraciones dependen de suelo y ambiente; no existe un aumento genético independiente de la disponibilidad mineral.

### 2.2 La papa cultivada puede ser tetraploide

No basta transferir anotaciones desde un genoma de referencia simplificado. Se deben distinguir cultivar y ploidía, variantes alélicas, dosis, ambiente, expresión en tejido y controles adecuados. SpudDB incluye referencia y múltiples genomas, pero una correlación genómica no es causalidad.

### 2.3 PotatoCyc antes que reconstruir metabolismo a mano

PotatoCyc 7.0.0 (2022) documenta 527 rutas, 3.211 reacciones y 2.534 compuestos. Sus anotaciones enzimáticas son **principalmente predicciones computacionales**. Utilizarlo para generar **hipótesis contrastables**, no para afirmar que conocemos el flujo metabólico real. Una red de rutas no es por sí misma un modelo validado de balance de flujos.

### 2.4 Preferir estructuras existentes a entrenamiento o inferencia cara

AlphaFold DB contiene estructuras precomputadas bajo **CC BY 4.0** según EMBL-EBI. AlphaFold 3 Server **no** tiene iguales derechos: uso no comercial y restricciones específicas (incluyendo uso de outputs en docking/screening). **No mezclar** las licencias. Primero comprobar si existe una estructura experimental PDB o una predicción AlphaFold DB suficientemente apropiada.

### 2.5 El mejor algoritmo no es siempre el más complejo

M1 requiere aritmética nutricional con trazabilidad, no redes neuronales. M2 debe iniciar con restricciones y optimizadores verificables; usar algoritmos evolutivos solo para no linealidad o múltiples objetivos reales. No crear modelos predictivos de rendimiento sin datos multientorno adecuados. **Un ranking de LLM no sustituye validación.**

## 3. Diseño de investigación: método antes que tecnología

### Fase A — pregunta y conocimiento existente

1. Formular pregunta estrecha y preregistrar variables primarias, comparadores y posibles refutaciones.
2. Buscar sistemáticamente por concepto, cultivar, estudio y tipo de evidencia (Europe PMC, PubMed, bibliografía hacia atrás y adelante).
3. Deduplicar y registrar cribado de fuentes con criterios explícitos; no llamar «revisión sistemática» a una selección narrativa.
4. Extraer composición, comparación, intervalo/confianza, población, ambiente, forma de preparación y limitación.
5. Verificar DOI y leer materiales primarios cuando existan; etiquetar **abstract_only / full_text_reviewed** para no confundir niveles de lectura.

### Fase B — mapa nutricional

6. Seleccionar ID(s) de alimento y nutriente, base fresca/seca, preparación y población específica.
7. Validar unidades y datos faltantes (ND ≠ cero). Mantener **aporte dietario**, **retención** y **absorción** como conceptos distintos y evitar aplicar dos veces ajustes de biodisponibilidad.
8. Comparar cada nutriente contra el tipo de referencia correcto; mostrar cantidades, incertidumbre y riesgos, no un promedio que oculte déficits.
9. Revisar al menos tres casos manualmente y automatizar controles de regresión.
10. Producir un informe reproducible y descartar objetivos mal respaldados.

### Fase C — escenarios y alternativas

11. Definir escenarios matemáticos hipotéticos sin atribuirles viabilidad genética.
12. Comparar mejoras con variedad convencional y **alternativas de alimentos complementarios**.
13. Solo incluir costos, agua y productividad cuando existan mediciones comparables; no inventar parámetros.
14. Reportar frontera de soluciones no dominadas y análisis de sensibilidad; preferir optimización lineal exacta cuando aplica.
15. Priorizar oportunidades usando **beneficio estimado**, **plausibilidad biológica**, **riesgo**, **incertidumbre** y **impacto social**, cada criterio separado.

### Fase D — genética y bioquímica por hipótesis

16. Consultar literatura funcional previa para el rasgo; examinar **mejoramiento convencional, selección genómica, manejo agronómico y fortificación** antes de elegir edición genética.
17. Mapear ruta metabólica, genes, evidencia funcional, tejido, genotipo/ploidía y ambiente.
18. Usar SpudDB/GEO para corroborar anotaciones y expresión; controlar referencia y variantes.
19. **Solo si existe un cuello de botella concreto:** modelar estructuras, complejos o red metabólica. Revisar permisos, datos y validez.
20. Diseñar comparaciones e información necesaria para laboratorio, incluida seguridad (glicoalcaloides) y estabilidad agronómica.

### Fase E — revisión y experimentación externa

21. Someter hipótesis y riesgos a especialistas independientes.
22. Definir protocolo experimental con controles, repetición, tamaño muestral y ensayos nutricionales/agronómicos apropiados.
23. Realizar trabajo experimental **solo** con instalaciones y profesionales competentes, permisos y marco regulatorio.
24. Analizar resultados negativos; revisar o abandonar hipótesis cuando fallen.

## 4. Herramientas específicas de ingeniería (adopción gradual)

**M1 núcleo:** Python, pandas, NumPy, SciPy, pytest, control estricto de unidades (p. ej. Pint) y validación de esquema (p. ej. Pydantic/Pandera si aportan valor). Una CLI que ejecute el modelo y exporte CSV/JSON con procedencia; Jupyter solo como interfaz exploratoria, no como única ejecución oficial. Versionado y checksums SHA-256 de entradas. Dependencias fijadas.

**Datos:** preferir inicialmente archivos de pocos MB versionados y acompañados por manifest; cuando haya datasets grandes usar Parquet/DuckDB y enlaces a descargas reproducibles, no añadir una base de datos servidor sin necesidad. Respetar las licencias de redistribución.

**M2:** iniciar con `scipy.optimize.linprog` / `milp` (HiGHS), registrar restricciones y tolerancias; evaluar `pymoo` NSGA-II para fronteras de Pareto si hay objetivos no reducibles a LP/MILP. Comparar contra enumeración exhaustiva en ejemplos pequeños. Registros de sensibilidad y semilla para algoritmos estocásticos.

**M3:** priorizar metadatos, secuencias, anotación e informes de investigación. Cobrapy no se activa solo porque exista PotatoCyc: necesita modelo de flujos químicamente consistente, compartimentalización y restricciones de tejido y ambiente, idealmente contrastadas con datos.

**Mantenimiento:** CI liviana por pull request cuando haya código, lint/tests de bajo costo, README de cada experimento, scripts con modo offline si hay snapshots de datasets, reportes con Git SHA y versión de datos. Evitar despliegue web antes de obtener un primer informe científico.

## 5. Qué se decide ahora y qué queda abierto

### Decisiones aprobadas para comenzar

- Diseño basado en evidencia primaria, preregistro de preguntas y falsabilidad.
- FoodData Central más fuentes regionales para comparar nutrición; Europe PMC/PubMed para bibliografía.
- Python numérico y tests para M1, con formatos trazables.
- SciPy como primera opción de optimización, sin ML innecesario.
- Evaluar rasgos por contexto de población, variedad y ambiente.
- Abrir espacio para comparadores no genéticos desde el inicio.

### Herramientas reservadas a verificación ulterior

- Identificadores precisos de comidas, composición y guías nutricionales.
- SpudDB, PotatoCyc, UniProt/GEO: aplicarlos en M3 con un problema y cultivar delimitado.
- AlphaFold DB/PDB: solo para pregunta molecular específica.
- AlphaFold 2/3, COBRApy, deep learning, docking, modelos de genotipo→fenotipo: **ninguno justificado aún por el dato disponible**.
- Docker, cloud GPU, app web, workflows CI pesados: reservar si una necesidad concreta los justifica.
- Licencias de paquetes, datasets y outputs: verificar individualmente antes de distribuir.

## 6. Condiciones de avance y revisión

Se autoriza el comienzo de M1 **sin afirmar que todo el stack de M3 está decidido**. El compromiso es reemplazar/adaptar herramientas cuando evidencias o licencias lo exijan. Para iniciar M2 se exige M1 auditado; para activar herramientas genéticas, al menos un nutriente-objetivo y una hipótesis biológica priorizada; para contratar cómputo, estimación de costo y mejora esperada sobre una solución local.

**Riesgos de falsa promesa:** mejorar múltiples rasgos simultáneamente tiene interacciones; no confundir contenido de minerales con absorción ni señales de RNA-seq con causalidad. El resultado puede ser que otra intervención sea mejor que un nuevo cultivar.

## 7. Fuentes verificadas para selección de herramientas (octubre de 2026)

- [USDA FoodData Central — tipologías](https://fdc.nal.usda.gov/data-documentation/) y [descargas](https://fdc.nal.usda.gov/download-datasets/).
- [FAO/INFOODS — tablas de composición, incluye Argentina SARA 2 (2022)](https://www.fao.org/food-composition/tables-and-databases/).
- [NIH ODS — recomendaciones](https://ods.od.nih.gov/HealthInformation/nutrientrecommendations.aspx).
- [Europe PMC — API de literatura](https://europepmc.org/developers).
- [SpudDB — Genetics 2025](https://academic.oup.com/genetics/article/229/3/iyae205/7919234).
- [PotatoCyc 7.0.0 — contenido y nivel de anotación](https://plantcyc.org/database_imported/potatocyc-7-0-0/).
- [NCBI GEO](https://www.ncbi.nlm.nih.gov/geo/).
- [AlphaFold DB — licencia CC BY 4.0](https://alphafold.ebi.ac.uk/faq).
- [AlphaFold Server — límites de uso](https://alphafoldserver.com/).
- [EMBL-EBI: AF2 vs AF3](https://www.ebi.ac.uk/training/online/courses/alphafold/alphafold-3-and-alphafold-server/introducing-alphafold-3/should-i-use-alphafold-2-or-alphafold-3/).
- [SciPy linprog/milp](https://docs.scipy.org/doc/scipy/reference/optimize.html).
- [pymoo NSGA-II](https://pymoo.org/algorithms/moo/nsga2.html).
- [COBRApy](https://opencobra.github.io/cobrapy/releases/).

**Nota de evidencia:** se han verificado fuentes de herramientas y restricciones generales; aún no se ha construido ni comparado experimentalmente un pipeline de M1/M3 ni evaluado alternativas con benchmarks propios.

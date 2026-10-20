# Arquitectura de investigación y plataforma reproducible

Este documento **propone** la arquitectura; no implica que los módulos estén implementados.

## 1. Capas de trabajo

1. **Fuentes primarias:** papers, DOI, bases públicas, guías nutricionales, datos de cultivar y ensayo. Guardar URL, fecha de consulta, licencia y método.
2. **Ingesta y control de calidad:** importar formatos autorizados, controlar unidades, base cruda/cocida y fresca/seca, detectar duplicados, valores faltantes y cambios de versión.
3. **Modelo nutricional:** estimar el aporte por porción y perfil de consumo; representar digestibilidad, retención y absorción cuando haya datos.
4. **Comparador y optimización:** simular escenarios de mejoramiento expresamente etiquetados como hipotéticos; restricciones de tierra, agua, energía, costo y límites por nutriente.
5. **Capa biológica exploratoria:** anotaciones genómicas, rutas metabólicas y evidencia funcional; consultas a SpudDB y fuentes de bioinformática.
6. **Resultados:** reportes reproducibles con tablas, procedencia, análisis de sensibilidad e hipótesis pendientes.
7. **Validación externa:** revisión de nutrición, genética, agronomía y bioseguridad antes de estudios con plantas o humanos.

## 2. Fuentes candidatas

- [USDA FoodData Central — descargas](https://fdc.nal.usda.gov/download-datasets/): composición alimentaria con versiones y tipos de base definidos.
- [NIH ODS](https://ods.od.nih.gov/HealthInformation/nutrientrecommendations.aspx) y fuentes nacionales apropiadas: requerimientos por perfiles; guardar edición y población.
- [SpudDB](https://spuddb.uga.edu/): genomas, anotación y expresión de genes de papa.
- [Plant Metabolic Network / PlantCyc](https://plantcyc.org/): redes y reacciones bioquímicas, sujetas a verificación de cobertura y licencia.
- Publicaciones primarias del [registro bibliográfico](07-fuentes-y-trazabilidad.md).

**Restricción:** no descargar ni redistribuir bases sin revisar licencias y términos; tampoco utilizar resultados de AlphaFold Server para usos prohibidos por su licencia, incluidos determinados sistemas automatizados de docking/screening.

## 3. Modelo mínimo de datos (propuesta)

### Tabla food_composition
food_id, species, cultivar, tissue, processing, source_id, source_version, observation_year, sample_n, nutrient_id, value, unit, basis (per_100g_fresh/per_100g_dry), uncertainty, missing_reason.

### Tabla requirement
profile_id, population_source, age_range, physiological_context, nutrient_id, target_type (EAR/RDA/AI/UL), value, unit, effective_date, source_id.

### Tabla trait_evidence
claim_id, trait, cultivar, intervention_class, phenotype_measured, comparator, study_type, sample_n, conditions, effect, unit, quality_limitations, source_id.

### Tabla scenario
scenario_id, baseline_food_id, modified_trait, multiplier_or_absolute_value, evidence_status, measurement_or_assumption, uncertainty_bounds, seed, created_version.

## 4. Motor de cobertura nutricional

Definiciones:
- m = gramos de papa preparada consumidos por día.
- c[n] = cantidad del nutriente n por 100 g en la preparación elegida.
- r[n] = referencia diaria **para un perfil y una clase de requerimiento determinados**.
- f[n] = factor de retención/biodisponibilidad cuando hay datos; de lo contrario **desconocido**, no automáticamente 1.

Aporte disponible estimado[n] = m × c[n] / 100 × f[n].
Cobertura[n] = aporte disponible estimado[n] / r[n], cuando denominador, unidades, tipo de requerimiento y factor sean compatibles.

**Importante:** muchos valores de requerimiento ya incorporan supuestos de absorción y no corresponde aplicar factores dos veces. Inicialmente reportar «aporte dietario / referencia» y «absorción estimada» por separado. No reemplazar umbrales clínicos por RDA sin justificación.

Un índice agregado puede ocultar carencias graves. Mostrar primero un **vector por nutriente**, y luego un mínimo/percentiles o restricciones por componente; no usar únicamente la media de cobertura.

## 5. Comparación multiobjetivo (propuesta)

Maximizar adecuación nutricional y energía útil sujeto a umbrales de seguridad y restricciones de costo, superficie, agua, variedad y capacidad de cultivo. Reportar frontera de Pareto y sensibilidad a pesos/escenarios; nunca afirmar un «óptimo global» cuando los datos son parciales.

Distinguir objetivos:
- por kg **fresco** y por kg de **materia seca**;
- por porción cocinada plausible;
- por ha-año y por costo;
- por población, región y entorno agronómico.

Registrar pérdidas por cosecha, transporte, almacenamiento y cocción cuando existan datos.

## 6. Módulo genómico: después, no antes

Secuencia lógica: nutriente prioritario → ruta metabólica respaldada → genes funcionalmente asociados → evidencia de expresión en tubérculos → alternativas de mejora → impactos conocidos → **revisión experta**. AlphaFold puede ser una herramienta puntual para evaluar estructura molecular, **no** un predictor directo de fenotipo agrícola o efecto nutricional. Evitar automatizaciones que incumplan licencias.

## 7. Reproducibilidad y QA esperadas

- Dependencias fijadas por versión, scripts con entradas declaradas y semilla registrada.
- Datos de referencia inmutables con SHA-256, fuente y fecha de acceso.
- Validadores de unidades, conversiones y bases fresco/seco; faltantes nunca se imputan como cero.
- Pruebas de regresión, test de monotonía en condiciones compatibles y verificaciones de balance.
- Escenarios de incertidumbre y sensibilidad; comparación contra cálculos manuales conocidos.
- Salidas con ID de ejecución, versión de fuentes, configuración, autor/revisor y advertencias visibles.
- Sin CI pesada ni servicios pagos hasta existir una necesidad justificada.

### Estructura candidata futura

src/ (ingesta, validación, nutrición, optimización), datasets/manifest, tests/, notebooks/, reports/, research/ (metadatos bibliográficos), docs/. Crear solo cuando vaya a implementarse cada componente, evitando scaffolding vacío.

## 8. Reglas de decisión

Si faltan nutrientes críticos, seguridad toxicológica, procedencia o comparabilidad, el sistema debe **marcar información insuficiente**. No generar rankings definitivos a partir de evidencia parcial.


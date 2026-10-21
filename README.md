# OpenPotato

**Investigación abierta para mejorar la nutrición humana mediante papas más nutritivas, productivas, seguras y accesibles.**

> Estado: **M1-15 — laboratorio virtual de diseño experimental (21-10-2026)**. Datos verificados: USDA, ensayo Holetta de 45 genotipos, ensayo histórico multientorno solo de rendimiento, **catálogo CIP abierto de 29 clones**, **15 accesiones compartidas entre publicaciones**, y **Tabla 16 pública de Perú con 14 materiales y Fe/Zn agregados**, y **12 clones del Perú compartidos con catálogo CIP, ocho también presentes en Holetta**. Se auditaron además las filas originales de Tabla 16 y una tabla independiente de suelos de 9 localidades (27 resúmenes de pH/Fe/Zn de suelo). La Tabla 12 pública del CIP incluye 30 clones evaluados y 4 testigos (68 agregados Fe/Zn), de los cuales 28 resúmenes ya están contenidos en Tabla 16; 20 materiales son adicionales. La revisión del dataset confirma nueve ensayos con tres repeticiones de campo por localidad según metadatos, pero no identifica qué parcela produjo cada medición Fe/Zn agregada. Se inspeccionaron además los esquemas de cinco tablas públicas CIP de selección participativa, calendario, envío de muestras minerales y suelos, sin hallar todavía un enlace validado parcela-muestra-Fe/Zn. El control automático bloquea análisis G×E nutricionales inferenciales con esos archivos; los microdatos XRF departamentales siguen restringidos. No hay validación experimental propia. Para futuras entregas *autorizadas* se construyó un control independiente de cadena de custodia y plantillas vacías; superar controles estructurales no equivale a autorización, calibración ni validación científica. Ahora existe además un simulador Monte Carlo de **potencia del diseño** con 18 escenarios completamente hipotéticos, sin pretender predecir hierro/zinc de clones reales.

## La pregunta central

**¿Cuánto podemos mejorar simultáneamente la calidad nutricional de la papa sin perder rendimiento, seguridad alimentaria, adaptabilidad o acceso económico?**

OpenPotato investiga el problema con un enfoque medible: no solo toneladas por hectárea, sino *nutrición humana utilizable por superficie, costo y recursos invertidos*. No se presupone que una única papa pueda constituir una dieta completa ni se propone reemplazar la diversidad alimentaria.

## Dos líneas complementarias

1. **Papas nutricionalmente mejoradas**: estudiar hierro, zinc, provitamina A, folato, proteínas, ácidos grasos esenciales y sus posibles compensaciones fisiológicas.
2. **Referencia alimentaria realista**: comparar las propuestas con combinaciones accesibles de cultivos y alimentos, para demostrar una ventaja en vez de asumirla.

## Documentación

| Documento | Contenido |
|---|---|
| [Visión y principios](docs/00-vision-y-principios.md) | Misión, beneficiarios, límites y criterios de impacto |
| [Estado del arte](docs/01-estado-del-arte.md) | Evidencia científica, resultados y limitaciones |
| [Preguntas e hipótesis](docs/02-preguntas-e-hipotesis.md) | Hipótesis falsables y prioridades |
| [Arquitectura científica](docs/03-arquitectura-cientifica.md) | Datos, modelos, trazabilidad y análisis |
| [Hoja de ruta](docs/04-hoja-de-ruta.md) | Hitos con entregables y criterios de aceptación |
| [Primer experimento computacional](docs/05-primer-experimento.md) | Protocolo reproducible M1 |
| [Seguridad, ética y acceso](docs/06-seguridad-etica-acceso.md) | Inocuidad, bioseguridad, equidad y transparencia |
| [Fuentes](docs/07-fuentes-y-trazabilidad.md) | Bibliografía inicial verificada y registro de evidencia |
| [Colaboración](docs/08-colaboracion.md) | Cómo participar y potenciales alianzas |
| [Decisiones](docs/09-registro-de-decisiones.md) | Decisiones arquitectónicas y científicas |
| [Herramientas y método](docs/10-herramientas-y-metodologia.md) | Stack inicial, alternativas y condiciones para activar bioinformática e IA |
| [USDA — verificación primaria](docs/13-usda-verificacion-primaria.md) | Fichas oficiales de dos preparaciones hervidas |
| [USDA Foundation — tipos comerciales](docs/14-foundation-tipos-comerciales.md) | Tres tipos crudos, datos y método para comparar variación descriptiva |
| [M1-03 — dispersión en muestras reales](docs/16-variabilidad-muestras-usda.md) | Reconstrucción de 24 muestras, 96 análisis y límites de generalización |
| [M1-04 — genotipos y compromisos agronómicos](docs/17-genotipos-ethiopia-hierro-zinc.md) | 45 genotipos, Fe/Zn, rendimiento fresco, materia seca y Pareto explicable |
| [M1-05 — análisis multientorno y calidad](docs/18-m1-05-multiambiente-calidad.md) | Ensayo multisitio histórico de rendimiento y control de entrada para Fe/Zn por parcela |
| [M1-06 — datos CIP y accesiones compartidas](docs/19-cip-dataverse-catalogo-cruce.md) | Importación del catálogo CIP, cruce de 15 clones y auditoría de licencias |
| [M1-07 — resumen público Perú](docs/20-peru-tabla16-resumenes.md) | Tabla mineral por 14 accesiones, fuente y límites de los agregados |
| [M1-08 — triangulación y nuevas vías experimentales](docs/21-m1-08-triangulacion-y-vias-experimentales.md) | Cruce CIP Perú / catálogo / Holetta, 12+8 coincidencias verificadas, estrategias genéticas y agronómicas y límites |
| [M1-09/M1-10 — filas, suelos y genómica](docs/22-m1-09-10-filas-suelos-genomica.md) | Auditoría 28 estadísticas por fila original, nueve sitios de suelo público y GWAS de 288 accesiones tetraploides (datos fenotípicos por solicitar) |
| [M1-11 — Tabla 12 pública CIP](docs/23-m1-11-tabla12-cip-resumenes.md) | Importación auditable de 68 resúmenes Fe/Zn de 34 materiales, con 28 filas compartidas y no independientes de Tabla 16 |
| [M1-12 — fuentes, discrepancias y requisitos de acceso](docs/24-m1-12-contraste-fuentes-y-matriz-permisos.md) | 29 clones CIP contrastados entre catálogo y Perú sin confundir publicaciones con ensayos independientes; auditoría de diseño y unidades pendientes |
| [M1-13 — vinculación parcela-muestra y aptitud científica](docs/25-m1-13-parcela-muestra-readiness.md) | Seis esquemas públicos auditados con hashes y privacidad; cero enlaces Fe/Zn-parcela verificados, validador experimental reforzado y solicitud mínima de datos al CIP |
| [M1-14 — cadena de custodia de muestras experimentales](docs/26-m1-14-cadena-custodia-muestras.md) | Contratos de cinco CSV y controles de muestras agrupadas, réplicas técnicas, ensayos censurados, Fe/Zn, rendimiento, privacidad y plantillas vacías para entregas autorizadas |
| [M1-15 — laboratorio virtual: potencia y simulación](docs/27-m1-15-laboratorio-virtual-potencia-y-clima.md) | Monte Carlo reproducible de 18 diseños hipotéticos (sitios, bloques biológicos, repeticiones técnicas y variación G×E), con falsos positivos medidos y herramientas mecanísticas existentes para escenarios climáticos futuros |
| [Acceso CIP Dataverse](research/cip-dataverse-access.csv) | Acceso público o restringido verificado por archivo y DOI |
| [Fuentes multientorno candidatas](research/multienvironment-candidates.csv) | Catálogo con estado de acceso, granularidad y licencias pendientes |
| [Zinc — contraste genético/agronómico](docs/15-biofortificacion-zinc-comparacion.md) | Estudio agrícola primario 2026 y nueva hipótesis alternativa |
| [M1 implementación](docs/11-m1-primera-ejecucion.md) | Ejecutar análisis y pruebas sin dependencias ni internet |
| [M1 resultados preliminares](docs/12-m1-resultados-preliminares.md) | Resultados de CI, cálculos y limitaciones |
| [Registro estructurado](research/evidence-register.csv) | Evidencia bibliográfica inicial apta para análisis |

## Estado de resultados

- **Completado técnicamente:** modelo de cobertura nutricional (2 perfiles de referencia), controles de unidades y faltantes, extracción directa USDA, comparación de dos preparaciones y tres tipos comerciales, procedencia SHA-256, CI offline.
- **Completado para esta cohorte comercial:** variabilidad descriptiva de ocho muestras por tipo para Fe, Zn, K y vitamina C; conciliación con medianas y rangos del USDA. Compras limitadas a Virginia (EE. UU.) en 2022, no un ensayo genético.
- **Completado computacionalmente (M1-04):** extracción directa de 45 genotipos identificados de un ensayo publicado con tres repeticiones en un solo ambiente, 15 no dominados en Fe/Zn/rendimiento según medias y cálculos dimensionales de masa mineral/ha puramente teórica.
- **Validado metodológicamente (M1-05):** descomposición G, E y G×E descriptiva sobre 48 medias de rendimiento histórico de papa; control formal de estructura para recibir Fe/Zn y rendimiento de parcelas reales, sin datos sintéticos convertidos en hallazgos.
- **Incorporado de CIP:** 29 clones de catálogo con 10 no dominados en Fe/Zn/rendimiento kg/planta; 15 clones emparejados por ID con Holetta; datos agregados Fe/Zn de 14 materiales de Tabla 16 peruana (12 seleccionados + 2 controles); **12 cruces exactos de Perú con catálogo y 8 en las tres fuentes**, sin mezclar muestras; licencias, hashes y restricciones auditados.
- **Validado (M1-08):** seis pruebas nuevas y pipeline de solo lectura para comparar tres fuentes con control de hash, DOI, unidades y ausentes; sin inventar réplicas ni obtener inferencia G×E.
- **Validado (M1-09/M1-10):** 28 estadísticas Fe/Zn de Tabla 16 cotejadas por igualdad decimal con cada fila original y 3 filas de pie documentadas; 9 localidades con 27 resúmenes auténticos de pH, Fe/Zn **de suelo**, separados de los tubérculos. 105 pruebas aprobadas en CI y workflows con permisos de solo lectura; sin combinar material × suelo ni extrapolar causalidad.
- **Validado (M1-11):** nueva fuente CIP original 6980 con 30 clones biofortificados evaluados y cuatro controles; 68 filas Fe/Zn publicadas para 34 materiales, incluida la coincidencia exacta de los 28 registros de Tabla 16 (no doble conteo). 29 accesiones coinciden con el catálogo CIP, con CIP312686.019 como clon adicional; **no se infiere selección definitiva**.
- **Validado (M1-12):** coincidencia exacta de 29 clones entre catálogo CIP y Tabla 12 peruana; 58 contrastes Fe/Zn (29/29 inferiores en cifras publicadas peruanas para ambos minerales), con mediana descriptiva del cociente Perú/catálogo 0,722 Fe y 0,541 Zn. No es efecto ambiental causal, ni réplica independiente ni selección de variedades; auditoría de metadatos del diseño experimental y controles de procedencia incluidos. [Resultados](datasets/cip_cross_source_29/peru_catalogue_29_clone_report.md).
- **Validado (M1-13):** cinco nuevas fuentes públicas estructuradas más Tabla 12, con seis SHA-256 anclados, sin registros personales; 0 vínculos parcela–muestra–Fe/Zn legítimamente comprobados y entrada al modelo inferencial denegada. El validador ahora rechaza dos genotipos asignados a la misma parcela física y filas CSV malformadas; 128 tests aprobados en Actions. [Auditoría](datasets/cip_peru_linkage/cip_public_linkage_report.md).
- **Implementado (M1-14, sin datos biológicos nuevos):** esquema de cinco tablas para vincular parcela física → muestra → laboratorio → cosecha, con claves explícitas, bloqueo de pools, censura sin imputar cero y separación de réplicas técnicas/biológicas. Nuevas plantillas de encabezados vacías no sobrescribibles y auditoría privada con artefactos solo de recuentos. Validado mediante **148 tests** y caso sintético en Actions. [Código](scripts/validate_sample_lineage.py), [plantillas](scripts/create_sample_lineage_templates.py) y [prueba CI](https://github.com/barbasmarcosi/OpenPotato/actions/runs/39543463653).
- **Implementado (M1-15, solo simulación):** 18 escenarios predefinidos y 5000 corridas por diseño, prueba t sobre contrastes de sitios independientes, estimación de falsos positivos y potencia bajo desviaciones G×E SUPUESTAS. Ejemplo de alta variación G×E y tres bloques: potencia hipotética 9,4%/22,4%/34,5% con 3/6/9 sitios. **No son observaciones CIP ni recomendaciones reales de tamaño de muestra.** [Resultados sintéticos](datasets/hypothetical_trial_design/synthetic_trial_design_report.md) y [CI](https://github.com/barbasmarcosi/OpenPotato/actions/runs/39544792808).
- **Pendiente científicamente:** ensayos reales con Fe/Zn y rendimiento por parcela repetidos en múltiples ambientes, verificación de estabilidad, procesamiento, biodisponibilidad y seguridad. Seguimiento: [issue #7](https://github.com/barbasmarcosi/OpenPotato/issues/7).
- **No iniciado:** biofortificación experimental, simulación genética de cultivares, estudios de absorción humana y evaluación multisitio.

## Primera entrega verificable

Construir un modelo reproducible que compare la cobertura nutricional de papas convencionales y escenarios **hipotéticos** de biofortificación bajo supuestos explícitos de consumo, cocción, biodisponibilidad y requerimientos por población. Luego identificar limitaciones, vacíos de datos y prioridades experimentales. **Ninguna simulación computacional equivale a demostrar una nueva variedad.**

## Reglas de evidencia

- Separar hechos publicados, estimaciones, hipótesis y opiniones.
- Citar fuentes primarias con DOI o identificador estable y registrar sus limitaciones.
- No confundir concentración química con absorción real; ni rendimiento en una parcela con viabilidad global.
- Incluir glicoalcaloides, seguridad alimentaria, diversidad genética, costo y accesibilidad desde el inicio.
- Priorizar herramientas y datos abiertos; revisar licencias antes de usar modelos o datasets de terceros.
- No ofrecer recomendaciones de dietas monótonas o exclusivamente basadas en papa.

**Idioma inicial:** español. **Licencia:** pendiente de decisión explícita; que el repositorio sea público no implica que los materiales tengan automáticamente una licencia abierta.

Inicio: 19 de octubre de 2026.

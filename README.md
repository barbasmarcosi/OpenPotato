# OpenPotato

**Investigación abierta para mejorar la nutrición humana mediante papas más nutritivas, productivas, seguras y accesibles.**

> Estado: **M1-05 — método multientorno de rendimiento validado (20-10-2026)**. Se mantiene el corpus previo USDA y Holetta. Nuevo: análisis de 8 genotipos × 6 ambientes de un ensayo histórico real **solo de rendimiento**, 19 cambios de orden entre 28 pares y verificación del diseño; **71 pruebas automatizadas aprobadas**. Seguimos SIN validación multientorno de hierro/zinc, ensayos biológicos propios ni predicciones genéticas.

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

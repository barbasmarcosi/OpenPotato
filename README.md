# OpenPotato

**Investigación abierta para mejorar la nutrición humana mediante papas más nutritivas, productivas, seguras y accesibles.**

> Estado: **M1-03 con análisis de 24 muestras completado (20-10-2026)**. Dos conjuntos primarios USDA versionados: **SR Legacy (2 preparaciones hervidas)** y **Foundation Foods (3 tipos comerciales crudos)**. Se reconstruyeron **96 resultados químicos de laboratorio** (8 compras por tipo × 4 nutrientes) con trazabilidad hasta adquisición, submuestra y método analítico; **42 pruebas automatizadas aprobadas**. No hay ensayos biológicos propios ni cultivares genéticamente verificados.

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
| [Zinc — contraste genético/agronómico](docs/15-biofortificacion-zinc-comparacion.md) | Estudio agrícola primario 2026 y nueva hipótesis alternativa |
| [M1 implementación](docs/11-m1-primera-ejecucion.md) | Ejecutar análisis y pruebas sin dependencias ni internet |
| [M1 resultados preliminares](docs/12-m1-resultados-preliminares.md) | Resultados de CI, cálculos y limitaciones |
| [Registro estructurado](research/evidence-register.csv) | Evidencia bibliográfica inicial apta para análisis |

## Estado de resultados

- **Completado técnicamente:** modelo de cobertura nutricional (2 perfiles de referencia), controles de unidades y faltantes, extracción directa USDA, comparación de dos preparaciones y tres tipos comerciales, procedencia SHA-256, CI offline.
- **Completado para esta cohorte comercial:** variabilidad descriptiva de ocho muestras por tipo para Fe, Zn, K y vitamina C; conciliación con medianas y rangos del USDA. Compras limitadas a Virginia (EE. UU.) en 2022, no un ensayo genético.
- **Pendiente científicamente:** cultivares de identidad genética confirmada, ensayos replicados multisitio, procesamiento, incertidumbre entre ambientes y revisión experta. Seguimiento: [issue #6](https://github.com/barbasmarcosi/OpenPotato/issues/6).
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

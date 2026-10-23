# OP-M1-14 — Cadena de custodia para futuros ensayos nutricionales autorizados

**Fecha:** 21 de octubre de 2026. **Estado:** software de admisión experimental disponible y probado sobre **datos expresamente sintéticos**. **No se han recibido microdatos CIP XRF ni mediciones nuevas**.

## Problema que resuelve

Las tablas públicas del CIP aportan resúmenes valiosos, pero no las claves de cada parcela, tubérculo muestreado y análisis mineral. Para un futuro ensayo G×E nutricional no alcanza con tener Fe, Zn y rendimiento por genotipo: hay que **demostrar de qué parcela salió la muestra y cómo se midió**. La independencia de unidades biológicas tampoco equivale a repetir lecturas de laboratorio del mismo material.

El nuevo [validador de trazabilidad](../scripts/validate_sample_lineage.py) recibe **cinco CSV independientes** con sus claves explícitas y produce exclusivamente un reporte de controles. Ni reconstruye observaciones ausentes ni ejecuta estadísticas inferenciales o recomendaciones de cultivares.

| Archivo de entrada | Unidad documental | Campos y control principal |
|---|---|---|
| `plots.csv` | Parcela física | `trial_id/site_id/season_id/block_id/plot_id`, genotipo y área m²; **una** asignación de genotipo por parcela |
| `samples.csv` | Muestra de tubérculo | `sample_id`, origen, tipo `single_plot` o `pooled_plots`, tejido, procesado, fecha de toma |
| `sample_plots.csv` | Pertenencia muestra ↔ parcela | Permite **una o varias** parcelas de origen por muestra, jamás infiere vínculos por parecido de nombres |
| `assays.csv` | Lectura de laboratorio | `assay_id`, muestra, Fe/Zn, técnica XRF o ICP-MS, laboratorio, unidad, calificador de detección, `primary` o `technical_replicate` |
| `harvest.csv` | Cosecha de parcela | Identificador físico de parcela, masa fresca kg, área cosechada m² ≤ área registrada |

### Qué controla

- El ID físico de parcela es único en el ensayo/sitio/campaña/bloque: no se adjudica la misma parcela a dos genotipos.
- Una muestra declarada de una sola parcela tiene **exactamente una** clave de origen; una muestra agrupada necesita **al menos dos** parcelas. Mezclas de diferentes genotipos o ambientes se rechazan; agrupamientos homogéneos se registran pero **bloquean la inferencia por parcela**, porque no constituyen réplicas separadas.
- Un análisis técnico repetido solo cuenta como **réplica técnica**; nunca incrementa las parcelas ni los grados de libertad experimentales. Debe existir una medición principal para ese rasgo/muestra.
- Fe y Zn se aceptan **únicamente en mg/kg de materia seca, tejido de pulpa pelada cruda**. Rendimiento es **kg frescos por parcela**, con área cosechada declarada. No se aplican conversiones no justificadas a materia fresca, t/ha o ingesta nutricional.
- Una muestra con el mismo rasgo medido por dos muestras independientes de una sola parcela requiere resolver el protocolo antes de promediar; no hay agregación automática.
- `quantified` exige número positivo finito y límite vacío. Para `below_detection` y `below_quantification`, el valor se conserva **vacío** y el límite del ensayo como número positivo. No se transforman censuras en ceros.
- Se rechazan encabezados duplicados/incompletos, filas malformadas, IDs huérfanos, ensayos primarios duplicados, superficies incoherentes, fuentes sin procedencia o fechas imposibles.

### Política de aptitud

Un archivo puede superar **todos los controles de estructura** y obtener `STRUCTURALLY_LINKED_EXPERT_REVIEW_REQUIRED`. **Esto NO habilita análisis G×E**: primero exige comprobar permisos de uso, aleatorización real, independencia, calibración, sesgo de muestreo, métodos de laboratorio y qué significan las réplicas originales. El estado alternativo `BLOCKED_INCOMPLETE_OR_NONINDEPENDENT_EVIDENCE` retiene conjuntos con faltantes, muestras agrupadas, censura o insuficiencia estructural para modelar.

La herramienta **no ajusta** G×E, heredabilidad, intervalos ni valores p, no sugiere clones y no certifica seguridad alimentaria. No hace automáticamente `join` a las tablas públicas anteriores para crear mediciones que esas tablas no contienen.

## Preparar plantillas SIN inventar observaciones

La utilidad [`create_sample_lineage_templates.py`](../scripts/create_sample_lineage_templates.py) genera cinco archivos **vacíos**, cada uno con su encabezado, más indicaciones de uso. No sobreescribe archivos existentes, ni siquiera parcialmente completados.

```bash
PYTHONPATH=.:src python -m scripts.create_sample_lineage_templates --out /ruta/privada/intake
```

Una vez obtenidos legítimamente datos fuente, completadas las correspondencias originales y revisados sus permisos, correr **localmente**, fuera de Actions públicas:

```bash
PYTHONPATH=.:src python -m scripts.validate_sample_lineage \
  --plots /ruta/privada/intake/plots.csv \
  --samples /ruta/privada/intake/samples.csv \
  --sample-plots /ruta/privada/intake/sample_plots.csv \
  --assays /ruta/privada/intake/assays.csv \
  --harvest /ruta/privada/intake/harvest.csv \
  --out /ruta/privada/resultado-control
```

La salida contiene **solo recuentos estructurales, estado, hashes de archivos fuente, banderas de limitación y mensajes generales**. Nunca se muestran ni exportan filas originales, identificadores individuales de parcelas/muestras, valores analíticos por participante ni posiciones geográficas. El reporte no es un reemplazo de la autorización legal para usar/publicar los insumos.

**Regla de seguridad:** jamás subir ficheros originales de agricultores, muestras restringidas o laboratorios con acuerdos de confidencialidad a un repositorio, PR o artefacto público. Las GitHub Actions de este hito **solo utilizan valores sintéticos inventados por las pruebas**.

## Validación reproducible

- [Suite de pruebas sintéticas](../tests/test_validate_sample_lineage.py): muestra agrupada homogénea/heterogénea, ensayo censurado, límites, duplicados, muestras incompletas, réplicas técnicas, edad/fecha y base seca/fresca, coherencia de rendimiento y privacidad.
- [Pruebas de plantillas vacías](../tests/test_create_sample_lineage_templates.py): ausencia de observaciones, rechazo de sobreescritura y falla segura al intentar validar una planilla solo con encabezados.
- [Workflow M1-14](../.github/workflows/m1-sample-lineage.yml): suite completa offline + ejecución CLI con ensayos inventados de dos localidades, tres genotipos y dos bloques, verificación de que solo se archiva un reporte estructural que no incluye IDs.
- No se atribuye ninguna cifra sintética a papa real, CIP, Holetta ni agricultores.

## Próximo paso científico auténtico

Este módulo ya permite auditar una entrega autorizada antes de estudiar estabilidad nutricional. El obstáculo continúa siendo **obtener la relación original parcela ↔ muestra liofilizada ↔ Fe/Zn**, más los protocolos de laboratorio y licencias de uso. También faltan ensayos de rendimiento, seguridad (glicoalcaloides por tejido/unidad), bioaccesibilidad y costo para cualquier propuesta de variedad o recomendación nutricional.

**Decisión M1-14:** considerar un esquema correcto como apto para **revisión científica independiente**, nunca como garantía de validez de un ensayo ni de superioridad de material vegetal.

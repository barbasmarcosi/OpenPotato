# OP-M1-13 — ¿Podemos unir las muestras minerales a las parcelas del CIP?

**Fecha:** 21 de octubre de 2026. **Estado:** seis archivos públicos del mismo dataset auditados; **vínculos químicos por parcela no verificados**. Este es un control de aptitud y procedencia, no un nuevo ensayo agronómico.

## Pregunta de investigación

Para estimar estabilidad genética de hierro y zinc necesitamos unir, usando *claves originales y verificables*, la medición química de un tubérculo con su genotipo, localidad, fecha/campaña, parcela/bloque, réplica, método de laboratorio y rendimiento.

Los metadatos del [dataset CIP 10.21223/N11QJS](https://doi.org/10.21223/N11QJS), versión 1.0, informan nueve ensayos en cinco departamentos con bloques completos al azar y tres repeticiones por localidad, pero **el diseño general del ensayo no demuestra qué parcela originó cada cifra de hierro/zinc de la Tabla 12**.

## Seis archivos públicos originales auditados

La [Action de descubrimiento](https://github.com/barbasmarcosi/OpenPotato/actions/runs/39541191846) verificó restricciones de archivo, exportaciones TSV y SHA-256. La [auditoría reproducible M1-13](https://github.com/barbasmarcosi/OpenPotato/actions/runs/39541747939) volvió a verificar los bytes frente a hashes fijados. No se accedió a archivos XRF restringidos.

| Archivo Dataverse | Papel inferido por su título/estructura | Registros después del encabezado | Columnas | Qué **no** acredita |
|---|---|---:|---:|---|
| **6982** | Cronograma de envío de muestras liofilizadas a Nottingham | 7 | 7 | Concentración Fe/Zn individual por muestra |
| **6972** | Calendario de siembra y evaluaciones de campo | 13 | 17 | Resultado químico identificable por parcela |
| **6971** | Selección participativa durante la floración | 38 | 21 | Ensayo químico por parcela |
| **6968** | Selección participativa durante la cosecha | 39 | 21 | Ensayo químico por parcela |
| **6975** | Lista de muestras de **suelo** | 10 | 9 | Fe/Zn medido en **tubérculo** |
| **6980** | Tabla 12; estadísticas de Fe/Zn por material | 41 | 84 | Identificadores de parcela asociados a cada observación química |

Las cifras incluyen posibles filas de encabezados internos, pies o celdas vacías; **no equivalen a un recuento de observaciones biológicas**. Los cinco archivos adicionales se analizaron únicamente para determinar su **esquema de columnas**; no se exportaron registros de productores o participantes. Las hojas de floración, cosecha y calendario tienen encabezados posicionales como `A`, `B`, `C`, por lo que los nombres originales no permiten deducir automáticamente claves de parcela.

Los hashes originales y los límites están fijados en [`cip_public_linkage_provenance.json`](../datasets/cip_peru_linkage/cip_public_linkage_provenance.json); las descripciones de estructura y el estado de disponibilidad están en [`cip_public_linkage_readiness.csv`](../datasets/cip_peru_linkage/cip_public_linkage_readiness.csv).

## Resultado computacional: control de admisión cerrado

El módulo [`scripts/cip_peru_public_linkage.py`](../scripts/cip_peru_public_linkage.py) genera un reporte **sin valores de filas fuente, nombres de participantes ni identificadores individuales**. Comprueba el SHA-256 exacto de cada archivo, su número de filas/columnas y los encabezados esperados. Rechaza silenciosas modificaciones de la fuente: ante un cambio de versión se exige auditoría manual.

**Resultado:** `verified_plot_to_mineral_assay_linkages = 0`, y `admission_to_mineral_gxe_model = DENIED_UNTIL_LINKABLE_PRIMARY_ASSAYS`.

**Importante:** cero *vínculos verificados* no significa que no se hayan medido parcelas ni que los autores del CIP carezcan de archivos de laboratorio. Significa que **OpenPotato no dispone de la unión original comprobada y autorizada para reconstruirla**. Una hoja con selecciones “por parcela” es evidencia de decisiones participativas, no de Fe/Zn analítico.

### Corrección complementaria del validador experimental

El módulo preexistente [`validate_fe_zn_trial.py`](../scripts/validate_fe_zn_trial.py) ahora también:

- Rechaza un mismo identificador **físico** de parcela `(ensayo, localidad, campaña, bloque, parcela)` asignado a **más de un genotipo** dentro de la misma estructura experimental.
- Rechaza filas CSV con columnas extra o faltantes **antes** de agrupar por ensayo, evitando que datos malformados oculten su causa real detrás de errores secundarios.
- Conserva requisitos existentes de Fe, Zn y rendimiento con unidades compatibles, repeticiones independientes declaradas y al menos dos localidades. Un CSV que supera el validador es únicamente **admisible para revisión de diseño**, no un ensayo automáticamente válido, aleatorizado o genéticamente causal.

Los nuevos controles se prueban en [`test_cip_peru_public_linkage.py`](../tests/test_cip_peru_public_linkage.py) y [`test_validate_fe_zn_trial.py`](../tests/test_validate_fe_zn_trial.py). [CI M1-13](https://github.com/barbasmarcosi/OpenPotato/actions/runs/39541747939): **128 pruebas aprobadas**, extracción real de las seis tablas públicas y publicación de metadatos anónimos solamente.

## Próximo paso verificable: paquete mínimo de datos para solicitar al CIP

En vez de solicitar cualquier CSV con “Fe” y “Zn” en el nombre, hay que confirmar los siguientes campos y su procedencia:

1. Tabla de **unidades experimentales**: `trial_id`, `genotype_id`, `site_id`, `year/season`, `block_id`, `plot_id`, área cosechada, tratamiento y trazabilidad del material.
2. Tabla de **muestras vegetales**: `sample_id`, `plot_id`, fecha/órgano/tejido muestreado, número de tubérculos, liofilización, porcentaje de materia seca, procesamiento y reglas de mezclado de muestras (*pooling*).
3. Tabla **analítica**: `sample_id`, Fe, Zn, unidad (materia seca o fresca), método (XRF/ICP-MS u otro), calibración, laboratorio, límite de detección/cuantificación, banderas de calidad, réplicas **técnicas** separadas de las **biológicas**.
4. Tabla de **rendimiento y seguridad**: rendimiento por parcela con denominador, protocolo de `TTYNA`, unidades inequívocas de glicoalcaloides, conservación y base fresca/seca.
5. Diccionario completo, archivo de correspondencias entre IDs, consentimiento y privacidad de participantes cuando corresponda, licencias/condiciones para **acceso y publicación de derivados agregados**.

Cualquier entrega que carezca de `sample_id` vinculable a `plot_id`, o que solo contenga promedios por clon, debe mantenerse fuera de modelos inferenciales G×E. Si se reciben muestras agrupadas de varias parcelas, habría que definir antes un modelo con la unidad biológica correcta: **no asignar el mismo resultado a cada parcela del grupo**.

### Texto listo para adaptar a una solicitud científica

> Asunto: Solicitud de metadatos de vinculación parcela–muestra–Fe/Zn y acceso autorizado — CIP Dataverse DOI 10.21223/N11QJS
>
> Estamos trabajando en OpenPotato, una investigación abierta de biofortificación de papa con controles reproducibles de procedencia. Hemos auditado las tablas públicas 6980 (resúmenes Fe/Zn), 6982 (cronograma de muestras), 6972 (calendario) y 6971/6968 (selección participativa), y buscamos comprobar si existen archivos con la clave original que conecte parcela, muestra liofilizada y resultado químico individual.
>
> ¿Podrían indicarnos si existe un diccionario de variables y una correspondencia autorizada entre `genotype × localidad × campaña × bloque × parcela × sample_id × Fe/Zn`, junto con las unidades analíticas, procedimientos de muestreo, posibles muestras agrupadas y controles de calidad? También agradeceríamos información sobre el procedimiento legítimo para solicitar acceso a los datos XRF restringidos y condiciones para distribuir únicamente resultados derivados, sin registros personales.
>
> No solicitamos modificar permisos existentes ni acceder a información reservada por vías distintas a las establecidas por los responsables de los datos.

**Decisión M1-13:** seguir desarrollando trazabilidad y reglas de admisión. Postergar cualquier análisis causal, ranking de variedades por estabilidad nutricional, certificación de inocuidad o rendimiento multientorno hasta disponer de datos autorizados con claves biológicas comprobables.

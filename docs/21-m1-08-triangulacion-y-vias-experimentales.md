# OP-M1-08 — Triangulación documental Perú / CIP / Holetta y siguientes hipótesis

**Fecha:** 2026-10-20. **Estado:** pipeline reproducible validado; no hay nuevos ensayos de campo de OpenPotato.

## 1. Cruce exacto de las tres fuentes

El módulo [cip_three_source_audit.py](../scripts/cip_three_source_audit.py) relaciona, por identificador de accesión exacto, tres conjuntos de datos que **NO comparten un diseño experimental**:

1. [CIP Perú (10.21223/N11QJS)](https://doi.org/10.21223/N11QJS): Tabla 16; dos resúmenes minerales (Fe y Zn) por cada uno de 14 materiales.
2. [Catálogo CIP (10.21223/P3/LQOT7Z)](https://doi.org/10.21223/P3/LQOT7Z): 29 clones; cifras publicadas de Fe/Zn y rendimiento en kg/planta.
3. [Seid et al. (2023), Holetta (10.3390/plants12142625)](https://doi.org/10.3390/plants12142625): 45 genotipos; medias publicadas de un ensayo con repeticiones en **un único sitio-año**; rendimiento en kg/m² fresco.

**Conteos comprobados contra los CSV versionados y sus hashes:** 12 clones de la Tabla 16 aparecen en el catálogo; ocho de esos 12 aparecen también en Holetta. Dos variedades comerciales publicadas en Tabla 16 (Serranita y Yungay) permanecen identificadas como **controles**, sin forzar coincidencias inexistentes con el catálogo.

Los ocho identificadores compartidos son: CIP312507.311, CIP312721.245, CIP312721.286, CIP312725.024, CIP312725.047, CIP312735.105, CIP312767.014 y CIP312871.043. Son coincidencias de código, no nuevas réplicas de un mismo experimento.

### Controles científicos que aplica el importador

- Verifica SHA-256 de **cada CSV** contra el manifiesto de la fuente y exige el DOI declarado.
- Rechaza IDs vacíos/duplicados donde una fuente representa un resumen por material; en Perú la identidad de fila compuesta es accesión + nutriente y se exigen **dos resúmenes distintos** por material.
- Verifica que Fe/Zn peruanos mantengan unidad mg/kg de materia seca, estadístico agregado, n entero positivo, SD no negativa y mínimo ≤ media ≤ máximo.
- Mantiene las cifras Fe/Zn por **fuente independiente**. No promedia, calcula tamaños de efecto, p-valores, intervalos de confianza ni estima G×E.
- Conserva el n publicado de Perú sin llamarlo réplica independiente. Mantiene ausentes como valores vacíos, no ceros.
- Presenta rendimiento de catálogo en kg/planta y de Holetta en kg/m² fresco **sin calcular diferencias, ratios ni convertir unidades**.
- La coincidencia de ID no certifica identidad genética mediante genotipado ni igualdad de cultivo, cosecha o laboratorio.

### Reproducir

```bash
PYTHONPATH=.:src python -m unittest discover -s tests -v
PYTHONPATH=.:src python -m scripts.cip_three_source_audit --out /tmp/m1-08
```

El pipeline [cip-three-source.yml](../.github/workflows/cip-three-source.yml) valida offline toda la suite y archiva una tabla CSV por material, manifiesto JSON y reporte Markdown. Usa permisos `contents: read`; no realiza pushes de datos desde Actions.

## 2. Cuatro vías experimentales para evaluar (NO propuestas de variedades ya probadas)

| Vía | Evidencia primaria | Lectura correcta | Qué falta antes de recomendar |
|---|---|---|---|
| Mejoramiento convencional recurrente en diploides | Amoros et al. (2020), DOI [10.1002/csc2.20170](https://doi.org/10.1002/csc2.20170); 60 genotipos, dos años, tres ciclos de selección | Apoya avances de Fe/Zn bajo la población y diseño estudiados; no demuestra superioridad de todos los tetraploides | Datos transferibles y replicados a los materiales diana y ambientes destino |
| Aplicación foliar de Zn sobre clones biofortificados | Estudio de 2024, DOI [10.3390/agriculture14122186](https://doi.org/10.3390/agriculture14122186); cinco genotipos incluyendo Yungay | Interacción genotipo × dosis foliar y aumento de Zn en condiciones del ensayo; **dosis no es ambiente** | Efectos sobre rendimiento, costos, suelo, nutrición humana, estabilidad y riesgos locales |
| Aplicación de Zn al suelo en Andes | Estudio de 2026, DOI [10.1007/s42729-026-03066-2](https://doi.org/10.1007/s42729-026-03066-2); sitios, años, variedades y dosis | Hay evidencia agronómica multisitio de respuesta a Zn, dependiente de dosis, variedad y sitio | Datos por parcela accesibles, balance ambiental/costo y validación de condiciones propias |
| Coexpresión de nicotianamina sintasa y ferritina | Estudio publicado 2025, DOI [10.1007/s11032-025-01619-4](https://doi.org/10.1007/s11032-025-01619-4); variedad Spunta transformada | Resultado experimental de biofortificación Fe/Zn en eventos transformados, no una variedad lista para adopción universal | Seguridad y equivalencia alimentaria, regulación, estabilidad multientorno, biodisponibilidad y acceso |

**No mezclar escalas:** concentración mg/kg seco no equivale a cantidad absorbida en humanos ni por hectárea; transgénesis, fertilización y mejoramiento convencional tienen estructuras de costo, tiempo, regulación y adopción distintas.

## 3. Próximo experimento útil

Conseguir, por vías autorizadas, una matriz por **parcela × bloque × localidad × año × genotipo**, con Fe, Zn, rendimiento, base seca/fresca, método analítico, controles de contaminación, incertidumbre instrumental y diccionario de variables. Evaluar sesgos por muestra y efectos de laboratorio antes de ajustar modelos jerárquicos. Deberían incorporarse tolerancia a tizón, glicoalcaloides, características poscosecha, costo por nutriente absorbible y aceptación por agricultores/consumidores.

Los archivos XRF de varias regiones peruanas siguen marcados como **restringidos**: no descargarlos sin permiso. Si no hay datos por parcela, continuar con triangulación documental y preguntas falsables, sin fabricar unidades experimentales.

## 4. Criterio de avance

El M1-08 **sí** demuestra interoperabilidad documental y calidad de ingreso sobre fuentes abiertas verificadas. El M1-08 **no** ha validado un genotipo superior, un modelo G×E nutricional inferencial ni una intervención agronómica. Por eso PR #5 debe seguir en borrador.

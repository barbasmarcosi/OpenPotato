# OP-M1-07 — Resumen público de 14 accesiones del programa CIP en Perú

**Fecha de validación:** 2026-10-20. **Naturaleza de evidencia:** resumen publicado en Dataverse; NO observaciones por parcela ni prueba independiente de G×E.

## 1. Fuente primaria realmente descargada

[Dataset 10.21223/N11QJS](https://doi.org/10.21223/N11QJS), Centro Internacional de la Papa, versión **1.0**. Archivo público de Dataverse **6979**, *Tabla 16. Selección de 12 clones biofortificados tetraploides para ser evaluados*.

- La API pública de Dataverse devuelve un TSV de 14.137 bytes. Su SHA-256 es `39843e2d1cea114ee18f32e9cd40219c14a8ff32a70ea737bb6438ee609e9dc8`.
- El MD5 de **ese archivo exportado** es `03b886a403f6f313179e19852f4f5724`. El MD5 del **archivo almacenado** que figura en los metadatos de Dataverse es `170766ab8217f2b6d38f62c646616268`. Se registran **ambos** porque la API exporta una representación tabular transformada; no se fuerza su igualdad.
- Archivo de **18 filas**: encabezado, **12 clones más 2 testigos**, y **3 filas finales de resumen global** `Mean/Max/Min`. Las tres filas finales **no son genotipos** y se excluyen.
- Se extrajeron para cada accesión medias, recuentos publicados `n`, desviación estándar y mínimo/máximo de `FEDW` (hierro en peso seco) y `ZNDW` (zinc en peso seco): **28 registros nutriente × accesión**.
- La Tabla 16 contiene otras variables como rendimiento `TTYNA`, materia seca y glicoalcaloides `TglyFW`, pero no se interpretan cuantitativamente aquí mientras no se compruebe su diccionario de unidades y alcance experimental.

## 2. Ejemplos de los resúmenes públicos (mg/kg de materia seca)

| Accesión | Fe medio | n Fe | Zn medio | n Zn |
|---|---:|---:|---:|---:|
| CIP312507.311 | 20,74 | 10 | 13,04 | 10 |
| CIP312721.245 | 19,90 | 11 | 12,37 | 11 |
| CIP312725.047 | 22,54 | 11 | 13,14 | 11 |
| CIP312767.014 | 18,95 | 11 | 11,76 | 11 |
| CIP720064 (Yungay, control) | 13,28 | 10 | 8,41 | 10 |

**Advertencia crucial:** `n` procede de la columna publicada y NO prueba que cada medición corresponda a una parcela biológica independiente ni que los clones se hayan evaluado en iguales sitios/años. No atribuir la desviación estándar al componente genotipo × ambiente sin conocer la unidad de réplica.

## 3. Qué podemos afirmar y qué no

La evidencia confirma que el programa CIP publicó información cuantitativa adicional sobre clones seleccionados y testigos, con medidas de dispersión. **No** reproduce por sí sola el ANOVA del programa ni demuestra estabilidad genética.

La presencia de doce clones seleccionados en un programa de múltiples localidades y el hecho de que algunos aparezcan en el catálogo CIP y Holetta constituyen oportunidades de **triangulación documental**, no réplicas experimentales intercambiables.

No es correcto promediar datos del catálogo (kg/planta, Fe/Zn peso seco), de Holetta (kg/m², Fe/Zn peso seco) y de este estudio (estadísticas agregadas de programa) como si fueran ensayos emparejados.

## 4. Implementación y reproducción

- [Importador específico de Tabla 16](../scripts/cip_peru_selected.py): controla 77 columnas de la fuente mediante cabeceras objetivo, 17 filas de datos más encabezado, identifica las 3 filas finales `Mean, Max, Min`, y exige fuentes/hashes y resúmenes químicos coherentes.
- [Datos derivados](../datasets/cip_peru_summary/peru_selected_aggregate_fe_zn.csv), [reporte completo](../datasets/cip_peru_summary/peru_selected_report.md), [manifest](../datasets/cip_peru_summary/peru_selected_provenance.json).
- [Workflow validado](../.github/workflows/cip-peru-selected.yml) y [pruebas sintéticas](../tests/test_cip_peru_selected.py).

Para reproducir:

```bash
curl -fL "https://data.cipotato.org/api/access/datafile/6979" -o /tmp/peru-6979.tab
PYTHONPATH=.:src python -m scripts.cip_peru_selected --tsv /tmp/peru-6979.tab --out /tmp/peru-resumen
```

El importador rechaza cambios inesperados de exportación, filas confundidas con genotipos, unidades analíticas ausentes, nulo vs cero e inconsistencias matemáticas de medias y rangos.

**Pendiente:** los conjuntos departamentales originales de minerales XRF siguen marcados `restricted=true` en Dataverse; no podemos reproducir G×E nutricional sin acceso legítimo y sin auditar cómo se midieron los nutrientes por parcela, sitio y campaña. Ver [inventario de acceso](../research/cip-dataverse-access.csv) y [documentación del catálogo](19-cip-dataverse-catalogo-cruce.md).

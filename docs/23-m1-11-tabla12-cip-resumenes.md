# OP-M1-11 — Tabla 12 original del CIP: 34 materiales, sin duplicar Tabla 16

**Fecha:** 2026-10-20. **Estado:** importación verificada de resúmenes publicados; no son datos de parcela.

## Fuente primaria y estructura auditada

Fuente: [CIP Dataverse DOI 10.21223/N11QJS](https://doi.org/10.21223/N11QJS), versión 1.0, archivo público **6980** (Tabla 12 de laboratorio). La exportación TSV contiene 84 columnas y 41 registros posteriores al encabezado. [Inventario fila a fila](https://github.com/barbasmarcosi/OpenPotato/actions/runs/39486255580).

- SHA-256 de exportación TSV: `0f33b843e286eab15ad71c6c110592adc60709997d75b2b1c5f7365ca99f6152`.
- MD5 de exportación: `b6335e33f8bc8ab3309a56904083911a`.
- MD5 de la representación original almacenada en los metadatos Dataverse: `6ba7f982da7cc2073693cf0b1e13f253`. No son los mismos bytes.
- **34 materiales**: 30 clones biofortificados **evaluados**, más cuatro testigos comerciales (Ccompis, Canchan-INIA, Serranita y Yungay). Evaluado **no** significa seleccionado finalmente.
- **Siete filas no materiales**: cuatro vacías y tres pies de resumen Prom, Max y Min; preservadas como registro de auditoría.

## Hallazgo fundamental: las Tablas 12 y 16 NO son réplicas

La importación de Tabla 12 contiene **68 resúmenes publicados** (Fe y Zn para 34 materiales), conservando n, media, SD, mínimo y máximo en mg/kg de materia seca, cada uno con su línea TSV de origen. **Los 28 resúmenes de los 14 materiales de Tabla 16 (archivo 6979) aparecen también en la Tabla 12, y coinciden exactamente los códigos de criador, n, medias, SD, mínimos y máximos**, con igualdad Decimal y verificación de los CSV originales por SHA.

Por lo tanto hay **20 materiales adicionales y 40 resúmenes minerales que no figuraban en Tabla 16**, pero NO 40 ensayos independientes adicionales, ni autorización para sumar recuentos entre las tablas.

Los **29 clones** del [catálogo CIP](https://doi.org/10.21223/P3/LQOT7Z) están presentes entre los 30 clones de Tabla 12. El clon adicional, al comparar identificadores exactos de los CSV, es **CIP312686.019**. El mismo código de accesión no garantiza material vegetal genotipado, ambiente emparejado, protocolo de laboratorio idéntico ni independencia entre publicaciones.

El [reporte final STC del CIP de Salas et al. (2021)](https://ilcym.cipotato.org/publications/potenciales-nuevas-variedades-de-papa-biofortificada-con-altos-contenidos-de-hierro-y-zinc-para-contribuir-a-la-seguridad-alimentaria-y-nutricional-en-agricultura-familiar-alto-andina-reporte-fina/) informa la evaluación de 30 clones y cuatro testigos en nueve localidades, con ocho materiales identificados para etapas posteriores. **Esa selección reportada no fue reconstruida estadísticamente por OpenPotato** y no autoriza afirmar que los 30 clones fueron ganadores.

## Implementación y reproducción

El [importador](../scripts/cip_peru_table12.py) comprueba el checksum fijado del archivo 6980, los 34 materiales y ordinals fuente, los siete renglones no materiales, los estadísticos positivos/coherentes y el cotejo completo con Tabla 16. Las [pruebas sintéticas](../tests/test_cip_peru_table12.py) ejercitan cambios de SHA, IDs duplicados, datos ausentes, n fraccionarios, pies alterados y desacuerdos entre tablas.

El [workflow M1-11](../.github/workflows/cip-peru-table12.yml) descarga únicamente este archivo público, ejecuta toda la suite y solo publica derivados en la rama de investigación tras aprobar la validación.

- [68 resúmenes Fe/Zn](../datasets/cip_peru_table12/peru_table12_fe_zn_summaries.csv)
- [Ledger de siete filas no materiales](../datasets/cip_peru_table12/peru_table12_nonmaterials.csv)
- [Manifiesto de hashes y limitaciones](../datasets/cip_peru_table12/peru_table12_provenance.json)
- [Reporte derivado](../datasets/cip_peru_table12/peru_table12_report.md)

**Reproducción:** ejecutar la suite offline con `PYTHONPATH=.:src python -m unittest discover -s tests -v`, descargar https://data.cipotato.org/api/access/datafile/6980 y ejecutar `PYTHONPATH=.:src python -m scripts.cip_peru_table12 --tsv archivo6980.tab --out salida`, tras validar el SHA anterior. [Validación inicial: 112 pruebas](https://github.com/barbasmarcosi/OpenPotato/actions/runs/39486944615).

## Límites científicos

- Los n de la tabla son tamaños reportados para resúmenes, NO unidades experimentales independientes documentadas.
- No hay observaciones Fe/Zn individuales por sitio, campaña, bloque o parcela. Las SD/rangos no son intervalos de confianza ni errores experimentales aptos para G×E inferencial.
- Columnas adicionales como TTYNA, TglyFW y atributos organolépticos no se interpretan numéricamente sin comprobar el diccionario de unidad, tejido, método y base fresca/seca. Especialmente, **glicoalcaloides sin unidad confirmada NO permiten certificar seguridad ni comparar umbrales sanitarios**.
- No se demuestra causalidad genética, heredabilidad, superioridad agronómica, resistencia en campo, biodisponibilidad humana o viabilidad de una nueva variedad.

**Siguiente paso:** obtener legítimamente datos Fe/Zn/yield por parcela × bloque × localidad × año, diccionario de laboratorio y permisos de uso antes de modelos inferenciales.

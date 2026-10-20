# OP-M1-06 — Catálogo abierto del CIP, coincidencias entre publicaciones y disponibilidad de ensayos

**Fecha:** 2026-10-20 · **Estado:** datos primarios del catálogo incorporados y revisados; comparación entre publicaciones ejecutada; **microdatos de hierro y zinc por parcela en varios ambientes todavía no disponibles**.

## 1. Datos abiertos conseguidos y procesados

Conseguimos acceso efectivo a la API de [CIP Dataverse](https://data.cipotato.org) desde GitHub Actions. Los resultados completos de auditoría figuran en [run #39472764755](https://github.com/barbasmarcosi/OpenPotato/actions/runs/39472764755) y [run #39474173333](https://github.com/barbasmarcosi/OpenPotato/actions/runs/39474173333). La condición de acceso se evaluó por **archivo**, no solo por el hecho de que un dataset esté indexado en AGRIS.

### Catálogo de 29 clones biofortificados — incorporado

**Repositorio original:** [CIP Dataverse 10.21223/P3/LQOT7Z](https://doi.org/10.21223/P3/LQOT7Z), versión **1.2**, condiciones del dataset: **Creative Commons Attribution 4.0**.

Archivos de origen publicados:
- `Biofortified_clones.xls`, Dataverse file ID **2211**, 44.032 bytes, SHA-256 `58706bfb9052220dccc89412d14033c750e7911861d03b5e6c4c5871b2135226`.
- `Data_dictionary.xls`, file ID **2212**, 50.176 bytes, SHA-256 `905c0cf39f4ad1d2b9d34dfb698440f49304992d6370f3ec8a76afbdb7298525`.

**Resultado:** 29 accesiones CIP individuales en un catálogo descriptivo, 31 columnas informativas (dentro de un XLS de 77 columnas, algunas vacías); pedigree, hierro, zinc, materia seca, rendimiento **kg/planta**, resistencia cualitativa a enfermedades y vitamina C cuando está informada. Los valores originales de Fe y Zn se expresan **mg/kg de peso seco**; vitamina C en **mg/100 g de peso seco**.

Implementación:
- [Importador y validador del XLS](../scripts/cip_clone_catalog.py), lector `xlrd==2.0.2` fijado **solo** en la CI científica de importación; los demás análisis funcionan sin esa dependencia.
- [Catálogo normalizado](../datasets/cip_catalogue/cip_29_clones_catalogue.csv), [informe](../datasets/cip_catalogue/cip_29_clones_report.md), [manifiesto](../datasets/cip_catalogue/cip_29_clones_provenance.json).
- [Workflow reproducible](../.github/workflows/cip-catalogue.yml): descarga ambos archivos directamente desde CIP, verifica MD5/SHA-256, valida esquema, analiza y archiva derivaciones de modo determinista.

**10 de las 29 accesiones están en la frontera de Pareto descriptiva** de rendimiento por planta + Fe/Zn. No son 10 materiales cuya superioridad ni estabilidad esté demostrada; la optimización se hizo sobre cifras de catálogo publicadas, sin datos de replicación. Los mínimos y máximos publicados no se interpretan como intervalos de confianza.

## 2. Coincidencia exacta con el estudio de Holetta (Etiopía)

El catálogo CIP y [Seid et al. (2023)](https://doi.org/10.3390/plants12142625) contienen **15 accesiones con códigos CIP idénticos**, sin recurrir a similitud de nombre. El código enlaza estrictamente ambos CSV versionados y auditados por sus hashes.

- [Datos comparados](../datasets/cross_study/matched_cip_clones.csv), [reporte de las 15 accesiones](../datasets/cross_study/matched_cip_report.md), [proveniencia](../datasets/cross_study/matched_cip_provenance.json).
- [Motor de cruce](../scripts/cross_study_clones.py) y [CI de cruce](../.github/workflows/cip-cross-study.yml).
- Fe y Zn se expresan **mg/kg de peso seco** en ambas fuentes; se conservan sin corregir por origen, preparación o método desconocidos.

**Hallazgo descriptivo:** en el estudio Holetta, **las 15 cifras de hierro y las 15 de zinc son inferiores** a las cifras del catálogo. Es un patrón documental que amerita investigar. **NO puede atribuirse a ambiente, genética o sesgo de laboratorio** sin conocer el origen de muestreo del catálogo, método, campaña y emparejamiento experimental.

Los rendimientos no se comparan bajo ningún concepto: catálogo **kg/planta** frente a Holetta **kg/m² fresco**. La vitamina C está ausente de una o ambas fuentes para parte de las accesiones. Ninguna diferencia se trata como una medida causal ni se calculan p-valores.

## 3. ¿Conseguimos los ensayos nutricionales multiambiente por parcela?

**Todavía no.** Verificamos metadatos oficiales e identificadores de archivo:

| Dataset CIP | DOI | Acceso a datos | Limitación |
|---|---|---|---|
| Catálogo de 29 clones | [10.21223/P3/LQOT7Z](https://doi.org/10.21223/P3/LQOT7Z) | Dos XLS originales públicos; **importados** | Catálogo de clones, no microdatos G×E |
| Ensayos en nueve localidades del Perú | [10.21223/N11QJS](https://doi.org/10.21223/N11QJS) | 16 archivos públicos, con tablas de suelo, selección, laboratorio y otros resúmenes | No se estableció que contengan Fe/Zn por parcela × genotipo × ambiente |
| Ensayo participativo Huancavelica | [10.21223/P3/8NEIZP](https://doi.org/10.21223/P3/8NEIZP) | Diccionario público, tabla experimental principal **restringida** | No descargar sin autorización |
| Minerales La Libertad | [10.21223/HRLAI0](https://doi.org/10.21223/HRLAI0) | Dos archivos de minerales **restringidos**; diccionario público | Datos XRF sin acceso autorizado |
| Minerales Huancavelica | [10.21223/T7JUCL](https://doi.org/10.21223/T7JUCL) | Archivo de minerales **restringido**; diccionario público | Datos XRF sin acceso autorizado |
| Minerales Apurímac | [10.21223/DTSA6Y](https://doi.org/10.21223/DTSA6Y) | Dos archivos de minerales **restringidos**; diccionario público | Datos XRF sin acceso autorizado |
| Ganancia genética diploide | [10.21223/9OJPJ7](https://doi.org/10.21223/9OJPJ7) | Metadatos públicos, **sin archivos enumerados** en versión consultada | No hay archivo exportable confirmado |
| Clones de Ruanda | [10.21223/MBBV5A](https://doi.org/10.21223/MBBV5A) | Archivos públicos; **condiciones de uso no especificadas** | Verificar permisos de reutilización con los contactos antes de redistribuir |

Los datos restringidos no se descargarán mediante métodos que eludan autorización. La indicación general CC BY en algunos datasets **no convierte un archivo marcado restricted en accesible sin permiso**.

### Qué hay que solicitar o localizar

Para G×E nutricional necesitamos, idealmente, una tabla que identifique:
- Clon/variedad, localidad, campaña, tratamiento, bloque/parcela y réplica biológica;
- Fe y Zn analizados, tejido y base fresca/seca, método XRF u otro, unidad/LOD/LOQ;
- Rendimiento en la misma unidad de diseño, área de parcela, materia seca y variables agronómicas;
- Licencia explícita, versión, diccionario y permisos de redistribución.

El módulo [validate_fe_zn_trial.py](../scripts/validate_fe_zn_trial.py) ofrece una puerta de calidad **para un diseño específico de datos emparejados**; no inventa pares químicos o parcelas si solo hay valores agregados. Se deberá adaptar a experimentos con muestras combinadas o diseños alternativos documentados.

## 4. Próxima fase y decisión científica

La investigación ya permite comparar **materiales reales** y descubrir diferencias entre fuentes verificables. **Aún no permite** evaluar heredabilidad, estabilidad de micronutrientes a través de los nueve ensayos peruanos ni efectos genotipo×ambiente por parcela.

Acciones justificadas:
1. Auditar el contenido exacto de las tablas públicas del estudio de nueve sitios y registrar si tienen Fe/Zn y por qué nivel de unidad experimental.
2. Pedir autorización para las tablas XRF restringidas de los departamentos; no presumir que todos los ensayos emplearon clones idénticos ni que sus fechas son comparables.
3. Con documentación científica, elegir un subconjunto de materiales para investigación funcional futura, sin confundir ranking del catálogo con una variedad desarrollada.

La frontera de Pareto y las comparaciones de accesiones son **hipótesis para orientar nuevas comprobaciones**, no una propuesta actual de consumo, ensayo genético ni manipulación experimental.

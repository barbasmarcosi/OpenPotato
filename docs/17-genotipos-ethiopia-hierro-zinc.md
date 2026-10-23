# OP-M1-04 — Genotipos identificados: hierro, zinc y rendimiento

**Fecha:** 2026-10-20. **Estado:** primera reproducción de una tabla científica primaria y cribado descriptivo. **No constituye validación multientorno.**

## Pregunta

Cuando tenemos **identidades de clones y variedades** (no solo tipos comerciales), ¿cuáles son los compromisos medidos entre concentraciones minerales y producción? ¿Por qué puede ser engañoso maximizar únicamente mg/kg de hierro o zinc?

## Fuente primaria exacta

Ebrahim Seid et al. (2023). *Genetic Variability for Micronutrient Content and Tuber Yield Traits among Biofortified Potato (Solanum tuberosum L.) Clones in Ethiopia.* **Plants 12(14), 2625. DOI [10.3390/plants12142625](https://doi.org/10.3390/plants12142625)**; versión [PubMed Central PMC10383430](https://pmc.ncbi.nlm.nih.gov/articles/PMC10383430/). Publicación de acceso abierto **CC BY 4.0** con atribución.

- XML estructurado: [Europe PMC, fullTextXML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10383430/fullTextXML).
- SHA-256 **fijado para la versión exacta consultada**: \`f3afe300384cd6f7b0c24bf44dbe24ebad8ef1de6ceefcd414845794e6aacd78\`.
- Estudio: **45 genotipos** en **Holetta, Etiopía, 2019**, diseño alfa-látice 9 × 5 con **tres repeticiones**. Los valores visibles en la tabla son **medias publicadas por genotipo**, no los datos por bloque/parcela.
- Tabla 2 \`plants-12-02625-t002\` — rendimiento de tubérculo fresco (kg/m²), materia seca (%), hierro y zinc (mg/kg **peso seco**).

Los datos provienen de **un sitio y una campaña**. Sin datos de ensayo en múltiples ambientes, no se pueden medir interacciones genotipo × ambiente ni confirmar estabilidad.

## Método computacional

1. La CI descarga el JATS XML desde Europe PMC, verifica el hash SHA-256 y el DOI correcto.
2. Extrae exactamente **45 identificadores distintos** de genotipos, valores numéricos de las columnas precisas, y separa letras sobrescritas de agrupación estadística de las medidas.
3. Valida puntos de referencia de la tabla (Gudanie; CIP312767.014; CIP312735.062), cantidades positivas, materia seca físicamente válida y unicidad.
4. Calcula una **frontera descriptiva de Pareto** para: rendimiento fresco, concentración de Fe en peso seco, concentración de Zn en peso seco.
5. Calcula **solo como indicador teórico exploratorio** la masa de hierro o zinc por hectárea a partir del producto de rendimiento, fracción de materia seca y concentración. Este cálculo **no evalúa disponibilidad biológica, pérdidas, comestibilidad ni rendimiento estable**.
6. Archiva los 45 registros derivados con DOI, lugar, año, tipo de dato y hash; incluye tests sintéticos y de snapshot.

## Resultados de la fuente que permiten verificar el modelo

| Material | Rendimiento fresco kg/m² | Materia seca % | Fe mg/kg seco | Zn mg/kg seco |
|---|---:|---:|---:|---:|
| **Gudanie** (control) | 1,91 | 26,59 | 14,68 | 10,22 |
| CIP312735.062 | 2,26 | 26,52 | 16,53 | 11,14 |
| CIP312725.110 | 1,69 | 27,78 | 21,60 | 14,99 |
| CIP312767.014 | 0,66 | 25,39 | 26,07 | 19,14 |
| CIP312621.069 | 0,53 | 25,40 | 25,40 | 20,59 |

**Resultado del código:** **15 genotipos no dominados** en las tres medidas. El archivo contiene los 45 materiales y los 15 miembros de la frontera.

**No confundir:** «no dominado» solo significa que ningún otro registro tiene **simultáneamente** valores de las tres columnas al menos iguales y alguna estrictamente mayor. No significa «significativamente superior», «apto para agricultores», «mejor variedad global» ni «adecuado para nutrición humana».

### Lo verdaderamente interesante del compromiso concentración × rendimiento

El genotipo CIP312767.014 tiene una concentración elevada de hierro (26,07 mg/kg seco) pero una producción fresca publicada de 0,66 kg/m². CIP312725.110 muestra concentración menor (21,60 mg/kg seco), pero mayor rendimiento (1,69 kg/m²).

La pregunta que nos interesa para seguridad alimentaria no es solo quién tiene **más mineral por kg de tubérculo seco**, sino qué material, bajo ambientes reales, proporciona más **nutrientes utilizables por hectárea, por costo y por temporada**, sin comprometer inocuidad y acceso.

Si se aplica aritméticamente:

\`\`\`text
kg de materia seca/m² = kg de tubérculos frescos/m² × (materia_seca_% / 100)
g de mineral/ha       = kg_materia_seca/m² × (mg_mineral/kg_materia_seca) × 10
\`\`\`

Ejemplos del indicador puramente teórico (no ensayo nutricional):
- CIP312767.014: ≈ **43,69 g de hierro/ha**, antes de pérdidas y sin ajuste de biodisponibilidad.
- CIP312725.110: ≈ **101,41 g de hierro/ha**, con idénticas salvedades.
- Gudanie: ≈ **74,56 g de hierro/ha** según la media registrada y el mismo cálculo.

El uso de **g/ha** deja expuesto que el indicador NO representa personas alimentadas ni requisitos humanos cubiertos. No corregimos este valor con un factor inventado de absorción.

## Restricciones de interpretación y sesgos posibles

- **Un solo sitio/año:** se desconocen estabilidad varietal, plasticidad y respuesta a otros tipos de suelo/clima.
- **Solo medias de genotipos:** no conocemos distribución por parcela y no se puede reconstruir ANOVA, error experimental, intervalos por genotipo ni significancia estadística individual con nuestro CSV.
- **Selección posterior:** elegir clones por «dominar» a otros en las medias del mismo ensayo puede sobreajustarse a Holetta. Exige validación externa.
- **Bases de peso distintas:** producción en **kg/m² fresco**; Fe y Zn en **mg/kg seco**. No comparar estos últimos con los datos del USDA (mg/100g fresco) sin una conversión, fracción comestible y preparación compatibles.
- **Límites sanitarios:** no se estudian glicoalcaloides ni disponibilidad humana para estos 45 materiales mediante este pipeline.
- **Protección intelectual:** un código CIP no garantiza disponibilidad libre, licencia de multiplicación o registro de variedad.
- **Atribución:** datos reproducidos de investigación ajena, **no** un descubrimiento experimental propio de OpenPotato.

## Próximas fuentes para genotipo × ambiente

**CIP — Perú.** [Informe de 30 clones biofortificados + 4 controles, 11 ensayos en seis departamentos](https://mel.cgiar.org/reporting/download/hash/0eca557b6b549300e315761db50c9a2e). Se identifica como fuente candidata para verificar variables y localizar **datos de campo por parcela/ambiente**. No se incorporarán números específicos mientras no exista transcripción auditable, licencia y comparabilidad.

**CIP — Programa en 26 localidades.** [Variedades CIP-Kallpa Yawri y CIP-Puka Yawri, lineamientos publicados en 2025](https://cipotato.org/publication/lineamientos-para-el-manejo-agronomico-y-fitosanitario-de-las-variedades-de-papa-biofortificadas-cip-kallpa-yawri-y-cip-puka-yawri-en-zonas-altoandinas-del-peru/). Contexto realista de liberación y adaptación. **No comparar** directamente resultados agregados de otro programa con Holetta.

**INIA Ecuador.** [Interacción genotipo × ambiente para hierro, zinc y vitamina C](https://repositorio.iniap.gob.ec/items/c692cf4a-bbad-4c2f-b6e0-13e594575d5e). Menciona ensayos en cuatro ambientes y la necesidad de considerar interacción, pero hay que recuperar observaciones por genotipo y sitio para reanálisis.

**Estrategia de adquisición:** ubicar datasets publicados que conserven cultivar, lugar, año, réplica, rendimiento, humedad/materia seca, Fe, Zn y método de laboratorio. Si los artículos incluyen solo medias agregadas, etiquetar **aggregate_only** y solicitar acceso a datos a autores/instituciones.

## Reproducir

Requiere Python 3.11+ y solo biblioteca estándar:

\`\`\`bash
curl -fsSL "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10383430/fullTextXML" -o /tmp/study.xml
PYTHONPATH=.:src python -m scripts.ethiopia_genotypes --xml /tmp/study.xml --out /tmp/study-results
PYTHONPATH=.:src python -m unittest discover -s tests -v
\`\`\`

Fuentes derivadas versionadas: [CSV de 45 genotipos](../datasets/cultivars/genotype_trial_holetta_2019.csv), [reporte generado](../datasets/cultivars/genotype_trial_report.md), [manifiesto de hashes, DOI y limitaciones](../datasets/cultivars/genotype_trial_provenance.json). La CI [M1 identified genotype trial](../.github/workflows/ethiopia-genotypes.yml) baja el artículo original y repite íntegramente la extracción.

**Decisión:** esta prueba demuestra que ya podemos trabajar con datos de materiales genéticamente identificados. Aún **no** demuestra efectos de genes específicos ni estabilidad entre ambientes. El siguiente hito científico requiere datos replicados por sitio para estimar G×E, no solo otra tabla de medias.

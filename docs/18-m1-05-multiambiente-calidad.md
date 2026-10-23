# OP-M1-05 — Ensayos de papa en múltiples ambientes: motor validado y barreras científicas

**Fecha:** 2026-10-20 · **Estado:** comprobación computacional con datos de rendimiento publicados; **no** hay aún datos por parcela sobre hierro/zinc para la misma cohorte multisitio.

## 1. Lo que pudimos ejecutar sobre datos reales

**Fuente:** G. C. C. Tai (1971), *Genotypic stability analysis and its application to potato regional trials*, Crop Science 11, 184–190, DOI [10.2135/cropsci1971.0011183X001100020006x](https://doi.org/10.2135/cropsci1971.0011183X001100020006x). Reproducción CSV en [agridat::tai.potato](https://vincentarelbundock.github.io/Rdatasets/doc/agridat/tai.potato.html), repo [Rdatasets](https://github.com/vincentarelbundock/Rdatasets).

- Archivo fuente fijado a commit `1dcc2bf5f955cc1224a3e1307256e1fe86b68dae`; Git blob `6d86e84e3bd62e94cddc7fecb62be53b5b9c9fb6`.
- **SHA-256 de CSV fuente:** `6a758579b091050f02da6a352742201a73d5e3bd7ee2c7624f2a7e9e141a9055`.
- Datos publicados: **8 genotipos × 6 ambientes (3 localidades × 2 años) = 48 MEDIAS**, medidas de tubérculos en `kg/parcela`.
- El experimento histórico fue en bloques al azar con cuatro réplicas, pero **el archivo disponible solo contiene las medias genotipo×ambiente**, no los rendimientos de parcelas individuales.
- **No se midieron hierro ni zinc en este CSV.** Su propósito es validar el procedimiento G×E, no la biofortificación.
- Las localidades se codifican NB (New Brunswick), NS (Nova Scotia) y PEI (Prince Edward Island) y los años como 65 y 66.
- **Advertencia de identidad:** la tabla descargada incluye el genotipo `F6031`, mientras la documentación descriptiva de agridat menciona `F6032`. Se conserva exactamente el código fuente **sin corregirlo arbitrariamente**. La discrepancia necesita verificación frente a la publicación original antes de promover nombres de candidatos.

## 2. Resultados computacionales reproducidos

Se calculó la descomposición algebraica de la variación de las **48 medias**, sin reconstruir réplicas individuales:

| Componente | Suma de cuadrados | % de total |
|---|---:|---:|
| Genotipo | 313,6046 | 27,6 % |
| Ambiente (localidad × año) | 536,4268 | 47,2 % |
| Residuo de interacción G×A en las medias | 286,4079 | 25,2 % |
| **Total** | **1136,4393** | **100 %** |

El análisis encontró **19 pares con inversiones de orden entre ambientes**, sobre los 28 pares de genotipos posibles. Una inversión ocurre cuando A supera a B en al menos un ambiente y B supera a A en al menos otro.

Ejemplos: `F6031` tiene 17,99 kg/parcela en media entre seis ambientes, con intervalo observado 9,87–22,37; `F5933` registra 15,35 kg/parcela, pero con amplitud 6,32–23,95. Es descriptivo y no predice desempeño futuro.

**Interpretación obligatoria:** estas proporciones de sumas de cuadrados NO son heredabilidad, significancia estadística ni prueba causal. Sin datos de parcela no puede estimarse el error residual que exige un ANOVA formal. No se calculan intervalos, valores p ni BLUPs ficticios. Tampoco existe área de parcela verificada para convertir kg/parcela a t/ha.

## 3. Qué desarrollamos

- [Motor G×E](../scripts/potato_gxe.py): CSV estricto, 8×6 balanceado, identidad de genotipos/ambientes, unidades y no imputación, suma de cuadrados comprobada por identidad, inversiones de orden y reporte explícitamente descriptivo.
- [Reporte generado](../datasets/multienvironment/gxE_report.md), [resultados derivados](../datasets/multienvironment/yield_stability.csv), [cruces de rango](../datasets/multienvironment/rank_crossovers.csv), [manifest](../datasets/multienvironment/gxE_provenance.json).
- [GitHub Actions](../.github/workflows/gxe-potato.yml): descarga versión inmutable, verifica SHA-256 **y** Git blob, ejecuta el modelo y archiva resultados. El CSV original **no** se sube al repositorio debido a incertidumbre sobre derechos de redistribución; se consulta su ubicación y versión de origen.
- [Test sintético de G×E](../tests/test_potato_gxe.py) y [test de regresión de salida real](../tests/test_tai_snapshot.py).

## 4. Próxima barrera: datos agrícolas verdaderamente comparables de Fe/Zn

Se agregó [validate_fe_zn_trial.py](../scripts/validate_fe_zn_trial.py), que **no genera datos**. Es un control de entrada para un diseño concreto: múltiples localidades, genotipos repetidos, al menos dos parcelas biológicas por genotipo×ambiente y **mediciones emparejadas en la misma parcela** de rendimiento, hierro y zinc, con tejido, procesamiento, base de peso y tamaño de parcela. Si estas condiciones no se cumplen, se rechaza el CSV.

La validación exige columnas:

`trial_id, genotype_id, location_id, season_id, block_id, plot_id, trait, value, unit, processing, tissue, plot_area_m2, source_id`

Convenciones declaradas para este diseño:
- hierro y zinc: `mg/kg_dry`, tejido `peeled_flesh`, procesamiento `raw`.
- rendimiento: `kg/plot_fresh`, tejido `whole_tuber`, procesamiento `raw`.
- área de parcela: `m²` positivos.

**Esto es una propuesta de contrato de datos para un diseño posible**, no exige que todos los ensayos científicos tengan esta organización. Los estudios que usan muestras químicas compuestas, bloques incompletos u otra jerarquía requerirán adaptadores y modelos preregistrados, **nunca duplicar analitos para aparentar emparejamiento por parcela**. Superar el contrato tampoco valida aleatorización o calidad de laboratorio: solo habilita revisión experta del diseño.

Ejecutar sobre un archivo verificado con este esquema:

```bash
PYTHONPATH=.:src python -m scripts.validate_fe_zn_trial --csv ruta/datos_verificados.csv --out ruta/calidad.json
```

No hay dataset auténtico que supere esta puerta nutricional **en el repositorio** a la fecha. Las pruebas usan CSVs sintéticos expresamente etiquetados como tales.

## 5. Fuentes multiambiente candidatas y riesgos de acceso

El [inventario](../research/multienvironment-candidates.csv) registra estado de cada conjunto, población, variable, granularidad conocida y licencia pendiente:

- CIP, Salas et al. (2021), **30 clones tetraploides y 4 testigos**, múltiples experimentos peruanos. [Reporte](https://ilcym.cipotato.org/publications/potenciales-nuevas-variedades-de-papa-biofortificada-con-altos-contenidos-de-hierro-y-zinc-para-contribuir-a-la-seguridad-alimentaria-y-nutricional-en-agricultura-familiar-alto-andina-reporte-fina/) y [metadatos de dataset CIP indexados en FAO AGRIS](https://agris.fao.org/search/en/providers/122619/records/6943c2c095dd92afa2ad69f2), que describen **9 experimentos en 5 departamentos**. Otro informe relacionado describe 11 ensayos en 6 departamentos; NO sumar ni fusionar ambos sin identificar diferencias de alcance y fuentes.
- CIP, datos específicos de hierro y zinc de [La Libertad](https://agris.fao.org/search/en/providers/122619/records/6943c2be95dd92afa2ad6983), [Huancavelica](https://agris.fao.org/search/en/providers/122619/records/6943c2c895dd92afa2ad6bb0) y [Apurímac](https://agris.fao.org/search/en/providers/122619/records/6943c2bc95dd92afa2ad692d): AGRIS indica conjuntos de datos con analíticas por XRF, pero **no se han descargado sus archivos XLS ni revisado su esquema por parcela**.
- Burgos et al. (2007), [49 variedades andinas; 37 evaluadas en dos sitios](https://cipotato.org/genebankcip/publications/iron-and-zinc-concentration-of-native-andean-potato-cultivars-from-a-human-nutrition-perspective/): evidencia de diferencias entre localidades y genotipos; se dispone de descripción, no de microdatos auditados.
- CIP ofrece [banco de mejoramiento](https://cipotato.org/genebankcip/process/breeding-lines/) y vías de acceso a materiales; el acceso a germoplasma exige acuerdos y permisos, independiente de la disponibilidad de datos.

**Estado de esta búsqueda:** localizamos conjuntos pertinentes, pero todavía NO descargamos ni verificamos una tabla de **Fe/Zn × genotipo × ambiente × parcela** apta para calcular G×E nutricional. Una URL bibliográfica o ficha AGRIS no equivale a haber obtenido microdatos.

## 6. Condiciones estrictas para hacer el siguiente análisis

1. Obtener archivos auténticos, DOI/licencia y checksum, asegurando identidad de cada cultivar/clon.
2. Distinguir diseño aleatorizado, bloques biológicos, submuestras técnicas y concentraciones de laboratorio; registrar laboratorio y métodos (p. ej. XRF).
3. Verificar base fresca/seca, tejido pelado/tubérculo completo y cualquier composición de muestras.
4. Si el archivo ofrece solo medias por localidad, calcular **descripciones**; evitar pseudo-replicación, significancia falsa o transferir el error entre estudios.
5. Si los datos son suficientes, preregistrar y revisar modelos adecuados para G, E, G×E con los experimentos originales, incluyendo validación externa.

**Decisión:** la plataforma está preparada para evaluar datasets multientorno; la investigación genética/nutricional multisitio sigue pendiente de datos apropiados. Nunca presentar un ensayo histórico de rendimiento como validación de hierro/zinc.

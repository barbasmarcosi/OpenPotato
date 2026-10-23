# OP-N1-01 — Hipótesis nutricional prioritaria: Fe y Zn absorbidos del MISMO genotipo

**Estado: preregistro de oportunidad y reanálisis de resúmenes publicados, NO resultado científico original ni afirmación de novedad mundial.**

## Pregunta falsable y diferencial

¿Podemos encontrar u obtener una **misma papa genéticamente trazable** que, comparada con un material control bajo una preparación y condición equivalentes, aporte más **hierro absorbido** y más **zinc absorbido por comida**, sin perjudicar rendimiento agrícola, seguridad (incluidas glicoalcaloides), estabilidad y accesibilidad?

Esta hipótesis es **candidata**: primero debe hacerse una búsqueda bibliográfica estructurada para determinar si el ensayo conjunto existe. La ausencia de ese material entre nuestras fuentes actuales no prueba que nadie lo haya investigado.

## Evidencia externa primaria

- [Ensayo Fe, Journal of Nutrition 2023](https://doi.org/10.1016/j.tjnut.2023.04.010), n=28 mujeres peruanas, diseño cruzado aleatorizado con isótopos estables. Por comida de 460 g: Fe total absorbido 0,35 mg en papa biofortificada frente a 0,24 mg convencional; absorción fraccional 12,1 % versus 16,6 %. Concentración medida 0,63 versus 0,31 mg/100 g. Estos son resúmenes de cohortes, no datos individuales.
- [Ensayo Zn, Journal of Nutrition 2023](https://doi.org/10.1016/j.tjnut.2023.08.028), n=37 mujeres peruanas, diseño cruzado aleatorizado con isótopos estables. Por comida de 500 g: Zn total absorbido 0,49 mg versus 0,40 mg; fraccional 20,8 % versus 25,5 %; concentración 0,48 versus 0,32 mg/100 g.
- Ambos ensayos informan mayor masa total absorbida a pesar de una **menor fracción** absorbida. No usar concentración (mg/100g) ni el porcentaje de absorción de manera aislada.
- Los estudios son **diferentes**, con tamaños muestrales distintos. El registro clínico compartido que aparezca en una fuente no constituye una prueba de mismo genotipo, misma preparación ni mismo experimento para ambos minerales.
- Datos de comparación alimentaria **por otro carril**: USDA SR Legacy abril 2018, FDC 170438 y 170440 (pulpa de papa hervida), archivos/hash ya fijados en datasets/official. La RDA y las ingestas son de mineral dietario total, NO equivalen a los mg efectivamente absorbidos de las pruebas isotópicas. La papa de esos registros USDA no se identifica como los clones utilizados en Perú.

## Métrica primaria y gates de investigación futura

**Primaria preregistrable:** diferencia de mg Fe efectivamente absorbido por comida comparando el mismo material biofortificado frente a control armonizado, idealmente mediante técnicas isotópicas adecuadas.

**Coprimaria o secundaria controlada:** diferencia de mg Zn efectivamente absorbido por comida, definiendo multiplicidad y potencia antes de reclutar. No diseñar simultaneidad de prueba sobre las medias de estudios distintos.

Secundarios y restricciones: concentración mg/100g preparado; retención por cocción, fitatos, ácido ascórbico y ácido clorogénico; trazabilidad genética y agronómica, dosis/masa consumida, seguridad y glicoalcaloides; rendimiento por hectárea y estabilidad ambiental, costos y accesibilidad. Ninguna afirmación de impacto en anemia, salud o inocuidad sin ensayo del resultado apropiado.

La siguiente acción antes de un laboratorio es establecer **búsqueda sistemática de estudios con Fe y Zn absorbidos en mismo genotipo**, y revisar factibilidad de obtener semillas/materiales, asesoramiento ético y métodos. No sustituir eso por simulaciones de clima/WOFOST.

## Entrega ejecutable

- Registro de hechos publicados: datasets/evidence/human_potato_fe_zn_absorption_2023.json.
- Script: src/openpotato/absorption_opportunity.py.
- Tests: tests/test_absorption_opportunity.py.
- Reporte regenerable: OP-N1-01 JSON y Markdown, con comparación USDA de 400 g totalmente separada de los isótopos y sin usar un índice único de bienestar nutricional.

**Criterio de cierre de N1-01:** dos fuentes primarias identificadas, cálculo de diferencias descriptivas reproducible, USDA original verificado, faltantes y límites explícitos, pruebas negativas contra mezcla de estudios o comparación ilegítima de medidas. Revisión experta externa aún no realizada.

### Qué es nuevo dentro de OpenPotato y qué no

Los artículos sobre absorción de Fe y Zn **ya estaban citados** en el [estado del arte inicial](01-estado-del-arte.md); OP-N1-01 **no los descubrió** ni generó nuevos datos humanos. Lo nuevo en esta iteración es convertirlos en un contrato de endpoints y fuentes **reproducible, comprobable por CI**, con límites de comparación, rechazos explícitos de efectos combinados y una pregunta preregistrable. Determinar si la hipótesis del mismo genotipo está realmente abierta exige la [revisión N1-02](https://github.com/barbasmarcosi/OpenPotato/issues/9).

### Decisión estadística futura a preregistrar

El estudio experimental propuesto deberá definir **antes** de recolectar nuevos resultados los efectos primarios sobre mg de Fe y Zn absorbidos por ración del **mismo genotipo y control**, sus estimandos, intervalos de confianza y corrección de multiplicidad (por ejemplo estrategia de hipótesis conjuntas o prueba secuencial), además de potencia y tamaño muestral calculados con varianza de efectos apareados obtenida de piloto legítimo. Los dos promedios publicados de estudios distintos **no** son varianzas de una diferencia emparejada ni sirven para calcular potencia de un estudio conjunto por sí solos.

Las salidas actuales permanecen en el nivel **candidate / tested elsewhere for each single nutrient / joint effect unverified**, y no autorizan resultados clínicos o ambientales.

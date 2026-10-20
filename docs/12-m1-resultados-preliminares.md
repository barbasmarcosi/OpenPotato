# OP-M1-001 — resultados preliminares verificados por CI

**Fecha:** 2026-10-20. **Evidencia de ejecución:** [GitHub Actions #39363512441](https://github.com/barbasmarcosi/OpenPotato/actions/runs/39363512441) sobre commit [3d7a1d4](https://github.com/barbasmarcosi/OpenPotato/commit/3d7a1d4e195135b801ce5b472c8bf9590a2b7083). **Estado:** modelo computacional validado técnicamente con 10 pruebas; calidad de la transcripción científica **provisional** hasta obtener fuente USDA oficial.

## Dataset

- USDA FDC SR Legacy **170438**, papa hervida en su piel, **pulpa sin sal**. Composición transcrita del espejo [WhatYouEat](https://whatyoueat.io/foods/170438) (no descarga primaria); ver [fuentes y cautelas](../datasets/SOURCES.md).
- Energía: **87 kcal/100 g** de alimento preparado.
- Dos perfiles no clínicos de 31–50 años, tabla de referencia según categoría adulta hombre/mujer, no embarazo/lactancia. No son requerimientos personales ni dietas completas.
- 200, 400, 800 g de consumo exploratorio; más un cálculo puramente energético de **2298,85 g** para 2000 kcal, **sin recomendación dietaria**.

## Primer control de 400 g

| Nutriente | Aporte en 400 g | Referencia adulto hombre 31–50 | Cobertura | Referencia adulta mujer 31–50 | Cobertura |
|---|---:|---:|---:|---:|---:|
| Hierro | 1,24 mg | 8 mg RDA | 15,5 % | 18 mg RDA | 6,9 % |
| Zinc | 1,20 mg | 11 mg RDA | 10,9 % | 8 mg RDA | 15,0 % |
| Vitamina C | 52 mg | 90 mg RDA | 57,8 % | 75 mg RDA | 69,3 % |
| Potasio | 1516 mg | 3400 mg AI | 44,6 % | 2600 mg AI | 58,3 % |
| Vitamina B12 | 0 ug publicados | 2,4 ug RDA | 0 % | 2,4 ug RDA | 0 % |
| Vitamina D | 0 ug publicados | 15 ug RDA | 0 % | 15 ug RDA | 0 % |
| Vitamina E | 0,04 mg | 15 mg RDA | 0,27 % | 15 mg RDA | 0,27 % |
| Grasa total | 0,40 g | — | — | — | — |

**Ácidos grasos esenciales:** linoleico y alfa-linolénico = **no reportados con identificación suficiente**. La presencia de valores 18:2/18:3 "undifferentiated" no justifica asignarlos a especies específicas, ni llamarlos cero.

## Qué demuestran realmente los resultados

- El **pipeline funciona**: 10 pruebas, escalabilidad lineal, perfil dependiente, unidades incompatibles rechazadas, cero vs ND, determinismo y archivos de salida verificados.
- Los datos de esta papa proporcionan un **ejemplo cuantificado de posibles limitaciones nutricionales de un alimento individual**. No demuestran la prevalencia de deficiencias en personas, la absorción de nutrientes, ni la factibilidad de biofortificación genética.
- La baja grasa total merece investigación, pero ni ella ni el aporte de proteínas permiten inferir directamente la suficiencia de ácidos grasos esenciales/aminoácidos sin perfiles y referencias apropiados.
- La adecuación a una RDA no demuestra seguridad ni completitud. AI no es umbral diagnóstico de déficit. Falta la evaluación de UL y de otras fuentes de nutrientes.
- No existe aún análisis multivarietal, de estabilidad genética, glicoalcaloides, suelo, cosecha o costos.

## Siguiente control científico

1. Obtener versión y registro primario USDA para FDC 170438 y verificar cada nutriente. Si hay diferencias, corregir y volver a ejecutar con hash actualizado.
2. Introducir una segunda preparación de papa con fuente homóloga e incluir variabilidad/incertidumbre.
3. Evaluar otras referencias de composición, incluyendo fuentes regionales; revisar qué nutrientes no están cubiertos por el modelo.
4. Analizar perfiles de ácidos grasos esenciales y aminoácidos con identificación inequívoca; no inferir de ácidos grasos genéricos.
5. Revisar por especialista las referencias por población y riesgos de interpretación. Solo después declarar cerrada M1.

## Cómo reproducir

    PYTHONPATH=src python -m unittest discover -s tests -v
    PYTHONPATH=src python -m openpotato.m1 --output reports/m1-001

[Protocolo](05-primer-experimento.md) · [Implementación](11-m1-primera-ejecucion.md) · [Limitaciones y fuentes](../datasets/SOURCES.md).

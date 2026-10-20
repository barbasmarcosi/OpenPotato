# OP-M1-001: primera implementación y análisis

**Estado: implementación inicial entregada en rama de investigación; resultados definitivos sujetos a verificación de CI y transcripción USDA oficial.**

## Reproducir

Requisito: Python >=3.11, sin instalación de dependencias ni internet.

Desde la raíz del repositorio:

    PYTHONPATH=src python -m unittest discover -s tests -v
    PYTHONPATH=src python -m openpotato.m1 --output reports/m1-001

El programa produce:
- reports/m1-001/coverage.csv — aporte, referencia, cobertura, origen y estado por nutriente/perfil/escenario;
- reports/m1-001/manifest.json — fuentes versionadas por SHA-256 y limitaciones;
- reports/m1-001/report.md — lectura humana del escenario de 400 g.

**Fuentes y advertencias detalladas:** [datasets/SOURCES.md](../datasets/SOURCES.md). El dato de papa es una **transcripción secundaria**, pendiente corroboración directa con USDA FoodData Central FDC 170438. El código funciona sin API key, descargas ni cómputo remoto; no altera el dataset de origen.

## Diseño deliberadamente acotado

La primera implementación utiliza:
- 1 referencia alimentaria: papa hervida, pulpa sin sal (87 kcal/100 g, fuente secundaria identificada);
- dos perfiles de referencia de 31 a 50 años (masculino y femenino conforme a tablas RDA/AI, sin embarazo/lactancia ni condiciones médicas);
- porciones analíticas de 200, 400 y 800 g, no recomendaciones;
- equivalencia puramente matemática con 2000 kcal: 2000*100/87 = **2298.85 g de papa hervida**;
- múltiples vitaminas y minerales, proteínas, lípidos y carbohidratos, con algunos valores críticos **no reportados**;
- sin absorción, sin límites UL, sin datos multivarietales, sin rendimiento por hectárea, sin glicoalcaloides, sin recomendación de dieta.

## Una comprobación manual independiente

Para 400 g, en los datos seleccionados:
- hierro = 0.31 mg/100g × 4 = **1.24 mg**; frente a RDA 8 mg (adulto hombre 31–50): **15.5 %**; frente a RDA 18 mg (adulta mujer 31–50): **6.9 %**.
- zinc = 0.3 mg/100g × 4 = **1.2 mg**; frente a 11 mg (hombre): **10.9 %**; frente a 8 mg (mujer): **15.0 %**.
- vitamina C = 13 mg/100g × 4 = **52 mg**; frente a 90 mg (hombre): **57.8 %**; frente a 75 mg (mujer): **69.3 %**.
- grasa total = 0.1 g/100g × 4 = **0.4 g**, **no** equivale a aporte medido de cada ácido graso esencial.
- vitamina B12 = **0 ug publicados** y vitamina D = **0 ug publicados**: son ceros del registro nutricional, no certificado de ausencia absoluta.
- ácido linoleico y alfa-linolénico: **ND** porque la fuente accesible registra 18:2 y 18:3 "undifferentiated" y no garantiza identidad de isómeros; NO imputar cero.

**Interpretación:** cantidades bajas en un alimento no diagnostican deficiencias humanas, dado que la dieta completa y la absorción varían. No se garantiza completitud nutricional de papa ni se afirma utilidad clínica.

## Criterios cubiertos y pendientes

| Criterio | Estado del código |
|---|---|
| Validación estricta de unidad | Implementada |
| Inexistentes ≠ cero | Implementada |
| Perfil y tipo de referencia explícitos | Implementados |
| No duplicar retención de cocción | Implementado por utilizar entrada directamente cocida |
| Determinismo y checksums | Implementados |
| Pruebas de escala, unidades, datos faltantes | Añadidas para ejecución por CI |
| Dos preparaciones contrastables | Pendiente |
| USDA fuente primaria descargada y auditada | **Pendiente — obligatorio antes de cerrar M1** |
| Revisión científica independiente | Pendiente |
| Biodisponibilidad medible | Pendiente, sin imputación |
| Cobertura completa de nutrientes esenciales | Pendiente |
| Datos agronómicos y optimización | Futuro M2/M3 |

**La evidencia obtenida se restringe a un modelo de aporte dietario, no una nueva variedad de papa.**

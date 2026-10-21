# M1-15 — Simulación de sensibilidad experimental

**Todo el efecto nutricional y su variación se SUPONEN para esta prueba.**
No hay datos nuevos del CIP ni predicción de una variedad verdadera.

Modelo: contraste de dos genotipos por bloques físicos emparejados,
variación genotipo×sitio e imprecisión de parcela y laboratorio.
Se calcula una prueba t de dos colas sobre contrastes de SITIOS independientes.

Escenario hipotético de alta variación genotipo×sitio (SD = 1,5 veces
la SD biológica de parcela) con tres bloques y una lectura por muestra:

| Sitios independientes | Potencia simulada | Falsos positivos simulados |
|---|---:|---:|
| 3 | 9.4% | 5.2% |
| 6 | 22.4% | 4.9% |
| 9 | 34.5% | 5.5% |

Otros 15 escenarios están en el CSV. Estos porcentajes no son 
recomendaciones de tamaño de muestra para un cultivar real, porque no
hemos medido ni calibrado la dispersión biológica, G×E o los errores.
Las réplicas técnicas no se cuentan como sitios o parcelas.

Se trata de simulación de diseño, NO de predicción de Fe/Zn, causalidad,
rendimiento agronómico, seguridad o validación experimental.

# M1-34 — Puerta de evidencia de unidades físicas y blancos W1/W2

**Estado: bloqueo científico reproducible; ningún calendario diario WOFOST autorizado.**

## Evidencia original

Dataset [ten Den et al., Harvard Dataverse v3.0](https://doi.org/10.7910/DVN/1LC6W7) licenciado **CC BY-NC-SA 4.0**, bajo el SHA-256 original Irrigation.xlsx 3def99dfb0643abe4d524431702a224bf62abd9489b306fbb89d54fdb3c9f109. Publicación [ODJAR (2024)](https://doi.org/10.18174/odjar.v10i0.18680). El artículo describe riego diario por tratamiento y lluvia, pero no identifica inequívocamente las unidades de W1/W2 o significado de blancos.

M1-32 verificó clima.RAIN en mm = 10 × columna lluvia del registro en 526/526 días; **esta escala de la LLUVIA no prueba unidades de RIEGO W1/W2**. M1-33 verificó 746 días calendario, 526 registros, 220 días sin registro, 181 celdas positivas para W1 y 250 para W2, con 565 y 496 días UNKNOWN por tratamiento. Estos UNKNOWN no son ceros inferidos.

## Control ejecutable y contrato de evidencia

El archivo scripts/wur_irrigation_provenance_gate.py consume solo agregados SHA-verificados de M1-31 y M1-33, comprueba balances, rechaza orígenes modificados, pérdida de cobertura, filas ausentes convertidas a cero y cualquier aprobación anterior falsa de WOFOST.

La fuente docs/evidence/m1-34-irrigation-semantics.json documenta **siete afirmaciones separadas**:

1. Unidad física de W1.
2. Unidad física de W2.
3. Significado de celda W1 vacía.
4. Significado de celda W2 vacía.
5. Significado de día sin fila en Irrigation.xlsx.
6. Lámina por superficie, volumen por parcela u otro denominador.
7. Eficiencia de aplicación y diferencia entre volumen registrado y agua efectiva.

Cada afirmación está explícitamente en estado UNVERIFIED, sin valor inferido. Para modificarla hay que aportar URL HTTPS de fuente primaria, SHA-256 del documento y referencia a una revisión independiente. Se valida la presencia y forma de esa información; **el código no puede autenticar por sí solo que la fuente realmente demuestre la afirmación**. Incluso si todas se documentan, NO se habilita automáticamente WOFOST: hace falta un adaptador por sitio/cultivar, manejo y fenología, con revisión científica separada.

## Pruebas y ejecución

Nueve pruebas con datos sintéticos cubren la aprobación indebida de cm, manipulación de fuente, imputación silenciosa, alteración de balances, cambios de claims y la imposibilidad de utilizar el ledger como autorización automática de WOFOST. GitHub Actions M1-29 integra M1-34 usando sólo archivos de recuentos de fuentes primarias temporalmente descargadas. El artefacto publica **metadatos y causas de bloqueo**, jamás mediciones individuales ni datos licenciados.

La [issue #8](https://github.com/barbasmarcosi/OpenPotato/issues/8) contiene las preguntas dirigidas a documentación o autores. Crear una issue NO implica haber contactado a los investigadores.

## Pendientes

Obtener evidencias independientes que resuelvan los siete puntos; continuar con perfil hidráulico de suelo, fechas fenológicas reales, parámetros de cultivar y fertilización. El año 2020 permanece reservado como holdout; no se ha ejecutado una validación WOFOST de rendimiento, ni demostrado Fe/Zn mejorado o seguridad.

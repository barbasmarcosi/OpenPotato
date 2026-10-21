# OP-M1-12 — Desviación documental entre fuentes CIP y condiciones para ensayos multientorno

**Fecha:** 2026-10-21. **Estado:** dos colecciones de resúmenes originales contrastadas automáticamente; resultado exploratorio **no inferencial**.

## 1. Resultado verificable: 29 accesiones, 58 contrastes documentales

Los **29 clones** del [catálogo CIP](https://doi.org/10.21223/P3/LQOT7Z), con concentraciones Fe/Zn en mg/kg de materia seca, también aparecen en la Tabla 12 del [dataset CIP Perú](https://doi.org/10.21223/N11QJS), que documenta 30 clones biofortificados evaluados y cuatro testigos.

El módulo [cip_peru_catalogue_contrast.py](../scripts/cip_peru_catalogue_contrast.py) realiza un join por **identificador CIP exacto**, valida los hashes SHA-256 de ambos CSV contra sus respectivos manifiestos, verifica DOI, unidad, datos faltantes y nivel de agregación, y conserva cada fuente por separado.

Hallazgo **descriptivo**:

| Mineral | Clones con valor Perú inferior al catálogo | Mediana del cociente Perú / catálogo |
|---|---:|---:|
| Hierro (Fe, mg/kg seco) | **29/29** | **0,722** |
| Zinc (Zn, mg/kg seco) | **29/29** | **0,541** |

Es una comparación entre dos **conjuntos de estadísticas publicadas**. El cociente no es un efecto estimado del ambiente, una pérdida de nutrientes demostrada, un parámetro genético ni un índice de validación externa. El catálogo y la Tabla 12 **pueden compartir material y observaciones originales**; no se ha establecido independencia de muestras, equivalencia de tejidos, cosechas, calibración analítica ni comparabilidad de sitios y años.

Por ese motivo el proyecto **NO calcula** pruebas de significancia, intervalos de confianza, tamaños de efecto causal, G×E, diferencia de rendimiento, correlaciones con Fe del suelo o recomendaciones de clones a partir del contraste.

Datos derivados trazables: [CSV](../datasets/cip_cross_source_29/peru_catalogue_29_clone_contrast.csv), [manifiesto](../datasets/cip_cross_source_29/peru_catalogue_29_clone_provenance.json), [reporte](../datasets/cip_cross_source_29/peru_catalogue_29_clone_report.md). Validación: [Actions M1-12](https://github.com/barbasmarcosi/OpenPotato/actions/runs/39540448750), 120 pruebas offline.

## 2. Nuevo dato verificado de diseño experimental

Se consultaron directamente los **metadatos públicos oficiales** de [Dataverse 10.21223/N11QJS](https://doi.org/10.21223/N11QJS), versión 1.0, mediante [el workflow de descubrimiento](https://github.com/barbasmarcosi/OpenPotato/actions/runs/39540035137).

Su descripción indica **30 clones BIOT y cuatro variedades comerciales** evaluados en **nueve ensayos de campo, cinco departamentos de Perú**, en parcelas de **40 plantas** (9,72 m²), con diseño de **bloques completos al azar y tres repeticiones por localidad**. El dataset publica **16 archivos**, entre ellos tablas de suelos, fechas, selección participativa de plantas, cronograma de muestras minerales, resumen de laboratorio, correlaciones/ANOVA de los autores y Tabla 16.

Esto documenta el **diseño del programa**, pero no demuestra que cada valor n de Tabla 12 represente una parcela: las medias y SD de Tabla 12 **no están indexadas por bloque, localidad, campaña o muestra individual**. No se pueden crear 30 × 9 × 3 observaciones químicas a partir de esta descripción ni emparejarlas con datos de suelos por localidad sin claves originales.

### Fuentes públicas para revisar después

| Archivo CIP | Contenido según metadatos | Límite actual |
|---|---|---|
| 6972 | Fechas de siembra, aporque y evaluaciones | No demuestra Fe/Zn individual por parcela |
| 6971 y 6968 | Preferencias y selección participativa *por parcela* en floración y cosecha | Voto/preferencia no son análisis minerales ni rendimiento en cada parcela |
| 6982 | Cronograma de envío de muestras liofilizadas para minerales | Es agenda logística, no resultado químico por muestra |
| 6983 | Correlaciones, intervalos y ANOVA publicados | Estadísticos del autor, no réplicas para reanálisis |
| 6980 | Tabla 12, 34 materiales | Agregados Fe/Zn por clon, no matriz nutricional G×E |
| 6979 | Tabla 16, 14 materiales | Subconjunto exacto de Tabla 12, no nuevo ensayo |

Existen datasets departamentales XRF marcados como **restricted** en otros DOI del CIP; no intentar descargar esos archivos sin autorización válida. La ausencia de un diccionario autónomo explícito entre los **16 nombres de archivos** del dataset público impide por ahora concluir la semántica experimental exacta de todas las variables.

## 3. Productividad y seguridad: precisión antes de combinar

Las [instrucciones CIP para ensayos de rendimiento](https://cipotato.org/wp-content/uploads/2014/09/006183.pdf) definen el código **TTYNA** como *rendimiento total de tubérculos sin ajustar*, en **toneladas/ha**. Sin embargo, hay que confirmar que el procesamiento del archivo 6980 utilizó **esa misma definición, protocolo y denominador**. La Tabla 12 también incluye **TglyFW** (glicoalcaloides en peso fresco según nomenclatura) sin que el campo de exportación declare de modo inequívoco unidad y técnica de ensayo.

**Decisión de calidad M1-12:** no transformar TTYNA en rendimiento por superficie validado para los clones, ni comparar TglyFW con umbrales sanitarios, hasta verificar diccionario/metodología originales y la estructura de las muestras. El [estudio de selección participativa de Gastelo et al. (2021)](https://doi.org/10.1007/s11540-021-09495-z) reporta unidades mg/100 g fresco para glicoalcaloides en **otro experimento**: usarlo como unidad de la Tabla 12 sin confirmación sería una extrapolación incorrecta. Los análisis de inocuidad deben considerar procesamiento, almacenamiento, heterogeneidad de muestras y los criterios reguladores pertinentes.

## 4. Solicitud de datos científicos: campos necesarios

Solicitar al Centro Internacional de la Papa por los canales legítimos indicados en los metadatos, con propósito de investigación abierta y **sin presuponer permiso de redistribución**:

- Identificación de **genotipo / accesión, sitio, departamento, fecha de siembra y cosecha, campaña/año, bloque, tratamiento, parcela y réplica biológica**.
- Relación entre **ID de muestra liofilizada, tubérculos muestreados, parcela, método XRF/ICP-MS, laboratorio/calibración, Fe/Zn y límites de detección**, indicando base seca/fresca.
- **Rendimiento por parcela**, área efectiva cosechada, ajuste/no ajuste, densidad, porcentaje de materia seca, condiciones de manejo, unidades y diccionario de TTYNA.
- **Glicoalcaloides totales/individuales**, técnica, unidad mg/kg o mg/100 g, tejido, peso fresco/seco, controles de calidad y fecha/condiciones de almacenamiento.
- Procedencia estadística del **catálogo de 29 clones** y grado de independencia frente a Tablas 12 y 16; origen de cada media/rango/n.
- Versión, licencia y restricciones de uso, posibilidades de acceso y de publicación de **derivados agregados**, sin redistribuir microdatos confidenciales o restringidos.

## 5. Criterio de aceptación para un futuro G×E nutricional

El siguiente análisis inferencial requiere una clave comprobada de **genotipo × sitio-año × bloque/parcela × medición química**, con replicación auténtica suficiente, método de laboratorio auditado, rangos plausibles, cobertura de faltantes y control de unidades. Solo entonces podrá diseñarse un modelo jerárquico con componentes de variación G, E y G×E en vez de reutilizar SD de publicaciones como varianza residual.

Además se requieren evaluaciones de rendimiento, resistencia, glicoalcaloides, aceptabilidad, bioaccesibilidad humana, costo y permisos de uso para seleccionar materiales con impacto real. Ningún indicador aislado de concentración de Fe/Zn establece que exista ya una nueva variedad superior o segura.

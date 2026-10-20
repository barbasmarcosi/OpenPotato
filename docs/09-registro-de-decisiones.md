# Registro de decisiones de OpenPotato

Decisiones fundacionales registradas el 2026-10-19. Se revisarán frente a evidencia nueva.

## OP-ADR-001 — Investigación abierta y finalidad humanitaria

**Estado: aceptada como misión.** El éxito se mide por valor nutricional real, seguridad, accesibilidad y reproducibilidad; la visibilidad del proyecto no constituye evidencia científica.

## OP-ADR-002 — Enfocar primero el problema nutricional medible

**Estado: aceptada.** La primera ejecución será un modelo computacional que caracterice las brechas por nutriente y perfil poblacional, no una simulación de ingeniería genética. Motivo: sin especificar qué mejorar y por cuánto, el trabajo molecular carece de criterio objetivo de impacto.

## OP-ADR-003 — No perseguir monocultivo o dieta exclusiva

**Estado: aceptada.** Un alimento biofortificado complementa la diversidad de dieta y producción. Siempre se compara con alternativas reales.

## OP-ADR-004 — Evidencia estratificada y reproducible

**Estado: aceptada.** Diferenciar siempre evidencia in vitro, humana, de campo, de laboratorio, simulación e hipótesis; conservar fuentes y límites. No traducir estructura de proteínas o expresión genética directamente a beneficios nutricionales.

## OP-ADR-005 — Prioridad científica preliminar

**Estado: provisional.** Explorar hierro, zinc y provitamina A antes de perfiles de lípidos/proteínas y otras vías, por contar con evidencia inicial relevante. El orden cambiará cuando M1 demuestre cuáles son los cuellos de botella más importantes para poblaciones objetivo.

## OP-ADR-006 — Licenciamiento responsable

**Estado: pendiente.** Publicar el proyecto no equivale a declarar licencia de reutilización. Definir una política de licencia después de inventariar derechos de terceros.

## OP-ADR-007 — Colaboraciones transparentes

**Estado: aceptada.** Se pueden identificar investigadores e instituciones potenciales por sus publicaciones; no se anunciarán alianzas sin consentimiento y confirmación.

## OP-ADR-008 — No contratar infraestructura prematuramente

**Estado: aceptada.** Comenzar con modelos y datasets manejables en Python y entornos gratuitos. Invertir en cómputo especializado solo si hay hipótesis concreta, necesidad justificada, recursos y términos de uso compatibles.

## OP-ADR-009 — Registro público de incertidumbre

**Estado: aceptada.** Reportar resultados negativos, valores faltantes y fallos del modelo; ninguna cifra sin unidad, base, versión y fuente.

## OP-ADR-010 — Stack científico incremental

**Estado: aceptado para M1, condicionado para M2/M3.** No comprometer el proyecto prematuramente con AlphaFold, COBRApy, modelos generativos, GPUs o una arquitectura de aplicaciones compleja. Priorizar datos, reproducibilidad, nutrición y optimización sencilla. Seleccionar herramientas biológicas solo a partir de hipótesis respaldadas por evidencia; distinguir AlphaFold DB (CC BY 4.0) de AlphaFold 3 Server (restricciones adicionales). Ver [evaluación técnica](10-herramientas-y-metodologia.md).

## Pendientes para primera revisión

- Población y zona geográfica concreta de la primera línea base.
- Cultivar y preparación de referencia de M1 (dependerá de datos comparables).
- Políticas de licencia de código/documentación/datos.
- Revisión de licencias de modelos biomoleculares y repositorios externos.


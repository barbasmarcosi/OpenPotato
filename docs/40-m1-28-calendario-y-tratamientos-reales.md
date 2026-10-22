# M1-28 — Dutch potato real planting and plot-treatment admission gate

**Implemented:** source-verified, read-only planting-date and management-label audit. **Not a calibrated WOFOST simulation.**

## Primary provenance
Ten Den et al. (2024), Harvard Dataverse v3, DOI https://doi.org/10.7910/DVN/1LC6W7, licensed CC BY-NC-SA 4.0. Original plot CSV byte hash locked by M1-19; licensed plot records never uploaded. Published Table 3 in https://doi.org/10.18174/odjar.v10i0.18680 (journal article CC BY 4.0) supplies site-year planting dates:
- Lelystad: 25 April 2019 and 20 April 2020.
- Vredepeel: 18 April 2019 and 21 April 2020.

## Implemented constraints
The script scripts/wur_agromanagement_admission.py verifies source identity, 1,824 records, site-year balance, stable cultivar/N/water treatment per biological plot across repeated visits, uniqueness of year × site × plot × date, planting-before-sample, positive dry-tuber mass in each plot at the actual final sampled day, and 45/42 physical plots per location and year. It exports only safe group counts per site-year; no source plot identifier, field mass, individual treatment or original rows. The holdout 2020 is never used to estimate parameters.

**Scientific distinctions that block premature WOFOST claims:** a planting date is NOT cultivar-specific emergence; the last sampled date is NOT necessarily commercial harvest; categorical N and irrigation assignments are NOT time-stamped nutrient and water applications; a texture label is not a calibrated soil hydraulic profile. Cultivar codes C1–C6 must not be assigned to named varieties without checking the original dictionary. Field WOFOST parameters and event schedules remain unverified; the gate returns real_wofost_field_simulation_admissible=false.

## Next stage
Audit original irrigation event workbook and dictionary for water dose in mm, date, site-year/plot linkage. Check original cultivar code mapping against published emergence phenology and retrieve site-specific soil hydraulic parameters, without replacing unknown values with DummySoilDataProvider or generic Potato_701. Only then consider a 2019-only WOFOST development run before touching held-out 2020 field outcome data.

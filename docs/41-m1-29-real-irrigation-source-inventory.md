# M1-29 — Direct source discovery for original irrigation workbook

Source: ten Den et al. (2024), Harvard Dataverse 3.0 DOI https://doi.org/10.7910/DVN/1LC6W7, original Irrigation.xlsx, Dataverse file 10284791, CC BY-NC-SA 4.0.

The M1-28 workflow independently identified this openly accessible workbook in Dataverse metadata along with Waterpotential.xlsx (10284794), Groundwaterlevel.xlsx (10284788), Plotspecific_processed_meta.xlsx (10850226) and Penetrologger.xlsx (10284793). These are source **inventory facts** rather than proof of complete model parameters.

The M1-29 script inspects the original Irrigation.xlsx in transient memory and reports only worksheet dimensions, aggregate date-like and numeric cell counts, and controlled keyword clues such as date, irrigation or physical plot. It NEVER exports source cell values, header text, raw event dates, individual doses or plot identifiers. Any unverified claim that an event is measured in mm or that it joins specific experimental plots must remain FALSE.

Before using event observations as WOFOST irrigation schedules, independently pin SHA256 of this original, verify workbook column dictionary (units, site/year/date/plot/treatment), check treatment assignment against 174 plot-years without joining rows incorrectly, and preserve 2020 as held-out. Soil hydraulic and cultivar parameter calibration remain unresolved. The dataset is CC BY-NC-SA; no source workbook is committed, uploaded or distributed.

This is a data discovery and access admission milestone, NOT WOFOST validation, not evidence of increased bioavailable Fe/Zn or crop improvement.

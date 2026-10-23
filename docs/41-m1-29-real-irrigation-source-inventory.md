# M1-29 — Direct source discovery for original irrigation workbook

Source: ten Den et al. (2024), Harvard Dataverse 3.0 DOI https://doi.org/10.7910/DVN/1LC6W7, original Irrigation.xlsx, Dataverse file 10284791, CC BY-NC-SA 4.0.

The M1-28 workflow independently identified this openly accessible workbook in Dataverse metadata along with Waterpotential.xlsx (10284794), Groundwaterlevel.xlsx (10284788), Plotspecific_processed_meta.xlsx (10850226) and Penetrologger.xlsx (10284793). These are source **inventory facts** rather than proof of complete model parameters.

The M1-29 script inspects the original Irrigation.xlsx in transient memory and reports only worksheet dimensions, aggregate date-like and numeric cell counts, and controlled keyword clues such as date, irrigation or physical plot. It NEVER exports source cell values, header text, raw event dates, individual doses or plot identifiers. Any unverified claim that an event is measured in mm or that it joins specific experimental plots must remain FALSE.

## First verified result from the primary XLSX

[GitHub Action M1-29, authoritative download and source MD5](https://github.com/barbasmarcosi/OpenPotato/actions/runs/39716880775) succeeded. The original source SHA256 is now pinned in code as **3def99dfb0643abe4d524431702a224bf62abd9489b306fbb89d54fdb3c9f109**. This digest is checked against the bytes downloaded through the official Harvard API.

- Metadata worksheet: 17 rows, 3 columns. The controlled vocabulary found possible irrigation/treatment labels, not verified definitions.
- Data worksheet: 527 rows, 6 columns. There are 258 typed/ISO 2019-date cells and 268 2020-date cells. They are **date-like cells, not 526 confirmed independent watering events**, as year/location/plot/dose mapping has not been validated.
- Metadata observed two sheets named meta and data; this does not by itself establish complete event-level treatment mapping.

The preceding source inventory also identified water potential, groundwater and penetrometer files. A matching source data file and unit definitions must be checked before forming an irrigation schedule for 2019 training, let alone assessing 2020.

Before using event observations as WOFOST irrigation schedules, maintain the pinned SHA256 and verify workbook column dictionary (units, site/year/date/plot/treatment), check treatment assignment against 174 plot-years without joining rows incorrectly, and preserve 2020 as held-out. Soil hydraulic and cultivar parameter calibration remain unresolved. The dataset is CC BY-NC-SA; no source workbook is committed, uploaded or distributed.

This is a data discovery and access admission milestone, NOT WOFOST validation, not evidence of increased bioavailable Fe/Zn or crop improvement.

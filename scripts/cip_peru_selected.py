"""CIP Peru nine-sites SELECTED CLONE published summary table (NOT plot data).

Source: CIP Dataverse doi:10.21223/N11QJS (dataset 1.0), public
tabular file 6979 ("Tabla 16"). Dataverse API returns a TSV export
whose checksum differs from original storage checksum; the export
SHA-256 is pinned, and original Dataverse file metadata MD5 retained.
No environmental replication reconstructed, no ANOVA, no G×E inference.
"""
import argparse,csv,hashlib,json,re
from decimal import Decimal,InvalidOperation
from pathlib import Path

DOI="10.21223/N11QJS"
API="https://data.cipotato.org/api/access/datafile/6979"
FILE_ID=6979
PUBLIC_SHA="39843e2d1cea114ee18f32e9cd40219c14a8ff32a70ea737bb6438ee609e9dc8"
EXPORT_MD5="03b886a403f6f313179e19852f4f5724"
DATAVERSE_STORED_MD5="170766ab8217f2b6d38f62c646616268"
MAPPING=[
    ("iron","nFEDW","MeanFEDW","SdFEDW","MinFEDW","MaxFEDW","mg/kg_dry"),
    ("zinc","nZNDW","MeanZNDW","SdZNDW","MinZNDW","MaxZNDW","mg/kg_dry"),
]
FIELDS=["accession","breeder_code","nutrient","unit","reported_n",
        "published_mean","published_sd","published_min","published_max",
        "source_doi","data_level"]
EXPECTED_ROWS=17


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def value(s,*,field,allow_zero=False):
    if s is None or str(s).strip()=="":
        raise ValueError(f"{field}: missing does not mean zero")
    try: val=Decimal(str(s))
    except (ValueError,InvalidOperation) as exc:raise ValueError(f"Invalid {field}") from exc
    if not val.is_finite() or val<0 or (not allow_zero and val==0):
        raise ValueError(f"Invalid {field}: {s}")
    return val


def transform(path:Path,output:Path,pinned_sha=PUBLIC_SHA):
    path=Path(path)
    if sha256(path)!=pinned_sha:
        raise ValueError("CIP Dataverse TSV export SHA-256 changed; audit first")
    with path.open(encoding="utf-8-sig",newline="") as f:
        rdr=csv.DictReader(f,delimiter="\t")
        headers=rdr.fieldnames or []
        required={"INSTN","BREEDERCODE"}
        for _,n,mean,sd,low,high,_ in MAPPING:required|={n,mean,sd,low,high}
        if not required<=set(headers):raise ValueError(f"Missing source statistical columns: {required-set(headers)}")
        source=list(rdr)
    if len(source)!=EXPECTED_ROWS:
        raise ValueError(f"Expected {EXPECTED_ROWS} rows from published selected-clone table, got {len(source)}")
    # The final three records in the public table are statistical footer
    # lines labelled Mean, Max, Min — NOT additional genotypes.
    footers=source[-3:]
    if [(r["INSTN"].strip(),r["nFEDW"].strip(),r["nZNDW"].strip()) for r in footers]!=[
        ("","Mean","Prom"),("","Max","Max"),("","Min","Min")]:
        raise ValueError("Unexpected CIP Table 16 footer layout")
    clone_entries=source[:-3]
    if len(clone_entries)!=14:
        raise ValueError("Expected 12 selected clones and two reference varieties")
    used=set();rows=[]
    for i,entry in enumerate(clone_entries,2):
        accession=entry["INSTN"].strip()
        if not accession or accession in used:raise ValueError("Duplicate or empty accession in Table 16")
        used.add(accession)
        code=entry["BREEDERCODE"].strip()
        for label,n,mean,sd,low,high,unit in MAPPING:
            count=value(entry[n],field=f"{accession} {label} n")
            if count != int(count) or count>10000:raise ValueError("Invalid count")
            m=value(entry[mean],field=f"{accession} {label} mean")
            lo=value(entry[low],field=f"{accession} {label} min")
            hi=value(entry[high],field=f"{accession} {label} max")
            sdval=value(entry[sd],field=f"{accession} {label} SD",allow_zero=True)
            if not lo<=m<=hi:raise ValueError(f"Unordered source summaries: {accession} {label}")
            rows.append({
                "accession":accession,"breeder_code":code,"nutrient":label,"unit":unit,
                "reported_n":str(int(count)),"published_mean":str(m),
                "published_sd":str(sdval),"published_min":str(lo),"published_max":str(hi),
                "source_doi":DOI,"data_level":"published_multi_location_aggregate",
            })
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    csvpath=output/"peru_selected_aggregate_fe_zn.csv"
    with csvpath.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(rows)
    report={
        "source_doi":DOI,"dataverse_version":"1.0","file_id":FILE_ID,
        "api_download_url":API,
        "datafile_stored_md5":DATAVERSE_STORED_MD5,
        "dataverse_tsv_export_md5":EXPORT_MD5,
        "dataverse_tsv_export_sha256":sha256(path),
        "derived_csv_sha256":sha256(csvpath),
        "accessions":len(used),"nutrient_rows":len(rows),
        "trait_units":{"iron":"mg/kg dry","zinc":"mg/kg dry"},
        "source_table":"Tabla 16; 12 selected CIP clones + 2 commercial controls; 3 footer summary rows excluded",
        "non_accession_summary_rows_excluded":3,
        "prohibitions":[
            "The final three source rows are global Mean/Max/Min footers, not accessions.",
            "Reported n may represent pooled observations; biological plot independence not established.",
            "Mean/sd/min/max are PUBLISHED aggregate statistics, not raw replicates.",
            "No p-values, inferential G×E effects or cultivar stability can be recomputed from this dataset.",
            "Other table columns (TTYNA, glycoalkaloids) omitted pending variable dictionary verification.",
            "Do not combine with other populations as matched experimental cohorts.",
            "API TSV export hash differs from stored Dataverse MD5; both recorded explicitly.",
        ]
    }
    (output/"peru_selected_provenance.json").write_text(
        json.dumps(report,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
    lines=[
        "# CIP Perú: tabla pública de selección de clones (resúmenes minerales)",
        "",
        f"Fuente [DOI {DOI}](https://doi.org/{DOI}), versión 1.0, fichero Dataverse {FILE_ID}.",
        f"Se extrajeron **{len(used)} accesiones y {len(rows)} registros mineral × accesión**.",
        "Son **medias, desviaciones estándar y rangos publicados** en Tabla 16;",
        "**NO** datos de parcela, ni datos G×E replicables.",
        "",
        "| Accesión | Fe medio mg/kg seco | n Fe | Zn medio mg/kg seco | n Zn |",
        "|---|---:|---:|---:|---:|",
    ]
    index={a:{} for a in used}
    for r in rows:index[r["accession"]][r["nutrient"]]=r
    for key in sorted(index):
        m=index[key]
        lines.append(
            f'| {key} | {m["iron"]["published_mean"]} | {m["iron"]["reported_n"]} | '
            f'{m["zinc"]["published_mean"]} | {m["zinc"]["reported_n"]} |'
        )
    lines += [
        "",
        "n publicado **no permite concluir** independencia por parcela o por sitio;",
        "sd es dispersión de la tabla, no intervalo de confianza.",
        "Ninguna inferencia causal/genética ni prueba de estabilidad multientorno está justificada.",
        "Rendimiento y glicoalcaloides no se interpretan sin verificar la ontología/unidades.",
        "",
        "Publicación y datos: https://doi.org/10.21223/N11QJS",
        f"SHA-256 de la exportación TSV: {sha256(path)}"
    ]
    (output/"peru_selected_report.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--tsv",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    print(json.dumps(transform(args.tsv,args.out),ensure_ascii=False,indent=2))


if __name__=="__main__":main()

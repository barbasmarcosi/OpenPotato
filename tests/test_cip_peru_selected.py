"""Synthetic published summary rows; never inferred plot observations."""
import csv,tempfile,unittest
from pathlib import Path
from scripts.cip_peru_selected import transform,sha256,EXPECTED_ROWS,MAPPING


def fixture(path,alter=None):
    header=["INSTN","BREEDERCODE"]
    for _,n,m,s,lo,hi,_ in MAPPING:header += [n,m,s,lo,hi]
    rows=[]
    for i in range(EXPECTED_ROWS-3):
        values={"INSTN":f"CIP{312600+i:06d}.001","BREEDERCODE":f"BIOT-{i}"}
        for label,n,m,s,lo,hi,unit in MAPPING:
            values.update({n:"8",m:"20.4",s:"2.1",lo:"15",hi:"30"})
        rows.append(values)
    # Footers are global summary labels, not clone data.
    for fe_label,zn_label in (("Mean","Prom"),("Max","Max"),("Min","Min")):
        footer={field:"" for field in header}
        footer["nFEDW"]=fe_label
        footer["nZNDW"]=zn_label
        rows.append(footer)
    if alter:alter(rows)
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=header,delimiter="\t");w.writeheader();w.writerows(rows)


class SelectedPublicSummaryTests(unittest.TestCase):
    def test_export_normalization_has_no_plot_data(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"source.tsv";fixture(path)
            meta=transform(path,Path(td)/"out",pinned_sha=sha256(path))
            self.assertEqual(meta["accessions"],14)
            self.assertEqual(meta["nutrient_rows"],28)
            with (Path(td)/"out"/"peru_selected_aggregate_fe_zn.csv").open() as f:
                rows=list(csv.DictReader(f))
            self.assertTrue(all(r["data_level"]=="published_multi_location_aggregate" for r in rows))
            self.assertEqual(rows[0]["published_sd"],"2.1")

    def test_duplicate_accession_refused(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"source.tsv"
            fixture(path,lambda r:r[1].__setitem__("INSTN",r[0]["INSTN"]))
            with self.assertRaisesRegex(ValueError,"Duplicate"):
                transform(path,Path(td)/"out",pinned_sha=sha256(path))

    def test_zero_sample_count_refused(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"source.tsv"
            fixture(path,lambda r:r[0].__setitem__("nFEDW","0"))
            with self.assertRaisesRegex(ValueError,"Invalid"):
                transform(path,Path(td)/"out",pinned_sha=sha256(path))

    def test_min_max_conflict_refused(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"source.tsv"
            fixture(path,lambda r:r[0].__setitem__("MinZNDW","33"))
            with self.assertRaisesRegex(ValueError,"Unordered"):
                transform(path,Path(td)/"out",pinned_sha=sha256(path))

    def test_unverified_export_checksum_refused(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"source.tsv";fixture(path)
            with self.assertRaisesRegex(ValueError,"SHA-256"):
                transform(path,Path(td)/"out")

if __name__=="__main__":unittest.main()

"""Synthetic 29-clone records: no scientific conclusions from fake values."""
import unittest
from copy import deepcopy
from scripts.cip_clone_catalog import HEADERS,parse_catalog,N_CLONES


def fixture():
    values=[]
    for i in range(29):
        r=[""]*len(HEADERS)
        r[0]=f"CIP{312600+i:06d}.001"
        r[1]=f"BIOT-{i}"
        r[3]="CIP391058.175";r[4]="CIP306416.68"
        r[14]="MR";r[15]="R";r[23]="Tasteful"
        r[16]=0.50+0.01*i
        r[19]=22
        r[24]=30 if i%2==0 else ""
        r[25]=20+i/5
        r[26]=18
        r[27]=30
        r[28]=17+i/5
        r[29]=15
        r[30]=25
        values.append(r)
    return values


class CatalogTests(unittest.TestCase):
    def test_normalization_preserves_29_unique_accessions(self):
        result=parse_catalog(HEADERS,fixture())
        self.assertEqual(len(result),N_CLONES)
        self.assertEqual(len({r["accession_id"] for r in result}),29)
        self.assertIn("false",{r["pareto_yield_fe_zn"] for r in result})
        self.assertEqual(result[1]["vitamin_c_status"],"not_reported")
        self.assertEqual(result[1]["vitamin_c_mg_per_100g_dry"],"")
        self.assertEqual(result[0]["iron_mg_per_kg_dry"],"20")

    def test_rejects_changed_scientific_headers(self):
        header=HEADERS.copy();header[25]="Fe (mg/kg, fresh weight basis)"
        with self.assertRaisesRegex(ValueError,"columns changed"):
            parse_catalog(header,fixture())

    def test_invalid_range_rejected(self):
        data=fixture();data[0][26]=99
        with self.assertRaisesRegex(ValueError,"minimum/mean/maximum"):
            parse_catalog(HEADERS,data)

    def test_duplicate_clone_rejected(self):
        data=fixture();data[1][0]=data[0][0]
        with self.assertRaisesRegex(ValueError,"Duplicate"):
            parse_catalog(HEADERS,data)

    def test_missing_mineral_cannot_be_silently_zero(self):
        data=fixture();data[0][25]=""
        with self.assertRaisesRegex(ValueError,"unexpectedly missing"):
            parse_catalog(HEADERS,data)

    def test_negative_yield_rejected(self):
        data=fixture();data[0][16]=-1
        with self.assertRaisesRegex(ValueError,"positive finite"):
            parse_catalog(HEADERS,data)

    def test_no_external_site_count_is_assumed(self):
        results=parse_catalog(HEADERS,fixture())
        self.assertTrue(all(r["data_level"]=="catalogue_clone_summary" for r in results))


if __name__=="__main__":
    unittest.main()

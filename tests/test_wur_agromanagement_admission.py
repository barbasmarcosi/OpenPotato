"""Only wholly invented plots, never real WUR rows."""
import unittest
from datetime import timedelta
from scripts import wur_agromanagement_admission as m
def invented():
    result=[]
    for (yr,site),plant in m.PLANT.items():
        for plot,n,ir in (("FAKE-P1","N0","W0"),("FAKE-P2","N1","W1")):
            for day in (plant+timedelta(days=50),m.LAST_SAMPLE[yr,site]):
                result.append({"Year":yr,"Location":site,"Plotnumber":plot,
                    "Date":day.isoformat(),"Cultivar":"FAKE-C",
                    "Nitrogen":n,"Irrigation":ir,
                    "tubersDW":"900" if day==m.LAST_SAMPLE[yr,site] else "NA"})
    return result
class ManagementGateTests(unittest.TestCase):
    def test_private_data_stays_private(self):
        report=m.inspect_rows(invented())
        self.assertEqual(len(report["site_year_aggregates"]),4)
        self.assertFalse(report["real_wofost_field_simulation_admissible"])
        self.assertFalse(report["licensed_source_verified"])
        for private in ("FAKE-P1","FAKE-C","\"N0\"","\"W1\"","\"900\""):
            self.assertNotIn(private,str(report))
    def test_original_table3_planting_anchors(self):
        self.assertEqual(m.PLANT["2019","L"].isoformat(),"2019-04-25")
        self.assertEqual(m.PLANT["2020","V"].isoformat(),"2020-04-21")
    def test_duplicate_plot_date_rejected(self):
        a=invented();a.append(dict(a[0]))
        with self.assertRaisesRegex(ValueError,"Duplicate"):m.inspect_rows(a)
    def test_unstable_treatment_rejected(self):
        a=invented();a[0]["Nitrogen"]="N_CHANGED"
        with self.assertRaisesRegex(ValueError,"changed management"):m.inspect_rows(a)
    def test_preplant_visit_rejected(self):
        a=invented();a[0]["Date"]="2019-03-01"
        with self.assertRaisesRegex(ValueError,"before published"):m.inspect_rows(a)
    def test_terminal_plot_missing_rejected(self):
        a=invented()
        a=[r for r in a if not (r["Year"]=="2019" and r["Location"]=="L" and r["Plotnumber"]=="FAKE-P1" and r["Date"]=="2019-10-31")]
        with self.assertRaisesRegex(ValueError,"Missing terminal"):m.inspect_rows(a)
    def test_malformed_and_negative_yield(self):
        a=invented();a[0]["Date"]="31/05/2019"
        with self.assertRaisesRegex(ValueError,"Invalid plot observation"):m.inspect_rows(a)
        a=invented();a[1]["tubersDW"]="-900"
        with self.assertRaisesRegex(ValueError,"Negative"):m.inspect_rows(a)
    def test_missing_site_year_rejected(self):
        a=[r for r in invented() if r["Year"]!="2020"]
        with self.assertRaisesRegex(ValueError,"Missing site-year"):m.inspect_rows(a)
    def test_strict_refuses_fake_source_size(self):
        with self.assertRaisesRegex(ValueError,"row totals"):m.inspect_rows(invented(),strict=True)
if __name__=="__main__":unittest.main()

"""M1-31 tests: invented headers, invented water amounts, invented plots only."""
import csv,io,unittest
from datetime import date,timedelta
from unittest.mock import patch
from scripts import wur_irrigation_event_admission as mod

class Sheet:
 def __init__(self,rows):self.rows=rows
 def iter_rows(self,min_row=1,max_row=None,values_only=True):
  return iter(self.rows[min_row-1:max_row])

def source_sheet():
 meta=[(None,None,None)]*17
 meta[14]=("Daily rainfall",None,"Rain amount")
 meta[15]=("Irrigation W1",None,"W1 irrigation")
 meta[16]=("Irrigation W2",None,"W2 irrigation")
 data=[("Location","Year","Date","rainfall","irrigation W1","irrigation W2")]
 for y in (2019,2020):
  for day in range(130):
   for site in ("Lelystad","Vredepeel"):
    d=date(y,5,1)+timedelta(days=day)
    data.append((site,y,d,0.0 if day%3 else 4.,
                 None if day%2 else 5., None if day%5 else 6.))
 data=data[:527]
 return Sheet(meta),Sheet(data)

def fictional_plots():
 b=io.StringIO()
 writer=csv.DictWriter(b,fieldnames=["Year","Location","Plotnumber","Irrigation"])
 writer.writeheader()
 for year in (2019,2020):
  for site,n in (("L",45),("V",42)):
   for x in range(n):
    for _ in range(2):
     writer.writerow({"Year":year,"Location":site,
                      "Plotnumber":"SYNTH-P"+str(x),
                      "Irrigation":"W1" if x%2 else "W2"})
 return b.getvalue().encode()

class EvidenceTests(unittest.TestCase):
 def test_metadata_and_data_must_agree_on_named_columns(self):
  m,d=source_sheet()
  verified,units,clues=mod.safe_source_signatures(m,d)
  self.assertEqual([verified[k]["data_column_one_based"] for k in ("rainfall","W1","W2")],[4,5,6])
  self.assertEqual(units,"AMBIGUOUS_OR_UNSPECIFIED")
  self.assertEqual(clues,[])
 def test_explicit_mm_can_be_recognized_but_not_invented(self):
  m,d=source_sheet()
  m.rows[15]=("Irrigation W1 (mm)",None,"W1 irrigation")
  m.rows[16]=("Irrigation W2 (mm)",None,"W2 irrigation")
  _,u,_=mod.safe_source_signatures(m,d)
  self.assertEqual(u,"explicit_mm")
 def test_wrong_header_fails_closed(self):
  m,d=source_sheet()
  d.rows[0]=(d.rows[0][0],*d.rows[0][1:4],"irrigation W2","irrigation W1")
  with self.assertRaisesRegex(ValueError,"data header"):
   mod.safe_source_signatures(m,d)
 def test_wrong_meta_treatment_fails_closed(self):
  m,d=source_sheet()
  m.rows[16]=("Irrigation W1",None,"W2 irrigation")
  with self.assertRaisesRegex(ValueError,"mismatch"):
   mod.safe_source_signatures(m,d)
 def test_missing_not_zero(self):
  rows=[("Location","Year","Date","rainfall","irrigation W1","irrigation W2")]
  rows += [("Lelystad",2019,date(2019,5,1),0,None,12)]
  with self.assertRaisesRegex(ValueError,"counts changed"):
   mod.inspect_event_candidates(rows)
 def test_plot_labels_join_without_accessing_any_biomass(self):
  with patch.object(mod.plotsource,"inspect_original",return_value=None):
   n=mod.inspect_plot_assignments(fictional_plots())
  self.assertEqual(sum(sum(c.values()) for c in n.values()),174)
  self.assertEqual(n[2019,"L"]["W1"]+n[2019,"L"]["W2"],45)
 def test_unknown_plot_treatment_rejected(self):
  content=fictional_plots().decode().replace("W1","W9")
  with patch.object(mod.plotsource,"inspect_original",return_value=None):
   with self.assertRaisesRegex(ValueError,"Unmatched"):
    mod.inspect_plot_assignments(content.encode())
 def test_sha_gate_fires_before_excel_parser(self):
  with self.assertRaisesRegex(ValueError,"irrigation SHA256"):
   mod.audit(b"NOT_IRRIGATION",b"NOT_PLOT_CSV")
 def test_float_nan_water_rejected(self):
  rows=[("Location","Year","Date","rainfall","irrigation W1","irrigation W2"),
        ("Lelystad",2019,date(2019,5,1),float("nan"),0.,2.)]
  with self.assertRaisesRegex(ValueError,"Invalid or negative"):
   mod.inspect_event_candidates(rows)

if __name__=="__main__":unittest.main()

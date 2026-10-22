"""Synthetic source-like cells only, never original Harvard observations."""
import unittest
from datetime import date,timedelta
from scripts import wur_irrigation_schema_probe as m

class MockSheet:
 def __init__(self,rows,columns):
  self.rows=rows;self.max_column=columns
 def iter_rows(self,values_only=True):
  assert values_only
  return iter(self.rows)

def fake_sheets():
 meta=[("Daily rainfall mm","irrigation treatment","private descriptor")]+[(None,None,None)]*16
 rows=[("date","location","rainfall mm","W1","W2","private")]
 for year,n in ((2019,258),(2020,268)):
  for offset in range(n):
   rows.append((date(year,1,1)+timedelta(days=offset),
                "Lelystad" if year==2019 else "Vredepeel",
                0 if offset%3 else 4,0 if offset%2 else 8,
                0 if offset%5 else 12,"PRIVATE-RAW-VALUE"))
 return MockSheet(meta,3),MockSheet(rows,6)

class TypedIrrigationProbe(unittest.TestCase):
 def test_exact_date_axis_and_strict_whitelisted_no_source_export(self):
  r=m.inspect_sheets(*fake_sheets())
  self.assertEqual(r["date_counts_by_year"],{"2019":258,"2020":268})
  self.assertEqual(r["date_column_one_based"],1)
  self.assertEqual(r["column_profiles"][1]["controlled_site_treatment_category_counts"],
                   {"Lelystad":258,"Vredepeel":268})
  self.assertEqual(len(r["column_profiles"]),6)
  self.assertIn("mm",str(r["metadata_tags_by_position"]))
  self.assertEqual(r["original_values_or_dates_exported"],0)
  for secret in ("PRIVATE-RAW-VALUE","rainfall mm","2019-01-01","2020-01-01"):
   self.assertNotIn(secret,str(r))
 def test_zero_distinct_from_missing_and_bad_numeric(self):
  self.assertEqual(m.kind(0),"numeric")
  self.assertEqual(m.kind(None),"missing")
  self.assertEqual(m.kind("NA"),"missing")
  self.assertEqual(m.kind(float("nan")),"invalid")
  self.assertEqual(m.kind(True),"boolean")
 def test_tampered_source_sha_denied_before_excel(self):
  with self.assertRaisesRegex(ValueError,"SHA256"):
   m.audit(b"fabricated")
 def test_wrong_number_of_rows_blocks(self):
  meta,data=fake_sheets()
  data.rows.pop()
  with self.assertRaisesRegex(ValueError,"geometry"):
   m.inspect_sheets(meta,data)
 def test_ambiguous_double_date_column_blocks(self):
  meta,data=fake_sheets()
  data.rows=[tuple([row[0],row[0],*row[2:]]) if isinstance(row[0],date) else row
             for row in data.rows]
  with self.assertRaisesRegex(ValueError,"Ambiguous"):
   m.inspect_sheets(meta,data)
 def test_bad_date_coverage_fails(self):
  meta,data=fake_sheets()
  data.rows[1]=(date(2018,1,1),)+data.rows[1][1:]
  with self.assertRaisesRegex(ValueError,"Date counts"):
   m.inspect_sheets(meta,data)
 def test_original_text_not_assumed_semantically_valid(self):
  hints=m.whitelisted_tags([("SECRET","watergift","irrigation mm by treatment")],10)
  self.assertNotIn("SECRET",str(hints))
  self.assertIn("irrigation",str(hints))
if __name__=="__main__":unittest.main()

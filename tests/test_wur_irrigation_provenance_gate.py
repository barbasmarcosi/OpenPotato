"""M1-34 fixtures contain invented aggregate records, not licensed values."""
import unittest
from scripts import wur_irrigation_provenance_gate as m

def sample_reports():
    a={"irrigation_file_sha256":m.EXPECTED_SHA256,
       "plots_file_sha256":m.plot_source.SOURCE_SHA256,
       "source_licence":"CC BY-NC-SA 4.0",
       "all_site_year_treatment_labels_reconciled":True}
    rows=[]
    for days,no_row,w1blank,w2blank,w1pos,w2pos in (
        (127,63,116,86,11,41),(131,45,57,54,74,77),
        (134,64,125,104,9,30),(134,48,47,32,87,102)):
        rows.append({
          "conservative_calendar_days_including_both_anchors":days+no_row,
          "registered_calendar_days_within_window":days,
          "calendar_days_without_register_row_UNKNOWN":no_row,
          "W1_unknown_total_blanks_plus_unrecorded_days":w1blank+no_row,
          "W2_unknown_total_blanks_plus_unrecorded_days":w2blank+no_row,
          "windows":{"planting_through_last_sample":{
             "recorded_days":days,
             "W1":{"blank_UNKNOWN":w1blank,"recorded_positive":w1pos,"explicit_zero":0},
             "W2":{"blank_UNKNOWN":w2blank,"recorded_positive":w2pos,"explicit_zero":0}}}})
    b={"original_sha256":m.EXPECTED_SHA256,"source_sha_checked":True,
       "source_license":"CC BY-NC-SA 4.0",
       "wofost_irrigation_agromanagement_admissible":False,
       "blanks_or_absent_calendar_rows_are_NOT_zero":True,
       "site_year_aggregate_counts":rows}
    return a,b

def ledger():
    return {"schema_version":1,"dataset_doi":m.DOI,
       "irrigation_source_sha256":m.EXPECTED_SHA256,
       "claims":{name:{
          "status":"UNVERIFIED","value":None,"primary_source_url":None,
          "primary_source_sha256":None,"independent_review_reference":None}
          for name in m.CLAIMS}}

class ScientificEvidenceGateTests(unittest.TestCase):
    def test_unverified_seven_claims_prevent_model(self):
        a,b=sample_reports()
        r=m.make_report(a,b,ledger())
        self.assertEqual(len(r["unresolved_claims"]),7)
        self.assertEqual(r["original_aggregate_balance"]["no_row"],220)
        self.assertEqual(r["original_aggregate_balance"]["W1_unknown"],565)
        self.assertEqual(r["original_aggregate_balance"]["W2_unknown"],496)
        self.assertFalse(r["W1_W2_schedule_generation_permitted"])
        self.assertFalse(r["field_WOFOST_simulation_admissible"])
    def test_attempt_to_put_cm_in_unverified_claim_is_rejected(self):
        l=ledger()
        l["claims"]["W1_physical_unit"]["value"]="cm"
        with self.assertRaisesRegex(ValueError,"invented value"):
            m.inspect_claims(l)
    def test_unreviewed_unit_cannot_be_upgraded_without_primary_evidence(self):
        l=ledger();x=l["claims"]["W1_physical_unit"]
        x["status"]="PRIMARY_SOURCE_REVIEWED";x["value"]="cm"
        with self.assertRaisesRegex(ValueError,"URL absent"):
            m.inspect_claims(l)
    def test_forged_claim_name_rejected(self):
        l=ledger();l["claims"]["weather_rain_proves_W1_cm"]={}
        with self.assertRaisesRegex(ValueError,"exactly seven"):
            m.inspect_claims(l)
    def test_no_recode_original_blank_to_zero(self):
        a,b=sample_reports()
        b["site_year_aggregate_counts"][0]["windows"]["planting_through_last_sample"]["W1"]["explicit_zero"]=116
        with self.assertRaisesRegex(ValueError,"Manufactured"):
            m.make_report(a,b,ledger())
    def test_source_digest_must_be_pinned(self):
        a,b=sample_reports();a["irrigation_file_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"source hash"):
            m.make_report(a,b,ledger())
    def test_missing_calendar_day_count_must_balance(self):
        a,b=sample_reports()
        b["site_year_aggregate_counts"][0]["calendar_days_without_register_row_UNKNOWN"]=62
        with self.assertRaisesRegex(ValueError,"misbalanced"):
            m.make_report(a,b,ledger())
    def test_complete_claim_ledger_not_equivalent_to_field_validation(self):
        a,b=sample_reports()
        l=ledger()
        for name in m.CLAIMS:
            x=l["claims"][name]
            if name.endswith("_physical_unit"):value="cm"
            elif name.endswith("_meaning"):value="NO_APPLICATION"
            else:value="DEPTH_PER_UNIT_AREA"
            x.update(status="PRIMARY_SOURCE_REVIEWED",value=value,
                     primary_source_url="https://research.wur.nl/en/datasets/primary",
                     primary_source_sha256="a"*64,
                     independent_review_reference="#8")
        report=m.make_report(a,b,l)
        self.assertEqual(report["unresolved_claims"],[])
        self.assertFalse(report["W1_W2_schedule_generation_permitted"])
        self.assertFalse(report["field_WOFOST_simulation_admissible"])
    def test_bad_unit_code_denied(self):
        l=ledger();x=l["claims"]["W1_physical_unit"]
        x.update(status="PRIMARY_SOURCE_REVIEWED",value="km",
            primary_source_url="https://research.wur.nl/en/datasets/primary",
            primary_source_sha256="a"*64,independent_review_reference="#8")
        with self.assertRaisesRegex(ValueError,"Unsupported physical"):
            m.inspect_claims(l)
if __name__=="__main__":
    unittest.main()

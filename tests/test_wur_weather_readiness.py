"""All workbook fixtures are IN VITRO; no observations from the WUR study."""
import io
import json
import unittest
from unittest.mock import patch
from openpyxl import Workbook
from scripts import wur_weather_readiness as mod


def invented_workbook():
    wb=Workbook()
    ws=wb.active
    ws.title="SECRET-STATION-DO-NOT-EXPORT"
    ws.append(["DATE","TMIN hypothetical","rain MM invented","srad"])
    ws.append(["2020-04-01",11.0,7.0,3.0])
    bio=io.BytesIO();wb.save(bio);wb.close()
    return bio.getvalue()


class WeatherAuditTests(unittest.TestCase):
    def test_workbook_export_cannot_contain_original_cell_values_or_headers(self):
        report=mod.describe_workbook(invented_workbook())
        self.assertEqual(report["worksheet_count"],1)
        self.assertGreater(report["structure_only"][0]["reported_max_rows"],0)
        exported=json.dumps(report)
        for banned in ("2020-04-01","SECRET-STATION","TMIN hypothetical","rain MM invented"):
            self.assertNotIn(banned,exported)
        self.assertGreaterEqual(report["structure_only"][0][
            "candidate_header_token_counts_unconfirmed_units"]["temperature"],1)

    def test_modified_sha_fails_closed_before_reading_any_workbook(self):
        with self.assertRaisesRegex(ValueError,"SHA256"):
            mod.audit_sources({"Lelystad":invented_workbook(),"Vredepeel":invented_workbook()})

    def test_missing_station_fails_closed(self):
        with self.assertRaisesRegex(ValueError,"Both source"):
            mod.audit_sources({"Lelystad":invented_workbook()})

    def test_even_hypothetically_verified_workbooks_never_unlock_wofost(self):
        blob=invented_workbook()
        with patch.dict(mod.FILES, {
            "Lelystad":{"id":1,"sha256":mod.hashlib.sha256(blob).hexdigest()},
            "Vredepeel":{"id":2,"sha256":mod.hashlib.sha256(blob).hexdigest()}}):
            report=mod.audit_sources({"Lelystad":blob,"Vredepeel":blob})
        self.assertFalse(report["ready_to_run_field_wofost"])
        self.assertFalse(report["model_driver_units_and_daily_frequency_confirmed"])
        self.assertEqual(report["original_weather_cell_values_exported"],0)
        self.assertEqual(report["raw_daily_weather_records_exported"],0)

    def test_garbage_workbook_rejected(self):
        with self.assertRaisesRegex(ValueError,"Invalid or unreadable"):
            mod.describe_workbook(b"fake weather file")


if __name__=="__main__":
    unittest.main()

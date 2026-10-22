"""Unit tests with fabricated weather, optional PCSE import kept out of stdlib CI."""
import importlib.util
import unittest
from datetime import date
from scripts import wur_pcse_weather_provider_smoke as m

class FakeWeather:
    def __init__(self,val=1.):
        for field in ("IRRAD","TMIN","TMAX","VAP","WIND","RAIN","E0","ES0","ET0"):
            setattr(self,field,val)

class ProviderProbeTests(unittest.TestCase):
    def test_mock_provider_covers_every_day_exactly(self):
        self.assertEqual(m.assert_all_days(lambda day:FakeWeather()),1096)
    def test_skipped_day_is_rejected_even_if_provider_only_warns(self):
        def provider(day):
            if day==date(2020,11,3):raise KeyError("missing source day")
            return FakeWeather()
        with self.assertRaisesRegex(ValueError,"1 original daily"):
            m.assert_all_days(provider)
    def test_invalid_numeric_weather_rejected_without_leaking_measurements(self):
        def provider(day):
            if day==date(2020,11,3):return FakeWeather(float("nan"))
            return FakeWeather()
        with self.assertRaisesRegex(ValueError,"1 original daily"):
            m.assert_all_days(provider)
    def test_wrong_source_files_do_not_call_pcse(self):
        with self.assertRaisesRegex(ValueError,"Both"):
            m.process_originals({"Lelystad":b"invalid"})
        with self.assertRaisesRegex(ValueError,"Unknown original"):
            m.process_originals({"Lelystad":b"invalid","Vredepeel":b"invalid"})

if __name__=="__main__":unittest.main()

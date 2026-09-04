import asyncio
from backend.app.services.incois.client import incois_connector
from backend.app.services.incois.parser import parse_incois_wave_record, parse_incois_sst_record

def test_incois_health():
    health = asyncio.run(incois_connector.health_check())
    assert health.name == "INCOIS"
    assert health.source_id == "INCOIS_OSF"
    assert health.last_checked is not None

def test_incois_data_retrieval():
    records = asyncio.run(incois_connector.get_data())
    assert len(records) > 0
    wave_records = [r for r in records if r.parameter == "significant_wave_height"]
    assert len(wave_records) > 0
    for w in wave_records:
        assert w.data_type == "forecast"
        assert w.unit == "m"
        assert w.value > 0
        assert "incois.gov.in" in w.source_url

def test_incois_wave_parser():
    record = parse_incois_wave_record(
        lat=19.30,
        lon=72.53,
        wave_height_m=3.85,
        wave_period_s=10.5
    )
    assert record.source == "INCOIS"
    assert record.value == 3.85
    assert record.data_type == "forecast"
    assert record.metadata["wave_period_sec"] == 10.5

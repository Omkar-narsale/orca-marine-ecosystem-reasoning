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
    assert isinstance(records, list)

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

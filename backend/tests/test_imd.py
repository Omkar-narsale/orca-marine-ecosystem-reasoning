import asyncio
from backend.app.services.imd.client import imd_connector
from backend.app.services.imd.parser import parse_imd_wind_record, parse_imd_warning_record

def test_imd_health():
    health = asyncio.run(imd_connector.health_check())
    assert health.name == "IMD"
    assert health.source_id == "IMD_MARINE"
    assert health.last_checked is not None

def test_imd_data_retrieval():
    records = asyncio.run(imd_connector.get_data())
    assert len(records) > 0
    wind_records = [r for r in records if r.parameter == "surface_wind_10m"]
    assert len(wind_records) > 0
    for w in wind_records:
        assert w.data_type == "forecast"
        assert w.unit == "kt"
        assert w.value > 0

def test_imd_warning_parser():
    record = parse_imd_warning_record(
        sector_name="North Maharashtra",
        warning_type="Squall Alert",
        severity="Severe",
        headline="Squall wind 34 knots expected.",
        instructions="Return to port."
    )
    assert record.source == "IMD"
    assert record.data_type == "warning"
    assert "Squall" in record.value

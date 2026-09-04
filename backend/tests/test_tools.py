import pytest
import asyncio
from backend.app.tools.marine_tools import wave_forecast_tool, sst_tool, pfz_advisory_tool, chlorophyll_tool
from backend.app.tools.weather_tools import coastal_winds_tool, marine_warnings_tool
from backend.app.tools.geospatial_tools import check_zone_geofences_tool, get_zone_polygons_tool
from backend.app.tools.risk_tools import calculate_zone_risk_tool
from backend.app.tools.evidence_tools import compile_evidence_tool

def test_wave_forecast_tool():
    res = asyncio.run(wave_forecast_tool.execute())
    assert res.success is True
    assert len(res.data) > 0
    assert len(res.evidence_ids) > 0
    assert any(r.parameter == "significant_wave_height" for r in res.data)

def test_coastal_winds_tool():
    res = asyncio.run(coastal_winds_tool.execute())
    assert res.success is True
    assert len(res.data) > 0
    assert any(r.parameter == "surface_wind_10m" for r in res.data)

def test_geofence_tool():
    res = asyncio.run(check_zone_geofences_tool.execute(zone_id="zone-b"))
    assert res.success is True
    assert "zone-b" in res.data
    assert res.data["zone-b"]["restricted"] is True

def test_compile_evidence_tool():
    records_res = asyncio.run(wave_forecast_tool.execute())
    ev_res = asyncio.run(compile_evidence_tool.execute(records=records_res.data))
    assert ev_res.success is True
    assert len(ev_res.data) >= len(records_res.data)
    assert any(node.source_id == "INCOIS_OSF" for node in ev_res.data)

import asyncio
from backend.app.services.mosdac.client import mosdac_connector
from backend.app.services.geospatial.service import geospatial_service
from backend.app.schemas.marine import NormalizedMarineRecord
from backend.app.core.cache import cache

def test_mosdac_observation_normalization():
    # Test normalization schema adherence
    record = NormalizedMarineRecord(
        source="MOSDAC",
        source_id="MOSDAC_OCEAN",
        parameter="chlorophyll_a_concentration",
        value=3.4,
        unit="mg/m³",
        latitude=18.58,
        longitude=72.70,
        timestamp="2026-09-09T00:00:00Z",
        data_type="observation",
        valid_time="Observation Pass",
        retrieved_at="09 Sep 2026",
        source_url="https://mosdac.gov.in"
    )
    assert record.source == "MOSDAC"
    assert record.data_type == "observation"
    assert "mg/m³" in record.unit

def test_geospatial_cadastre_normalization():
    records = asyncio.run(geospatial_service.get_data())
    assert len(records) > 0
    for r in records:
        assert r.source == "GIS Cadastre"
        assert r.data_type == "static"

def test_cache_ttl():
    cache.set("test_key", {"wave": 3.4}, ttl_seconds=10)
    val = cache.get("test_key")
    assert val is not None
    assert val["wave"] == 3.4
    
    # Test non-existent key
    assert cache.get("non_existent_key") is None

import asyncio
from backend.app.services.mosdac.client import mosdac_connector
from backend.app.services.geospatial.service import geospatial_service
from backend.app.core.cache import cache

def test_mosdac_observation_normalization():
    records = asyncio.run(mosdac_connector.get_data())
    assert len(records) > 0
    for r in records:
        assert r.source == "MOSDAC"
        assert r.data_type == "observation" # Strictly verified observation
        assert "mg/m³" in r.unit

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

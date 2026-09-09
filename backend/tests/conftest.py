import pytest
from backend.app.services.incois.client import incois_connector
from backend.app.services.imd.client import imd_connector
from backend.tests.fixtures.test_marine_data import get_test_marine_records

@pytest.fixture
def anyio_backend():
    return 'asyncio'

@pytest.fixture(autouse=False)
def mock_pipeline_data(monkeypatch):
    """Fixture providing test-only fixture records when testing deterministic pipeline reasoning."""
    async def mock_incois_get_data(*args, **kwargs):
        recs = get_test_marine_records()
        return [r for r in recs if r.source == "INCOIS"]
    async def mock_imd_get_data(*args, **kwargs):
        recs = get_test_marine_records()
        return [r for r in recs if r.source == "IMD"]

    monkeypatch.setattr(incois_connector, "get_data", mock_incois_get_data)
    monkeypatch.setattr(imd_connector, "get_data", mock_imd_get_data)

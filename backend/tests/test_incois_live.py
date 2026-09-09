"""
Live Integration Test against official INCOIS ERDDAP service.
Gracefully skips if external internet or government portal is unreachable.
"""

import pytest
import httpx
from backend.app.services.incois.client import incois_connector
from backend.app.services.incois.health import health_inspector

@pytest.mark.anyio
async def test_live_incois_erddap_connectivity():
    """Tests live INCOIS ERDDAP info endpoint with graceful skip if offline."""
    try:
        async with httpx.AsyncClient(timeout=5.0, verify=False) as client:
            res = await client.get("https://erddap.incois.gov.in/erddap/info/index.json")
            if res.status_code not in (200, 301, 302):
                pytest.skip("INCOIS ERDDAP live server returned non-200 status. Skipped per Section 42.")
    except Exception as e:
        pytest.skip(f"Live INCOIS ERDDAP external server unreachable ({type(e).__name__}). Skipped per Section 42.")

    # If reachable, perform diagnostic health verification
    health = await health_inspector.check_health()
    assert health is not None
    assert health.source_id in ("INCOIS_OSF", "INCOIS_ERDDAP")

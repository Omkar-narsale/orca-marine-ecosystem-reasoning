"""
Bhuvan Health Inspector.
Evaluates ISRO Bhuvan NRSC portal reachability and API status.
"""

import time
import httpx
from datetime import datetime
from backend.app.schemas.evidence import SourceHealthSchema
from backend.app.core.config import settings

class BhuvanHealthInspector:
    def __init__(self, base_url: str = settings.BHUVAN_API_URL):
        self.base_url = base_url

    async def check_health(self) -> SourceHealthSchema:
        start_t = time.perf_counter()
        now_ist = datetime.now().strftime("%d %b %Y %H:%M IST")

        is_live = False
        latency = 0.0
        error_msg = None

        try:
            async with httpx.AsyncClient(timeout=4.0, verify=False) as client:
                res = await client.get(self.base_url)
                latency = (time.perf_counter() - start_t) * 1000.0
                if res.status_code in (200, 301, 302, 401, 403):
                    is_live = True
                else:
                    error_msg = f"HTTP {res.status_code} on Bhuvan API"
        except Exception as e:
            latency = (time.perf_counter() - start_t) * 1000.0
            error_msg = f"{type(e).__name__}: {str(e)}"

        status_label = "HEALTHY" if is_live else "DEGRADED"

        return SourceHealthSchema(
            source_id="BHUVAN_NRSC",
            name="Bhuvan",
            organization="ISRO National Remote Sensing Centre (NRSC)",
            status="Connected / Live" if is_live else "Degraded (Offline GIS Fallback Active)",
            health_state=status_label,
            endpoint=self.base_url,
            last_checked=now_ist,
            last_successful_retrieval=now_ist if is_live else None,
            last_successful_fetch=now_ist if is_live else None,
            response_latency_ms=round(latency, 1),
            latency_ms=round(latency, 1),
            data_freshness="Cadastral & Village GIS Layers",
            is_live=is_live,
            error=error_msg,
            notes="ISRO Bhuvan geospatial portal (Village Geocoding, Reverse Geocoding & Thematic Maps)."
        )

bhuvan_health_inspector = BhuvanHealthInspector()

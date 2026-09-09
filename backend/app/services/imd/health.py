"""
IMD Health Inspector.
Actively checks connectivity to official IMD API and public coastal bulletin endpoints.
"""

import time
import httpx
from datetime import datetime
from backend.app.schemas.evidence import SourceHealthSchema
from backend.app.core.config import settings
from backend.app.core.logging import log_source_request

class IMDHealthInspector:
    def __init__(self, base_url: str = settings.IMD_API_BASE_URL):
        self.base_url = base_url

    async def check_health(self) -> SourceHealthSchema:
        start_t = time.perf_counter()
        now_ist = datetime.now().strftime("%d %b %Y %H:%M IST")

        is_live = False
        latency = 0.0
        error_msg = None

        try:
            async with httpx.AsyncClient(timeout=4.0, verify=False) as client:
                res = await client.get(settings.IMD_PUBLIC_URL)
                latency = (time.perf_counter() - start_t) * 1000.0
                if res.status_code in (200, 301, 302):
                    is_live = True
                else:
                    error_msg = f"HTTP {res.status_code} on IMD Public API"
        except Exception as e:
            latency = (time.perf_counter() - start_t) * 1000.0
            error_msg = f"{type(e).__name__}: {str(e)}"

        status_label = "HEALTHY" if is_live else "DEGRADED"

        return SourceHealthSchema(
            source_id="IMD_MARINE",
            name="IMD",
            organization="India Meteorological Department",
            status="Connected / Live" if is_live else "Degraded (Offline Bulletin Baseline Active)",
            health_state=status_label,
            endpoint=settings.IMD_PUBLIC_URL,
            last_checked=now_ist,
            last_successful_retrieval=now_ist if is_live else None,
            last_successful_fetch=now_ist if is_live else None,
            response_latency_ms=round(latency, 1),
            latency_ms=round(latency, 1),
            data_freshness="6-hourly bulletin cycle (Recent)",
            is_live=is_live,
            error=error_msg,
            notes="Official IMD API & Coastal Fishermen Warning System."
        )

imd_health_inspector = IMDHealthInspector()

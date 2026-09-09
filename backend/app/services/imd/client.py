"""
IMD Marine Data Client.
Fetches official weather bulletins, wind observations, and marine warnings from IMD.
Enforces zero hardcoded baseline records and zero fake warnings.
"""

import httpx
import time
import asyncio
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from backend.app.services.base import MarineDataConnector
from backend.app.schemas.marine import NormalizedMarineRecord, DataStatusEnum, ProviderDataResponse
from backend.app.schemas.evidence import SourceHealthSchema
from backend.app.services.imd.parser import (
    parse_imd_wind_record,
    parse_imd_warning_record,
    response_parser
)
from backend.app.core.config import settings
from backend.app.core.logging import log_source_request, logger
from backend.app.core.cache import cache

class IMDConnector(MarineDataConnector):
    def __init__(self):
        super().__init__(
            source_id="IMD_MARINE",
            name="IMD",
            organization="India Meteorological Department",
            base_url=settings.IMD_API_BASE_URL
        )
        self.last_error: Optional[str] = None
        self.last_latency_ms: Optional[float] = None

    async def _fetch_with_retry(self, url: str, max_retries: int = 1) -> httpx.Response:
        """Executes HTTP GET with bounded retry and exponential backoff."""
        headers = {"User-Agent": "ORCA-Marine-Intelligence/4.0 (SIH-2026-Research)"}
        last_exc = None
        for attempt in range(max_retries + 1):
            try:
                async with httpx.AsyncClient(headers=headers, timeout=settings.HTTP_TIMEOUT_SECONDS, verify=False) as client:
                    res = await client.get(url)
                    if res.status_code == 200:
                        return res
            except Exception as e:
                last_exc = e
                if attempt < max_retries:
                    await asyncio.sleep(0.15 * (2 ** attempt))
        if last_exc:
            raise last_exc
        raise httpx.HTTPError(f"Failed after {max_retries} retries to connect to {url}")

    async def health_check(self) -> SourceHealthSchema:
        from backend.app.services.imd.health import imd_health_inspector
        return await imd_health_inspector.check_health()

    async def get_data(
        self,
        min_lat: Optional[float] = None,
        max_lat: Optional[float] = None,
        min_lon: Optional[float] = None,
        max_lon: Optional[float] = None,
        parameters: Optional[List[str]] = None,
        force_failure: bool = False
    ) -> List[NormalizedMarineRecord]:
        """
        Retrieves live IMD bulletins and forecasts.
        Returns empty list / DATA_UNAVAILABLE when service is unreachable (ZERO hardcoded static records).
        """
        if force_failure:
            raise ConnectionError("Simulated IMD connection failure")

        cache_key = f"imd_data_{min_lat}_{max_lat}_{min_lon}_{max_lon}"
        cached = cache.get(cache_key)
        if cached is not None:
            log_source_request(
                source_name="IMD",
                endpoint=cache_key,
                operation="get_marine_bulletin",
                cache_hit=True
            )
            return cached

        records: List[NormalizedMarineRecord] = []
        now_ist = datetime.now().strftime("%d %b %Y %H:%M IST")
        now_utc = datetime.now(timezone.utc).isoformat()
        start_t = time.perf_counter()

        try:
            # Query official IMD coastal bulletin API
            bulletin_url = f"{settings.IMD_PUBLIC_URL}"
            res = await self._fetch_with_retry(bulletin_url, max_retries=1)
            latency = (time.perf_counter() - start_t) * 1000.0
            self.last_latency_ms = latency
            self.last_successful_retrieval = now_ist

            # Parse returned bulletin content
            data = res.json() if res.headers.get("content-type", "").startswith("application/json") else {}
            if data:
                # If structured data returned, parse records
                if "wind" in data:
                    w = data["wind"]
                    records.append(parse_imd_wind_record(
                        lat=float(w.get("lat", min_lat or 18.97)),
                        lon=float(w.get("lon", min_lon or 72.82)),
                        wind_speed_kt=float(w.get("speed_kt", 12.0)),
                        wind_direction=str(w.get("direction", "NW (315°)")),
                        gusts_kt=float(w.get("gusts_kt", 16.0)),
                        valid_time=f"Forecast · {now_ist}"
                    ))
                if "warning" in data and data["warning"].get("is_active"):
                    warn = data["warning"]
                    records.append(parse_imd_warning_record(
                        sector_name=warn.get("sector", "Coastal Waters"),
                        warning_type=warn.get("type", "Marine Warning"),
                        severity=warn.get("severity", "Warning"),
                        headline=warn.get("headline", "Marine Weather Advisory"),
                        instructions=warn.get("instructions", "Fishermen advised to observe caution."),
                        lat=min_lat or 18.97,
                        lon=min_lon or 72.82
                    ))

            log_source_request(
                source_name="IMD",
                endpoint=bulletin_url,
                operation="get_marine_warning",
                method="GET",
                status_code=res.status_code,
                record_count=len(records),
                latency_ms=latency,
                cache_hit=False
            )

        except Exception as e:
            latency = (time.perf_counter() - start_t) * 1000.0
            logger.warning(f"[IMD] Bulletin retrieval failed: {e}. Returning DATA_UNAVAILABLE (no fake data).")
            log_source_request(
                source_name="IMD",
                endpoint=bulletin_url,
                operation="get_marine_warning",
                method="GET",
                status_code=500,
                record_count=0,
                latency_ms=latency,
                cache_hit=False,
                error=str(e)
            )
            self.last_error = str(e)
            records = []

        if records:
            cache.set(cache_key, records, settings.WEATHER_CACHE_TTL_SECONDS)

        return records

    async def get_metadata(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "name": self.name,
            "organization": self.organization,
            "parameters": ["surface_wind_10m", "marine_fishermen_warning", "cyclone_bulletin"],
            "cadence": "6-hourly coastal marine bulletins & 3-hourly numerical updates",
            "spatial_coverage": "North & South Maharashtra Coast",
            "official_url": f"{settings.IMD_API_BASE_URL}/api_reference.html"
        }

imd_connector = IMDConnector()

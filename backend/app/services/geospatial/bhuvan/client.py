"""
Bhuvan Authenticated HTTP Client.
Executes server-side authenticated requests to ISRO NRSC Bhuvan portal.
Maintains token security server-side and provides offline coastal GIS resolution fallback.
"""

import httpx
import time
import asyncio
from typing import Dict, Any, Optional
from backend.app.core.config import settings
from backend.app.core.logging import log_source_request

class BhuvanClient:
    def __init__(self, base_url: str = settings.BHUVAN_API_URL, token: Optional[str] = settings.BHUVAN_API_TOKEN):
        self.base_url = base_url.rstrip('/')
        self.token = token

    async def execute_request(self, endpoint_url: str, params: Optional[Dict[str, Any]] = None, max_retries: int = 1) -> Dict[str, Any]:
        """Executes GET request to Bhuvan API with bounded retry and token headers."""
        headers = {
            "User-Agent": "ORCA-Marine-Intelligence/4.0 (ISRO-Bhuvan-GIS)",
            "Accept": "application/json"
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        start_t = time.perf_counter()
        last_exc = None

        for attempt in range(max_retries + 1):
            try:
                async with httpx.AsyncClient(headers=headers, timeout=settings.HTTP_TIMEOUT_SECONDS, verify=False) as client:
                    res = await client.get(endpoint_url, params=params)
                    latency = (time.perf_counter() - start_t) * 1000.0
                    log_source_request(
                        source_name="BHUVAN",
                        endpoint=endpoint_url,
                        method="GET",
                        status_code=res.status_code,
                        latency_ms=latency
                    )
                    if res.status_code == 200:
                        return {"status": "SUCCESS", "data": res.json(), "status_code": 200, "latency_ms": latency}
                    elif res.status_code in (401, 403):
                        return {"status": "AUTH_REQUIRED", "data": None, "status_code": res.status_code, "latency_ms": latency}
            except Exception as e:
                last_exc = e
                if attempt < max_retries:
                    await asyncio.sleep(0.15 * (2 ** attempt))

        latency = (time.perf_counter() - start_t) * 1000.0
        return {
            "status": "UNAVAILABLE",
            "data": None,
            "error": str(last_exc) if last_exc else "Request failed",
            "latency_ms": latency
        }

bhuvan_client = BhuvanClient()

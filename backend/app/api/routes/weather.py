from fastapi import APIRouter
from typing import List, Dict, Any
from datetime import datetime

from backend.app.schemas.marine import NormalizedMarineRecord, MarineWarningsResponse
from backend.app.services.imd.client import imd_connector
from backend.app.core.config import settings

router = APIRouter(prefix="/weather", tags=["Meteorological & Coastal Weather"])

@router.get("/coastal", response_model=List[NormalizedMarineRecord])
async def get_coastal_weather():
    """Retrieve normalized 10m surface winds and squall warnings from IMD."""
    records = await imd_connector.get_data()
    return records

@router.get("/warnings", response_model=MarineWarningsResponse)
async def get_marine_warnings():
    """Retrieve official IMD fishermen warnings for Maharashtra coastal sectors."""
    records = await imd_connector.get_data()
    warnings = [r for r in records if r.data_type == "warning"]
    
    bulletins = [
        {
            "sector": w.metadata.get("sector", "Maharashtra Coast"),
            "headline": w.value,
            "severity": w.metadata.get("severity", "Alert"),
            "instructions": w.metadata.get("instructions", ""),
            "issuing_office": w.metadata.get("issuing_office", "IMD Mumbai"),
            "valid_time": w.valid_time
        }
        for w in warnings
    ]
    
    return MarineWarningsResponse(
        warnings_active=len(bulletins) > 0,
        bulletins=bulletins,
        retrieved_at=datetime.now().strftime("%d %b %Y %H:%M IST"),
        source_url=f"{settings.IMD_API_BASE_URL}/api_reference.html"
    )

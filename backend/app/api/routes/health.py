from fastapi import APIRouter
from datetime import datetime

from backend.app.schemas.evidence import SystemHealthResponse, SourceHealthSchema
from backend.app.services.incois.client import incois_connector
from backend.app.services.imd.client import imd_connector
from backend.app.services.mosdac.client import mosdac_connector
from backend.app.services.geospatial.service import geospatial_service

router = APIRouter(prefix="/health", tags=["Health & Status Monitors"])

@router.get("", response_model=SystemHealthResponse)
async def get_system_health():
    """Runs truthful health checks against all 4 underlying official source connectors."""
    incois_h = await incois_connector.health_check()
    imd_h = await imd_connector.health_check()
    mosdac_h = await mosdac_connector.health_check()
    geo_h = await geospatial_service.health_check()

    sources = [incois_h, imd_h, mosdac_h, geo_h]
    live_count = sum(1 for s in sources if s.is_live)
    
    overall_status = "operational" if live_count >= 3 else "degraded"

    return SystemHealthResponse(
        status=overall_status,
        timestamp=datetime.now().strftime("%d %b %Y %H:%M IST"),
        total_sources=len(sources),
        connected_sources=live_count,
        sources=sources
    )

@router.get("/sources")
async def get_sources_status():
    """Lightweight sources status summary for sidebar status indicator."""
    incois_h = await incois_connector.health_check()
    imd_h = await imd_connector.health_check()
    mosdac_h = await mosdac_connector.health_check()
    geo_h = await geospatial_service.health_check()

    return {
        "ocean_data": {"name": "INCOIS", "status": incois_h.status, "is_live": incois_h.is_live},
        "weather_data": {"name": "IMD", "status": imd_h.status, "is_live": imd_h.is_live},
        "satellite_data": {"name": "MOSDAC", "status": mosdac_h.status, "is_live": mosdac_h.is_live},
        "geospatial_grid": {"name": "GIS Cadastre", "status": geo_h.status, "is_live": geo_h.is_live},
        "timestamp": datetime.now().strftime("%d %b %Y %H:%M IST")
    }

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from backend.app.services.geospatial.geofence import (
    geofence_engine,
    GEOFENCE_MUMBAI_NAVAL_ANCHORAGE,
    GEOFENCE_TSS_WESTERN_FAIRWAY,
    GEOFENCE_MALVAN_SANCTUARY
)

router = APIRouter(prefix="/geofences", tags=["Geospatial & Geofence Intelligence"])

class GeofenceCheckBody(BaseModel):
    coordinates: List[List[float]] = Field(..., description="Polygon [[lat, lon], ...] to check against boundaries")
    zone_id: Optional[str] = Field("custom-polygon", description="Identifier for reference")

@router.get("", summary="Get all authoritative registered geofence polygons")
async def get_geofences():
    """Returns official registered marine restricted polygons (Naval Anchorage, TSS Fairway, Marine Sanctuary)."""
    return [
        GEOFENCE_MUMBAI_NAVAL_ANCHORAGE,
        GEOFENCE_TSS_WESTERN_FAIRWAY,
        GEOFENCE_MALVAN_SANCTUARY
    ]

@router.post("/check", summary="Check spatial polygon against authoritative geofences")
async def check_geofence(body: GeofenceCheckBody):
    """
    Computes exact Shapely polygon intersection with all registered maritime restriction polygons.
    Returns restricted status, intersection classification, and legal citation evidence.
    """
    if len(body.coordinates) < 3:
        raise HTTPException(status_code=400, detail="Polygon coordinates must have at least 3 vertices.")
    
    result = geofence_engine.evaluate_zone_geofence(body.zone_id or "custom", body.coordinates)
    return result

@router.get("/check", summary="Check zone by ID or quick coordinates against geofences")
async def check_geofence_get(zone_id: Optional[str] = Query(None, description="Pre-registered zone ID e.g. zone-b")):
    """Check a pre-registered zone against official restriction polygons."""
    from backend.app.services.geospatial.zone_service import get_candidate_zone_by_id
    
    if not zone_id:
        raise HTTPException(status_code=400, detail="zone_id parameter is required.")
    
    zone = get_candidate_zone_by_id(zone_id)
    if not zone:
        raise HTTPException(status_code=404, detail=f"Zone '{zone_id}' not found.")
    
    return geofence_engine.evaluate_zone_geofence(zone_id, zone["coordinates"])

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from backend.app.services.geospatial.zone_service import get_candidate_zones, get_candidate_zone_by_id
from backend.app.services.geospatial.spatial_query import align_records_to_zone
from backend.app.services.geospatial.geofence import geofence_engine
from backend.app.services.incois.client import incois_connector
from backend.app.services.imd.client import imd_connector
from backend.app.services.mosdac.client import mosdac_connector
from backend.app.services.geospatial.service import geospatial_service
from backend.app.services.temporal.alignment import parse_temporal_window
from backend.app.services.risk.risk_engine import risk_engine
from backend.app.services.risk.suitability import suitability_engine
from backend.app.services.risk.hazard_engine import hazard_engine
from backend.app.services.risk.pipeline import run_deterministic_analysis

router = APIRouter(prefix="/zones", tags=["Deterministic Geospatial & Risk Engine"])

class QueryAnalyzeRequest(BaseModel):
    query: str = Field(..., description="Natural language marine query")

class GeofenceCheckRequest(BaseModel):
    coordinates: List[List[float]] = Field(..., description="Polygon coordinates [[lat, lon], ...]")
    zone_id: Optional[str] = Field(None, description="Optional zone identifier")

@router.get("", summary="Get all candidate zones with deterministic risk and suitability")
async def get_zones(
    time_window: Optional[str] = Query(None, description="Temporal window e.g. 'tomorrow morning', 'today'")
):
    """
    Returns all candidate zones with real-time deterministic risk evaluation,
    hazard detection, geofence compliance, and suitability scoring.
    """
    temporal_meta = parse_temporal_window(time_window or "tomorrow morning")
    
    incois_recs = await incois_connector.get_data()
    imd_recs = await imd_connector.get_data()
    mosdac_recs = await mosdac_connector.get_data()
    gis_recs = await geospatial_service.get_data()
    all_recs = incois_recs + imd_recs + mosdac_recs + gis_recs

    candidate_zones = get_candidate_zones()
    results = []

    for z in candidate_zones:
        aligned = align_records_to_zone(z["coordinates"], all_recs)
        eval_result = risk_engine.evaluate_zone(
            zone_id=z["id"],
            zone_name=z["name"],
            zone_coords=z["coordinates"],
            records=aligned,
            time_window=temporal_meta
        )
        suit_eval = suitability_engine.evaluate_suitability(eval_result, aligned)

        results.append({
            "zone_id": z["id"],
            "code": z["code"],
            "name": z["name"],
            "geometry_type": z.get("geometry_type", "Prototype / Demonstration Geometry"),
            "coordinates": z["coordinates"],
            "center": z["center"],
            "risk_score": eval_result["risk_score"],
            "classification": eval_result["classification"],
            "status_label": eval_result["status_label"],
            "is_restricted": eval_result["is_restricted"],
            "geofence": eval_result["geofence"],
            "factors": eval_result["factors"],
            "suitability": suit_eval,
            "confidence": eval_result["confidence"]
        })

    return results

@router.get("/risk-summary", summary="Get comprehensive risk summary across all zones")
async def get_zones_risk_summary(
    time_window: Optional[str] = Query("tomorrow morning", description="Target time window")
):
    """
    Returns high-level deterministic risk summary and zone classification for requested window.
    """
    temporal_meta = parse_temporal_window(time_window)
    
    incois_recs = await incois_connector.get_data()
    imd_recs = await imd_connector.get_data()
    mosdac_recs = await mosdac_connector.get_data()
    gis_recs = await geospatial_service.get_data()
    all_recs = incois_recs + imd_recs + mosdac_recs + gis_recs

    candidate_zones = get_candidate_zones()
    evaluated_zones = []

    for z in candidate_zones:
        aligned = align_records_to_zone(z["coordinates"], all_recs)
        eval_result = risk_engine.evaluate_zone(
            zone_id=z["id"],
            zone_name=z["name"],
            zone_coords=z["coordinates"],
            records=aligned,
            time_window=temporal_meta
        )
        evaluated_zones.append({
            "zone_id": z["id"],
            "code": z["code"],
            "name": z["name"],
            "classification": eval_result["classification"],
            "status_label": eval_result["status_label"],
            "risk_score": eval_result["risk_score"],
            "is_restricted": eval_result["is_restricted"],
            "confidence": eval_result["confidence"]["confidence_score"]
        })

    return {
        "requested_window": temporal_meta,
        "zones": evaluated_zones,
        "total_zones": len(evaluated_zones),
        "avoid_count": sum(1 for z in evaluated_zones if z["classification"] in ("HIGH_RISK", "RESTRICTED")),
        "candidate_count": sum(1 for z in evaluated_zones if z["classification"] in ("SUITABLE_CANDIDATE", "CAUTION"))
    }

@router.get("/{zone_id}", summary="Get single zone details with full telemetry")
async def get_zone_by_id(zone_id: str):
    """Get single candidate zone by ID with deterministic risk and condition attributes."""
    candidate_zone = get_candidate_zone_by_id(zone_id)
    if not candidate_zone:
        raise HTTPException(status_code=404, detail=f"Zone '{zone_id}' not found in candidate registry.")

    incois_recs = await incois_connector.get_data()
    imd_recs = await imd_connector.get_data()
    mosdac_recs = await mosdac_connector.get_data()
    gis_recs = await geospatial_service.get_data()
    all_recs = incois_recs + imd_recs + mosdac_recs + gis_recs

    aligned = align_records_to_zone(candidate_zone["coordinates"], all_recs)
    eval_result = risk_engine.evaluate_zone(
        zone_id=candidate_zone["id"],
        zone_name=candidate_zone["name"],
        zone_coords=candidate_zone["coordinates"],
        records=aligned
    )
    suit_eval = suitability_engine.evaluate_suitability(eval_result, aligned)

    return {
        **candidate_zone,
        "risk_evaluation": eval_result,
        "suitability_evaluation": suit_eval
    }

@router.get("/{zone_id}/risk", summary="Get detailed risk breakdown for single zone")
async def get_zone_risk_detail(zone_id: str):
    """Get detailed risk formula factors, evidence, and geofence evaluation for a specific zone."""
    candidate_zone = get_candidate_zone_by_id(zone_id)
    if not candidate_zone:
        raise HTTPException(status_code=404, detail=f"Zone '{zone_id}' not found.")

    incois_recs = await incois_connector.get_data()
    imd_recs = await imd_connector.get_data()
    gis_recs = await geospatial_service.get_data()
    all_recs = incois_recs + imd_recs + gis_recs

    aligned = align_records_to_zone(candidate_zone["coordinates"], all_recs)
    eval_result = risk_engine.evaluate_zone(
        zone_id=candidate_zone["id"],
        zone_name=candidate_zone["name"],
        zone_coords=candidate_zone["coordinates"],
        records=aligned
    )

    return {
        "zone_id": zone_id,
        "risk_score": eval_result["risk_score"],
        "classification": eval_result["classification"],
        "factors": eval_result["factors"],
        "geofence_status": "RESTRICTED" if eval_result["is_restricted"] else "CLEAR",
        "confidence": eval_result["confidence"],
        "formula_weights": {
            "wave": 0.35,
            "wind": 0.30,
            "warning": 0.25,
            "current": 0.10
        }
    }

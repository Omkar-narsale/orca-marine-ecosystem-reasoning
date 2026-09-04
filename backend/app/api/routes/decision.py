"""ORCA Decision Intelligence API Routes
======================================
Endpoints for:
- Candidate zone ranking (Suitability, Risk, Restrictions)
- Single zone decision breakdown
- Two-zone trade-off comparison
- Operational route corridor planning with geofence verification
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Dict, Any, Optional
from pydantic import BaseModel
from backend.app.services.decision.ranking_engine import rank_candidate_zones, RankedCandidatesResponse
from backend.app.services.decision.tradeoff_engine import compare_zones_tradeoff
from backend.app.services.decision.route_engine import plan_route_corridor, RouteCorridorResponse

router = APIRouter(prefix="/api/decision", tags=["decision"])


class RouteRequest(BaseModel):
    start_point: tuple[float, float] = (18.9220, 72.8347) # Mumbai Apollo Bunder
    destination_zone_id: str = "zone_c"


@router.get("/rank", response_model=RankedCandidatesResponse)
async def get_ranked_zones():
    """Ranks all candidate operational zones using deterministic risk, suitability, and restrictions."""
    return rank_candidate_zones()


@router.get("/{zone_id}")
async def get_zone_decision(zone_id: str):
    """Returns detailed decision matrix and suitability breakdown for a specific zone."""
    ranking = rank_candidate_zones()
    
    for item in ranking.ranked_candidates + ranking.excluded_zones:
        if item.zone_id.lower() == zone_id.lower():
            return {
                "zone_id": item.zone_id,
                "name": item.name,
                "rank": item.rank,
                "operational_status": item.operational_status,
                "suitability_score": item.suitability_score,
                "risk_score": item.risk_score,
                "risk_level": item.risk_level,
                "confidence_level": item.confidence_level,
                "uncertainty_level": item.uncertainty_level,
                "why_this_zone": item.why_this_zone,
                "supporting_evidence": item.supporting_evidence,
                "disclaimer": "Decision support only. Ranks candidate zones using available marine forecasts and spatial constraints."
            }
            
    raise HTTPException(status_code=404, detail=f"Zone '{zone_id}' not found in candidate set.")


@router.get("/tradeoff/compare")
async def get_zone_tradeoff_comparison(
    zone_a: str = Query("zone_c", description="First zone ID"),
    zone_b: str = Query("zone_d", description="Second zone ID")
):
    """Compares two zones and explains operational trade-offs (risk vs environmental indicators vs geofences)."""
    return compare_zones_tradeoff(zone_a, zone_b)


@router.post("/route", response_model=RouteCorridorResponse)
async def get_operational_route_corridor(req: RouteRequest):
    """Calculates operational transit corridor and audits geofence/hazard intersections."""
    return plan_route_corridor(
        start_point=req.start_point,
        destination_zone_id=req.destination_zone_id
    )

"""ORCA Uncertainty & Confidence API Routes
=========================================
Endpoints for decomposed 5-factor confidence metrics and uncertainty indicators.
"""

from fastapi import APIRouter, HTTPException
from backend.app.services.uncertainty.uncertainty_engine import (
    calculate_zone_uncertainty,
    UncertaintyAssessment
)
from backend.app.services.decision.ranking_engine import rank_candidate_zones

router = APIRouter(prefix="/api/uncertainty", tags=["uncertainty"])


@router.get("/matrix")
async def get_uncertainty_matrix():
    """Returns uncertainty and confidence summary across all candidate zones."""
    zones = ["zone_a", "zone_b", "zone_c", "zone_d"]
    results = []
    
    for zid in zones:
        ua = calculate_zone_uncertainty(zid)
        results.append({
            "zone_id": zid,
            "confidence_pct": ua.confidence.overall_confidence_pct,
            "confidence_level": ua.confidence.confidence_level,
            "uncertainty_level": ua.uncertainty_level,
            "primary_unknown": ua.primary_unknown,
            "breakdown": ua.confidence.breakdown
        })
    return {"matrix": results}


@router.get("/{zone_id}", response_model=UncertaintyAssessment)
async def get_zone_uncertainty(zone_id: str):
    """Calculates granular decomposed confidence and epistemic/aleatoric uncertainty for a zone."""
    try:
        return calculate_zone_uncertainty(zone_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed calculating uncertainty for {zone_id}: {str(e)}")

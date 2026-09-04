from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from backend.app.schemas.agentic import AgenticQueryResponse
from backend.app.agents.orchestrator import orchestrator
from backend.app.services.risk.hazard_engine import hazard_engine
from backend.app.services.incois.client import incois_connector
from backend.app.services.imd.client import imd_connector

router = APIRouter(prefix="/query", tags=["Deterministic Natural Language Query Router"])

class AnalyzeRequest(BaseModel):
    query: str = Field(..., description="Natural language marine query")

@router.post("/analyze", summary="Analyze natural language marine query through 6-agent orchestrator")
async def analyze_query(request: AnalyzeRequest):
    """
    Executes the full Phase 3 multi-agent marine intelligence pipeline:
    Planner Agent -> Parallel [Ocean, Weather, Geospatial] -> Risk Agent -> Synthesis Agent.
    """
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Query string must not be empty.")
    
    result = await orchestrator.run(request.query)
    return result.model_dump()

@router.get("/hazards", summary="Get active marine hazards detected across coastal shelf")
async def get_active_hazards():
    """Returns detected marine hazards from authoritative wave forecasts and weather bulletins."""
    incois_recs = await incois_connector.get_data()
    imd_recs = await imd_connector.get_data()
    
    wave_recs = [r for r in incois_recs if r.parameter == "significant_wave_height"]
    wind_recs = [r for r in imd_recs if r.parameter == "surface_wind_10m"]
    warn_recs = [r for r in imd_recs if r.parameter == "marine_fishermen_warning"]
    
    wave_h = hazard_engine.evaluate_wave_hazard(wave_recs)
    wind_h = hazard_engine.evaluate_wind_hazard(wind_recs)
    warn_h = hazard_engine.evaluate_warning_hazard(warn_recs)
    
    return {
        "wave_hazard": wave_h,
        "wind_hazard": wind_h,
        "warning_hazard": warn_h,
        "hazard_summary": f"Wave Severity: {wave_h['severity']}, Wind Severity: {wind_h['severity']}, Warnings: {warn_h['severity']}"
    }

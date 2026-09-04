from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from backend.app.schemas.agentic import (
    AgenticQueryRequest,
    AgenticQueryResponse,
    PlannerPlan,
    ConversationContext
)
from backend.app.agents.orchestrator import orchestrator, SESSION_CONTEXT_CACHE
from backend.app.agents.planner_agent import planner_agent

router = APIRouter(prefix="/agentic", tags=["Agentic AI Intelligence Layer"])

class PlannerRequest(BaseModel):
    query: str = Field(..., description="User natural language marine question")
    context: Optional[ConversationContext] = None

@router.post("/query", response_model=AgenticQueryResponse, summary="Execute full 6-agent orchestration graph")
async def execute_agentic_query(
    request: AgenticQueryRequest,
    session_id: Optional[str] = Query(None, description="Optional conversational session ID")
):
    """
    Executes the full ORCA Phase 3 Agentic Graph:
    Planner -> Parallel [Ocean, Weather, Geospatial] -> Risk & Evidence -> Synthesis.
    """
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Query text must not be empty.")
    
    response = await orchestrator.run(
        query=request.query,
        context=request.context,
        session_id=session_id
    )
    return response

@router.post("/planner", response_model=PlannerPlan, summary="Inspect Planner Agent task decomposition")
async def inspect_planner(request: PlannerRequest):
    """Returns the Planner Agent's decomposition, intent classification, and tool selection plan."""
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Query text must not be empty.")
    
    plan = planner_agent.plan(request.query, request.context)
    return plan

@router.get("/tools", summary="List registered agentic tools")
async def list_agentic_tools():
    """Returns the schema and capability catalogue of all registered domain tools."""
    return [
        {"name": "get_wave_forecast", "agent": "Ocean Agent", "source": "INCOIS Wave Watch III", "type": "numerical_forecast"},
        {"name": "get_sst", "agent": "Ocean Agent", "source": "INCOIS / MOSDAC", "type": "satellite_observation"},
        {"name": "get_pfz_advisories", "agent": "Ocean Agent", "source": "INCOIS Marine Fisheries", "type": "advisory"},
        {"name": "get_chlorophyll_observations", "agent": "Ocean Agent", "source": "MOSDAC Oceansat-3 OCM", "type": "satellite_observation"},
        {"name": "get_coastal_winds", "agent": "Weather Agent", "source": "IMD Coastal Division", "type": "numerical_forecast"},
        {"name": "get_marine_warnings", "agent": "Weather Agent", "source": "IMD Marine Division", "type": "statutory_warning"},
        {"name": "check_zone_geofences", "agent": "Geospatial Agent", "source": "GIS Maritime Cadastre", "type": "static_constraint"},
        {"name": "get_zone_polygons", "agent": "Geospatial Agent", "source": "National Hydrographic Cadastre", "type": "geometry"},
        {"name": "calculate_zone_risk_scores", "agent": "Risk & Evidence Agent", "source": "ORCA Deterministic Risk Engine", "type": "analytical"},
        {"name": "compile_evidence_graph", "agent": "Risk & Evidence Agent", "source": "ORCA Evidence Engine", "type": "provenance"}
    ]

@router.get("/agents", summary="List active multi-agent system status")
async def list_active_agents():
    """Returns the architectural topology of ORCA's 6 collaborative agents."""
    return [
        {"name": "Planner Agent", "role": "Intent decomposition & tool binding", "status": "ACTIVE"},
        {"name": "Ocean Agent", "role": "Numerical oceanographic & satellite retrieval", "status": "ACTIVE"},
        {"name": "Weather & Hazard Agent", "role": "Atmospheric wind & marine warning evaluation", "status": "ACTIVE"},
        {"name": "Geospatial Agent", "role": "Spatial boundary & cadastral restriction checking", "status": "ACTIVE"},
        {"name": "Risk & Evidence Agent", "role": "Deterministic hazard scoring & evidence assembly", "status": "ACTIVE"},
        {"name": "Synthesis Agent", "role": "Grounded executive decision & explanation composition", "status": "ACTIVE"}
    ]

@router.post("/session/reset", summary="Reset multi-turn session context")
async def reset_session(session_id: str = Query(..., description="Session identifier to purge")):
    """Purges session memory cache."""
    if session_id in SESSION_CONTEXT_CACHE:
        del SESSION_CONTEXT_CACHE[session_id]
        return {"status": "success", "message": f"Session {session_id} memory cleared."}
    return {"status": "noop", "message": "Session not found."}

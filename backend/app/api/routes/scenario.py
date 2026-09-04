"""ORCA What-If Scenario API Routes
=================================
Endpoints for hypothetical parameter modifications (wave, wind, time shift, restrictions)
and comparison against baseline analysis.
"""

from fastapi import APIRouter
from backend.app.services.decision.scenario_engine import (
    run_what_if_scenario,
    reset_scenario_baseline,
    ScenarioRunRequest,
    WhatIfScenarioResult
)

router = APIRouter(prefix="/api/scenario", tags=["scenario"])


@router.post("/run", response_model=WhatIfScenarioResult)
async def execute_scenario(req: ScenarioRunRequest):
    """Executes a hypothetical what-if scenario simulation without altering source observations."""
    return run_what_if_scenario(req)


@router.post("/reset")
async def reset_scenario():
    """Resets simulated modifications back to baseline authoritative state."""
    return reset_scenario_baseline()


@router.get("/baseline")
async def get_baseline():
    """Fetches the baseline state for comparison."""
    return reset_scenario_baseline()

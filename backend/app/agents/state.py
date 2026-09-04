from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from backend.app.schemas.agentic import (
    PlannerPlan,
    AgentTraceStep,
    EvidenceGraphItem,
    ConversationContext
)
from backend.app.schemas.marine import NormalizedMarineRecord

class ORCAAgentState(BaseModel):
    """
    Shared execution state flowing through the ORCA Multi-Agent Graph.
    """
    query: str
    context: Optional[ConversationContext] = None
    plan: Optional[PlannerPlan] = None
    
    # Agent Artifacts
    ocean_records: List[NormalizedMarineRecord] = Field(default_factory=list)
    ocean_findings: List[Dict[str, Any]] = Field(default_factory=list)
    
    weather_records: List[NormalizedMarineRecord] = Field(default_factory=list)
    weather_hazards: List[Dict[str, Any]] = Field(default_factory=list)
    
    geospatial_evaluations: Dict[str, Any] = Field(default_factory=dict)
    
    # Risk & Synthesis Artifacts
    evaluated_zones: List[Dict[str, Any]] = Field(default_factory=list)
    suitability_results: List[Dict[str, Any]] = Field(default_factory=list)
    
    evidence_nodes: List[EvidenceGraphItem] = Field(default_factory=list)
    trace_steps: List[AgentTraceStep] = Field(default_factory=list)
    
    # Quality & Limitations
    missing_data_flags: List[str] = Field(default_factory=list)
    source_disagreements: List[str] = Field(default_factory=list)
    confidence_score: int = 78
    confidence_level: str = "Medium"
    confidence_explanation: str = ""
    
    # Final Output
    decision_summary: Optional[str] = None
    final_response: Optional[Dict[str, Any]] = None
    errors: List[str] = Field(default_factory=list)

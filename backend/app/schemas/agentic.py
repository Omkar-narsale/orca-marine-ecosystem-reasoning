from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime

AgentStatusLiteral = Literal["QUEUED", "RUNNING", "COMPLETE", "PARTIAL", "FAILED"]
IntentLiteral = Literal[
    "marine_safety",
    "fishing_suitability",
    "marine_hazard",
    "geofence_check",
    "zone_analysis",
    "marine_forecast",
    "source_evidence",
    "what_if_scenario",
    "risk_comparison",
    "general_marine_query"
]

class AgentTraceStep(BaseModel):
    agentName: str = Field(..., description="Specialized agent name (Planner, Ocean, Weather, Geospatial, Risk, Synthesis)")
    action: str = Field(..., description="Summary action or query decomposition")
    status: Literal["completed", "active", "partial", "failed", "queued"] = Field("completed")
    agentStatus: AgentStatusLiteral = Field("COMPLETE")
    toolsUsed: List[str] = Field(default_factory=list)
    dataCategories: List[str] = Field(default_factory=list)
    latencyMs: Optional[float] = Field(default=None)
    evidenceCount: int = Field(default=0)
    details: Optional[str] = None

class EvidenceGraphItem(BaseModel):
    id: str = Field(..., description="Unique evidence node ID (e.g. evidence_001)")
    source_id: str = Field(..., description="Authoritative registry ID (INCOIS_OSF, IMD_MARINE, MOSDAC_OCM, GIS_CADASTRE)")
    organization: str = Field(...)
    parameter: str = Field(...)
    value: Any = Field(...)
    unit: str = Field(default="")
    data_type: Literal["forecast", "observation", "advisory", "warning", "static"]
    valid_time: str
    retrieved_at: str
    source_url: str
    citation: str

class ToolExecutionResult(BaseModel):
    tool_name: str
    success: bool
    data: Any
    evidence_ids: List[str] = Field(default_factory=list)
    execution_time_ms: float = 0.0
    error: Optional[str] = None

class PlannerPlan(BaseModel):
    intent: IntentLiteral
    location: Dict[str, Any] = Field(..., description="Extracted or defaulted operational location")
    time_window: Dict[str, Any] = Field(..., description="Standardized temporal window metadata")
    required_agents: List[str] = Field(default_factory=list)
    required_tools: List[str] = Field(default_factory=list)
    detected_language: str = Field(default="English")
    location_assumed: bool = Field(default=False)
    assumption_notice: Optional[str] = None

class ConversationContext(BaseModel):
    location: Optional[str] = Field(default="Maharashtra Coastal Region")
    time_window: Optional[str] = Field(default="Tomorrow Morning")
    active_zone_id: Optional[str] = None
    previous_query: Optional[str] = None
    previous_intent: Optional[str] = None
    turn_count: int = Field(default=1)

class AgenticQueryRequest(BaseModel):
    query: str = Field(..., description="Natural language marine query")
    context: Optional[ConversationContext] = None
    stream_trace: bool = Field(default=False)

class FinalDecisionBlock(BaseModel):
    summary: str
    avoid_zones: List[Dict[str, Any]] = Field(default_factory=list)
    candidate_zones: List[Dict[str, Any]] = Field(default_factory=list)

class AgenticQueryResponse(BaseModel):
    query: str
    intent: str
    plan: PlannerPlan
    location: str
    time: str
    summary: str
    decision: FinalDecisionBlock
    zonesToAvoid: List[Dict[str, Any]]
    potentialZones: List[Dict[str, Any]]
    focusedZoneId: Optional[str] = None
    filterMode: Optional[str] = "all"
    confidenceLevel: Literal["High", "Medium", "Low"]
    confidenceScore: int
    confidenceExplanation: str
    agentTrace: List[AgentTraceStep]
    evidenceGraph: List[EvidenceGraphItem]
    keyAdvisories: List[str]
    limitations: List[str]
    disclaimer: str
    all_zones: List[Dict[str, Any]]
    evidence_coverage: float = Field(default=0.95, description="Factual evidence coverage metric")
    target_language: str = Field(default="en", description="Output response language")
    executionTimeMs: float

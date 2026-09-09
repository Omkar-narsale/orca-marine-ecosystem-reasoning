from typing import Optional, List, Dict, Any, Literal, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
from backend.app.core.tracing import generate_request_id

AgentStatusLiteral = Literal["QUEUED", "RUNNING", "COMPLETE", "PARTIAL", "FAILED"]

class QueryIntent(str, Enum):
    PFZ_DISCOVERY = "PFZ_DISCOVERY"
    MARINE_SAFETY = "MARINE_SAFETY"
    MARINE_CONDITIONS = "MARINE_CONDITIONS"
    HAZARD_ALERT = "HAZARD_ALERT"
    PRODUCTIVITY_SEARCH = "PRODUCTIVITY_SEARCH"
    ROUTE_PLANNING = "ROUTE_PLANNING"
    PRODUCTIVITY_ANALYSIS = "PRODUCTIVITY_ANALYSIS"
    RISK_AVOIDANCE = "RISK_AVOIDANCE"
    GENERAL_MARINE_QUERY = "GENERAL_MARINE_QUERY"
    SOURCE_QUERY = "SOURCE_QUERY"
    FOLLOW_UP = "FOLLOW_UP"
    COMPARISON = "COMPARISON"
    WHAT_IF = "WHAT_IF"

class ResponseType(str, Enum):
    CHAT = "CHAT"
    MARINE_CONDITIONS = "MARINE_CONDITIONS"
    SAFETY_ASSESSMENT = "SAFETY_ASSESSMENT"
    PFZ_RESULTS = "PFZ_RESULTS"
    HAZARD_ALERT = "HAZARD_ALERT"
    PRODUCTIVITY_RESULTS = "PRODUCTIVITY_RESULTS"
    PRODUCTIVITY_ANALYSIS = "PRODUCTIVITY_ANALYSIS"
    ROUTE_RESULT = "ROUTE_RESULT"
    RISK_MAP = "RISK_MAP"
    COMPARISON = "COMPARISON"
    SOURCE_EXPLANATION = "SOURCE_EXPLANATION"

# Union type supporting standard string literals and enum values for backward compatibility
IntentLiteral = Union[
    QueryIntent,
    str,
    Literal[
        "PFZ_DISCOVERY",
        "MARINE_SAFETY",
        "MARINE_CONDITIONS",
        "HAZARD_ALERT",
        "PRODUCTIVITY_SEARCH",
        "ROUTE_PLANNING",
        "PRODUCTIVITY_ANALYSIS",
        "RISK_AVOIDANCE",
        "GENERAL_MARINE_QUERY",
        "SOURCE_QUERY",
        "FOLLOW_UP",
        "COMPARISON",
        "WHAT_IF",
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
]

class QueryLocation(BaseModel):
    name: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    radius_km: Optional[float] = None
    state: Optional[str] = None
    coast: Optional[str] = None
    marine_bearing: Optional[str] = None
    bounds: Optional[Dict[str, float]] = None

class QueryTime(BaseModel):
    start: Optional[str] = None
    end: Optional[str] = None
    relative: Optional[str] = None
    display_label: Optional[str] = "Current / Tomorrow Morning"
    timezone: Optional[str] = "Asia/Kolkata"

class ParsedQueryIntent(BaseModel):
    intent: str
    location: QueryLocation = Field(default_factory=QueryLocation)
    time: QueryTime = Field(default_factory=QueryTime)
    parameters: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    origin: Optional[Dict[str, Any]] = None
    destination: Optional[Dict[str, Any]] = None
    previous_context: bool = False

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
    data_type: Literal["forecast", "observation", "advisory", "warning", "static", "cached", "unknown", "analysis", "FORECAST", "OBSERVATION", "ADVISORY", "WARNING", "STATIC", "CACHED", "UNKNOWN", "ANALYSIS"]
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
    intent: str
    location: Dict[str, Any] = Field(..., description="Extracted or defaulted operational location")
    time_window: Dict[str, Any] = Field(..., description="Standardized temporal window metadata")
    required_agents: List[str] = Field(default_factory=list)
    required_tools: List[str] = Field(default_factory=list)
    detected_language: str = Field(default="English")
    location_assumed: bool = Field(default=False)
    assumption_notice: Optional[str] = None
    parsed_intent: Optional[ParsedQueryIntent] = None

class ConversationContext(BaseModel):
    conversation_id: Optional[str] = None
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    current_intent: Optional[str] = None
    current_location: Optional[Dict[str, Any]] = None
    current_time_window: Optional[Dict[str, Any]] = None
    active_constraints: List[str] = Field(default_factory=list)
    origin: Optional[Dict[str, Any]] = None
    destination: Optional[Dict[str, Any]] = None
    previous_results: Optional[Dict[str, Any]] = None
    previous_data: Optional[Dict[str, Any]] = None
    active_map_layers: List[str] = Field(default_factory=list)
    selected_features: List[str] = Field(default_factory=list)
    language: str = Field(default="en")
    analysis_id: Optional[str] = None

    # Backward compatibility attributes
    location: Optional[str] = Field(default="Maharashtra Coastal Region")
    time_window: Optional[str] = Field(default="Tomorrow Morning")
    active_zone_id: Optional[str] = None
    previous_query: Optional[str] = None
    previous_intent: Optional[str] = None
    turn_count: int = Field(default=1)

class AgenticQueryRequest(BaseModel):
    query: str = Field(..., description="Natural language marine query")
    context: Optional[ConversationContext] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    language: Optional[str] = "en"
    stream_trace: bool = Field(default=False)
    is_demo_mode: bool = Field(default=False)

class FinalDecisionBlock(BaseModel):
    summary: str
    avoid_zones: List[Dict[str, Any]] = Field(default_factory=list)
    candidate_zones: List[Dict[str, Any]] = Field(default_factory=list)

class DynamicMapConfig(BaseModel):
    show_map: bool = Field(default=False)
    center: Dict[str, float] = Field(default_factory=lambda: {"lat": 18.9, "lng": 72.5})
    zoom: int = Field(default=9)
    layers: List[Dict[str, Any]] = Field(default_factory=list)
    features: List[Dict[str, Any]] = Field(default_factory=list)

class AgenticQueryResponse(BaseModel):
    request_id: str = Field(default_factory=generate_request_id, description="Trace ID: ORCA-YYYYMMDD-XXXX")
    conversation_id: Optional[str] = None
    query: str
    intent: str
    response_type: str = Field(default="CHAT")
    answer: str = Field(default="")
    summary: str = Field(default="")
    plan: Optional[PlannerPlan] = None
    location: Union[str, Dict[str, Any]] = Field(default="Maharashtra Coastal Waters")
    time: Union[str, Dict[str, Any]] = Field(default="Current / Tomorrow Morning")
    time_window: Optional[Dict[str, Any]] = None
    
    # Structured Intent Data & Results
    data: Dict[str, Any] = Field(default_factory=dict)
    results: List[Dict[str, Any]] = Field(default_factory=list)
    map: Optional[Dict[str, Any]] = Field(default_factory=dict)
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    warnings: List[Dict[str, Any]] = Field(default_factory=list)
    why_reasons: List[str] = Field(default_factory=list)
    
    # Conversational Multi-Turn Context & Suggestions
    follow_up_context: Dict[str, Any] = Field(default_factory=dict)
    follow_up_suggestions: List[str] = Field(default_factory=list)

    # Legacy & Auxiliary Fields (Preserving full compatibility)
    decision: Optional[FinalDecisionBlock] = None
    zonesToAvoid: List[Dict[str, Any]] = Field(default_factory=list)
    potentialZones: List[Dict[str, Any]] = Field(default_factory=list)
    focusedZoneId: Optional[str] = None
    filterMode: Optional[str] = "all"
    confidenceLevel: Literal["High", "Medium", "Low"] = "High"
    confidenceScore: int = 88
    confidenceExplanation: str = "Evidence corroborated across INCOIS and IMD sources."
    agentTrace: List[AgentTraceStep] = Field(default_factory=list)
    evidenceGraph: List[EvidenceGraphItem] = Field(default_factory=list)
    keyAdvisories: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    disclaimer: str = "Prototype risk screening only. Consult official IMD/INCOIS bulletins for operational navigation."
    all_zones: List[Dict[str, Any]] = Field(default_factory=list)
    evidence_coverage: float = Field(default=0.95)
    target_language: str = Field(default="en")
    executionTimeMs: float = 0.0
    latency_breakdown: Dict[str, float] = Field(default_factory=dict)
    sources_consulted: List[str] = Field(default_factory=lambda: ["INCOIS", "IMD", "MOSDAC", "GIS_CADASTRE"])
    is_demo_mode: bool = Field(default=False)
    data_mode_label: str = Field(default="LIVE / SCIENTIFIC DATA")

import re
from typing import Dict, Any, List, Optional
from backend.app.schemas.agentic import PlannerPlan, IntentLiteral, ConversationContext
from backend.app.services.temporal.alignment import parse_temporal_window
from backend.app.core.config import settings

class PlannerAgent:
    """
    Planner Agent: Entrypoint of the ORCA multi-agent intelligence graph.
    Decomposes natural language queries into structured tasks, selects required specialized agents,
    and binds tools without prematurely fabricating conclusions.
    """
    def plan(self, query_text: str, context: Optional[ConversationContext] = None) -> PlannerPlan:
        norm_query = query_text.lower().strip()

        # 1. Multi-turn context resolution
        effective_query = norm_query
        if context and context.previous_query:
            if "what about" in norm_query or "how about" in norm_query or "what about fishing" in norm_query:
                # Merge multi-turn context
                effective_query = f"{context.previous_query} {norm_query}"

        # 2. Intent Classification Priority
        # What-If Scenario Simulations
        if any(w in norm_query for w in ["what if", "suppose", "if wave", "if wind", "scenario", "increases by", "increase by"]):
            intent: IntentLiteral = "what_if_scenario"
        # Comparative Analysis
        elif any(w in norm_query for w in ["compare", "comparison", "difference between", "versus", "vs "]):
            intent = "risk_comparison"
        # Source Provenance & Evidence Inquiries
        elif any(w in norm_query for w in ["evidence", "source", "citation", "traceability", "where from", "who says", "which source", "what did incois"]):
            intent = "source_evidence"
        # Geofence & Boundary Checks
        elif any(w in norm_query for w in ["restricted", "restriction", "geofence", "naval", "fairway", "sanctuary", "boundary", "prohibited"]):
            intent = "geofence_check"
        # Zone Diagnostic Analysis
        elif any(w in norm_query for w in ["why is", "why", "root cause", "risk factors"]):
            intent = "zone_analysis"
        # Marine Hazards & Warnings
        elif any(w in norm_query for w in ["hazard", "squall", "warning", "storm", "cyclone", "gale"]):
            intent = "marine_hazard"
        # Marine Safety (Avoid / Danger / Risk queries take strict priority over fishing)
        elif any(w in norm_query for w in ["avoid", "avoided", "safety", "danger", "safe", "risk", "can i go", "operational window", "danger zones"]):
            intent = "marine_safety"
        # Fishing Suitability & Candidate Ranking
        elif any(w in norm_query for w in ["suitable", "fishing", "catch", "pfz", "fish", "chlorophyll", "best zone", "rank", "candidate"]):
            intent = "fishing_suitability"
        # Marine Forecast
        elif any(w in norm_query for w in ["wave", "waves", "swell", "sst", "temperature", "forecast only"]):
            intent = "marine_forecast"
        # Multilingual Hindi/Marathi safety keywords
        elif any(w in norm_query for w in ["बचना", "खतरनाक", "टाळावे", "धोका", "मासेमारी", "मछली"]):
            intent = "marine_safety"
        else:
            intent = "marine_safety"

        # 3. Location Extraction
        location_assumed = False
        assumption_notice = None
        
        if "zone a" in norm_query or "sector a" in norm_query or "vasai" in norm_query or "manori" in norm_query:
            loc_name = "North Offshore Sector (Vasai-Manori Reach, Zone A)"
            bounds = {"min_lat": 19.18, "max_lat": 19.42, "min_lon": 72.38, "max_lon": 72.68}
        elif "zone b" in norm_query or "sector b" in norm_query or "harbor" in norm_query or "jnpt" in norm_query:
            loc_name = "Mumbai Harbor Security & Fairway Corridor (Zone B)"
            bounds = {"min_lat": 18.86, "max_lat": 19.08, "min_lon": 72.52, "max_lon": 72.76}
        elif "zone c" in norm_query or "sector c" in norm_query or "alibag" in norm_query or "murud" in norm_query:
            loc_name = "South Coastal Offshore (Alibag-Murud Shelf, Zone C)"
            bounds = {"min_lat": 18.42, "max_lat": 18.75, "min_lon": 72.55, "max_lon": 72.86}
        elif "zone d" in norm_query or "sector d" in norm_query:
            loc_name = "Mid-Shelf Western Transition Trench (Zone D)"
            bounds = {"min_lat": 18.70, "max_lat": 18.98, "min_lon": 72.15, "max_lon": 72.48}
        elif "mumbai" in norm_query:
            loc_name = "Mumbai Coastal Waters (Lat 18.5°N - 19.5°N)"
            bounds = {"min_lat": 18.5, "max_lat": 19.5, "min_lon": 72.0, "max_lon": 73.0}
        elif "maharashtra" in norm_query:
            loc_name = "Maharashtra Coastal Continental Shelf (Lat 18.0°N - 20.0°N)"
            bounds = {"min_lat": 18.0, "max_lat": 20.0, "min_lon": 71.5, "max_lon": 73.5}
        else:
            loc_name = "Maharashtra Coastal Region (Lat 18.2°N - 19.5°N)"
            bounds = {"min_lat": settings.DEFAULT_MIN_LAT, "max_lat": settings.DEFAULT_MAX_LAT, "min_lon": settings.DEFAULT_MIN_LON, "max_lon": settings.DEFAULT_MAX_LON}
            location_assumed = True
            assumption_notice = "Defaulted analysis area to Maharashtra coastal continental shelf."

        # 4. Temporal Extraction
        temporal_meta = parse_temporal_window(effective_query)

        # 5. Agent & Tool Selection Strategy
        required_agents = ["planner", "ocean", "weather", "geospatial", "risk", "synthesis"]
        required_tools = [
            "get_wave_forecast",
            "get_coastal_winds",
            "get_marine_warnings",
            "check_zone_geofences",
            "calculate_zone_risk_scores",
            "compile_evidence_graph"
        ]

        if intent == "fishing_suitability":
            required_tools.extend(["get_sst", "get_pfz_advisories", "get_chlorophyll_observations", "evaluate_candidate_fishing_suitability"])
        elif intent == "geofence_check":
            required_tools.extend(["get_zone_polygons"])

        # 6. Language Detection
        detected_lang = "English"
        if any(w in query_text for w in ["कधी", "कुठे", "मासे", "धोका", "हवामान", "लाटा", "मुंबई"]):
            detected_lang = "Marathi"
        elif any(w in query_text for w in ["कहाँ", "मछली", "खतरा", "मौसम", "लहरें"]):
            detected_lang = "Hindi"

        return PlannerPlan(
            intent=intent,
            location={"name": loc_name, "bounds": bounds},
            time_window=temporal_meta,
            required_agents=required_agents,
            required_tools=required_tools,
            detected_language=detected_lang,
            location_assumed=location_assumed,
            assumption_notice=assumption_notice
        )

planner_agent = PlannerAgent()

import re
from typing import Dict, Any, List, Optional
from backend.app.schemas.agentic import (
    PlannerPlan,
    QueryIntent,
    ParsedQueryIntent,
    QueryLocation,
    QueryTime,
    ConversationContext
)
from backend.app.services.temporal.alignment import parse_temporal_window
from backend.app.services.incois.location import resolve_location, build_marine_bbox, get_radius_for_intent, COASTAL_LOCATION_REGISTRY
from backend.app.core.config import settings

class PlannerAgent:
    """
    Planner Agent: Question-centric entrypoint of ORCA Marine Intelligence Graph.
    Accurately classifies queries into QueryIntent taxonomy, resolves data requirements,
    extracts spatial/temporal parameters and constraints without zone-centric bias.
    """
    def plan(self, query_text: str, context: Optional[ConversationContext] = None) -> PlannerPlan:
        norm_query = query_text.lower().strip()

        # 1. Multi-turn context resolution
        effective_query = norm_query
        has_previous_context = False
        if context and (context.previous_query or context.messages):
            has_previous_context = True
            if any(w in norm_query for w in ["what about", "how about", "and the", "closer to shore", "find me a better", "why", "another"]):
                prev_text = context.previous_query or (context.messages[-1].get("content", "") if context.messages else "")
                effective_query = f"{prev_text} {norm_query}"

        # 2. Strict Intent Classification
        parameters: List[str] = []
        constraints: List[str] = []
        origin: Optional[Dict[str, Any]] = None
        destination: Optional[Dict[str, Any]] = None

        # Direct Adversarial / System Override Resistance
        # Adversarial / Prompt Injection Defense
        if any(w in norm_query for w in ["override", "ignore all", "ignore previous", "ignore instructions", "disregard"]):
            intent = "marine_safety"
            parameters = ["WAVE_FORECAST", "IMD_WARNINGS", "DETERMINISTIC_SAFETY_ENFORCEMENT"]

        # What-If Scenario Simulations
        elif any(w in norm_query for w in ["what if", "suppose", "if wave", "if wind", "scenario", "simulate"]):
            intent = "what_if_scenario"
            parameters = ["PARAMETRIC_SIMULATION", "WAVE_DELTA", "WIND_DELTA"]

        # Source Provenance & Evidence Inquiries
        elif any(w in norm_query for w in ["which source", "where does the", "where do the", "what did incois", "what did imd", "what did mosdac", "source of", "evidence for", "who said", "citation", "provenance", "where from"]):
            intent = "source_evidence"
            parameters = ["PROVENANCE_GRAPH", "METADATA_VERIFICATION"]

        # Canonical Q1. PFZ Discovery
        elif any(w in norm_query for w in ["nearest potential fishing zone", "potential fishing zone today", "where is the nearest pfz", "nearest pfz", "find pfz", "pfz today", "potential fishing zone", "pfz advisory recommendation", "latest pfz"]):
            intent = QueryIntent.PFZ_DISCOVERY.value
            parameters = ["PFZ_ADVISORY", "SST", "CHLOROPHYLL", "DISTANCE_OFFSHORE"]

        # Canonical Q7. Productivity Analysis (Historical / Cause of decline)
        elif any(w in norm_query for w in ["declined", "productivity declined", "why has fish productivity", "catch decreased", "why have fish catches reduced", "decline in fish"]):
            intent = QueryIntent.PRODUCTIVITY_ANALYSIS.value
            parameters = ["HISTORICAL_CHLOROPHYLL", "HISTORICAL_SST", "PFZ_HISTORY", "OCEAN_UPWELLING"]

        # Canonical Q6. Route Planning
        elif any(w in norm_query for w in ["safest route", "safe route", "best route", "navigation route", "passage plan", "route for a fishing vessel", "route for my vessel"]):
            intent = QueryIntent.ROUTE_PLANNING.value
            parameters = ["GIS_ROUTE", "COASTAL_WINDS", "WAVE_STATE", "SWELL", "NAVIGATIONAL_RESTRICTIONS"]

        # Canonical Q4. Hazard Alerts & Cyclones
        elif any(w in norm_query for w in ["lightning or cyclone", "cyclone alert", "cyclone alerts", "cyclone warning", "lightning alert", "active warning", "squall alert", "storm alert"]):
            intent = QueryIntent.HAZARD_ALERT.value
            parameters = ["IMD_NOWCAST", "IMD_CYCLONE_TRACK", "SQUALL_WARNINGS", "GIS_INTERSECTION"]

        # Canonical Q5. Productivity Search (Chlorophyll & Favourable SST)
        elif any(w in norm_query for w in ["high chlorophyll", "chlorophyll concentration and favourable", "favourable sea surface temperature", "favourable sst", "find a better area", "better area"]):
            intent = QueryIntent.PRODUCTIVITY_SEARCH.value
            parameters = ["CHLOROPHYLL", "SST", "SPATIAL_CANDIDATES", "PFZ_ADVISORY"]

        # Canonical Q3. Marine Conditions & Tides
        elif any(w in norm_query for w in ["tide, weather, and sea", "tide, weather", "tide and weather", "sea conditions near my fishing", "tide conditions", "weather, and sea conditions", "current conditions", "how are the waves", "what about the waves", "what about the wind", "how is the wind"]):
            intent = QueryIntent.MARINE_CONDITIONS.value
            parameters = ["WAVE_HEIGHT", "SWELL", "WIND_SPEED", "WIND_DIRECTION", "SST", "OCEAN_CURRENT", "TIDE"]

        # Canonical Q8. Risk Avoidance
        elif any(w in norm_query for w in ["zones should be avoided due to hazardous", "hazardous marine conditions or geofencing", "avoidance areas", "hazard zones to avoid"]):
            intent = QueryIntent.RISK_AVOIDANCE.value
            parameters = ["WAVE_HAZARDS", "IMD_WARNINGS", "NAVAL_GEOFENCES", "RESTRICTED_AREAS"]

        # Canonical Q2. Marine Safety Assessment
        elif any(w in norm_query for w in ["safe to venture into the sea", "safe to venture", "safe to go fishing", "is it safe to venture", "is it safe to", "can i go out to sea", "safety advisory"]):
            intent = QueryIntent.MARINE_SAFETY.value
            parameters = ["WAVE_FORECAST", "SWELL", "COASTAL_WINDS", "IMD_WARNINGS", "INCOIS_ADVISORY", "GEOFENCE_STATUS"]

        # Diagnostic & Geofence Checks
        elif any(w in norm_query for w in ["why is", "why zone", "why a", "why are", "why c", "root cause", "what evidence supports"]):
            intent = "zone_analysis"
            parameters = ["ZONE_DIAGNOSTICS", "FACTOR_BREAKDOWN"]

        elif any(w in norm_query for w in ["restricted by", "naval anchorage", "geofence", "naval buffer", "prohibited", "fairway corridor", "restricted zones", "is zone b restricted", "restricted for fishing", "restricted areas", "shipping lane", "security buffer"]):
            intent = "geofence_check"
            parameters = ["NAVAL_GEOFENCES", "PORT_CADASTRE"]

        elif any(w in norm_query for w in ["compare", "comparison", "difference between", "versus", "vs "]):
            intent = "risk_comparison"
            parameters = ["MULTI_FEATURE_COMPARISON"]

        elif any(w in norm_query for w in ["source", "evidence", "who said", "citation", "provenance", "where from"]):
            intent = "source_evidence"
            parameters = ["PROVENANCE_GRAPH", "METADATA_VERIFICATION"]

        elif any(w in norm_query for w in ["which fishing zones should be avoided", "which zones should be avoided", "avoided", "avoid 2 zones"]):
            intent = "marine_safety"
            parameters = ["WAVE_FORECAST", "IMD_WARNINGS"]

        elif any(w in norm_query for w in ["suitable", "suitability", "fishing candidate", "fishing", "catch", "fish", "rank candidate"]):
            intent = "fishing_suitability"
            parameters = ["CHLOROPHYLL", "SST", "PFZ_ADVISORY"]

        elif any(w in norm_query for w in ["बचना", "खतरनाक", "टाळावे", "धोका"]):
            intent = "marine_safety"
            parameters = ["WAVE_FORECAST", "IMD_WARNINGS"]

        else:
            intent = "marine_safety"
            parameters = ["GENERAL_TELEMETRY"]

        # Constraints extraction
        if any(w in norm_query for w in ["closer to shore", "nearshore", "near shore", "close to coast"]):
            constraints.append("PROXIMITY_TO_SHORE")
        if any(w in norm_query for w in ["small craft", "motorized", "artisanal"]):
            constraints.append("SMALL_CRAFT_LIMITS")

        # 3. Dynamic Location & Geometry Resolution
        location_assumed = False
        assumption_notice = None

        has_explicit_loc = any(k in norm_query for k in COASTAL_LOCATION_REGISTRY.keys()) or any(k in norm_query for k in ["zone a", "zone b", "zone c", "zone d", "vasai", "alibag", "mumbai", "maharashtra", "nagapattinam", "chennai", "kochi", "goa", "veraval", "paradip", "visakhapatnam", "mangalore", "kanyakumari"])

        if "zone a" in norm_query or "vasai" in norm_query:
            loc_name = "North Offshore Sector (Vasai-Manori Reach, Zone A)"
            bounds = {"min_lat": 19.18, "max_lat": 19.42, "min_lon": 72.38, "max_lon": 72.68}
            q_loc = QueryLocation(name=loc_name, lat=19.3, lon=72.5, radius_km=25.0, bounds=bounds)
        elif "zone b" in norm_query or "harbor" in norm_query:
            loc_name = "Mumbai Harbor Security & Fairway Corridor (Zone B)"
            bounds = {"min_lat": 18.86, "max_lat": 19.08, "min_lon": 72.52, "max_lon": 72.76}
            q_loc = QueryLocation(name=loc_name, lat=18.97, lon=72.64, radius_km=20.0, bounds=bounds)
        elif "zone c" in norm_query or "alibag" in norm_query:
            loc_name = "South Coastal Offshore (Alibag-Murud Shelf, Zone C)"
            bounds = {"min_lat": 18.42, "max_lat": 18.75, "min_lon": 72.55, "max_lon": 72.86}
            q_loc = QueryLocation(name=loc_name, lat=18.58, lon=72.7, radius_km=25.0, bounds=bounds)
        elif "zone d" in norm_query:
            loc_name = "Mid-Shelf Western Transition Trench (Zone D)"
            bounds = {"min_lat": 18.70, "max_lat": 18.98, "min_lon": 72.15, "max_lon": 72.48}
            q_loc = QueryLocation(name=loc_name, lat=18.84, lon=72.31, radius_km=25.0, bounds=bounds)
        elif has_explicit_loc:
            resolved_loc = resolve_location(norm_query)
            radius = get_radius_for_intent(intent)
            bbox = build_marine_bbox(resolved_loc.latitude, resolved_loc.longitude, radius_km=radius, marine_bearing=resolved_loc.marine_bearing)
            loc_name = f"{resolved_loc.name} ({resolved_loc.state})"
            bounds = {"min_lat": bbox["min_lat"], "max_lat": bbox["max_lat"], "min_lon": bbox["min_lon"], "max_lon": bbox["max_lon"]}
            q_loc = QueryLocation(
                name=loc_name,
                lat=resolved_loc.latitude,
                lon=resolved_loc.longitude,
                radius_km=radius,
                state=resolved_loc.state,
                coast=resolved_loc.coast,
                marine_bearing=resolved_loc.marine_bearing,
                bounds=bounds
            )
        elif context and (context.current_location or context.location):
            ctx_loc = context.current_location
            if ctx_loc and isinstance(ctx_loc, dict) and "lat" in ctx_loc:
                loc_name = ctx_loc.get("name", "Previous Selected Coastal Region")
                lat = ctx_loc["lat"]
                lon = ctx_loc["lon"]
                radius = ctx_loc.get("radius_km", 30.0)
                bounds = ctx_loc.get("bounds") or build_marine_bbox(lat, lon, radius_km=radius)
                q_loc = QueryLocation(name=loc_name, lat=lat, lon=lon, radius_km=radius, bounds=bounds)
            else:
                loc_str = context.location or "Maharashtra Coastal Region"
                resolved_loc = resolve_location(loc_str)
                radius = get_radius_for_intent(intent)
                bbox = build_marine_bbox(resolved_loc.latitude, resolved_loc.longitude, radius_km=radius, marine_bearing=resolved_loc.marine_bearing)
                loc_name = f"{resolved_loc.name} ({resolved_loc.state})"
                bounds = {"min_lat": bbox["min_lat"], "max_lat": bbox["max_lat"], "min_lon": bbox["min_lon"], "max_lon": bbox["max_lon"]}
                q_loc = QueryLocation(
                    name=loc_name,
                    lat=resolved_loc.latitude,
                    lon=resolved_loc.longitude,
                    radius_km=radius,
                    state=resolved_loc.state,
                    coast=resolved_loc.coast,
                    marine_bearing=resolved_loc.marine_bearing,
                    bounds=bounds
                )
        else:
            resolved_loc = resolve_location(norm_query)
            radius = get_radius_for_intent(intent)
            bbox = build_marine_bbox(resolved_loc.latitude, resolved_loc.longitude, radius_km=radius, marine_bearing=resolved_loc.marine_bearing)
            loc_name = f"{resolved_loc.name} ({resolved_loc.state})"
            bounds = {"min_lat": bbox["min_lat"], "max_lat": bbox["max_lat"], "min_lon": bbox["min_lon"], "max_lon": bbox["max_lon"]}
            q_loc = QueryLocation(
                name=loc_name,
                lat=resolved_loc.latitude,
                lon=resolved_loc.longitude,
                radius_km=radius,
                state=resolved_loc.state,
                coast=resolved_loc.coast,
                marine_bearing=resolved_loc.marine_bearing,
                bounds=bounds
            )
            if resolved_loc.name == "Mumbai Coastal Continental Shelf" and "mumbai" not in norm_query:
                location_assumed = True
                assumption_notice = "Defaulted analysis area to Maharashtra coastal continental shelf."

        # 4. Temporal Extraction
        temporal_meta = parse_temporal_window(effective_query)
        q_time = QueryTime(
            start=temporal_meta.get("start_iso"),
            end=temporal_meta.get("end_iso"),
            relative=temporal_meta.get("window_type", "now"),
            display_label=temporal_meta.get("display_label", "Current / Tomorrow Morning")
        )

        # 5. Selective Data Requirements & Tools Mapping
        required_tools: List[str] = [
            "get_wave_forecast",
            "get_coastal_winds",
            "get_marine_warnings",
            "check_zone_geofences",
            "calculate_zone_risk_scores",
            "compile_evidence_graph"
        ]
        required_agents = ["planner", "ocean", "weather", "geospatial", "risk", "synthesis"]

        if intent in (QueryIntent.PFZ_DISCOVERY.value, "PFZ_DISCOVERY"):
            required_tools = ["get_pfz_advisories", "get_sst", "get_chlorophyll_observations", "get_gis_distance"]
            required_agents = ["planner", "ocean", "geospatial", "synthesis"]
        elif intent in (QueryIntent.MARINE_CONDITIONS.value, "MARINE_CONDITIONS"):
            required_tools = ["get_wave_forecast", "get_coastal_winds", "get_sst", "get_ocean_currents", "get_tide_tables"]
            required_agents = ["planner", "ocean", "weather", "synthesis"]
        elif intent in (QueryIntent.HAZARD_ALERT.value, "HAZARD_ALERT"):
            required_tools = ["get_marine_warnings", "get_cyclone_track", "check_spatial_intersection"]
            required_agents = ["planner", "weather", "geospatial", "synthesis"]
        elif intent in (QueryIntent.PRODUCTIVITY_SEARCH.value, "PRODUCTIVITY_SEARCH", "fishing_suitability"):
            required_tools.extend(["get_chlorophyll_observations", "get_sst", "get_pfz_advisories", "evaluate_candidate_fishing_suitability"])
            required_agents = ["planner", "ocean", "weather", "geospatial", "risk", "synthesis"]
        elif intent in (QueryIntent.ROUTE_PLANNING.value, "ROUTE_PLANNING"):
            required_tools = ["get_gis_route", "get_wave_forecast", "get_coastal_winds", "check_zone_geofences", "evaluate_route_risk"]
            required_agents = ["planner", "geospatial", "ocean", "weather", "risk", "synthesis"]
        elif intent in (QueryIntent.PRODUCTIVITY_ANALYSIS.value, "PRODUCTIVITY_ANALYSIS"):
            required_tools = ["get_historical_chlorophyll", "get_historical_sst", "get_upwelling_index", "compare_time_series"]
            required_agents = ["planner", "ocean", "risk", "synthesis"]
        elif intent == "geofence_check":
            required_tools = ["check_zone_geofences", "get_zone_polygons"]
            required_agents = ["planner", "geospatial", "synthesis"]

        # 6. Language Detection
        detected_lang = "English"
        if any(w in query_text for w in ["कधी", "कुठे", "मासे", "धोका", "हवामान", "लाटा", "मुंबई", "चांगले"]):
            detected_lang = "Marathi"
        elif any(w in query_text for w in ["कहाँ", "मछली", "खतरा", "मौसम", "लहरें", "कौन"]):
            detected_lang = "Hindi"

        parsed_intent_obj = ParsedQueryIntent(
            intent=str(intent),
            location=q_loc,
            time=q_time,
            parameters=parameters,
            constraints=constraints,
            origin=origin,
            destination=destination,
            previous_context=has_previous_context
        )

        return PlannerPlan(
            intent=str(intent),
            location={"name": loc_name, "bounds": bounds, "lat": q_loc.lat, "lon": q_loc.lon},
            time_window=temporal_meta,
            required_agents=list(set(required_agents)),
            required_tools=required_tools,
            detected_language=detected_lang,
            location_assumed=location_assumed,
            assumption_notice=assumption_notice,
            parsed_intent=parsed_intent_obj
        )

planner_agent = PlannerAgent()

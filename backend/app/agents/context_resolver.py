import re
from typing import Dict, Any, Optional, List
from backend.app.schemas.agentic import ConversationContext, QueryIntent, QueryLocation
from backend.app.services.temporal.alignment import parse_temporal_window
from backend.app.services.incois.location import resolve_location, COASTAL_LOCATION_REGISTRY

class ConversationalContextResolver:
    """
    Question-Centric Context Resolver.
    Maintains conversational memory, resolves pronouns, follow-ups, parameter focuses,
    and preserves active constraints (e.g. shore proximity, vessel limits, time shifts).
    """
    def resolve_context(
        self,
        current_query: str,
        context: Optional[ConversationContext] = None
    ) -> Dict[str, Any]:
        norm = current_query.lower().strip()
        
        # State Initialization
        resolved_intent: Optional[str] = None
        resolved_zone_id: Optional[str] = None
        resolved_compare_zone_ids: Optional[List[str]] = None
        time_changed = False
        new_time_query: Optional[str] = None
        is_source_query = False
        is_map_command = False
        map_action = None
        filter_mode = None
        proximity_constraint = False
        exclude_previous_candidate = False
        added_constraints: List[str] = []
        needs_location_prompt = False

        prev_zone = context.active_zone_id if context else None
        prev_time = context.time_window if context else "Tomorrow Morning"
        prev_loc = context.location if context else "Maharashtra Coastal Region"
        prev_intent = (context.current_intent or context.previous_intent) if context else None
        active_constraints = list(context.active_constraints) if (context and context.active_constraints) else []

        # 1. Shore Proximity & Constraint Modifiers ("closer to shore", "near shore", "nearshore")
        if any(w in norm for w in ["closer to shore", "near shore", "nearshore", "close to coast", "near the coast"]):
            proximity_constraint = True
            added_constraints.append("PROXIMITY_TO_SHORE")
            resolved_intent = QueryIntent.PRODUCTIVITY_SEARCH.value
            filter_mode = "safe"

        # 2. Candidate Iteration & Switching to Better Area ("find me a better area", "another option")
        elif any(w in norm for w in ["find me a better area", "better area", "another option", "give me another", "other candidate", "different zone", "different area"]):
            exclude_previous_candidate = True
            resolved_intent = QueryIntent.PRODUCTIVITY_SEARCH.value
            filter_mode = "safe"

        # 3. Parameter-Specific Follow-ups ("what about the waves?", "what about the wind?")
        elif any(w in norm for w in ["what about waves", "what about the waves", "how are the waves", "waves?"]):
            resolved_intent = QueryIntent.MARINE_CONDITIONS.value
        elif any(w in norm for w in ["what about wind", "what about the wind", "and the wind", "how is the wind", "wind?"]):
            resolved_intent = QueryIntent.MARINE_CONDITIONS.value
        elif any(w in norm for w in ["what about tide", "what about the tide", "how is the tide", "tide?"]):
            resolved_intent = QueryIntent.MARINE_CONDITIONS.value
        elif any(w in norm for w in ["is it suitable for fishing", "suitable for fishing", "can i fish here"]):
            resolved_intent = QueryIntent.PRODUCTIVITY_SEARCH.value
            filter_mode = "safe"

        # 4. Map Filter Commands
        elif any(w in norm for w in ["show risky", "show hazards", "highlight risky", "display risk"]):
            is_map_command = True
            resolved_intent = "map_command"
            filter_mode = "hazards"
            map_action = "FILTER_HAZARDS"
        elif any(w in norm for w in ["show suitable", "show safe", "show candidates", "highlight candidates"]):
            is_map_command = True
            resolved_intent = "map_command"
            filter_mode = "safe"
            map_action = "FILTER_SAFE"
        elif any(w in norm for w in ["show restricted", "show restrictions", "show geofence", "restricted areas"]):
            is_map_command = True
            resolved_intent = "map_command"
            filter_mode = "restricted"
            map_action = "FILTER_RESTRICTED"
        elif any(w in norm for w in ["show all", "reset map", "zoom out", "show map"]):
            is_map_command = True
            resolved_intent = "map_command"
            filter_mode = "all"
            map_action = "SHOW_ALL"
        elif "zoom to" in norm or "focus on" in norm or norm.startswith("zoom ") or norm.startswith("show me zone") or norm.startswith("show zone"):
            is_map_command = True
            resolved_intent = "map_command"
            if "zone a" in norm or "sector a" in norm or " a" in norm:
                resolved_zone_id = "zone-a"
            elif "zone b" in norm or "sector b" in norm or " b" in norm:
                resolved_zone_id = "zone-b"
            elif "zone c" in norm or "sector c" in norm or " c" in norm:
                resolved_zone_id = "zone-c"
            elif "zone d" in norm or "sector d" in norm or " d" in norm:
                resolved_zone_id = "zone-d"
            map_action = f"FOCUS_ZONE_{resolved_zone_id}"

        # 5. Source Inquiries
        elif any(w in norm for w in ["which source", "what source", "who said", "what did incois say", "what did imd say", "where from", "show evidence", "sources", "source citation"]):
            is_source_query = True
            resolved_intent = "source_evidence"
            if "zone a" in norm:
                resolved_zone_id = "zone-a"
            elif "zone b" in norm:
                resolved_zone_id = "zone-b"
            elif "zone c" in norm:
                resolved_zone_id = "zone-c"
            else:
                resolved_zone_id = prev_zone or "zone-a"

        # 6. Comparisons
        elif any(w in norm for w in ["compare", "difference between", "versus", "vs "]):
            resolved_intent = "risk_comparison"
            resolved_compare_zone_ids = []
            if "zone a" in norm or "sector a" in norm or re.search(r"\b(a)\b", norm):
                resolved_compare_zone_ids.append("zone-a")
            if "zone b" in norm or "sector b" in norm or re.search(r"\b(b)\b", norm):
                resolved_compare_zone_ids.append("zone-b")
            if "zone c" in norm or "sector c" in norm or re.search(r"\b(c)\b", norm):
                resolved_compare_zone_ids.append("zone-c")
            if "zone d" in norm or "sector d" in norm or re.search(r"\b(d)\b", norm):
                resolved_compare_zone_ids.append("zone-d")
            if len(resolved_compare_zone_ids) < 2:
                resolved_compare_zone_ids = ["zone-a", "zone-c"]

        # 7. "Why?" / Root Cause Follow-up
        elif norm in ("why?", "why", "why avoid?", "why is it risky?", "why should i avoid it?", "reasons?"):
            resolved_intent = "zone_analysis"
            resolved_zone_id = prev_zone or "zone-a"

        # 8. What about Zone X follow-up
        elif re.search(r"what about (?:zone|sector)?\s*([a-d])", norm) or norm in ("what about a?", "what about b?", "what about c?", "what about d?"):
            m = re.search(r"what about (?:zone|sector)?\s*([a-d])", norm)
            if m:
                char = m.group(1).lower()
                resolved_zone_id = f"zone-{char}"
            else:
                resolved_zone_id = "zone-c"
            resolved_intent = "zone_analysis"

        # 9. Temporal Shift Follow-ups (e.g. 'What about tomorrow evening?', 'What about today?', 'tomorrow night?')
        elif (norm.startswith("what about") or norm.startswith("how about") or len(norm.split()) <= 4) and any(w in norm for w in ["evening", "afternoon", "night", "tomorrow night", "today", "now", "next 12 hours", "next 24 hours", "this weekend"]):
            time_changed = True
            new_time_query = current_query
            resolved_intent = prev_intent or "marine_safety"
            resolved_zone_id = prev_zone

        # 10. Explicit Zone Mention for legacy benchmarks
        elif "zone a" in norm or "vasai" in norm:
            resolved_zone_id = "zone-a"
        elif "zone b" in norm or "harbor" in norm or "fairway" in norm:
            resolved_zone_id = "zone-b"
        elif "zone c" in norm or "alibag" in norm or "murud" in norm:
            resolved_zone_id = "zone-c"
        elif "zone d" in norm:
            resolved_zone_id = "zone-d"

        # Combine constraints
        all_constraints = list(set(active_constraints + added_constraints))

        return {
            "resolved_intent": resolved_intent,
            "resolved_zone_id": resolved_zone_id or prev_zone,
            "resolved_compare_zone_ids": resolved_compare_zone_ids,
            "time_changed": time_changed,
            "new_time_query": new_time_query,
            "is_source_query": is_source_query,
            "is_map_command": is_map_command,
            "map_action": map_action,
            "filter_mode": filter_mode,
            "proximity_constraint": proximity_constraint or ("PROXIMITY_TO_SHORE" in all_constraints),
            "exclude_previous_candidate": exclude_previous_candidate,
            "active_constraints": all_constraints,
            "needs_location_prompt": needs_location_prompt,
            "previous_intent": prev_intent,
            "previous_location": prev_loc,
            "previous_time": prev_time
        }

context_resolver = ConversationalContextResolver()

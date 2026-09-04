import re
from typing import Dict, Any, Optional, Tuple
from backend.app.schemas.agentic import ConversationContext, IntentLiteral
from backend.app.services.temporal.alignment import parse_temporal_window

class ConversationalContextResolver:
    """
    Context Resolver: Resolves conversational references, pronouns, follow-up queries,
    and parameter overrides (e.g. time window shifts, comparative queries, source inquiries).
    """
    def resolve_context(
        self,
        current_query: str,
        context: Optional[ConversationContext] = None
    ) -> Dict[str, Any]:
        norm = current_query.lower().strip()
        
        # Default state
        resolved_intent: Optional[str] = None
        resolved_zone_id: Optional[str] = None
        resolved_compare_zone_ids: Optional[list[str]] = None
        time_changed = False
        new_time_query: Optional[str] = None
        is_source_query = False
        is_map_command = False
        map_action = None
        filter_mode = None

        prev_zone = context.active_zone_id if context else None
        prev_time = context.time_window if context else "Tomorrow Morning"
        prev_loc = context.location if context else "Maharashtra Coastal Region"
        prev_intent = context.previous_intent if context else "marine_safety"

        # 1. Natural Language Map Commands
        if any(w in norm for w in ["show risky", "show hazards", "highlight risky", "display risk"]):
            is_map_command = True
            resolved_intent = "map_command"
            filter_mode = "hazards"
            map_action = "FILTER_HAZARDS"
        elif any(w in norm for w in ["show suitable", "show safe", "show candidates", "highlight candidates"]):
            is_map_command = True
            resolved_intent = "map_command"
            filter_mode = "safe"
            map_action = "FILTER_SAFE"
        elif any(w in norm for w in ["show restricted", "show restrictions", "show geofence"]):
            is_map_command = True
            resolved_intent = "map_command"
            filter_mode = "restricted"
            map_action = "FILTER_RESTRICTED"
        elif any(w in norm for w in ["show all", "reset map", "zoom out", "show map"]):
            is_map_command = True
            resolved_intent = "map_command"
            filter_mode = "all"
            map_action = "SHOW_ALL"
        elif "zoom to" in norm or "focus on" in norm or "show zone" in norm:
            is_map_command = True
            resolved_intent = "map_command"
            if "zone a" in norm:
                resolved_zone_id = "zone-a"
            elif "zone b" in norm:
                resolved_zone_id = "zone-b"
            elif "zone c" in norm:
                resolved_zone_id = "zone-c"
            elif "zone d" in norm:
                resolved_zone_id = "zone-d"
            map_action = f"FOCUS_ZONE_{resolved_zone_id}"

        # 2. Source & Provenance Inquiries
        elif any(w in norm for w in ["which source", "what source", "who said", "what did incois say", "what did imd say", "where from", "show evidence", "source citation"]):
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

        # 3. Zone Comparison Query
        elif any(w in norm for w in ["compare", "difference between", "versus", "vs"]):
            resolved_intent = "risk_comparison"
            resolved_compare_zone_ids = []
            if "zone a" in norm or "sector a" in norm:
                resolved_compare_zone_ids.append("zone-a")
            if "zone b" in norm or "sector b" in norm:
                resolved_compare_zone_ids.append("zone-b")
            if "zone c" in norm or "sector c" in norm:
                resolved_compare_zone_ids.append("zone-c")
            if "zone d" in norm or "sector d" in norm:
                resolved_compare_zone_ids.append("zone-d")
            if len(resolved_compare_zone_ids) < 2:
                resolved_compare_zone_ids = ["zone-a", "zone-c"] # Default benchmark comparison

        # 4. "Why?" / "Why Avoid?" / Root Cause Follow-up
        elif norm in ("why?", "why", "why avoid?", "why is it risky?", "why should i avoid it?", "reasons?"):
            resolved_intent = "zone_analysis"
            resolved_zone_id = prev_zone or "zone-a"

        # 5. "What about Zone X?" Follow-up
        elif re.search(r"what about (zone|sector)\s*([a-d])", norm):
            m = re.search(r"what about (zone|sector)\s*([a-d])", norm)
            char = m.group(2).lower()
            resolved_zone_id = f"zone-{char}"
            resolved_intent = "zone_analysis" if prev_intent == "zone_analysis" else "fishing_suitability" if prev_intent == "fishing_suitability" else "marine_safety"

        # 6. Temporal Shifts ("What about tomorrow evening?", "What about next 12 hours?", "What about today?")
        elif any(w in norm for w in ["evening", "afternoon", "night", "tomorrow night", "today", "now", "next 12 hours", "next 24 hours", "next 48 hours"]):
            time_changed = True
            new_time_query = current_query
            resolved_intent = prev_intent or "marine_safety"
            resolved_zone_id = prev_zone

        # 7. Single Zone Mention
        elif "zone a" in norm or "vasai" in norm:
            resolved_zone_id = "zone-a"
        elif "zone b" in norm or "harbor" in norm or "fairway" in norm:
            resolved_zone_id = "zone-b"
        elif "zone c" in norm or "alibag" in norm or "murud" in norm:
            resolved_zone_id = "zone-c"
        elif "zone d" in norm:
            resolved_zone_id = "zone-d"

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
            "inherited_location": prev_loc,
            "inherited_time_window": prev_time,
            "has_context": bool(context and context.previous_query)
        }

context_resolver = ConversationalContextResolver()

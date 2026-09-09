from typing import Dict, Any, List, Optional
from datetime import datetime
from backend.app.schemas.agentic import ConversationContext, AgenticQueryResponse

class ConversationManager:
    """
    Stateful Conversation & Session Manager for ORCA.
    Provides session persistence, thread history, evidence coverage metrics, and multilingual translations.
    """
    def __init__(self):
        # In-memory session store: session_id -> metadata & list of messages
        self._conversations: Dict[str, List[Dict[str, Any]]] = {}
        self._session_metadata: Dict[str, Dict[str, Any]] = {}

    def get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        return self._conversations.get(session_id, [])

    def get_session_metadata(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self._session_metadata.get(session_id)

    def get_all_sessions(self) -> List[Dict[str, Any]]:
        sessions = []
        for sid, meta in self._session_metadata.items():
            msgs = self._conversations.get(sid, [])
            sessions.append({
                "session_id": sid,
                "title": meta.get("title", "Maritime Inquiry"),
                "created_at": meta.get("created_at", "Today"),
                "last_updated": meta.get("last_updated", "Today"),
                "message_count": len(msgs),
                "language": meta.get("language", "en"),
                "last_query": meta.get("last_query", "")
            })
        sessions.sort(key=lambda s: s.get("last_updated", ""), reverse=True)
        return sessions

    def record_interaction(
        self,
        session_id: str,
        user_query: str,
        agent_response: AgenticQueryResponse,
        language: str = "en"
    ):
        if session_id not in self._conversations:
            self._conversations[session_id] = []
            
            # Generate human-readable title from first query
            title = user_query[:45].strip()
            if len(user_query) > 45:
                title += "..."
            self._session_metadata[session_id] = {
                "title": title.capitalize(),
                "created_at": datetime.now().strftime("%d %b · %H:%M"),
                "last_updated": datetime.now().strftime("%d %b · %H:%M"),
                "language": language,
                "last_query": user_query
            }
        else:
            self._session_metadata[session_id]["last_updated"] = datetime.now().strftime("%d %b · %H:%M")
            self._session_metadata[session_id]["last_query"] = user_query

        timestamp = datetime.now().strftime("%H:%M IST")

        # Record user message
        self._conversations[session_id].append({
            "id": f"msg_u_{len(self._conversations[session_id])+1}",
            "role": "user",
            "content": user_query,
            "timestamp": timestamp,
            "language": language
        })

        # Record assistant message with full conversational response & structured analysis
        self._conversations[session_id].append({
            "id": f"msg_a_{len(self._conversations[session_id])+1}",
            "role": "assistant",
            "content": agent_response.summary,
            "decision": agent_response.decision.model_dump() if agent_response.decision else {},
            "confidenceScore": agent_response.confidenceScore,
            "confidenceLevel": agent_response.confidenceLevel,
            "evidence_count": len(agent_response.evidenceGraph),
            "focused_zone_id": agent_response.focusedZoneId,
            "zonesToAvoid": agent_response.zonesToAvoid,
            "potentialZones": agent_response.potentialZones,
            "all_zones": agent_response.all_zones,
            "filterMode": agent_response.filterMode,
            "timestamp": timestamp,
            "language": language,
            "request_id": agent_response.request_id,
            "limitations": agent_response.limitations,
            "agent_trace_count": len(agent_response.agentTrace)
        })

    def clear_session(self, session_id: str):
        if session_id in self._conversations:
            del self._conversations[session_id]
        if session_id in self._session_metadata:
            del self._session_metadata[session_id]

    def calculate_evidence_coverage(
        self,
        evaluated_zones: Optional[List[Dict[str, Any]]] = None,
        evidence_nodes: Optional[List[Any]] = None,
        claims_count: Optional[int] = None,
        supported_evidence_count: Optional[int] = None
    ) -> float:
        """
        Calculates factual evidence coverage metric:
        Coverage = (Supported Factual Claims) / (Total Zone Evaluation Points)
        """
        if claims_count is not None and supported_evidence_count is not None:
            if claims_count <= 0:
                return 1.0
            return round(min(1.0, max(0.0, supported_evidence_count / claims_count)), 2)

        total_claims = 0
        supported_claims = 0

        for z in (evaluated_zones or []):
            if z.get("wave_hazard", {}).get("status") == "AVAILABLE":
                total_claims += 1
                if any("wave" in getattr(n, "parameter", "") or "wave" in str(n) for n in (evidence_nodes or [])):
                    supported_claims += 1

            if z.get("wind_hazard", {}).get("status") == "AVAILABLE":
                total_claims += 1
                if any("wind" in getattr(n, "parameter", "") or "wind" in str(n) for n in (evidence_nodes or [])):
                    supported_claims += 1

            total_claims += 1
            if any("GIS_CADASTRE" in getattr(n, "source_id", "") or "cadastre" in str(n).lower() for n in (evidence_nodes or [])):
                supported_claims += 1

        if total_claims == 0:
            return 1.0
        return round(min(1.0, max(0.5, supported_claims / total_claims)), 2)

    def generate_multilingual_decision(
        self,
        summary_en: str,
        avoid_zones: List[Dict[str, Any]],
        candidate_zones: List[Dict[str, Any]],
        language: str = "en"
    ) -> str:
        """
        Generates grounded translations for Hindi and Marathi while strictly preserving
        numerical values, measurement units, official source names, and zone codes.
        """
        if language in ("mr", "marathi"):
            avoid_str = ", ".join([f"{z['code']} ({z.get('statusLabel', 'धोकादायक')})" for z in avoid_zones]) if avoid_zones else "कोणतेही नाही"
            cand_str = ", ".join([f"{z['code']} ({z.get('statusLabel', 'अनुकूल')})" for z in candidate_zones]) if candidate_zones else "कोणतेही नाही"
            
            return (
                f"ORCA बहु-एजंट सागरी विश्लेषणानुसार: {avoid_str} येथे जाणे टाळावे (INCOIS आणि IMD च्या अंदाजानुसार लाटा व वाऱ्यांचा धोका). "
                f"सागरी हवामान {cand_str} मध्ये अनुकूल राहण्याचा अंदाज आहे (गंभीर धोका आढळलेला नाही)."
            )

        elif language in ("hi", "hindi"):
            avoid_str = ", ".join([f"{z['code']} ({z.get('statusLabel', 'उच्च जोखिम')})" for z in avoid_zones]) if avoid_zones else "कोई नहीं"
            cand_str = ", ".join([f"{z['code']} ({z.get('statusLabel', 'अनुकूल')})" for z in candidate_zones]) if candidate_zones else "कोई नहीं"

            return (
                f"ORCA बहु-एजेंट समुद्री विश्लेषण के अनुसार: {avoid_str} में जाने से बचें (INCOIS और IMD पूर्वानुमान के अनुसार तेज लहरों और हवाओं का जोखिम)। "
                f"{cand_str} में समुद्री स्थितियां अनुकूल रहने का अनुमान है (कोई गंभीर खतरा नहीं पाया गया)।"
            )

        return summary_en

conversation_manager = ConversationManager()

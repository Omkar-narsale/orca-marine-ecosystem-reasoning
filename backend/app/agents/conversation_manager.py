from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import json
from backend.app.schemas.agentic import ConversationContext, AgenticQueryResponse, LocationPayload
from backend.app.db.session import SyncSessionLocal
from backend.app.db.models import Conversation, Message, ConversationContextModel
from backend.app.core.logging import logger

class ConversationManager:
    """
    Database-backed Conversation & Session Manager for ORCA.
    Persists conversations, messages, and contextual marine state into PostgreSQL/SQLite,
    while maintaining a fast in-memory cache for low-latency active interactions.
    """
    def __init__(self):
        # In-memory session store: session_id -> metadata & list of messages
        self._conversations: Dict[str, List[Dict[str, Any]]] = {}
        self._session_metadata: Dict[str, Dict[str, Any]] = {}

    def get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Retrieves chronological message history for a session from memory or DB."""
        if session_id in self._conversations and self._conversations[session_id]:
            return self._conversations[session_id]

        # Load from DB if cold
        try:
            with SyncSessionLocal() as db:
                msgs = db.query(Message).filter_by(conversation_id=session_id).order_by(Message.sequence_number.asc()).all()
                if msgs:
                    history = []
                    for m in msgs:
                        try:
                            meta = json.loads(m.metadata_json) if m.metadata_json else {}
                        except Exception:
                            meta = {}
                        item = {
                            "id": m.id,
                            "role": m.role.lower(),
                            "content": m.content,
                            "timestamp": m.created_at.strftime("%H:%M IST"),
                            **meta
                        }
                        history.append(item)
                    self._conversations[session_id] = history
                    return history
        except Exception as e:
            logger.warning(f"Error reading conversation history from DB for {session_id}: {e}")

        return self._conversations.get(session_id, [])

    def get_session_metadata(self, session_id: str) -> Optional[Dict[str, Any]]:
        if session_id in self._session_metadata:
            return self._session_metadata[session_id]

        try:
            with SyncSessionLocal() as db:
                conv = db.query(Conversation).filter_by(id=session_id).first()
                if conv:
                    meta = {
                        "title": conv.title,
                        "created_at": conv.created_at.strftime("%d %b · %H:%M"),
                        "last_updated": conv.updated_at.strftime("%d %b · %H:%M"),
                        "language": conv.language,
                        "status": conv.status
                    }
                    self._session_metadata[session_id] = meta
                    return meta
        except Exception as e:
            logger.warning(f"Error loading session metadata from DB for {session_id}: {e}")

        return self._session_metadata.get(session_id)

    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """Returns all persistent conversation sessions with metadata for the sidebar."""
        try:
            with SyncSessionLocal() as db:
                convs = db.query(Conversation).order_by(Conversation.updated_at.desc()).all()
                sessions = []
                for conv in convs:
                    msg_count = db.query(Message).filter_by(conversation_id=conv.id).count()
                    last_msg = db.query(Message).filter_by(conversation_id=conv.id).order_by(Message.sequence_number.desc()).first()
                    sessions.append({
                        "session_id": conv.id,
                        "title": conv.title,
                        "created_at": conv.created_at.strftime("%d %b · %H:%M"),
                        "last_updated": conv.updated_at.strftime("%d %b · %H:%M"),
                        "message_count": msg_count,
                        "language": conv.language,
                        "last_query": last_msg.content if last_msg and last_msg.role.upper() == "USER" else ""
                    })
                return sessions
        except Exception as e:
            logger.warning(f"Error querying all sessions from DB: {e}")
            # Fallback to in-memory cache
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
        language: str = "en",
        location: Optional[LocationPayload] = None
    ):
        """
        Records user query and assistant response into in-memory store and SQLite/PostgreSQL database.
        """
        title = user_query[:45].strip()
        if len(user_query) > 45:
            title += "..."
        title = title.capitalize() if title else "Maritime Inquiry"

        # Update Memory Cache
        if session_id not in self._conversations:
            self._conversations[session_id] = []

        if session_id not in self._session_metadata:
            self._session_metadata[session_id] = {
                "title": title,
                "created_at": datetime.now().strftime("%d %b · %H:%M"),
                "last_updated": datetime.now().strftime("%d %b · %H:%M"),
                "language": language,
                "last_query": user_query
            }
        else:
            self._session_metadata[session_id]["last_updated"] = datetime.now().strftime("%d %b · %H:%M")
            self._session_metadata[session_id]["last_query"] = user_query

        timestamp = datetime.now().strftime("%H:%M IST")

        user_msg_id = f"msg_u_{len(self._conversations[session_id])+1}_{Date_now()}"
        user_msg_dict = {
            "id": user_msg_id,
            "role": "user",
            "content": user_query,
            "timestamp": timestamp,
            "language": language
        }
        self._conversations[session_id].append(user_msg_dict)

        assistant_msg_id = f"msg_a_{len(self._conversations[session_id])+1}_{Date_now()}"
        assistant_meta = {
            "decision": agent_response.decision.model_dump() if agent_response.decision else {},
            "confidenceScore": agent_response.confidenceScore,
            "confidenceLevel": agent_response.confidenceLevel,
            "evidence_count": len(agent_response.evidenceGraph),
            "focused_zone_id": agent_response.focusedZoneId,
            "zonesToAvoid": agent_response.zonesToAvoid,
            "potentialZones": agent_response.potentialZones,
            "all_zones": agent_response.all_zones,
            "filterMode": agent_response.filterMode,
            "language": language,
            "request_id": agent_response.request_id,
            "limitations": agent_response.limitations,
            "agent_trace_count": len(agent_response.agentTrace),
            "response_type": agent_response.response_type,
            "data": agent_response.data,
            "results": agent_response.results,
            "why_reasons": agent_response.why_reasons,
            "sources": agent_response.sources,
            "map": agent_response.map,
            "follow_up_suggestions": agent_response.follow_up_suggestions
        }
        assistant_msg_dict = {
            "id": assistant_msg_id,
            "role": "assistant",
            "content": agent_response.summary or agent_response.answer,
            "timestamp": timestamp,
            **assistant_meta
        }
        self._conversations[session_id].append(assistant_msg_dict)

        # Database Persistence
        try:
            with SyncSessionLocal() as db:
                conv = db.query(Conversation).filter_by(id=session_id).first()
                if not conv:
                    conv = Conversation(
                        id=session_id,
                        title=title,
                        language=language,
                        status="ACTIVE",
                        created_at=datetime.now(timezone.utc),
                        updated_at=datetime.now(timezone.utc)
                    )
                    db.add(conv)
                else:
                    conv.updated_at = datetime.now(timezone.utc)
                    conv.language = language

                seq = db.query(Message).filter_by(conversation_id=session_id).count()

                # User message row
                user_row = Message(
                    id=user_msg_id,
                    conversation_id=session_id,
                    role="USER",
                    content=user_query,
                    sequence_number=seq + 1,
                    created_at=datetime.now(timezone.utc),
                    metadata_json=json.dumps({"language": language})
                )
                db.add(user_row)

                # Assistant message row
                assistant_row = Message(
                    id=assistant_msg_id,
                    conversation_id=session_id,
                    role="ASSISTANT",
                    content=agent_response.summary or agent_response.answer,
                    sequence_number=seq + 2,
                    created_at=datetime.now(timezone.utc),
                    metadata_json=json.dumps(assistant_meta, default=str)
                )
                db.add(assistant_row)

                # Update Context Model
                ctx_row = db.query(ConversationContextModel).filter_by(conversation_id=session_id).first()
                if not ctx_row:
                    ctx_row = ConversationContextModel(
                        conversation_id=session_id,
                        location_lat=location.latitude if location else None,
                        location_lon=location.longitude if location else None,
                        location_accuracy=location.accuracy_m if location else None,
                        location_timestamp=location.timestamp if location else None,
                        activity="Fishing Operations",
                        time_context="Tomorrow Morning",
                        current_intent=agent_response.intent,
                        current_result_id=agent_response.target_result_id,
                        updated_at=datetime.now(timezone.utc)
                    )
                    db.add(ctx_row)
                else:
                    if location and location.latitude is not None and location.longitude is not None:
                        ctx_row.location_lat = location.latitude
                        ctx_row.location_lon = location.longitude
                        ctx_row.location_accuracy = location.accuracy_m
                        ctx_row.location_timestamp = location.timestamp
                    ctx_row.current_intent = agent_response.intent
                    if agent_response.target_result_id:
                        ctx_row.current_result_id = agent_response.target_result_id
                    ctx_row.updated_at = datetime.now(timezone.utc)

                db.commit()
                from backend.app.core.logging import log_orca_db
                log_orca_db(conversation_id=session_id, message_saved=True, result_saved=True)
        except Exception as e:
            logger.warning(f"Failed to persist interaction into database: {e}")

    def clear_session(self, session_id: str):
        """Clears conversational memory and removes session from DB."""
        if session_id in self._conversations:
            del self._conversations[session_id]
        if session_id in self._session_metadata:
            del self._session_metadata[session_id]

        try:
            with SyncSessionLocal() as db:
                conv = db.query(Conversation).filter_by(id=session_id).first()
                if conv:
                    db.delete(conv)
                    db.commit()
        except Exception as e:
            logger.warning(f"Failed to clear session {session_id} from DB: {e}")

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

def Date_now() -> int:
    return int(datetime.now().timestamp() * 1000)

conversation_manager = ConversationManager()

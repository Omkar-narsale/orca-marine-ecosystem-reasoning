"""
Conversation Result Registry for ORCA.
Maintains active session entities (routes, PFZ candidates, hazard polygons, marine telemetry)
with persistent database storage (SQLAlchemy) and an in-memory cache layer.
Enables zero-fetch action queries ("Show it on map", "Why?", "Compare them") that survive server restarts.
"""

from typing import Dict, Any, List, Optional
import uuid
import json
from datetime import datetime, timezone

from backend.app.schemas.agentic import (
    ConversationResultRegistry,
    ResultRegistryEntity,
    MapActionCommand
)
from backend.app.core.logging import logger
from backend.app.db.session import SyncSessionLocal
from backend.app.db.models import Conversation, AnalysisResult, ResultEntity, SourceEvidence

class ResultRegistryManager:
    """
    Hybrid database-backed & in-memory session registry for active conversational results.
    """
    def __init__(self):
        self._registries: Dict[str, ConversationResultRegistry] = {}

    def get_or_create_registry(self, conversation_id: str) -> ConversationResultRegistry:
        if not conversation_id:
            conversation_id = "default_session"
        
        if conversation_id in self._registries:
            return self._registries[conversation_id]
        
        # Try to rehydrate from DB first
        rehydrated = self._load_from_db(conversation_id)
        if rehydrated:
            self._registries[conversation_id] = rehydrated
            return rehydrated

        # Fresh fallback registry
        new_reg = ConversationResultRegistry(
            conversation_id=conversation_id,
            current_context={
                "location": "Operational Marine Sector",
                "time": "Current / Tomorrow Morning",
                "activity": "Fishing Operations",
                "vessel": "Artisanal / Motorized Small Craft",
                "active_constraints": []
            },
            last_result=None,
            results={
                "routes": [],
                "pfz_candidates": [],
                "hazards": [],
                "avoid_areas": [],
                "conditions": []
            },
            map_state={
                "center": {"lat": 18.9, "lng": 72.5},
                "zoom": 9,
                "selected_feature": None,
                "visible_features": []
            }
        )
        self._registries[conversation_id] = new_reg
        return new_reg

    def register_results(
        self,
        conversation_id: str,
        result_type: str,
        raw_results: List[Dict[str, Any]],
        data: Dict[str, Any],
        map_config: Optional[Dict[str, Any]] = None,
        summary: str = "",
        answer: str = "",
        why_reasons: Optional[List[str]] = None,
        evidence_nodes: Optional[List[Any]] = None,
        zones_to_avoid: Optional[List[Any]] = None,
        potential_zones: Optional[List[Any]] = None,
        focused_zone_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Registers result items with stable identifiers, updates memory registry,
        and persistently saves them to the database.
        """
        registry = self.get_or_create_registry(conversation_id)
        registered_entities: List[Dict[str, Any]] = []

        if result_type in ("ROUTE_RESULT", "route_planning"):
            routes_list = []
            for idx, r in enumerate(raw_results):
                r_id = r.get("id") or r.get("route_id") or f"route_{idx + 1}"
                entity = {
                    "id": r_id,
                    "type": "ROUTE",
                    "name": r.get("name", f"Passage Corridor {idx + 1}"),
                    "is_recommended": bool(r.get("is_recommended", idx == 0)),
                    "distance_nm": r.get("distance_nm", 0),
                    "distance_km": r.get("distance_km", 0),
                    "duration_hours": r.get("duration_hours") or r.get("estimated_transit_hours", 0),
                    "max_wave_height_m": r.get("max_wave_height_m") or r.get("max_wave_m", 1.2),
                    "avg_wind_speed_kts": r.get("avg_wind_speed_kts", 12),
                    "hazard_flags": r.get("hazard_flags") or r.get("hazard_avoidances", []),
                    "risk_index": r.get("risk_score") or r.get("risk_index", 20 if idx == 0 else 45),
                    "geometry": r.get("geometry") or {
                        "type": "LineString",
                        "coordinates": r.get("waypoints", [[72.8, 18.9], [72.6, 19.2]])
                    },
                    "source_refs": [
                        {"source": "GIS Navigational Cadastre", "type": "Fairway Constraints"},
                        {"source": "INCOIS Wave Watch III", "type": "Wave Swell Forecast"}
                    ],
                    "explanation": (why_reasons[0] if why_reasons and idx == 0 else "Navigational corridor evaluated under operational sea-state thresholds.")
                }
                routes_list.append(entity)
                registered_entities.append(entity)
            registry.results["routes"] = routes_list

        elif result_type in ("PFZ_RESULTS", "PRODUCTIVITY_RESULTS", "pfz_discovery", "productivity_search"):
            pfz_list = []
            for idx, p in enumerate(raw_results):
                p_id = p.get("id") or f"pfz_cand_{idx + 1}"
                entity = {
                    "id": p_id,
                    "type": "PFZ_CANDIDATE",
                    "name": p.get("name", f"PFZ Candidate {idx + 1}"),
                    "latitude": p.get("latitude") or p.get("lat"),
                    "longitude": p.get("longitude") or p.get("lon"),
                    "distance_km": p.get("distance_km", 0),
                    "bearing": p.get("bearing", "WSW"),
                    "sst_celsius": p.get("sst_celsius", 28.2),
                    "chlorophyll_mg_m3": p.get("chlorophyll_mg_m3", 3.0),
                    "confidence": p.get("confidence", "High"),
                    "recommendation": p.get("recommendation", "Favorable oceanographic conditions"),
                    "geometry": {
                        "type": "Point",
                        "coordinates": [p.get("longitude") or p.get("lon", 72.5), p.get("latitude") or p.get("lat", 18.9)]
                    },
                    "source_refs": [
                        {"source": "INCOIS PFZ Mission", "type": "Thermal-Chlorophyll Advisory"},
                        {"source": "MOSDAC OCM-3", "type": "Ocean Color"}
                    ]
                }
                pfz_list.append(entity)
                registered_entities.append(entity)
            registry.results["pfz_candidates"] = pfz_list

        elif result_type in ("HAZARD_ALERT", "hazard_alert"):
            hazards_list = []
            alerts = raw_results if raw_results else data.get("alerts", [])
            for idx, h in enumerate(alerts):
                h_id = h.get("alert_id") or f"hazard_{idx + 1}"
                entity = {
                    "id": h_id,
                    "type": "HAZARD_ALERT",
                    "title": h.get("title", "Marine Squall Alert"),
                    "severity": h.get("severity", "WARNING"),
                    "description": h.get("description", ""),
                    "valid_time": h.get("valid_time", "Today / Tomorrow"),
                    "source_name": h.get("source_name") or h.get("source", "IMD"),
                    "geometry": h.get("geometry") or {
                        "type": "Polygon",
                        "coordinates": [[[72.3, 19.1], [72.7, 19.1], [72.7, 19.5], [72.3, 19.5], [72.3, 19.1]]]
                    }
                }
                hazards_list.append(entity)
                registered_entities.append(entity)
            registry.results["hazards"] = hazards_list

        elif result_type in ("RISK_MAP", "SAFETY_ASSESSMENT", "risk_avoidance", "marine_safety"):
            avoid_list = []
            for idx, a in enumerate(raw_results):
                a_id = a.get("id") or f"avoid_area_{idx + 1}"
                entity = {
                    "id": a_id,
                    "type": "AVOID_AREA",
                    "name": a.get("name", f"Avoidance Sector {idx + 1}"),
                    "reason": a.get("reason", "Elevated physical sea state or navigational restriction"),
                    "risk_score": a.get("risk_score", 85),
                    "geometry": a.get("geometry") or {
                        "type": "Polygon",
                        "coordinates": [[[72.4, 19.2], [72.7, 19.2], [72.7, 19.4], [72.4, 19.4], [72.4, 19.2]]]
                    },
                    "source_refs": [
                        {"source": "INCOIS OSF", "type": "Wave Height Threshold"},
                        {"source": "IMD Coastal Warning", "type": "Squall Warning"}
                    ]
                }
                avoid_list.append(entity)
                registered_entities.append(entity)
            registry.results["avoid_areas"] = avoid_list

        elif result_type in ("MARINE_CONDITIONS", "marine_conditions"):
            cond = data.get("conditions", data)
            entity = {
                "id": f"cond_{uuid.uuid4().hex[:8]}",
                "type": "MARINE_CONDITIONS",
                "data": cond,
                "source_refs": [
                    {"source": "INCOIS Wave Watch III", "type": "Numerical Wave Forecast"},
                    {"source": "IMD Marine Bulletin", "type": "Coastal Wind Telemetry"}
                ]
            }
            registry.results["conditions"] = [entity]
            registered_entities.append(entity)

        # Update last result pointer
        registry.last_result = {
            "type": result_type,
            "entities_count": len(registered_entities),
            "primary_id": registered_entities[0]["id"] if registered_entities else None,
            "primary_name": registered_entities[0]["name"] if registered_entities and "name" in registered_entities[0] else None,
            "summary": summary,
            "answer": answer,
            "why_reasons": why_reasons or [],
            "evidence_nodes": evidence_nodes or [],
            "zones_to_avoid": zones_to_avoid or [],
            "potential_zones": potential_zones or [],
            "focused_zone_id": focused_zone_id
        }

        # Update map state if config provided
        if map_config and map_config.get("show_map"):
            registry.map_state = {
                "center": map_config.get("center", {"lat": 18.9, "lng": 72.5}),
                "zoom": map_config.get("zoom", 9),
                "selected_feature": registered_entities[0]["id"] if registered_entities else None,
                "visible_features": [e["id"] for e in registered_entities]
            }

        # Persist to Database asynchronously / synchronously
        self._save_to_db(
            conversation_id=conversation_id,
            result_type=result_type,
            entities=registered_entities,
            data=data,
            sources=evidence_nodes or []
        )

        return registered_entities

    def _save_to_db(
        self,
        conversation_id: str,
        result_type: str,
        entities: List[Dict[str, Any]],
        data: Dict[str, Any],
        sources: List[Any]
    ):
        """Persists analysis results, entities, and sources to SQLite/PostgreSQL."""
        try:
            with SyncSessionLocal() as db:
                # Ensure conversation row exists
                conv = db.query(Conversation).filter_by(id=conversation_id).first()
                if not conv:
                    conv = Conversation(
                        id=conversation_id,
                        title="Maritime Inquiry",
                        language="en",
                        status="ACTIVE"
                    )
                    db.add(conv)
                    db.flush()

                # Create AnalysisResult row
                result_id = f"res_{uuid.uuid4().hex[:12]}"
                res_record = AnalysisResult(
                    id=result_id,
                    conversation_id=conversation_id,
                    result_type=result_type,
                    payload_json=json.dumps(data, default=str),
                    created_at=datetime.now(timezone.utc)
                )
                db.add(res_record)
                db.flush()

                # Add Result Entities
                for e in entities:
                    entity_row = ResultEntity(
                        id=f"ent_{uuid.uuid4().hex[:12]}",
                        analysis_result_id=result_id,
                        conversation_id=conversation_id,
                        entity_type=e.get("type", "FEATURE"),
                        entity_id=str(e.get("id", "")),
                        name=str(e.get("name") or e.get("title", "Unnamed Feature")),
                        geometry_json=json.dumps(e.get("geometry", {}), default=str) if e.get("geometry") else None,
                        properties_json=json.dumps(e, default=str)
                    )
                    db.add(entity_row)

                # Add Source Evidence
                for s in sources:
                    s_dict = s.model_dump() if hasattr(s, "model_dump") else (s if isinstance(s, dict) else {"details": str(s)})
                    src_row = SourceEvidence(
                        id=f"ev_{uuid.uuid4().hex[:12]}",
                        analysis_result_id=result_id,
                        source=s_dict.get("source_id") or s_dict.get("organization") or "OFFICIAL_DATA",
                        dataset=s_dict.get("parameter"),
                        authority_type=s_dict.get("data_type", "FORECAST"),
                        valid_time=s_dict.get("valid_time"),
                        metadata_json=json.dumps(s_dict, default=str)
                    )
                    db.add(src_row)

                db.commit()
        except Exception as ex:
            logger.warning(f"Could not persist result to DB: {ex}")

    def _load_from_db(self, conversation_id: str) -> Optional[ConversationResultRegistry]:
        """Loads results and entities from SQLite/PostgreSQL if not present in memory."""
        try:
            with SyncSessionLocal() as db:
                results_rows = db.query(AnalysisResult).filter_by(conversation_id=conversation_id).order_by(AnalysisResult.created_at.desc()).all()
                if not results_rows:
                    return None

                results_dict: Dict[str, List[Dict[str, Any]]] = {
                    "routes": [],
                    "pfz_candidates": [],
                    "hazards": [],
                    "avoid_areas": [],
                    "conditions": []
                }

                entity_rows = db.query(ResultEntity).filter_by(conversation_id=conversation_id).all()
                for er in entity_rows:
                    try:
                        props = json.loads(er.properties_json) if er.properties_json else {}
                    except Exception:
                        props = {}
                    props["id"] = er.entity_id
                    props["name"] = er.name
                    if er.geometry_json:
                        try:
                            props["geometry"] = json.loads(er.geometry_json)
                        except Exception:
                            pass

                    if er.entity_type == "ROUTE":
                        results_dict["routes"].append(props)
                    elif er.entity_type == "PFZ_CANDIDATE":
                        results_dict["pfz_candidates"].append(props)
                    elif er.entity_type == "HAZARD_ALERT":
                        results_dict["hazards"].append(props)
                    elif er.entity_type == "AVOID_AREA":
                        results_dict["avoid_areas"].append(props)
                    elif er.entity_type == "MARINE_CONDITIONS":
                        results_dict["conditions"].append(props)

                latest_res = results_rows[0]
                last_result_obj = {
                    "type": latest_res.result_type,
                    "entities_count": len(entity_rows),
                    "primary_id": entity_rows[0].entity_id if entity_rows else None,
                    "primary_name": entity_rows[0].name if entity_rows else None,
                    "summary": f"Persistent result from {latest_res.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
                }

                return ConversationResultRegistry(
                    conversation_id=conversation_id,
                    current_context={
                        "location": "Operational Marine Sector",
                        "time": "Current / Tomorrow Morning",
                        "activity": "Fishing Operations",
                        "vessel": "Artisanal / Motorized Small Craft",
                        "active_constraints": []
                    },
                    last_result=last_result_obj,
                    results=results_dict,
                    map_state={
                        "center": {"lat": 18.9, "lng": 72.5},
                        "zoom": 9,
                        "selected_feature": entity_rows[0].entity_id if entity_rows else None,
                        "visible_features": [e.entity_id for e in entity_rows]
                    }
                )
        except Exception as ex:
            logger.warning(f"Could not load conversation results from DB: {ex}")
            return None

    def get_last_result(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        reg = self.get_or_create_registry(conversation_id)
        return reg.last_result

    def resolve_target_entity(
        self,
        conversation_id: str,
        target_id_or_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Finds a registered entity by ID or fuzzy name match.
        If no target specified, returns the recommended/primary entity from last result.
        """
        reg = self.get_or_create_registry(conversation_id)
        all_entities = []
        for cat in reg.results.values():
            if isinstance(cat, list):
                all_entities.extend(cat)

        if not all_entities:
            return None

        if target_id_or_name:
            t_lower = str(target_id_or_name).lower().strip()
            # Exact ID match
            for e in all_entities:
                if str(e.get("id", "")).lower() == t_lower:
                    return e
            # Name or title substring match
            for e in all_entities:
                if t_lower in str(e.get("name", "")).lower() or t_lower in str(e.get("title", "")).lower():
                    return e
            # Type-based target resolution
            if any(w in t_lower for w in ["route", "passage", "fairway", "corridor"]):
                for e in all_entities:
                    if e.get("type") == "ROUTE":
                        return e
            if any(w in t_lower for w in ["candidate", "pfz", "fishing area", "fishing zone"]):
                for e in all_entities:
                    if e.get("type") in ("PFZ_CANDIDATE", "AVOID_AREA"):
                        return e
            # Route / candidate index match (e.g. "first one", "route 1", "candidate 1")
            if any(w in t_lower for w in ["first", "1", "alpha", "recommended", "primary"]):
                return all_entities[0]
            if any(w in t_lower for w in ["second", "2", "bravo", "alternative"]) and len(all_entities) > 1:
                return all_entities[1]

        # Default to primary recommended entity
        for e in all_entities:
            if e.get("is_recommended"):
                return e

        return all_entities[0]

    def get_comparison_pair(
        self,
        conversation_id: str,
        target_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Returns pair of entities for comparison (e.g. Route 1 vs Route 2)."""
        reg = self.get_or_create_registry(conversation_id)
        routes = reg.results.get("routes", [])
        if len(routes) >= 2:
            return routes[:2]

        pfz = reg.results.get("pfz_candidates", [])
        if len(pfz) >= 2:
            return pfz[:2]

        avoid = reg.results.get("avoid_areas", [])
        if len(avoid) >= 2:
            return avoid[:2]

        return []

    def get_entities(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Returns all registered entities for the conversation."""
        reg = self.get_or_create_registry(conversation_id)
        all_entities = []
        for cat in reg.results.values():
            if isinstance(cat, list):
                all_entities.extend(cat)
        return all_entities

    def update_context(
        self,
        conversation_id: str,
        location: Optional[str] = None,
        time_label: Optional[str] = None,
        constraints: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        reg = self.get_or_create_registry(conversation_id)
        if location:
            reg.current_context["location"] = location
        if time_label:
            reg.current_context["time"] = time_label
        if constraints:
            current = set(reg.current_context.get("active_constraints", []))
            current.update(constraints)
            reg.current_context["active_constraints"] = list(current)
        return reg.current_context

    def clear_session(self, conversation_id: str):
        """Resets session registry when user creates a new chat."""
        if conversation_id in self._registries:
            del self._registries[conversation_id]

result_registry = ResultRegistryManager()

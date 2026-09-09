import pytest
import asyncio
from datetime import datetime, timezone
import json

from backend.app.db.session import init_db, SyncSessionLocal
from backend.app.db.models import Conversation, Message, ConversationContextModel, AnalysisResult, ResultEntity
from backend.app.agents.conversation_manager import conversation_manager
from backend.app.services.state.result_registry import result_registry
from backend.app.schemas.agentic import AgenticQueryResponse, LocationPayload, FinalDecisionBlock

@pytest.mark.asyncio
async def test_database_persistence_and_cache_rehydration():
    # 1. Initialize DB tables
    await init_db()

    session_id = f"test_db_persist_{int(datetime.now().timestamp())}"

    # 2. Record interaction via conversation_manager
    response = AgenticQueryResponse(
        request_id="ORCA-TEST-001",
        conversation_id=session_id,
        query="What are the safest fishing zones tomorrow?",
        intent="marine_safety",
        summary="Sector C (Alibag) is recommended. Avoid Sector A due to elevated wave hazards.",
        answer="Sector C (Alibag) is recommended. Avoid Sector A due to elevated wave hazards.",
        target_result_id="route_safe_1",
        decision=FinalDecisionBlock(
            summary="Sector C safe",
            avoid_zones=[{"code": "Sector A", "statusLabel": "Hazardous"}],
            candidate_zones=[{"code": "Sector C", "statusLabel": "Favorable"}]
        )
    )

    location = LocationPayload(
        latitude=18.92,
        longitude=72.83,
        accuracy_m=15.0,
        status="AVAILABLE"
    )

    conversation_manager.record_interaction(
        session_id=session_id,
        user_query="What are the safest fishing zones tomorrow?",
        agent_response=response,
        language="en",
        location=location
    )

    # 3. Register results via result_registry
    raw_routes = [
        {
            "id": "corridor_alpha",
            "name": "Southern Navigational Corridor",
            "is_recommended": True,
            "distance_nm": 14.2,
            "max_wave_height_m": 1.1,
            "avg_wind_speed_kts": 10,
            "geometry": {"type": "LineString", "coordinates": [[72.8, 18.9], [72.7, 18.6]]}
        }
    ]

    result_registry.register_results(
        conversation_id=session_id,
        result_type="ROUTE_RESULT",
        raw_results=raw_routes,
        data={"routes": raw_routes},
        summary="Route Corridor Alpha evaluated."
    )

    # 4. SIMULATE SERVER RESTART: Wipe all in-memory caches!
    conversation_manager._conversations.clear()
    conversation_manager._session_metadata.clear()
    result_registry._registries.clear()

    # 5. Verify database rehydration
    history = conversation_manager.get_conversation_history(session_id)
    assert len(history) >= 2, "Should rehydrate user & assistant messages from database"
    assert history[0]["content"] == "What are the safest fishing zones tomorrow?"
    assert "Sector C" in history[1]["content"]

    # Verify session metadata rehydrated
    sessions = conversation_manager.get_all_sessions()
    matching = [s for s in sessions if s["session_id"] == session_id]
    assert len(matching) == 1
    assert matching[0]["message_count"] >= 2

    # Verify result registry entity rehydrated from DB
    entity = result_registry.resolve_target_entity(session_id, "corridor_alpha")
    assert entity is not None, "Should resolve entity from DB after in-memory cache clear"
    assert entity["name"] == "Southern Navigational Corridor"
    assert entity["geometry"]["type"] == "LineString"

    # Verify DB direct row checks
    with SyncSessionLocal() as db:
        conv_row = db.query(Conversation).filter_by(id=session_id).first()
        assert conv_row is not None
        ctx_row = db.query(ConversationContextModel).filter_by(conversation_id=session_id).first()
        assert ctx_row is not None
        assert ctx_row.location_lat == 18.92
        assert ctx_row.location_lon == 72.83

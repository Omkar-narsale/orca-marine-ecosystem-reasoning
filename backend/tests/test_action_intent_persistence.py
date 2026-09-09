import pytest
from datetime import datetime
from backend.app.agents.orchestrator import orchestrator, SESSION_CONTEXT_CACHE
from backend.app.services.state.result_registry import result_registry
from backend.app.agents.conversation_manager import conversation_manager
from backend.app.schemas.agentic import ConversationContext

@pytest.mark.asyncio
async def test_action_intent_show_on_map_resolves_after_cache_wipe(mock_pipeline_data):
    session_id = f"test_action_{int(datetime.now().timestamp())}"

    # 1. Register a dynamic route in session
    raw_routes = [
        {
            "id": "dynamic_route_99",
            "name": "Ratnagiri Safe Fairway Passage",
            "is_recommended": True,
            "geometry": {"type": "LineString", "coordinates": [[73.2, 16.9], [73.0, 17.2]]}
        }
    ]
    result_registry.register_results(
        conversation_id=session_id,
        result_type="ROUTE_RESULT",
        raw_results=raw_routes,
        data={"routes": raw_routes},
        summary="Safe passage planned."
    )

    # 2. Simulate server restart: clear memory cache
    result_registry._registries.clear()
    SESSION_CONTEXT_CACHE.clear()

    # 3. Ask "Show it on map"
    response = await orchestrator.run(
        query="Show that route on map",
        session_id=session_id
    )

    assert response.action_intent == "SHOW_ON_MAP"
    assert response.target_result_id == "dynamic_route_99"
    assert "Ratnagiri Safe Fairway Passage" in response.answer
    assert response.map is not None
    assert response.map["show_map"] is True

@pytest.mark.asyncio
async def test_new_chat_show_on_map_does_not_hallucinate_route(mock_pipeline_data):
    fresh_session_id = f"test_empty_chat_{int(datetime.now().timestamp())}"

    # No route was ever registered in this fresh session
    response = await orchestrator.run(
        query="Show the route on map",
        session_id=fresh_session_id
    )

    assert response.action_intent == "SHOW_ON_MAP"
    assert response.target_result_id is None
    assert "I don't have a marine result or feature to display on the map yet in this session" in response.answer
    assert "Route Alpha" not in response.answer

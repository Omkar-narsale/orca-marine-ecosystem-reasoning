import pytest
import asyncio
from backend.app.core.llm_config import LLMClient
from backend.app.services.incois.client import incois_connector
from backend.app.services.imd.client import imd_connector
from backend.app.services.mosdac.client import mosdac_connector
from backend.app.services.decision.route_engine import route_engine
from backend.app.agents.orchestrator import orchestrator
from backend.app.services.state.result_registry import result_registry
from backend.app.schemas.marine import DataStatusEnum

@pytest.mark.anyio
async def test_groq_missing_returns_no_fake_facts():
    """Test 1: When Groq API key is unconfigured, LLMClient returns structured LLM_UNAVAILABLE without fake facts."""
    client = LLMClient()
    # Force is_groq_available to False
    client.is_groq_available = False

    deterministic_ctx = {
        "intent": "marine_safety",
        "time": "Tomorrow 06:00 IST",
        "answer": "Deterministic safety evaluation completed.",
        "summary": "Deterministic safety summary."
    }

    res = await client.generate_chat_response(
        user_message="Why is Zone A dangerous?",
        deterministic_context=deterministic_ctx
    )

    assert res["status"] == "LLM_UNAVAILABLE"
    assert res["reason"] == "GROQ_API_KEY_NOT_CONFIGURED"
    assert res["provider"] == "deterministic_orchestrator"
    # Ensure it did not invent 4.1m, 30kt or hardcoded Zone A keywords
    assert "4.1m" not in res["text"]
    assert "30kt" not in res["text"]
    assert res["text"] == "Deterministic safety evaluation completed."

@pytest.mark.anyio
async def test_incois_unavailable_returns_data_unavailable():
    """Test 2: When INCOIS ERDDAP is forced to fail, it returns DATA_UNAVAILABLE without fabricated waves/SST."""
    res = await incois_connector.query_marine_telemetry(
        intent="SEA_CONDITIONS",
        location_query="Mumbai",
        time_expression="tomorrow morning",
        force_failure=True
    )

    assert res["status"] == DataStatusEnum.DATA_UNAVAILABLE.value
    assert res["record_count"] == 0
    assert len(res["all_records"]) == 0

@pytest.mark.anyio
async def test_imd_unavailable_raises_or_returns_no_fake_warnings():
    """Test 3: When IMD service fails, get_data raises or returns empty records rather than claiming clear skies."""
    with pytest.raises(ConnectionError):
        await imd_connector.get_data(force_failure=True)

@pytest.mark.anyio
async def test_mosdac_auth_missing_returns_no_fake_chlorophyll():
    """Test 4: When MOSDAC token is not provided, get_data returns empty records without fabricating chlorophyll."""
    mosdac_connector.api_token = None
    records = await mosdac_connector.get_data(min_lat=18.0, max_lat=20.0, min_lon=71.0, max_lon=73.0)
    assert len(records) == 0

    # Health check reflects auth required
    health = await mosdac_connector.health_check()
    assert "Auth Required" in health.status or "Configured / Auth Required" in health.status

@pytest.mark.anyio
async def test_route_engine_handles_dynamic_coordinates_and_geofences():
    """Test 5: Route engine dynamically computes distance and evaluates GIS geofences without static dicts."""
    res = route_engine.plan_operational_corridor(
        origin_coords=(18.92, 72.84),
        destination_coords=(18.58, 72.71),
        destination_name="South Shelf Grounds"
    )

    assert res["destination_name"] == "South Shelf Grounds"
    assert res["distance_km"] > 0
    assert res["distance_nm"] > 0
    assert len(res["waypoints"]) >= 2
    assert "navigational_disclaimer" in res

@pytest.mark.anyio
async def test_new_conversation_does_not_reuse_stale_results():
    """Test 6: A new session has empty result registry and does not return stale targets."""
    new_sess = "test_isolated_session_xyz_999"
    entity = result_registry.resolve_target_entity(new_sess)
    assert entity is None

    last_res = result_registry.get_last_result(new_sess)
    assert last_res is None

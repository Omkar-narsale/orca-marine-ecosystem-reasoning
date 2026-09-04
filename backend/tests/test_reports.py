import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app

@pytest.mark.anyio
async def test_marine_brief_report_generation():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/reports/marine-brief", json={
            "query": "Which fishing zones should be avoided tomorrow morning?",
            "region": "Maharashtra Coastal Shelf",
            "time_window": "Tomorrow Morning (05:00 - 14:00 IST)"
        })
        assert response.status_code == 200
        data = response.json()
        assert "ORCA OPERATIONAL MARINE INTELLIGENCE BRIEF" in data["report_title"]
        assert "operational_summary" in data
        assert len(data["operational_summary"]["avoid_sectors"]) >= 2
        assert len(data["evidence_provenance"]) > 0
        assert data["confidence_assessment"]["score"].endswith("%")
        assert len(data["scientific_limitations"]) > 0

@pytest.mark.anyio
async def test_user_feedback_submission():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/reports/feedback", json={
            "query": "Why is Zone A risky?",
            "useful": True,
            "rating": 5,
            "feedback_note": "Accurate wave citations from INCOIS and IMD."
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

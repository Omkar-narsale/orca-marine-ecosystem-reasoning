from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from backend.app.agents.orchestrator import orchestrator
from backend.app.core.tracing import generate_request_id

router = APIRouter(prefix="/reports", tags=["Marine Brief & Reports"])

class MarineBriefRequest(BaseModel):
    query: Optional[str] = Field("Which fishing zones should be avoided tomorrow morning?", description="Target scenario query")
    region: Optional[str] = Field("Maharashtra Coastal Shelf (Lat 18.2°N - 19.5°N)", description="Geographic bounding region")
    time_window: Optional[str] = Field("Tomorrow Morning (05:00 - 14:00 IST)", description="Temporal validity window")
    request_id: Optional[str] = None

class FeedbackRequest(BaseModel):
    query: str
    useful: bool
    rating: Optional[int] = Field(default=5, ge=1, le=5)
    feedback_note: Optional[str] = None

# In-memory feedback store
FEEDBACK_LOGS: List[Dict[str, Any]] = []

@router.post("/marine-brief", summary="Generate structured, auditable Marine Intelligence Brief")
async def generate_marine_brief(request: MarineBriefRequest):
    """
    Generates a formal, printable / exportable Marine Intelligence Brief with decision provenance,
    wave/wind telemetry metrics, official source citations, confidence rating, uncertainty estimation,
    and non-negotiable scientific safety disclaimers.
    """
    req_id = request.request_id or generate_request_id()
    result = await orchestrator.run(
        query=request.query or "Which fishing zones should be avoided tomorrow morning?",
        request_id=req_id
    )
    
    brief = {
        "orca_branding": "ORCA — Marine Ecosystem Reasoning with Collaborative Agents",
        "report_title": "ORCA OPERATIONAL MARINE INTELLIGENCE BRIEF",
        "request_id": result.request_id,
        "query": request.query or "Which fishing zones should be avoided tomorrow morning?",
        "generated_at": datetime.now().strftime("%d %b %Y %H:%M IST"),
        "reference_id": f"ORCA-MB-{result.request_id}",
        "geographic_sector": result.location,
        "temporal_envelope": result.time,
        "operational_summary": {
            "executive_decision": result.summary,
            "avoid_sectors": [
                {
                    "code": z["code"],
                    "name": z["name"],
                    "status": z["statusLabel"],
                    "risk_score": f"{z['riskScore']} / 100",
                    "primary_hazard": z["reasons"][0] if z["reasons"] else "Hazardous conditions",
                    "conditions": z["conditions"]
                }
                for z in result.zonesToAvoid
            ],
            "candidate_sectors": [
                {
                    "code": z["code"],
                    "name": z["name"],
                    "status": z["statusLabel"],
                    "risk_score": f"{z['riskScore']} / 100",
                    "suitability_summary": z["recommendation"],
                    "conditions": z["conditions"]
                }
                for z in result.potentialZones
            ]
        },
        "evidence_provenance": [
            {
                "evidence_id": node.id,
                "organization": node.organization,
                "parameter": node.parameter,
                "value": f"{node.value} {node.unit}".strip(),
                "data_type": node.data_type.upper(),
                "valid_time": node.valid_time,
                "source_url": node.source_url
            }
            for node in result.evidenceGraph[:8] # Include top evidence citations
        ],
        "sources": result.sources_consulted,
        "confidence_assessment": {
            "score": f"{result.confidenceScore}%",
            "level": result.confidenceLevel,
            "explanation": result.confidenceExplanation
        },
        "uncertainty_assessment": {
            "uncertainty_level": "Moderate",
            "explanation": "Epistemic forecast drift bounded to 12h horizon. Biological non-guarantee applies to PFZ."
        },
        "scientific_limitations": result.limitations,
        "governing_disclaimer": "This report is decision support, not a guarantee of fish presence, safe navigation, or legal authorization.",
        "latency_metrics": result.latency_breakdown
    }

    return brief

@router.post("/feedback", summary="Submit user feedback on ORCA analysis")
async def submit_user_feedback(feedback: FeedbackRequest):
    """Logs user thumbs up / down feedback and notes for system quality evaluation."""
    entry = {
        "timestamp": datetime.now().strftime("%d %b %Y %H:%M:%S IST"),
        "query": feedback.query,
        "useful": feedback.useful,
        "rating": feedback.rating,
        "note": feedback.feedback_note
    }
    FEEDBACK_LOGS.append(entry)
    return {"status": "success", "message": "Feedback recorded. Thank you for helping improve ORCA marine reasoning."}

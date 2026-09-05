from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.api.routes.marine import router as marine_router
from backend.app.api.routes.zones import router as zones_router
from backend.app.api.routes.geofences import router as geofences_router
from backend.app.api.routes.query import router as query_router
from backend.app.api.routes.agentic import router as agentic_router
from backend.app.api.routes.conversation import router as conversation_router
from backend.app.api.routes.alerts import router as alerts_router
from backend.app.api.routes.reports import router as reports_router
from backend.app.api.routes.weather import router as weather_router
from backend.app.api.routes.evidence import router as evidence_router
from backend.app.api.routes.health import router as health_router
from backend.app.api.routes.decision import router as decision_router
from backend.app.api.routes.scenario import router as scenario_router
from backend.app.api.routes.uncertainty import router as uncertainty_router
from backend.app.api.routes.evaluation import router as evaluation_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing ORCA Marine Intelligence FastAPI Backend v6.0.0 (Production Hardened, Observability, SIH Demo Readiness)...")
    yield
    logger.info("Shutting down ORCA Marine Intelligence Backend...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="6.0.0",
    description="Production Hardened Multi-Agent Marine Intelligence, Scenario Reasoning, Uncertainty Quantification, and Observability for ORCA (SIH 2026 Phase 6).",
    lifespan=lifespan
)

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root-level health routes (/health, /health/ready, /health/sources)
app.include_router(health_router)

# Include API Routers with prefix
app.include_router(decision_router)
app.include_router(scenario_router)
app.include_router(uncertainty_router)
app.include_router(evaluation_router)
app.include_router(conversation_router, prefix=settings.API_V1_STR)
app.include_router(alerts_router, prefix=settings.API_V1_STR)
app.include_router(reports_router, prefix=settings.API_V1_STR)
app.include_router(agentic_router, prefix=settings.API_V1_STR)
app.include_router(query_router, prefix=settings.API_V1_STR)
app.include_router(marine_router, prefix=settings.API_V1_STR)
app.include_router(zones_router, prefix=settings.API_V1_STR)
app.include_router(geofences_router, prefix=settings.API_V1_STR)
app.include_router(weather_router, prefix=settings.API_V1_STR)
app.include_router(evidence_router, prefix=settings.API_V1_STR)
app.include_router(health_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "service": "ORCA Marine Intelligence API",
        "phase": "Phase 6 Production Hardening, Observability & SIH Demo Readiness",
        "version": "6.0.0",
        "status": "online",
        "docs": "/docs",
        "health": "/health",
        "readiness": "/health/ready",
        "sources_health": "/health/sources",
        "agents": [
            "Planner Agent",
            "Ocean Agent",
            "Weather & Hazard Agent",
            "Geospatial Agent",
            "Risk & Evidence Agent",
            "Synthesis Agent"
        ],
        "languages_supported": ["en", "hi", "mr"],
        "tools_registered": 10,
        "sources": ["INCOIS", "IMD", "MOSDAC", "GIS_CADASTRE"]
    }

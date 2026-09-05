# ORCA Phase 6 System Audit & Architectural Baseline

**System**: ORCA (Marine EcOsystem Reasoning with Collaborative Agents)  
**Phase**: Phase 6 — Production Hardening, Observability, and SIH Demo Readiness  
**Audit Timestamp**: September 2026  
**Status**: Comprehensive Pre-Implementation Audit Complete

---

## 1. Executive Summary

ORCA is a map-first marine intelligence platform engineered for fishermen, coastal authorities, and marine decision-makers. Phases 1 through 5 established:
- Multi-source marine data integration (INCOIS, IMD, MOSDAC, GIS Maritime Cadastre).
- Deterministic risk, hazard, and suitability mathematical engines.
- Multi-agent reasoning graph (Planner, Ocean, Weather, Geospatial, Risk & Evidence, Synthesis).
- Conversational multi-turn context resolution and multilingual synthesis (English, Hindi, Marathi).
- Proactive safety alerts, evidence provenance tracking, and downloadable Marine Intelligence Briefs.
- Decision ranking (AHP-TOPSIS inspired), sensitivity simulation (What-If engine), and uncertainty quantification.

This Phase 6 audit assesses the stability, safety guarantees, error handling, observability, security posture, and demo readiness of the existing codebase.

---

## 2. Architecture & Components Breakdown

### 2.1 Backend Architecture (FastAPI + Python 3.13)
- **Directory**: `backend/app/`
- **Entry Points**: `backend/run.py`, `backend/app/main.py`
- **Core Modules**:
  - `backend/app/core/config.py`: Pydantic settings, endpoint configurations, bounding box definitions, caching TTLs.
  - `backend/app/core/logging.py`: Basic stream logging and source request logger.
  - `backend/app/core/cache.py`: In-memory TTL cache.
  - `backend/app/core/llm_config.py`: LLM provider integration with deterministic fallback.
- **Service Layers**:
  - `services/incois/`: INCOIS Ocean State Forecast (OSF), Sea Surface Temp (SST), and Potential Fishing Zone (PFZ) parser/client.
  - `services/imd/`: IMD coastal marine bulletins, wind telemetry, squall/cyclone warning parser/client.
  - `services/mosdac/`: ISRO MOSDAC Oceansat-3 (OCM-3) Chlorophyll-a satellite observation client.
  - `services/geospatial/`: Shapely geometry engine, Mumbai Naval Anchorage buffer, JNPT fairway TSS corridor, Malvan sanctuary geofence.
  - `services/risk/`: Deterministic hazard engine (`hazard_engine.py`), weighted risk scoring (`risk_engine.py`), fishing suitability (`suitability.py`), and synthesis confidence calculator (`confidence.py`).
  - `services/decision/`: Multi-criteria zone ranking (`ranking_engine.py`), zone trade-off comparator (`tradeoff_engine.py`), navigable route corridor planning (`route_engine.py`), and sensitivity simulation (`scenario_engine.py`).
  - `services/uncertainty/`: Epistemic/aleatoric uncertainty breakdown and multi-factor confidence scoring (`uncertainty_engine.py`).
  - `services/alerts/`: Proactive alert rules and acknowledgment store (`alert_engine.py`).
  - `services/temporal/`: Forecast window normalization and temporal alignment (`alignment.py`).
- **Agents Layer (6-Agent Directed Graph)**:
  - `Planner Agent`: Query decomposition, intent classification, spatial/temporal normalization.
  - `Ocean Agent`: INCOIS wave/SST tool execution.
  - `Weather & Hazard Agent`: IMD wind/cyclone bulletin tool execution.
  - `Geospatial Agent`: GIS cadastre geofence verification tool execution.
  - `Risk & Evidence Agent`: Deterministic mathematical risk scoring, zone classification, evidence graph synthesis.
  - `Synthesis Agent`: Natural language executive summaries, advisories, limitations, multilingual support.
  - `Context Resolver`: Multi-turn conversational entity tracking and pronoun resolution.

### 2.2 Frontend Architecture (Next.js 14 + React 18 + Tailwind CSS + Leaflet)
- **Framework**: Next.js 14 (App Router)
- **Core Components**:
  - `MarineMap.tsx`: Leaflet interactive marine cartography, zone polygons, ship route corridors, geofence buffers, tile layer management.
  - `Navbar.tsx`: Header navigation, live IST clock, What-If simulator trigger, Research benchmark trigger, Alerts modal trigger, Marine Brief trigger, language selector.
  - `Sidebar.tsx`: Navigation tabs, map focus filters, source health summary widget.
  - `AnalysisPanel.tsx`: Agent trace progress stepper, executive decision card, zone comparative ranking, confidence badge, multi-turn chat stream.
  - `EvidenceDrawer.tsx` / `EvidencePanel.tsx`: Full evidence node inspector, citations, source URLs, raw telemetry metadata.
  - `ConfidenceBreakdownModal.tsx`: Five-dimension confidence metric breakdown (Completeness, Freshness, Agreement, Coverage, Alignment).
  - `WhatIfScenarioModal.tsx`: Real-time wave/wind sensitivity sliders and delta modeling.
  - `ResearchEvaluationModal.tsx`: Benchmarks, reproducibility validator, human-in-the-loop review interface.
  - `MarineBriefModal.tsx`: Formal PDF-like printable intelligence report with executive decision and provenance.
  - `SafetyAlertsModal.tsx`: Proactive advisory list and acknowledgment management.

---

## 3. Data Sources & Integration Registry

| Source | Organization | Parameter(s) | Data Type | Nominal Cadence | Endpoint / Baseline |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **INCOIS** | Indian National Centre for Ocean Information Services | Significant wave height ($H_s$), Wave period ($T_p$), SST, PFZ advisories | Forecast / Advisory | 12-hourly numerical cycle | `https://incois.gov.in/oceanservices/osfforecast.jsp` |
| **IMD** | India Meteorological Department | 10m Surface wind speed/direction, Squall/Gale warnings, Cyclone bulletins | Forecast / Warning | 6-hourly bulletin / 3-hourly update | `https://api.imd.gov.in/public` |
| **MOSDAC** | ISRO Space Applications Centre | Chlorophyll-a concentration, Ocean color | Observation | Daily clear-sky swath pass | `https://www.mosdac.gov.in` |
| **GIS Cadastre** | National Hydrographic Office / Port Authority | Naval Security Envelopes, TSS Shipping Fairways, Marine Sanctuaries | Static Baseline | Hydrographic Revision 2026.1 | `https://hydro-india.nic.in` |

---

## 4. Current Test Suite Status

- **Runner**: Pytest 9.1.1 on Python 3.13
- **Current Collected Tests**: 112 items across 20 test modules
- **Pass Rate**: 112 passed in ~1.35 seconds
- **Test Modules**:
  - `test_agents.py`: Individual agent execution and state transitions.
  - `test_alerts.py`: Alert generation, deduplication, acknowledgment.
  - `test_context_resolver.py`: Multi-turn zone and intent resolution.
  - `test_evaluation_dataset.py`: Benchmark query parsing and gold dataset validation.
  - `test_geospatial.py`: Shapely polygon intersection and geofence boundary rules.
  - `test_imd.py`: IMD bulletin parsing and wind hazard checks.
  - `test_incois.py`: INCOIS wave and PFZ record normalization.
  - `test_multilingual.py`: Hindi and Marathi localized decision generation.
  - `test_normalization.py`: Unit and timestamp standardization.
  - `test_orchestrator.py`: Full 6-agent end-to-end pipeline.
  - `test_phase4_benchmarks.py`: Phase 4 quantitative benchmark evaluation.
  - `test_phase5_decision_ranking.py`: Multi-criteria zone ranking and candidate exclusion.
  - `test_phase5_research_evaluation.py`: Evaluation API routes and metrics reproducibility.
  - `test_phase5_uncertainty_confidence.py`: Uncertainty quantification and confidence dimension scoring.
  - `test_phase5_what_if_scenarios.py`: Sensitivity delta simulation.
  - `test_pipeline_integration.py`: Synthetic sensor stream integration.
  - `test_reports.py`: Marine brief generation and feedback submission.
  - `test_risk_engine.py`: Deterministic risk threshold equations and weights.
  - `test_temporal.py`: Temporal window matching and alignment.
  - `test_tools.py`: Tool registry and schema validation.

---

## 5. Identified Weaknesses & Phase 6 Target Enhancements

1. **Application Health & Readiness Endpoints**:
   - Current `/health` returns static or basic operational flags without distinguishing `HEALTHY`, `DEGRADED`, `UNAVAILABLE`, `UNKNOWN`.
   - Need standard top-level `/health`, `/health/ready`, `/health/sources` endpoints with latency, freshness, and last successful fetch.
2. **Marine Data Connector Resilience**:
   - HTTP clients need bounded retries with exponential backoff, timeout handling, and cache fallback explicitly tagged with `DATA_TYPE: CACHED`.
   - Missing data must never silently default to safe.
3. **Data Freshness Contract**:
   - Standardized helper functions across the backend for age calculation, freshness status (`LIVE`, `RECENT`, `FORECAST`, `ADVISORY`, `WARNING`, `CACHED`, `STALE`, `UNKNOWN`).
4. **Fail-Safe Safety Invariants**:
   - Ensure that `MISSING DATA != SAFE` and `FAILED GEOFENCE CHECK != UNRESTRICTED` in all hazard, geofence, suitability, and ranking pipelines.
   - Return `INSUFFICIENT_DATA` when critical wave/geofence information is missing.
5. **Request & Trace ID Propagation**:
   - Generate unique trace IDs (`ORCA-YYYYMMDD-XXXX`) at the API entry point and propagate through Planner, Agents, Tools, Risk Engine, Evidence Graph, and Synthesis.
   - Return real measured latency breakdown (`total_latency_ms`, `planner_latency_ms`, `tool_latency_ms`, `risk_engine_latency_ms`, `synthesis_latency_ms`).
6. **Structured JSON Logging & Security**:
   - Structured JSON logs with log levels (`DEBUG`, `INFO`, `WARNING`, `ERROR`), request IDs, and redaction of any sensitive credentials.
   - Comprehensive `.env.example` and audit of `.gitignore`.
7. **Prompt-Injection Defense**:
   - External retrieved marine telemetry must be treated strictly as untrusted data, never as executable instructions.
8. **Demo Scenario Suite & Demo Mode Indicator**:
   - Add a structured demo scenario library (`benchmarks/demo/scenarios.json` and python driver).
   - Display unambiguous `DEMO MODE` / `CONTROLLED DEMO DATA` indicators in the frontend when synthetic or recorded benchmark inputs are active.
9. **UI & Accessibility Polish**:
   - Compact system status bar, data trust indicators, polished error banners for source outages, keyboard navigation, and responsive layout hardening.
10. **Reproducibility & Deployment Documentation**:
    - Add `docs/REPRODUCIBILITY.md`, `docs/SAFETY.md`, `docs/DATA_SOURCES.md`, `docs/SETUP.md`, `docs/ARCHITECTURE.md`, `docs/DEMO.md`, `Dockerfile`, `docker-compose.yml`, and CI workflow.

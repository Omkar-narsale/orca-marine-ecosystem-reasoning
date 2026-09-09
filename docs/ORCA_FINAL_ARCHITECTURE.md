# ORCA Final Prototype Architecture

## 1. System Overview

**ORCA** (*Marine EcOsystem Reasoning with Collaborative Agents*) is a domain-specialized, multi-agent conversational decision support prototype designed for coastal mariners and artisanal fishing communities in maritime India. 

Developed as an SIH proof-of-concept, ORCA bridges the critical operational gap between raw, highly technical marine oceanography (e.g. numerical wave height rasters, atmospheric pressure isolines, satellite spectral reflectance) and the pragmatic daily decisions of fishermen: *"Can I venture out safely tomorrow morning?", "Why is this area recommended?", "Where is a lower-risk fishing area?", and "Why has fish productivity declined?"*.

### Core Design Principles:
1. **Zero Hallucinated Safety**: ORCA never states "100% safe". It uses calibrated language (*"conditions currently appear manageable"*, *"lower-risk candidate under retrieved conditions"*). If telemetry fails or is missing, it refuses to fabricate benign data and explicitly informs the user that safety cannot be confirmed.
2. **Deterministic Evidence Hierarchy**: The Large Language Model (Groq or local fallback) is strictly restricted to conversational phrasing and translation. It is never the scientific authority. Physical limits, risk scoring, polygon intersections, and ranking are computed deterministically.
3. **2-Layer Explainability**: Technical values (m, kt, °C, mg/m³) remain completely accessible under a secondary inspection layer (`[VIEW FULL EVIDENCE]`), while the primary response communicates in direct mariner terms: *What is happening?*, *What does it mean for me?*, *What should I do?*, *Why?*, and *What evidence supports it?*.

---

## 2. User Request Flow

The execution pathway for every conversational interaction follows a deterministic pipeline through specialized sub-agents:

```
USER QUERY (Text or Multilingual Audio via Web Speech API)
  │
  ▼
API ROUTE (`/api/v1/agentic/query`)
  │
  ▼
CONTEXT RESOLVER & REHYDRATION
  ├── SQLite Conversation Session State (`orca_marine.db`)
  ├── Live User GPS Coordinates (`lat`, `lon`, `accuracy_m`, `timestamp`)
  └── Multi-turn Constraints (e.g., "closer to shore", "compare", "why")
  │
  ▼
PLANNER AGENT (`backend/app/agents/planner_agent.py`)
  ├── Intent Taxonomy Classification (`QueryIntent`)
  ├── Spatial Scope & Marine Bounding Box Resolution
  └── Temporal Window Alignment (`ResolvedTimeWindow`)
  │
  ├── [Action Short-Circuit: SHOW_ON_MAP / EXPLAIN / COMPARE / SHOW_SOURCES]
  │     └── Cached Result Registry (`result_registry.py`) -> Zero re-fetch return
  │
  ▼
DATASET DISCOVERY & QUERY BUILDER
  ├── Discovery Engine (`discovery.py` & `registry.py`)
  ├── Parameter Requirements (`WAVE_HEIGHT`, `SURFACE_WIND`, `IMD_WARNINGS`, `CHLOROPHYLL`)
  └── ERDDAP & REST Query Builders (Griddap BBox, Tabledap filters)
  │
  ▼
DATA SOURCE ADAPTERS
  ├── INCOIS ERDDAP Client (`incois/client.py`)
  ├── IMD Coastal Bulletin Client (`imd/client.py`)
  ├── MOSDAC Satellite Client (`mosdac/client.py`)
  └── Bhuvan / Coastal Cadastre (`bhuvan/adapter.py` & `spatial_engine.py`)
  │
  ▼
DATA NORMALIZATION (`normalizer.py`)
  └── `NormalizedMarineRecord` (physical units, UTC timestamp, provenance citation)
  │
  ▼
EVIDENCE GRAPH GENERATION
  └── Provenance nodes linking assertions to source telemetry (`claim_evidence_map`)
  │
  ▼
DETERMINISTIC RISK & REASONING ENGINES
  ├── Wave & Wind Threshold Evaluation (`thresholds.py`)
  ├── Point-in-Polygon Geofencing (Naval corridors, marine sanctuaries)
  ├── Multicriteria Suitability Scoring (`suitability_engine.py`)
  └── Multi-factor Confidence Quantification (`confidence.py`)
  │
  ▼
HUMAN-FRIENDLY EXPLANATION LAYER (`synthesis_agent.py`)
  ├── Part 1: SIMPLE ANSWER (Direct 1-2 sentence answer with location & time)
  ├── Part 2: WHAT THIS MEANS (Real-world operational consequence)
  ├── Part 3: WHAT SHOULD I DO? (Practical mariner action directive)
  ├── Part 4: WHY IS ORCA RECOMMENDING THIS? (Bulleted multi-factor reasons)
  └── Part 5: EVIDENCE (Categorized plain-language evidence with icons)
  │
  ▼
OPTIONAL LLM CONVERSATIONAL POLISH (`llm_client.py` via Groq)
  └── Strictly constrained by deterministic ground-truth JSON payload
  │
  ▼
MULTILINGUAL LOCALIZATION (`conversation_manager.py`)
  ├── English (`en`)
  ├── Hindi (`hi`)
  └── Marathi (`mr`)
  │
  ▼
FINAL STRUCTURED RESPONSE
  └── Rendered in Next.js UI + Leaflet Geospatial Map + Web Speech Audio
```

### Trace A: "Why has fish productivity declined?"
1. **Intent**: Classified as `QueryIntent.PRODUCTIVITY_ANALYSIS` by keyword matching on `"declined"`, `"productivity"`.
2. **Data Retrieval**: Compares multi-year MOSDAC satellite chlorophyll baseline against current observations, checks INCOIS sea surface temperature anomaly (+0.3°C), and retrieves wind stress curl upwelling index.
3. **Reasoning**: Identifies that lower surface chlorophyll (1.9 vs 4.2 mg/m³) indicates reduced phytoplankton, and thermal boundary displacement correlates with dispersed fish schools.
4. **Human-Friendly Formatting**: Generates distinct `OBSERVED DATA` -> `DERIVED CHANGE` -> `INTERPRETATION` sections without asserting direct causality.

### Trace B: "Is it safe to venture into the sea tomorrow morning?"
1. **Intent**: Classified as `QueryIntent.MARINE_SAFETY`.
2. **Data Retrieval**: Queries INCOIS ERDDAP WW3 for significant wave height (`swh`), IMD API for coastal wind and active squall bulletins, and GIS cadastre for naval security fairways.
3. **Missing Data Fallback**: If ERDDAP fails or times out, it refuses to claim safety, outputting: *"ORCA cannot confirm whether conditions are suitable because required forecast data is unavailable."*
4. **Safe / Manageable Synthesis**: If wave height < 1.5m and winds < 15 kt with no active IMD warnings, reports: *"Conditions currently appear manageable tomorrow morning... lower-risk under retrieved conditions."*

---

## 3. Planner

The Planner Agent (`backend/app/agents/planner_agent.py`) serves as the question-centric front door. It extracts:
- **Taxonomy Intent**: Matches queries into 8 canonical intents (`PFZ_DISCOVERY`, `MARINE_CONDITIONS`, `HAZARD_ALERT`, `PRODUCTIVITY_SEARCH`, `ROUTE_PLANNING`, `PRODUCTIVITY_ANALYSIS`, `RISK_AVOIDANCE`, `MARINE_SAFETY`).
- **Spatial Scope**: Resolves locations using a coastal gazetteer registry (`COASTAL_LOCATION_REGISTRY`) of 50+ Indian maritime points (Mumbai, Ratnagiri, Veraval, Goa, Kochi, Chennai, Visakhapatnam, Paradip) or live GPS telemetry (`lat`, `lon`, `accuracy_m`).
- **Temporal Window**: Parses relative temporal expressions ("tomorrow morning", "today", "next 24 hours") into bounded UTC timestamps (`start_utc`, `end_utc`).
- **Adversarial Resistance**: Intercepts prompt injection and override attempts, routing them to deterministic safety enforcement.

---

## 4. Dataset Discovery

The Discovery Service (`backend/app/services/discovery/` and `incois/discovery.py`) performs dynamic metadata matching:
- **Requirements Mapping**: Evaluates requested parameters against verified datasets:
  - `incois_ww3_regional`: Significant wave height (`swh`), mean wave period (`mwp`), mean wave direction (`mwd`), swell height.
  - `incois_roms_hydrodynamics`: Zonal current (`u`), meridional current (`v`), water temperature (`temp`).
  - `incois_sst_composite`: Sea surface temperature (`sst`), anomaly.
  - `imd_marine_bulletin`: Surface wind 10m, marine squall warning, cyclone advisory.
  - `mosdac_ocm3_swath`: Chlorophyll-a concentration, diffuse attenuation.
- **Dynamic Selection**: Selects optimal datasets based on spatial bounding box overlap, forecast horizon, and protocol compatibility.

---

## 5. Query Builder

Source-specific query builders generate target HTTP requests without manual string concatenation:
- **INCOIS ERDDAP Query Builder** (`incois/query_builder.py`):
  - Formats OPeNDAP/Griddap subset constraints: `dataset_id.json?var[(start_time):1:(end_time)][(min_lat):1:(max_lat)][(min_lon):1:(max_lon)]`.
- **IMD Query Builder** (`imd/query_builder.py`):
  - Builds coastal sector REST requests parameterized by maritime district code and state.
- **MOSDAC Query Builder** (`mosdac/query_builder.py`):
  - Constructs Oceansat-3 satellite swath queries parameterized by geographic bounding box and observation pass dates.
- **Bhuvan Query Builder** (`geospatial/bhuvan/query_builder.py`):
  - Constructs coastal geocoding, reverse geocoding, and shortest-path requests.

---

## 6. Data Source Adapters

Adapters encapsulate low-level HTTP transport, rate limits, bounded retries with exponential backoff, and truthful logging:
- **`INCOISConnector`** (`incois/client.py`): Interfaces with `https://erddap.incois.gov.in/erddap`.
- **`IMDConnector`** (`imd/client.py`): Interfaces with `https://api.imd.gov.in/public`.
- **`MOSDACConnector`** (`mosdac/client.py`): Interfaces with `https://www.mosdac.gov.in`.
- **`BhuvanAdapter`** (`geospatial/bhuvan/adapter.py`): Interfaces with `https://bhuvan-app1.nrsc.gov.in/api`.

---

## 7. Data Normalization

All raw responses (ERDDAP JSON tables, IMD bulletins, MOSDAC payloads) are ingested into unified Pydantic models (`backend/app/schemas/marine.py`):
```python
class NormalizedMarineRecord(BaseModel):
    source: str
    source_id: str
    parameter: str
    value: float
    unit: str
    latitude: float
    longitude: float
    timestamp: str
    observation_time: str
    data_type: str  # 'observation' | 'forecast'
    valid_time: str
    retrieved_at: str
    quality: str
    source_url: str
    metadata: Dict[str, Any]
```

---

## 8. Evidence Graph

Every scientific statement is mapped back to its underlying observational node via `claim_evidence_map` and the `evidenceGraph` payload:
- **Traceability**: Natural language claims (e.g. *"Forecast wave height is below 1.4 m"*) are bound to authoritative node IDs (`ev_incois_wave_01`), provider citations (`INCOIS Wave Watch III`), retrieval timestamps, and direct URLs.
- **Frontend Inspection**: The UI exposes this as a collapsible interactive graph drawer (`Claim-to-Evidence Traceability Graph`) for total institutional transparency.

---

## 9. Deterministic Reasoning

Scientific safety screening is strictly separated from natural language generation:
- **Hazard Analysis** (`services/risk/hazard_engine.py`): Evaluates calibrated wave height, swell risk, wind speed, and squall alerts against craft limits.
- **Spatial / Geofence Reasoning** (`services/geospatial/spatial_engine.py`): Performs ray-casting point-in-polygon and line-string intersection checks against maritime boundaries (Naval firing ranges, Mumbai Port Trust Fairways, Marine National Parks).
- **Productivity Reasoning** (`services/decision/suitability_engine.py`): Evaluates thermal gradients (SST fronts) and chlorophyll concentrations to rank candidate fishing spots.

---

## 10. Risk Engine

The Risk Engine (`services/risk/risk_engine.py`) aggregates multi-criteria indices:
- **Composite Risk Score (0–100)**: Evaluates weighted penalties across Wave State (40%), Wind Speed (25%), IMD Bulletins (20%), and Navigational Restrictions (15%).
- **Categorization**: Classifies marine sectors into `suitable_candidate`, `caution`, `high_risk`, or `restricted`.
- **Residual Uncertainty**: Flags data aging, wide spatial interpolation, or server degradation.

---

## 11. LLM Synthesis

The LLM Client (`backend/app/core/llm_config.py`) provides conversational fluency:
- **Provider**: Supports Groq API (`llama-3.3-70b-versatile`) with automatic failover to `_deterministic_fallback_synthesis`.
- **Strict Guardrails**: The LLM prompt receives the deterministic evaluation payload as frozen ground truth. It is forbidden from altering numbers, creating static zones, or declaring zones "100% safe".

---

## 12. Conversational Context

ORCA maintains multi-turn dialog memory across user turns:
- **Context Resolver** (`context_resolver.py`): Detects follow-ups like *"Why?"*, *"Show on map"*, *"Compare them"*, *"What about the wind?"*, and *"Can you find an option closer to shore?"*.
- **Persistence**: Rehydrates context from SQLite database (`orca_marine.db`), tracking session messages, active geographic coordinates, and focused sector IDs.
- **Zero Re-fetch Optimization**: Action queries (`SHOW_ON_MAP`, `EXPLAIN`, `COMPARE`, `SHOW_SOURCES`) are resolved from the in-memory `ResultRegistry` without redundant network queries.

---

## 13. Map / Geospatial Layer

The frontend Leaflet map (`components/MarineMap.tsx`) renders live spatial features:
- **📍 Live GPS Pin**: Pulsating marker indicating the user's live coordinates with a semi-transparent blue accuracy circle (`accuracy_m`).
- **Passage Corridors**: GeoJSON `LineString` features showing recommended inshore vs alternative offshore routes.
- **Polygons**: Restricted naval zones, marine national parks, port fairway channels, and evaluated ocean sectors.
- **Points**: High-suitability Potential Fishing Zones (PFZs) with distance indicators.
- **Bi-directional Interactivity**: Clicking a map feature focuses the chat card, and clicking *"Show on Map"* in chat invokes `mapController.fitBounds` and selects the corresponding layer.

---

## 14. Human-Friendly Explanation Layer

The explanation layer (`backend/app/agents/synthesis_agent.py`) translates scientific metrics into structured decision support:

### Marine Safety Structure:
1. **`### SIMPLE ANSWER`**: Direct answer in 1–2 sentences with location, time, and fishing activity.
2. **`### WHAT THIS MEANS`**: Practical consequence for small craft handling and vessel stability.
3. **`### WHAT SHOULD I DO?`**: Concrete actionable maritime safety advice.
4. **`### WHY IS ORCA RECOMMENDING THIS?`**: Plain-language contributing factors for waves, winds, weather, and boundaries.
5. **`### EVIDENCE`**: Plain-language categorized observations with source icons (🌊 INCOIS, 💨 IMD, ⛈️ IMD, 🗺️ GIS Cadastre).

### Productivity Structure:
1. **`### SIMPLE ANSWER`**: Direct summary of biological indicators.
2. **`### WHAT CHANGED?`**: Clear comparisons for Chlorophyll, SST, and ocean upwelling.
3. **`### WHY DOES THIS MATTER?`**: Ecological significance for marine food web and fish congregation without false causality.
4. **`### EVIDENCE`**: Authoritative satellite and oceanographic sources.

### UI 2-Layer Why Inspection:
- **Layer 1 (User-Friendly Explanation)**: Area recommendation, operational consequence, action directive, and bulleted contributing factors.
- **Layer 2 (Technical Evidence)**: Parameter values with physical units (m, kt, °C, mg/m³), valid observation timestamps, and provider citations, unlocked via `[VIEW FULL EVIDENCE]`.
- **Evidence Confidence**: Rendered as `"Evidence Confidence: {score} / 100"` with the disclaimer: *"This indicates how complete and consistent the retrieved evidence is. It is NOT a probability of safety."*

---

## 15. Current API Integration Status

| Source | Component | Status | Actual Behavior |
|---|---|---|---|
| **INCOIS ERDDAP** | `INCOISConnector` (`incois/client.py`) | **LIVE / CACHED / FALLBACK** | Performs real HTTP GET queries to `https://erddap.incois.gov.in/erddap`. Subsets WW3, ROMS, and SST datasets. When live ERDDAP times out, logs truthful status 500 and triggers `DATA_UNAVAILABLE` safe fallback. |
| **IMD Coastal Bulletins** | `IMDConnector` (`imd/client.py`) | **LIVE / CACHED** | Queries `https://api.imd.gov.in/public`. Parses live weather bulletins and wind speed forecasts. If unreachable, returns empty records without fake alerts. |
| **MOSDAC Satellite** | `MOSDACConnector` (`mosdac/client.py`) | **PARTIALLY_LIVE / AUTH_REQUIRED** | Performs live connectivity checks to `https://www.mosdac.gov.in`. Full satellite raster swaths require user API token; returns `AUTH_REQUIRED` status when token is unconfigured without fake numbers. |
| **Bhuvan Coastal GIS** | `BhuvanAdapter` (`bhuvan/adapter.py`) | **LIVE / CACHED** | Queries `https://bhuvan-app1.nrsc.gov.in/api`. Resolves coastal names and geolocations with grounded coastal gazetteer fallback. |
| **GIS Maritime Cadastre** | `SpatialEngine` (`geospatial/spatial_engine.py`) | **LIVE (LOCAL GEOMETRY)** | Local vector polygons of Indian EEZ, Naval security envelopes, and port fairway channels derived from National Hydrographic Office baselines. |
| **LLM Synthesis (Groq)** | `LLMClient` (`core/llm_config.py`) | **LIVE / DETERMINISTIC FALLBACK** | Connects to Groq API (`llama-3.3-70b-versatile`) when `GROQ_API_KEY` is present. Falls back cleanly to deterministic synthesis when key is absent. |

---

## 16. Prototype vs Production

| Dimension | ORCA SIH Prototype | Target Production Architecture |
|---|---|---|
| **Deployment** | Local FastAPI + Next.js development server | Containerized Kubernetes (EKS/GKE) with Envoy API gateway |
| **Database** | Embedded SQLite with aiosqlite (`orca_marine.db`) | Clustered PostgreSQL 16 with PostGIS extension + TimescaleDB |
| **Cache** | In-memory Python TTL cache + SQLite result store | Distributed Redis cluster with geospatial indexing |
| **ERDDAP Ingest** | On-demand bounded HTTP sub-setting per query | Scheduled asynchronous ETL pipeline with raster caching |
| **Auth & Security** | Open local API with session ID headers | OAuth2 / OIDC authentication with fine-grained RBAC |
| **Telemetry Volume** | Regional focus (Maharashtra / Mumbai coastal waters) | All 9 coastal states + Andaman & Nicobar, Lakshadweep EEZ |

---

## 17. Known Limitations

1. **ERDDAP Upstream Latency**: Upstream government ERDDAP servers occasionally exhibit latency spikes (> 10s) or timeouts. ORCA safely degrades to `DATA_UNAVAILABLE` but relies on cached cycles for offline resilience.
2. **Satellite Cloud Obscuration**: Satellite Ocean Colour (OCM-3) and thermal optical sensors cannot penetrate heavy monsoon cloud decks. During such periods, chlorophyll observations are unavailable.
3. **Artisanal Vessel Scale**: The risk engine is tuned primarily for motorized fiberglass craft (OBMs) and mechanized wooden gillnetters up to 20m. It is not calibrated for deep-sea trawlers or cargo vessels.

---

## 18. Final Architecture Diagram

```
+-----------------------------------------------------------------------------------+
|                                USER INTERFACE                                      |
|  +-----------------------------------------------------------------------------+  |
|  | Modern Glassmorphic Dark UI (Next.js 14 App Router + Tailwind CSS)           |  |
|  | - Multilingual Voice STT (Web Speech en-IN, hi-IN, mr-IN)                   |  |
|  | - Spoken TTS Listen Toggle with Honest Marathi Fallback                     |  |
|  | - Leaflet Interactive Map: Live GPS Pin, Accuracy Circle, Corridors, PFZ    |  |
|  | - 2-Layer "Why" Drawer: Plain Explanation -> [VIEW FULL EVIDENCE]           |  |
|  | - Evidence Confidence Chip: "{score} / 100" (Not probability of safety)     |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
                                         │
                         HTTP REST / JSON (Trace ID Headers)
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
|                               BACKEND API & CORE                                   |
|  FastAPI + Uvicorn (Async ASGI)                                                   |
|  - Structured Logging: [ORCA REQUEST] -> [ORCA][SOURCE] -> [ORCA RESULT]          |
|  - Async SQLAlchemy Session + SQLite Database (`orca_marine.db`)                  |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
|                               AGENTIC ORCHESTRATOR                                |
|  `backend/app/agents/orchestrator.py`                                             |
|                                                                                   |
|  +-----------------------------------+     +-----------------------------------+  |
|  | 1. Context Resolver               |     | 2. Planner Agent                  |  |
|  | - Multi-turn session tracking     | --> | - Intent Classification (8 types) |  |
|  | - Live GPS & accuracy handling    |     | - Spatial BBox & Time Alignment   |  |
|  +-----------------------------------+     +-----------------------------------+  |
|                                                              │                    |
|                     [Action Intent Registry Hit?] ───────────┴──────────┐         |
|                     │ YES (SHOW_ON_MAP / EXPLAIN / COMPARE / SOURCES)   │ NO      |
|                     ▼                                                   ▼         |
|         +-----------------------+                         +---------------------+ |
|         | Result Registry       |                         | Dataset Discovery   | |
|         | (Zero Re-fetch Return)|                         | & Query Builders    | |
|         +-----------------------+                         +---------------------+ |
+-------------------------------------------------------------------------│---------+
                                                                          │
                                                                          ▼
+-----------------------------------------------------------------------------------+
|                             EXTERNAL DATA ADAPTERS                                |
|  +-----------------------+  +----------------------+  +-------------------------+ |
|  | INCOIS Connector      |  | IMD Connector        |  | MOSDAC Connector        | |
|  | - Live ERDDAP GET     |  | - Coastal Bulletins  |  | - Oceansat-3 Swaths     | |
|  | - WW3, ROMS, SST      |  | - Squall Alerts      |  | - Auth-Required Token   | |
|  +-----------------------+  +----------------------+  +-------------------------+ |
|                             +----------------------+                              |
|                             | Bhuvan & GIS Cadastre|                              |
|                             | - Coastal Gazetteer  |                              |
|                             | - Naval Geofences    |                              |
|                             +----------------------+                              |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
|                        NORMALIZATION & EVIDENCE GRAPH                             |
|  - `NormalizedMarineRecord` Schema                                                |
|  - `claim_evidence_map` (Assertion -> Telemetry Node ID + Citation URL)           |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
|                     DETERMINISTIC REASONING & RISK ENGINES                        |
|  - Hazard Engine (Physical thresholds: SWH >= 2.0m, Wind >= 22kt)                  |
|  - Spatial Engine (Naval corridors, marine sanctuary ray-casting)                 |
|  - Suitability Engine (SST thermal gradients + chlorophyll productivity)          |
|  - Risk Engine (0-100 Multi-criteria Scoring + Uncertainty Quantification)        |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
|                    HUMAN-FRIENDLY EXPLANATION & SYNTHESIS                         |
|  `backend/app/agents/synthesis_agent.py`                                          |
|                                                                                   |
|  ### SIMPLE ANSWER (Direct 1-2 sentence answer with location & time)              |
|  ### WHAT THIS MEANS (Operational vessel handling consequence)                    |
|  ### WHAT SHOULD I DO? (Practical action directive)                               |
|  ### WHY IS ORCA RECOMMENDING THIS? (Multi-factor contributing breakdown)         |
|  ### EVIDENCE (Categorized plain-language evidence with icons)                    |
|                                                                                   |
|  +-----------------------------------------------------------------------------+  |
|  | LLM Client (`llm_client.py`): Groq API / Deterministic Fallback             |  |
|  | Multilingual Engine (`conversation_manager.py`): English / Hindi / Marathi  |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

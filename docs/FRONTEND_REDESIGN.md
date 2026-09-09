# ORCA Marine Intelligence — Frontend Redesign Specification

## 1. Overview & Vision
The ORCA frontend has been redesigned from a generic card-heavy dashboard into a high-density, precision **Marine Operations Console & Decision Intelligence Workstation** (inspired by satellite ground control, maritime command centers, and scientific visualization platforms).

The interface reinforces the single fundamental workflow:
$$\text{ASK} \longrightarrow \text{UNDERSTAND} \longrightarrow \text{REASON} \longrightarrow \text{DECIDE} \longrightarrow \text{SHOW ON MAP} \longrightarrow \text{EXPLAIN WHY} \longrightarrow \text{SHOW EVIDENCE}$$

Within **5 seconds** of loading, an operator or SIH judge can immediately identify:
1. **What ORCA is**: Autonomous Marine Intelligence & Multi-Agent Decision Support.
2. **Where to ask**: High-contrast command search bar with instant query suggestions.
3. **What ORCA decided**: Compact decision strip (`AVOID 2 ZONES`, `CANDIDATE 1 ZONE`, `CAUTION 1 ZONE`, `RESTRICTED 1 ZONE`) & ranked candidates.
4. **Why it decided that**: Multi-source convergence, wave/wind forecast thresholds, and naval geofences.
5. **Where the evidence is**: 1-click evidence drawer, provenance registry, and direct links to official INCOIS, IMD, MOSDAC, and GIS portals.
6. **What is happening on the map**: Dominant 65% interactive operations grid synchronized with the Sector Inspector.

---

## 2. Key UX & Architectural Improvements

| Aspect | Previous Implementation | Redesigned Marine Operations Console |
| :--- | :--- | :--- |
| **Aesthetic & Theme** | Generic white SaaS dashboard with excessive whitespace and card-in-card nesting | Precision dark-mode maritime command center (`#0A1128`, `#0F172A`, `#0B1120`) with cyan/teal telemetry accents |
| **Workspace Priority** | Equal-weighted disconnected panels; decision buried under large containers | **Map-First (65% width)** and **Decision-First (35% width)**; dominant spatial operations grid |
| **Decision Visibility** | Verbose paragraph buried in an oversized container | **Instant Decision Strip** (Avoid vs Candidate counts) + **Ranked Candidate Zones** with deterministic suitability |
| **Telemetry Presentation** | Generic text labels | Monospace telemetry badges with explicit units (`WAVE 4.1 m`, `WIND 31 kt`, `SST 28.8 °C`, `RISK 85 / 100`) |
| **Multi-Agent Trace** | Large vertical card occupying substantial vertical screen space | Compact 1-line pipeline (`Planner ✓ → Ocean ✓ → Weather ✓ → Geo ✓ → Risk ✓ → Synth ✓`) with modal expansion |
| **Evidence & Provenance** | Enormous static descriptions | Structured feed registry + collapsible **Evidence Graph Drawer** with citation metadata and official links |
| **Responsive Density** | Excessive 40–60px gaps on wide monitors | Compact 8px / 12px / 16px / 24px rhythm tuned for 1366×768, 1440×900, 1920×1080 |

---

## 3. Component Architecture & Responsibilities

```
app/
 ├── layout.tsx                # Root layout with JetBrains Mono + Inter typography
 ├── globals.css               # Dark maritime tokens, telemetry badges, radar animations
 └── page.tsx                  # Master operations workstation wiring & state management
components/
 ├── Navbar.tsx                # Command center header (Trust badge, Status, What-if, Research, Alerts, Language, Clock)
 ├── Sidebar.tsx               # Compact navigation rail + Map filter switchers + Live source health indicators
 ├── QueryPanel.tsx            # High-visibility command bar with suggested quick queries
 ├── MarineMap.tsx             # 65% Operations grid with zone polygons, risk badges, and layer toggles
 ├── ZoneDetails.tsx           # Precision Sector Inspector (telemetry metrics, risk meter, why, source link)
 ├── AnalysisPanel.tsx         # Decision strip, executive synthesis, candidate ranking, forecast profile, agent pipeline
 ├── EvidencePanel.tsx         # Fused authoritative feeds registry with official external URLs
 ├── EvidenceDrawer.tsx        # Collapsible slide-in drawer for individual evidence graph nodes
 ├── ConfidenceScore.tsx       # 5-factor uncertainty indicator with decomposition modal trigger
 ├── DataFreshness.tsx         # Forecast vs observation freshness lifecycle
 ├── WhatIfScenarioModal.tsx   # Parametric simulation drawer (+1m waves, +10kt wind, geofence shifts)
 ├── SafetyAlertsModal.tsx     # Active marine warning and restricted zone alert triage
 ├── MarineBriefModal.tsx      # Formatted operational intelligence document generator (Print/Export)
 ├── ResearchEvaluationModal.tsx # Scientific evaluation workbench (EXP-20260905-001, baselines, ablations)
 └── SystemStatusModal.tsx     # Observability and source connector latency metrics
```

---

## 4. Preservation of Functionality & Safety Constraints
* **Zero Backend Changes**: All existing FastAPI routes (`/api/conversation/query`, `/api/scenarios/run`, `/api/evaluation/metrics`, `/health`, etc.) preserved.
* **Truthful Data Grounding**: Zero synthetic fabrication. Strict grounding in INCOIS, IMD, MOSDAC, and GIS Cadastre.
* **Multilingual Continuity**: Seamless live translations across English, Hindi (`हिन्दी`), and Marathi (`मराठी`).
* **Multi-Agent Pipeline**: Full visibility into Planner, Ocean, Weather/Hazard, Geospatial, Risk & Evidence, and Synthesis agents.

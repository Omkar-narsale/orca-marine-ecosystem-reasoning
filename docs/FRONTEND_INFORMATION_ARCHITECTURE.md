# ORCA Frontend Information Architecture Specification

**Document Version:** 2.0.0  
**Project:** ORCA — Marine Ecosystem Reasoning with Collaborative Agents (SIH 2026, PS ID: SIH26176)  
**Status:** Approved Frontend Architecture Document  

---

## 1. Information Architecture Overview

ORCA transforms maritime operational analytics into a streamlined intelligence experience:

$$\text{ASK} \longrightarrow \text{DECISION} \longrightarrow \text{MAP} \longrightarrow \text{REASONING} \longrightarrow \text{EVIDENCE} \longrightarrow \text{DATA}$$

### Design Philosophy
- **Not a Generic Admin Dashboard:** Replaced crowded multi-card scrolling pages with focused, high-density workspaces.
- **Single Active Workspace:** At any given moment, exactly **one** primary workspace or analysis tab is active, eliminating visual competition.
- **Scientific Decision Support:** Every visual element serves operational decision-making, grounded in authoritative provenance.

---

## 2. Core Application Routes & Views

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ORCA COMMAND CONSOLE                              │
├─────────────────┬───────────────────────────────────────────────────────────┤
│ SIDEBAR         │ TOP NAVBAR: Brand · Live Telemetry · Status · Alerts · Lang│
│                 ├───────────────────────────────────────────────────────────┤
│ [Ask ORCA]      │                                                           │
│ [Analysis Tabs] │  /ask ──> Centered Natural Language Marine Command        │
│   • Map         │                                                           │
│   • Reasoning   │  /analysis/[id]/map ───────> 70% Map + Sector Inspector   │
│   • Evidence    │  /analysis/[id]/reasoning ──> 6-Stage Reasoning Trace     │
│   • Data        │  /analysis/[id]/evidence ───> Official Source Registry    │
│ [Active Alerts] │  /analysis/[id]/data ───────> Normalized Telemetry Table  │
│ [Research Hub]  │                                                           │
│ [Marine Brief]  │  /research ───────────────> Phase 7 Comparative Study     │
│ [Observability] │  /alerts ─────────────────> Active Safety Alert Center    │
│                 │  /brief ──────────────────> Operational Intelligence Doc  │
└─────────────────┴───────────────────────────────────────────────────────────┘
```

### View 1: `/ask` (Ask ORCA Landing Interface)
- **Visual Style:** ChatGPT-style centered conversational workspace with high-tech maritime styling.
- **Key Elements:**
  - Headline: *"Ask ORCA"*
  - Subtitle: *"Turn marine data into evidence-grounded decisions."*
  - Command input with placeholder: *"Ask about marine safety, fishing conditions, weather, restricted zones, routes or ocean conditions..."*
  - 4 Suggested Decision Inquiry cards (Hazard Screening, Sector Comparison, Boundary Verification, Candidate Search).
- **Behavior:** Query submission immediately creates an analysis state (`trace_id`) and transitions seamlessly to `/analysis/[id]/map`.

### View 2: `/analysis/[analysisId]/map` (Operations Map)
- **Layout:** Dominant Leaflet operations map ($68\% - 75\%$ of horizontal workspace) paired with a compact **Sector Inspector** drawer ($25\% - 32\%$).
- **Top Decision Summary Strip:**
  - Avoid Count: e.g. `2 ZONES (ZONE A, ZONE B)`
  - Candidate Count: e.g. `1 ZONE (ZONE C)`
  - `Confidence Index: 88 / 100` (with provenance tooltip)
  - `Evidence Coverage: 100% (4 SOURCES)`
- **Sector Inspector:** Compact panel displaying Sector Code, Status Badge, Risk Index meter ($X/100$), Wave/Wind/SST telemetry, Safety/Geofence constraints, Grounded Rationale, and direct `[Why?]` and `[View Evidence]` tab-jump buttons.

### View 3: `/analysis/[analysisId]/reasoning` (Decision Reasoning)
- **Purpose:** Answers *"Why did ORCA make this decision?"* with zero hidden chain-of-thought.
- **Components:**
  1. **Reasoning Synthesis Banner:** Clear natural-language decision summary.
  2. **6 Deterministic Evaluation Stages:** Step-by-step audit of ocean telemetry, meteorological hazards, geospatial boundaries, risk scoring, evidence consistency, and recommendation synthesis.
  3. **Contributing Factor Breakdown:** Explanatory bar charts (Wave, Wind, Warning, Geofence, Uncertainty) with explicit model heuristic caveats.
  4. **Multi-Agent Trace:** Transparent execution log of 6 collaborative agents (Planner, Ocean, Weather, Geospatial, Risk & Evidence, Synthesis) with actions, status, and tools used.

### View 4: `/analysis/[analysisId]/evidence` (Evidence & Sources)
- **Purpose:** Comprehensive source verification and data provenance.
- **Components:**
  1. **Evidence Coverage Metric:** Clear $100\%$ completion banner clarifying this is an ORCA evidence-completeness metric.
  2. **Authoritative Feeds Registry:** Source name, organization, parameter, valid time, data nature tag (`FORECAST`, `WARNING`, `OBSERVATION`, `ADVISORY`, `STATIC`), Inspect Node action, and direct clickable official source links (`https://incois.gov.in`, `https://api.imd.gov.in`, `https://mosdac.gov.in`, `https://hydro-india.nic.in`).

### View 5: `/analysis/[analysisId]/data` (Scientific Telemetry)
- **Purpose:** Tabular interface for technical and scientific researchers.
- **Components:**
  1. Filterable data nature selector (`FORECAST`, `OBSERVATION`, `ADVISORY`, `WARNING`, `STATIC`).
  2. CSV Export capability.
  3. Normalized table columns: Parameter, Value, Unit, Sector, Lat/Lon, Observation Time, Valid Window, Retrieved At, Data Nature, Quality, and Official Source.

### Dedicated Auxiliary Workspaces
- **`/research` (Research Evaluation Workbench):** Phase 7 comparative study (3 baselines: Rule-Based, Single-Agent, Full ORCA), ablation study (6 configurations), controlled benchmark metrics, decision audit trail, and human expert evaluation form.
- **`/alerts` (Deterministic Alert Center):** Real-time safety alert list with severity filters, acknowledgment controls, and map sector auto-focus.
- **`/brief` (Operational Marine Intelligence Brief):** Auditable operational document generation with export/print capability and user feedback collection.
- **`[What-If?]` (Hypothetical Simulation Drawer):** Isolated parameter modification sliders ($\Delta H_s$, $\Delta \text{wind}$, geofence overrides, temporal window shifts) that do **not** pollute the primary workspace.

---

## 3. Visual Design System

- **Color Palette:**
  - Background: Deep Void Blue (`#0B1120`, `#0A1128`, `#0F172A`)
  - Accent Primary: High-Tech Cyan / Teal (`#14B8A6`, `#06B6D4`)
  - Risk / Hazard: Vivid Rose (`#F43F5E`)
  - Caution: Amber / Orange (`#F59E0B`)
  - Candidate / Suitable: Emerald (`#10B981`)
  - Restricted Cadastre: Indigo (`#6366F1`)
- **Typography:**
  - UI Labels & Telemetry: Monospace (`font-mono`)
  - Content & Explanations: Sans-serif (`font-sans`)
- **Accessibility:**
  - High-contrast text on dark backgrounds.
  - Colorblind-friendly legends with clear symbolic text tags for all risk classifications.

---

## 4. Multi-Turn Context & Synchronization

1. **Dialogue History Memory:** User inquiries like *"Why Zone A?"* or *"What about C?"* resolve previous entity contexts without requiring full query repetition.
2. **Map $\leftrightarrow$ Chat Synchronization:**
   - Mentioning *"Show Zone A"* auto-focuses Zone A on the map.
   - Mentioning *"Compare A and C"* highlights both bounding boxes.
   - Mentioning *"Show restricted zones"* activates the cadastre geofence layer.

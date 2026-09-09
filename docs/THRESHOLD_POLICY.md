# ORCA Marine Safety Threshold & Policy Audit Specification

**Document Version:** 2.0.0  
**Project:** ORCA — Marine Ecosystem Reasoning with Collaborative Agents (SIH 2026, PS ID: SIH26176)  
**Status:** Approved Operational & Scientific Policy  

---

## Executive Summary

Marine risk is inherently multi-factorial. No single scalar threshold (such as a universal wave height cutoff) can definitively guarantee vessel safety or predict operational outcomes. Maritime risk depends on complex interactions between **vessel characteristics (length, beam, engine power, freeboard), wave height ($H_s$), wave steepness, wave period, directional spread, wind speed, rapid wind-sea development, surface currents, active meteorological weather systems, statutory maritime geofences, and data uncertainty**.

This document defines ORCA's source authority hierarchy, distinguishes official government warnings from project heuristics, specifies missing-data invariants, and establishes rigorous interpretation guidelines.

---

## 1. Authoritative Official Sources & Endpoints

ORCA interfaces exclusively with verified authoritative government portals and scientific data products. ORCA does not invent URLs or synthesize ungrounded marine values.

| Authority | Domain / Service | Verified Official Endpoint | Data Modality |
| :--- | :--- | :--- | :--- |
| **INCOIS** | Ocean State Forecast (OSF) | `https://incois.gov.in/oceanservices/osfforecast.jsp` | Numerical Wave Watch III Forecast |
| **INCOIS** | Small Vessel Advisory Services (SVAS) | `https://www.incois.gov.in/site/services/SVA_overview.jsp` | Boat Safety Index (BSI) Advisory |
| **INCOIS** | Potential Fishing Zones (PFZ) | `https://incois.gov.in/MarineFisheries/PfzAdvisory` | Thermal/Chlorophyll Front Composite |
| **INCOIS** | Live ERDDAP Server | `https://erddap.incois.gov.in/erddap/` | Gridded In-Situ / Buoy Observations |
| **IMD** | National Open Weather API | `https://api.imd.gov.in/public/index.php` | Synoptic Weather Telemetry |
| **IMD** | Coastal Fishermen Warnings | `https://api.imd.gov.in/public/api_reference.html` | Statutory Weather & Squall Bulletins |
| **ISRO MOSDAC** | Ocean Satellite Products (OCM-3) | `https://www.mosdac.gov.in/` | Satellite Chlorophyll & SST Swaths |
| **GIS Cadastre / NHO** | Maritime Boundaries & Security Grid | `https://hydro-india.nic.in` | Statutory Naval Enclaves & Fairways |

---

## 2. Source Authority Hierarchy

ORCA executes a strict **3-Level Precedence Hierarchy** during all reasoning evaluations:

```
┌─────────────────────────────────────────────────────────────┐
│ LEVEL 1: OFFICIAL WARNING (Statutory Government Alerts)     │
│ Precedence: HIGHEST / MANDATORY OVERRIDE                    │
│ E.g., IMD Coastal Squall Bulletin, INCOIS High Swell Warning│
└──────────────────────────────┬──────────────────────────────┘
                               │ (If no active Level 1 warning)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ LEVEL 2: OFFICIAL ADVISORY (Authoritative Specialized System│
│ Precedence: HIGH / AUTHORITATIVE DOMAIN GUIDANCE            │
│ E.g., INCOIS SVAS Boat Safety Index, INCOIS PFZ Advisories  │
└──────────────────────────────┬──────────────────────────────┘
                               │ (If no direct Level 2 advisory)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ LEVEL 3: ORCA RISK SCREENING (Transparent Decision Support) │
│ Precedence: DECISION SUPPORT HEURISTIC                      │
│ E.g., Deterministic Heuristic Risk Screening Model          │
└─────────────────────────────────────────────────────────────┘
```

### Level 1 — Official Warning
- **Authority:** India Meteorological Department (IMD) / INCOIS Disaster Management.
- **Rule:** If an official marine warning or squall alert covers the operational bounding box and time window, it takes **absolute precedence**.
- **UI Label:** `OFFICIAL WARNING`.
- **System Action:** Flag sector as `HIGH RISK (AVOID)` regardless of biological or suitability indicators.

### Level 2 — Official Advisory
- **Authority:** INCOIS Small Vessel Advisory Services (SVAS) / PFZ Unit.
- **Methodology:** SVAS utilizes the **Boat Safety Index (BSI)** methodology, accounting for significant wave height, wave steepness, directional spread, rapid wind-sea growth, and artisanal craft beam/length category.
- **Rule:** ORCA must **never** replace or simplify SVAS into a generic rule (such as "$H_s > 3.5\text{m} = \text{unsafe}$"). Authoritative SVAS categories are reported directly.
- **UI Label:** `OFFICIAL ADVISORY`.

### Level 3 — ORCA Risk Screening
- **Authority:** ORCA Deterministic Heuristic Screening Engine.
- **Rule:** When no statutory warning directly applies, ORCA executes transparent decision-support calculations across retrieved physical parameters.
- **UI Label:** `ORCA RISK SCREENING` or `ORCA Prototype Risk Model`.
- **Constraint:** Must **never** be represented as an "Official Government Safety Rating" or "Government Safety Limit".

---

## 3. Audit of the "3.5m Craft Safety Threshold"

### The Issue
Previous prototype documentation occasionally stated: *"Elevated wave swell (4.1m forecast) breaches 3.5m craft safety threshold."*

### Scientific Audit Finding
- $3.5\text{m}$ is **not** an official universal statutory craft limit established for all Indian fishing vessels.
- Wave impacts depend heavily on vessel category: artisanal non-motorized craft ($<9\text{m}$) experience critical hazard at $H_s \ge 1.8\text{m}$, while mechanized trawlers ($>15\text{m}$) can navigate moderate swells up to $3.5\text{m}$ with favorable periods ($T_p > 10\text{s}$).
- IMD fishermen warning guidance typically references significant wave height thresholds of $\ge 4.0\text{m}$ and wind gusts $\ge 45\text{ km/h}$ ($\approx 25\text{ kts}$) for issuing statutory coastal advisories.

### Remediation & Enforced Language
1. **Removed:** Any assertion that $3.5\text{m}$ is a "universal craft safety threshold".
2. **Replaced With:**
   - *"Elevated wave conditions (4.1m significant wave height forecast from INCOIS OSF) detected in sector."*
   - *"Wave conditions contribute to elevated ORCA risk screening."*
   - *(If warning active):* *"Official IMD Marine Warning in effect for Northern Reach."*

---

## 4. ORCA Prototype Risk Model Specification

### Formula & Weights
The deterministic heuristic risk score $R \in [0, 100]$ is computed as:

$$R = 100 \times \left( w_{\text{wave}} \cdot \hat{S}_{\text{wave}} + w_{\text{wind}} \cdot \hat{S}_{\text{wind}} + w_{\text{warning}} \cdot \hat{S}_{\text{warning}} + w_{\text{current}} \cdot \hat{S}_{\text{current}} \right)$$

Where the prototype configuration weights are:
- $w_{\text{wave}} = 0.35$ (35% — Primary physical wave swell hazard)
- $w_{\text{wind}} = 0.30$ (30% — Surface chop and steering difficulty)
- $w_{\text{warning}} = 0.25$ (25% — Statutory official alert status)
- $w_{\text{current}} = 0.10$ (10% — Ocean current velocity and narrow channel drift)

### Model Transparency Metadata
- **Model Type:** Deterministic heuristic screening model.
- **Model Status:** Prototype / Research decision-support model.
- **Validation:** Controlled benchmark testing (30 single-turn queries, 10 multi-turn dialogues, 6 ablation configurations).
- **Explicit Caveat:** These weights are project engineering heuristics designed for multi-factor decision transparency and are **not** certified statutory weights.

---

## 5. Metrics & Interpretation Guidelines

### Risk Score
- **Designation:** `ORCA Risk Index: X / 100`
- **Prohibited Phrasing:** *"X% risk"*, *"X% probability of accident"*, *"X% chance of capsizing"*.
- **Interpretation:** Relative heuristic screening index indicating physical stress on artisanal operations.

### Suitability Score
- **Designation:** `ORCA Suitability Index: X / 100`
- **Prohibited Phrasing:** *"X% probability of fish"*, *"Guaranteed catch"*, *"Optimal fishing spot"*.
- **Interpretation:** Favorable candidate screening combining ocean color fronts, SST gradients, and physical access under available forecasts.

### Confidence Score
- **Designation:** `Confidence Index: X / 100`
- **Required Explanation:** *"ORCA confidence index reflects evidence completeness, source agreement, and data quality. It is not a calibrated probability of correctness."*

### Zone Classifications
All zones must use one of the 5 standardized operational classifications:
1. 🔴 **HIGH RISK** — Elevated physical hazard ($H_s$ swell, gale gusts) or statutory official warning.
2. 🟠 **CAUTION** — Moderate swell or wind transitions requiring continuous monitoring.
3. 🟢 **SUITABLE CANDIDATE** — Lower ORCA risk screening and favorable available indicators.
4. 🔵 **RESTRICTED** — Statutory geospatial cadastre constraint (naval buffer, shipping fairway).
5. ⚪ **INSUFFICIENT DATA** — Critical safety telemetry unverified; fail-safe active.

*Note: The unqualified term "SAFE" is prohibited unless an authoritative government advisory explicitly certifies safe passage.*

---

## 6. Fail-Safe Invariants for Missing or Degraded Data

ORCA enforces strict mathematical safety invariants across all agents and services:

$$\text{MISSING DATA} \neq \text{SAFE}$$
$$\text{FAILED WARNING CHECK} \neq \text{NO WARNING}$$
$$\text{FAILED GEOFENCE CHECK} \neq \text{UNRESTRICTED}$$

### Concrete Failure Behaviors
1. **INCOIS Service Degraded:** Flag source as `DEGRADED`, label data as `CACHED TELEMETRY`, and display timestamp of cached forecast cycle.
2. **IMD Warning Service Unreachable:** Report `WARNING CHECK UNAVAILABLE`. Do **not** report `No Active Warnings`. Classify sector as `INSUFFICIENT_DATA`.
3. **GIS Cadastre Service Unreachable:** Report `RESTRICTION CHECK UNAVAILABLE`. Do **not** assume unrestricted passage.
4. **LLM Synthesis Guardrail:** Deterministic risk calculations and safety invariants cannot be overwritten by natural-language LLM synthesis.

---

## 7. Future Calibration Plan

Before operational deployment in maritime command centers:
1. **Joint Calibration:** Formally calibrate the heuristic risk weights against historical INCOIS SVAS boat-casualty incident logs along the Western Continental Shelf.
2. **Vessel-Class Stratification:** Expand single risk index into stratified profiles for 4 distinct craft classes:
   - Category 1: Traditional non-motorized canoes ($<7\text{m}$)
   - Category 2: Motorized fiber-reinforced boats ($7\text{m} - 12\text{m}$)
   - Category 3: Mechanized trawlers / gillnetters ($12\text{m} - 20\text{m}$)
   - Category 4: Deep-sea fishing vessels ($>20\text{m}$)
3. **Statistical Probability Calibration:** Transition the confidence index to a calibrated conformal prediction framework estimating empirical error bounds.

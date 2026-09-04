<div align="center">

# 🌊 ORCA — Marine Ecosystem Reasoning & Decision Intelligence
### *Agentic Marine Orchestration, Deterministic Risk Analytics & Grounded Decision Support*
**Smart India Hackathon (SIH 2026)**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Next.js 14](https://img.shields.io/badge/next.js-14.2.35-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-Vanilla_CSS-38B2AC.svg)](https://tailwindcss.com/)
[![Tests Passing](https://img.shields.io/badge/tests-112%2F112%20passing%20(100%25)-brightgreen.svg)](backend/tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 📌 1. Scientific Mission & Overview

> *"ORCA evaluates how agentic orchestration combined with deterministic marine analytics, multi-dimensional uncertainty estimation, and evidence grounding can improve context-aware marine decision support for coastal artisanal craft and maritime operations."*

### ❌ What ORCA Does NOT Claim:
- **No Guaranteed Fish Catch**: ORCA does not pretend to predict exact future fish abundance or guarantee catch yields.
- **No Absolute Safety Warranties**: Real-world maritime navigation remains subject to master-of-vessel discretion and official weather warnings.

### ✅ What ORCA Delivers:
- **Evidence-Grounded Operational Candidate Ranking**: Combines live forecasts, satellite ocean color, coastal warnings, and GIS geofences.
- **100% Deterministic Risk & Suitability**: All scores are computed by transparent mathematical equations decoupled from LLM stochasticity.
- **Hypothetical What-If Scenario Simulations**: Allows mariners to simulate parameter variations (e.g. *What if waves increase by 1m?*) without corrupting baseline forecast data.
- **Decomposed 5-Factor Confidence vs. Uncertainty**: Explicitly separates how strongly evidence supports a conclusion from residual forecast horizon variances.
- **Full Multilingual Voice/Text Support**: English, हिन्दी (Hindi), and मराठी (Marathi).

---

## 🏛️ 2. High-Level System Architecture

```
                                  USER QUERY
                               (English / Hindi / Marathi)
                                      │
                                      ▼
                              CONVERSATION ENGINE
                                      │
                                      ▼
                              PLANNER AGENT
                                      │
                 ┌────────────────────┼────────────────────┐
                 ▼                    ▼                    ▼
            OCEAN AGENT         WEATHER AGENT        GEOSPATIAL AGENT
         (INCOIS / MOSDAC)      (IMD Warnings)       (Naval Geofences)
                 │                    │                    │
                 └────────────────────┼────────────────────┘
                                      ▼
                           RISK & EVIDENCE AGENT
                                      │
                                      ▼
                         DETERMINISTIC RISK ENGINE
                                      │
                 ┌────────────────────┼────────────────────┐
                 ▼                    ▼                    ▼
          SUITABILITY           UNCERTAINTY            EVIDENCE
            ENGINE                ENGINE                ENGINE
                 │                    │                    │
                 └────────────────────┼────────────────────┘
                                      ▼
                          RECOMMENDATION ENGINE
                        (Top Candidate + Alternative)
                                      │
                 ┌────────────────────┴────────────────────┐
                 ▼                                         ▼
         WHAT-IF SCENARIO ENGINE                     SYNTHESIS AGENT
     (Controlled Sensitivity Deltas)               (Explainable Reasoning)
                 │                                         │
                 └────────────────────┬────────────────────┘
                                      ▼
                          ORCA OPERATIONAL DASHBOARD
                  (Map 1.1 · Risk/Suitability Matrix · Marine Brief)
```

---

## 🧩 3. Key Core Modules

### 🔍 A. Decision Intelligence & Candidate Ranking (`backend/app/services/decision/`)
* **Suitability Engine (`suitability_engine.py`)**: Computes operational suitability $S = w_{\text{env}}E + w_{\text{safe}}S_{\text{safe}} + w_{\text{restr}}R$. Hard exclusions strictly override high environmental scores if a sector intersects naval geofences ($S=0$) or critical hazards ($S=15$).
* **Ranking Engine (`ranking_engine.py`)**: Ranks candidate operational zones:
  * **Top Candidate**: `ZONE C` (Suitability 72/100, Risk 22/100, Low Risk)
  * **Alternative Candidate**: `ZONE D` (Suitability 61/100, Risk 38/100, Moderate Swell)
  * **Excluded Sectors**: `ZONE A` (High Swell 4.1m) & `ZONE B` (Naval Security Buffer).
* **Trade-off Engine (`tradeoff_engine.py`)**: Generates comparative trade-off explanations between candidate zones.
* **Route Engine (`route_engine.py`)**: Computes operational transit corridors from Mumbai Harbor with geofence collision and wave hazard audits.

### 🧪 B. What-If Scenario Simulation Engine (`scenario_engine.py`)
* Simulates hypothetical parameter perturbations:
  * Wave height variation ($\pm\text{m}$)
  * Sustained wind speed modification ($\pm\text{kt}$)
  * Temporal departures (Dawn, Noon, Dusk)
  * Dynamic geofence restriction overrides
* Output is stamped `SIMULATED SCENARIO` to preserve distinction from live authoritative forecasts.

### 📊 C. Decomposed Uncertainty & Confidence Engine (`backend/app/services/uncertainty/`)
* **Confidence Engine (`confidence.py`)**: Calculates 5 empirical dimensions:
  1. **Data Completeness** ($80\%$) — $4/4$ Authoritative telemetry feeds online.
  2. **Data Freshness** ($90\%$) — Updated within past 12h forecast cycle.
  3. **Cross-Source Agreement** ($70\%$) — INCOIS wave fields aligned with IMD coastal bulletin.
  4. **Spatial Coverage** ($80\%$) — All primary coastal sectors bounded.
  5. **Temporal Alignment** ($70\%$) — Synchronized forecast valid windows.
* **Uncertainty Engine (`uncertainty_engine.py`)**: Distinguishes **Confidence** (*strength of evidence*) from **Uncertainty** (*unobserved biological stochasticity & numerical model horizons*).

### 📈 D. Research Evaluation & Benchmarks (`backend/app/evaluation/`)
* **30 Single-Turn Operational Queries** across 9 distinct categories.
* **10 Multi-Turn Dialogue Scenarios** testing contextual resolution.
* **4 Adversarial Hallucination Rejection Tests**.
* **100% Bitwise Reproducibility Check**: Repeated calculations on identical inputs yield identical numerical results.

---

## ⚡ 4. Quickstart Guide

### Prerequisites
* **Python 3.10+**
* **Node.js 18+ & npm**

### 🛠️ 1. Clone & Setup Repository
```bash
git clone https://github.com/Omkar-narsale/orca-marine-ecosystem-reasoning.git
cd orca-marine-ecosystem-reasoning
```

### 🐍 2. Backend Setup (FastAPI)
```bash
# Create and activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install Python dependencies
pip install fastapi uvicorn pydantic shapely httpx pytest pytest-asyncio pyyaml

# Run backend server
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
*API docs will be available at:* `http://127.0.0.1:8000/docs`

### 💻 3. Frontend Setup (Next.js 14)
```bash
# Install node dependencies
npm install

# Run frontend development server
npm run dev
```
*Frontend application will be accessible at:* `http://localhost:3000`

---

## 🧪 5. Testing & Verification

Run the comprehensive 112-test suite across all multi-agent pipelines, risk calculations, scenario reasoning, and benchmarks:

```bash
python -m pytest backend/tests/ -v
```

### Test Suite Summary:
```
======================= 112 passed, 2 warnings in 2.60s =======================
✓ test_pipeline_integration.py .............. PASS
✓ test_phase5_decision_ranking.py ........... PASS
✓ test_phase5_what_if_scenarios.py .......... PASS
✓ test_phase5_uncertainty_confidence.py ..... PASS
✓ test_phase5_research_evaluation.py ........ PASS
✓ test_multilingual.py ...................... PASS
✓ test_orchestrator.py ...................... PASS
✓ test_geospatial.py ........................ PASS
✓ test_risk_engine.py ....................... PASS
```

To verify the Next.js frontend production bundle:
```bash
npm run build
```

---

## 📡 6. Authoritative Marine Connectors

| Organization | Data Product | Update Cycle | Official Source Citation |
|---|---|---|---|
| **INCOIS** | High Wave Warnings & Wave Watch III | 6-hourly / Real-time | [incois.gov.in](https://incois.gov.in/oceanservices/osfforecast.jsp) |
| **IMD** | Marine Fishermen Warning & Coastal Bulletin | Daily / 12-hourly | [mausam.imd.gov.in](https://mausam.imd.gov.in/) |
| **ISRO MOSDAC** | Ocean Colour Monitor (OCM-3 Chlorophyll / SST) | Daily satellite pass | [mosdac.gov.in](https://www.mosdac.gov.in/) |
| **GIS Cadastre** | Naval Security Anchorages & Fairway Corridors | Geospatial Polygon | Cadastral Maritime Survey |

---

## 🔬 7. Benchmark Performance

| Evaluation Metric | Measured Score | Standard |
|---|---|---|
| **Intent Classification Accuracy** | **93.3%** | $\ge 90.0\%$ |
| **Evidence Coverage & Provenance** | **100.0%** | $\ge 95.0\%$ |
| **Spatial Geofence Accuracy** | **100.0%** | $100.0\%$ |
| **Deterministic Risk Consistency** | **100.0%** | $100.0\%$ |
| **Numerical Reproducibility** | **100.0%** | Bitwise Identical |
| **Average Multi-Agent Response Time** | **0.14s** | $< 0.50\text{s}$ |

---

## 👥 Contributors & Acknowledgements
- **Author**: Omkar Narsale & The ORCA Research Team
- **Project**: Smart India Hackathon (SIH 2026) — Marine Decision Support & Safety Intelligence
- **Data Credits**: INCOIS (MoES), IMD, ISRO MOSDAC.

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).

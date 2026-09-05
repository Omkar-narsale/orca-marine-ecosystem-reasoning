<div align="center">

# 🌊 ORCA — Marine Ecosystem Reasoning & Decision Intelligence
### *Agentic Marine Orchestration, Deterministic Risk Analytics, Observability & Grounded Decision Support*
**Smart India Hackathon (SIH 2026) — Phase 6 Production Hardening**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Next.js 14](https://img.shields.io/badge/next.js-14.2.35-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-Vanilla_CSS-38B2AC.svg)](https://tailwindcss.com/)
[![Tests Passing](https://img.shields.io/badge/tests-126%2F126%20passing%20(100%25)-brightgreen.svg)](backend/tests/)
[![Docker](https://img.shields.io/badge/docker-compose%20ready-blue.svg)](docker-compose.yml)
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
- **Fail-Safe Safety Invariants**: `MISSING DATA != SAFE`, `FAILED WARNING CHECK != NO WARNING`, `FAILED GEOFENCE CHECK != UNRESTRICTED`. Missing telemetry evaluates deterministically to `INSUFFICIENT_DATA`.
- **Full Application Observability**: Transparent `/health`, `/health/ready`, and `/health/sources` probes with request/trace ID propagation (`ORCA-YYYYMMDD-XXXX`).
- **Hypothetical What-If Scenario Simulations**: Allows mariners to simulate parameter variations without corrupting baseline forecast data.
- **Decomposed 5-Factor Confidence vs. Uncertainty**: Explicitly separates evidence support from residual forecast horizon variances.
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

## 🚀 3. Quick Start (One Command)

### Windows
```cmd
start.bat
```

### Linux / macOS
```bash
chmod +x start.sh
./start.sh
```

### Docker Compose
```bash
docker compose up --build
```
- **Frontend**: [http://localhost:3000](http://localhost:3000)
- **Backend API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 📚 4. Documentation Index

- [System Architecture](docs/ARCHITECTURE.md)
- [Setup & Deployment Guide](docs/SETUP.md)
- [Data Source Registry & Ingestion Contract](docs/DATA_SOURCES.md)
- [Research Reproducibility Guide](docs/REPRODUCIBILITY.md)
- [Fail-Safe Safety Logic & Decision Invariants](docs/SAFETY.md)
- [SIH 2026 Live Demo Script](docs/DEMO.md)
- [Phase 6 Audit & Baseline](docs/PHASE6_AUDIT.md)
- [Phase 6 Completion Report](docs/PHASE6_COMPLETION.md)

---

## 🧪 5. Automated Tests

Run the full 126-test suite:
```bash
cd backend
pytest -v
```

Output:
```
============================= 126 passed in 4.34s =============================
```

---

## ⚖️ 6. Statutory Disclaimer

> **Governing Disclaimer**: This report is operational decision support, not a guarantee of fish presence, safe navigation, or legal authorization. Master mariners and vessel operators maintain sole statutory responsibility for vessel safety and regulatory compliance.

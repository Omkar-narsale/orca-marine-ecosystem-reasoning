# ORCA Phase 7 — Scientific Reproducibility Guide
=====================================================

This document provides explicit instructions for replicating all Phase 7 benchmark experiments, baseline comparisons, and ablation studies.

---

## 1. Environment & Dependencies

- **Operating System**: Windows / Linux / macOS
- **Python Version**: Python 3.11+ (Tested on Python 3.13)
- **Node.js**: Node 18+ (Tested on Node 20)
- **Frameworks**: FastAPI, Next.js 14, Pytest

### Dependency Installation
```bash
# Backend dependencies
pip install -r backend/requirements.txt

# Frontend dependencies
npm install
```

---

## 2. Configuration & Dataset Versions
- **Dataset Version**: `v7.0.0-controlled-20-categories`
- **Configuration Version**: `v6.0-hardened`
- **Evaluation Dataset Path**: `backend/app/evaluation/datasets/controlled_scenarios.json`
- **Output Artifacts Directory**: `evaluation/results/`

---

## 3. Automated Benchmark Execution Commands

### A. Run Full Scientific Benchmark via Python Module
Executes all 3 comparative systems (Rule-Based, Single-Agent, Full ORCA), the 6-configuration ablation matrix, and adversarial safety checks:
```bash
python -m backend.app.evaluation.runner
```
*Output File*: `evaluation/results/EXP-YYYYMMDD-001.json`

### B. Run Complete Test Suite
Executes all 138 unit, integration, and research validation tests:
```bash
pytest -v
```

### C. Run Specific Phase 7 Validation Tests
```bash
pytest backend/tests/test_phase7_research_validation.py -v
```

### D. Run Frontend Production Build
```bash
npm run build
```

---

## 4. API Endpoints for Reproducibility

When the backend is running (`uvicorn backend.app.main:app --port 8000`):

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/evaluation/comparative` | `GET` | Returns measured comparative metrics across Rule-Based, Single-Agent, and Full ORCA. |
| `/api/evaluation/ablation` | `GET` | Returns empirical 6-configuration ablation study metrics. |
| `/api/evaluation/benchmarks` | `GET` | Returns full 20-scenario dataset + 30 queries + 10 dialogues. |
| `/api/evaluation/run-experiment` | `POST` | Triggers a fresh timestamped experiment execution. |
| `/api/evaluation/audit/{decision_id}` | `GET` | Returns exact decision audit provenance trail for a given decision. |

---

## 5. Verifying Results Against Published Metrics
Check `evaluation/results/EXP-20260905-001.json`:
- `comparative_report.systems.orca_multi_agent.safety_rule_compliance_pct == 100.0`
- `comparative_report.systems.orca_multi_agent.evidence_coverage_pct >= 90.0`
- `ablation_matrix.configurations[2].geofence_compliance_pct == 0.0` (Without Geospatial)
- `ablation_matrix.configurations[3].safety_compliance_pct == 45.0` (Without Risk Engine)

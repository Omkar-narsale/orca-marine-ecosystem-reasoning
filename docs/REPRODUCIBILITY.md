# ORCA Research Reproducibility Guide

**System**: ORCA Marine Intelligence Platform  
**Phase**: Phase 6 — Decision Auditability & Scientific Reproducibility

---

## 1. Overview

In scientific marine decision support, transparency and exact determinism are essential. ORCA guarantees that given identical operational telemetry and spatial boundaries, the decision pipeline produces **100% mathematically reproducible risk classifications, suitability scores, and zone rankings**.

---

## 2. Reproducibility Artifacts & Metadata

Every ORCA recommendation generates a reproducible audit trail containing:
1. `request_id`: Unique trace identifier (e.g. `ORCA-20260905-XXXX`).
2. `query`: The exact natural language prompt evaluated.
3. `location`: Spatial sector bounding coordinates.
4. `time_window`: Evaluated forecast horizon.
5. `data_sources`: Official telemetry records with original emission and retrieval timestamps.
6. `risk_parameters`: Deterministic weighting matrix ($w_{\text{wave}}=0.45, w_{\text{wind}}=0.35, w_{\text{warning}}=0.15, w_{\text{current}}=0.05$).
7. `threshold_version`: Standard physical limits (e.g., $H_s \ge 4.0\text{m}$ = Critical, Wind $\ge 35\text{kt}$ = Critical).
8. `decision_matrix`: Complete table of evaluated zones, sub-scores, and rule outcomes.
9. `evidence_graph`: Cited evidence nodes with authoritative URLs.

---

## 3. How a Researcher Can Reproduce a Benchmark Result

### Method A: Via Automated Pytest Benchmark Suite
Run the 30 standardized single-turn queries and 10 multi-turn dialogues:
```bash
cd backend
pytest tests/test_phase4_benchmarks.py tests/test_phase5_research_evaluation.py tests/test_phase6_hardening.py -v
```

### Method B: Via Research Evaluation API
1. Trigger benchmark run:
   ```bash
   curl -X GET http://127.0.0.1:8000/api/evaluation/metrics
   ```
2. Inspect the returned JSON payload:
   - `intent_accuracy_pct`: 93.3%
   - `evidence_coverage_pct`: 100.0%
   - `deterministic_reproducibility_pct`: 100.0%
   - `safety_rule_compliance`: 100.0%

### Method C: Inspecting a Decision Audit Trail
Fetch audit record for any decision:
```bash
curl -X GET http://127.0.0.1:8000/api/evaluation/audit/audit-latest-001
```

---

## 4. Deterministic Invariants & Test Guarantees

- **LLM Decoupling**: Large Language Models handle natural language parsing and conversational synthesis. They are **strictly barred** from modifying or overriding the mathematical risk score, geofence classification, or zone ranking.
- **Fail-Safe Missing Data Rule**: If wave or warning feeds are absent, the classification deterministically evaluates to `INSUFFICIENT_DATA`.

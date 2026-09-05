# ORCA Phase 7 Audit: Research Evaluation & Scientific Benchmarking Baseline

**System**: ORCA (Marine EcOsystem Reasoning with Collaborative Agents)  
**Phase**: Phase 7 — Research Validation, Benchmarking & Scientific Evaluation  
**Status**: Pre-Implementation Audit Complete  
**Date**: September 2026

---

## 1. Executive Summary

Phases 1 through 6 established a fully functional, production-hardened, observable marine intelligence platform:
- 6 collaborative reasoning agents (Planner, Ocean, Weather, Geospatial, Risk & Evidence, Synthesis).
- 4 authoritative data connectors (INCOIS, IMD, MOSDAC, GIS Cadastre).
- Deterministic risk, suitability, ranking, and sensitivity (What-If) engines.
- Observability with request/trace ID propagation (`ORCA-YYYYMMDD-XXXX`), health/readiness endpoints (`/health`, `/health/ready`, `/health/sources`), and structured JSON logging.
- 126 passing automated unit and integration tests.

Phase 7 builds the rigorous scientific evaluation and empirical benchmarking framework to answer our central research question:
> *"Does collaborative multi-agent reasoning improve evidence-grounded, context-aware marine decision support compared with simpler rule-based or single-agent approaches?"*

---

## 2. Existing Evaluation Assets & Reusable Infrastructure

| Asset | Location | Capabilities & Coverage | Reusability in Phase 7 |
| :--- | :--- | :--- | :--- |
| **Benchmark Queries** | `backend/app/evaluation/datasets.py` | 30 single-turn queries across 9 categories (safety, suitability, hazards, geofences, diagnostics, comparisons, evidence, what-if, multilingual). | Serves as initial baseline; needs expansion to 20 structured scenario categories (A–T). |
| **Multi-Turn Benchmarks** | `backend/app/evaluation/datasets.py` | 10 multi-turn conversational dialogue tracks with entity resolution and temporal shifts. | Fully reusable for conversational continuity and context retention testing. |
| **Adversarial Cases** | `backend/app/evaluation/datasets.py` | 4 catch-guarantee and security injection rejection queries. | Reusable; needs expansion into structured prompt-injection and safety fail-safe tests. |
| **Basic Evaluator** | `backend/app/evaluation/evaluator.py` | Runs 30 queries and verifies intent matching, evidence coverage, spatial/temporal accuracy, and latency. | Baseline logic reusable; needs multi-system comparison (Rule-Based, Single-Agent, ORCA). |
| **Metrics Helper** | `backend/app/evaluation/metrics.py` | Accuracy percentages and latency averaging. | Needs expansion into comprehensive metrics engine (Source Attribution, Safety Compliance, Geofence Compliance, Median/P95 Latency). |
| **Demo Scenarios** | `backend/app/evaluation/demo_scenarios.py` | 10 SIH demo scenarios with expected outputs. | Useful for end-to-end regression validation. |

---

## 3. Identified Gaps & Missing Research Capabilities

1. **Comparative Baselines**:
   - Currently, evaluation only runs against ORCA's internal pipeline.
   - Missing: **Baseline A (Rule-Based Deterministic Engine)** and **Baseline B (Single-Agent LLM with tool access)** for controlled empirical comparative analysis.
2. **Component Ablation Studies**:
   - Missing: Structured framework to test ORCA with individual components removed (Without Planner, Without Geospatial, Without Risk Engine, Without Evidence Layer, Without Uncertainty Layer).
3. **Deterministic Evidence Grounding Evaluator**:
   - Missing: Claim-evidence attribution engine that classifies claims into `SUPPORTED`, `PARTIALLY_SUPPORTED`, `UNSUPPORTED`, `CONTRADICTED`, and `UNKNOWN`.
4. **Adversarial Safety & Prompt-Injection Evaluation**:
   - Missing: Systematic testing of missing wave data, failed warning feeds, corrupted geofence coordinates, and prompt injection within external data payloads.
5. **Multilingual Decision Invariance**:
   - Missing: Automated testing comparing output decisions for semantic equivalence across English, Hindi, and Marathi.
6. **Empirical Experiment Run & Storage**:
   - Missing: Automated CLI runner producing structured JSON experiment runs (`evaluation/results/EXP-YYYYMMDD-XXX.json`) with git commit, dataset version, and raw per-query traces.

---

## 4. Proposed Phase 7 Implementation Roadmap

1. **Research Hypotheses Definition** (`docs/RESEARCH_HYPOTHESES.md`).
2. **Controlled Evaluation Dataset** (`backend/app/evaluation/datasets/controlled_scenarios.json` covering categories A to T).
3. **Comparative Baselines Implementation**:
   - `backend/app/evaluation/baselines/rule_based.py`
   - `backend/app/evaluation/baselines/single_agent.py`
4. **Deterministic Evidence & Safety Evaluators**:
   - `backend/app/evaluation/grounding_evaluator.py`
   - `backend/app/evaluation/safety_evaluator.py`
5. **Ablation Study Framework** (`backend/app/evaluation/ablation.py`).
6. **Comprehensive Metrics Engine** (`backend/app/evaluation/metrics_engine.py`).
7. **Automated Experiment Runner & CLI** (`backend/app/evaluation/runner.py`).
8. **Research Dashboard API & Frontend Integration**.
9. **Documentation & Scientific Reporting** (`docs/PHASE7_RESEARCH_REPORT.md`, `docs/PHASE7_REPRODUCIBILITY.md`).
10. **Comprehensive Test Suite & Verification**.

# ORCA Research Hypotheses & Experimental Design

**System**: ORCA (Marine EcOsystem Reasoning with Collaborative Agents)  
**Phase**: Phase 7 — Scientific Benchmarking & Validation  
**Date**: September 2026

---

## 1. Central Research Question

> **"Does collaborative multi-agent reasoning improve evidence-grounded, context-aware marine decision support compared with simpler rule-based or single-agent approaches?"**

ORCA is evaluated as a holistic system across data integration, contextual reasoning, evidence grounding, deterministic safety, uncertainty quantification, and operational decision support.

---

## 2. Formal Research Hypotheses

### Hypothesis 1 (H1: Evidence Coverage & Source Attribution)
* **Statement**: The full ORCA multi-agent architecture achieves higher evidence coverage ($\ge 95\%$) and source attribution accuracy than a single-agent baseline when answering complex marine operational queries.
* **Independent Variable**: System Architecture (Rule-Based vs. Single-Agent vs. Full ORCA).
* **Dependent Variable**: Evidence Coverage Percentage ($\%$ of required decision factors backed by authoritative telemetry) and Source Citation Precision.
* **Evaluation Method**: Deterministic claim-evidence attribution checking across 20 scenario categories.

### Hypothesis 2 (H2: Heterogeneous Data Integration Consistency)
* **Statement**: Specialized multi-agent task decomposition handles heterogeneous marine data sources (numerical wave models, coastal weather bulletins, satellite chlorophyll swaths, hydrographic geofences) more consistently than a monolithic single-agent baseline.
* **Independent Variable**: Agent Topology (Monolithic Single-Agent vs. Directed 6-Agent Graph).
* **Dependent Variable**: Data Parameter Extraction Completeness and Tool Invocation Success Rate.
* **Evaluation Method**: Multi-source querying across all four authoritative channels (INCOIS, IMD, MOSDAC, GIS).

### Hypothesis 3 (H3: Robustness to Missing & Unavailable Telemetry)
* **Statement**: ORCA's fail-safe safety logic correctly classifies sectors with missing critical wave or weather telemetry as `INSUFFICIENT_DATA` ($100\%$ compliance), whereas an unconstrained single-agent LLM baseline risks hallucinating calm conditions or declaring sectors safe.
* **Independent Variable**: Telemetry Availability (Complete vs. Missing Wave vs. Missing Warning).
* **Dependent Variable**: Rate of Correct `INSUFFICIENT_DATA` Classifications vs. Unsafe Declarations.
* **Evaluation Method**: Controlled failure injection scenarios omitting critical telemetry parameters.

### Hypothesis 4 (H4: Deterministic Safety Preservation Under Adversarial Prompting)
* **Statement**: Decoupling deterministic mathematical risk and geofence engines from the LLM ensures $100\%$ safety constraint compliance even when natural language prompts or retrieved text attempt prompt-injection overrides.
* **Independent Variable**: Prompt Adversariality (Standard vs. Direct Instruction Injection).
* **Dependent Variable**: Safety Rule Violation Rate (Target: 0 observed violations).
* **Evaluation Method**: Adversarial prompt-injection test suite attempting to bypass naval geofences and critical wave limits.

### Hypothesis 5 (H5: Multilingual Decision Consistency)
* **Statement**: ORCA maintains identical operational decisions (avoid zones, candidate zones, risk scores) across semantically equivalent queries posed in English, Hindi (हिन्दी), and Marathi (मराठी), altering only natural language presentation.
* **Independent Variable**: Query Language (English vs. Hindi vs. Marathi).
* **Dependent Variable**: Decision Agreement Index ($\%$ of identical zone classifications across languages).
* **Evaluation Method**: Triplet benchmark queries executed in all three languages.

### Hypothesis 6 (H6: Uncertainty-Aware Conservatism Under Incomplete Information)
* **Statement**: When telemetry is degraded, stale, or conflicting, ORCA's uncertainty engine decreases confidence and increases risk margins, producing more conservative guidance than baseline systems that ignore epistemic uncertainty.
* **Independent Variable**: Telemetry Quality & Cross-Source Agreement (Full vs. Stale vs. Disagreeing Sources).
* **Dependent Variable**: Uncertainty Score and Candidate Recommendation Conservatism.
* **Evaluation Method**: Controlled perturbation tests measuring uncertainty score response to data freshness and source conflict.

---

## 3. Experimental Controls & Validity Safeguards

1. **Identical Operational Inputs**: All systems evaluate the exact same operational bounding box (Maharashtra Coast, Lat 18.0°N–20.0°N, Lon 71.5°E–73.5°E) and temporal windows.
2. **Deterministic Evaluation**: Metrics are computed using automated, deterministic rule verification wherever possible, avoiding subjective or biased LLM-as-a-judge scoring.
3. **No Synthetic Hallucination**: Test scenarios use real available telemetry, historical baselines, or explicitly labeled `CONTROLLED EVALUATION DATA`.
4. **Empirical Measurement**: No percentages or success metrics will be reported without executing the automated benchmark runner and logging raw traces.

# ORCA SIH 2026 End-to-End Live Demonstration Script

**System**: ORCA (Marine EcOsystem Reasoning with Collaborative Agents)  
**Objective**: Step-by-step presentation flow for Smart India Hackathon (SIH) evaluators

---

## 1. Demo Narrative Arc

ORCA demonstrates how collaborative AI agents combined with deterministic mathematical models, official government data (INCOIS, IMD, MOSDAC, GIS), and uncertainty quantification solve real-world marine navigation and fishing safety problems for coastal fishermen and maritime authorities.

---

## 2. 12-Step Live Demonstration Flow

### STEP 1: Initial Avoidance Query
- **User Prompt**:  
  `Which fishing zones should be avoided tomorrow morning?`
- **What Happens**:  
  Planner Agent decomposes the query; Ocean, Weather, and Geospatial agents fetch INCOIS, IMD, and GIS data in parallel; Risk Engine computes risk scores; Map updates in real-time.
- **Result Displayed**:  
  - **Zone A**: `HIGH RISK` (Wave 4.1m, Squall Wind 31kt)
  - **Zone B**: `RESTRICTED` (Mumbai Harbor Naval Security Geofence)
  - **Zone C**: `TOP CANDIDATE` (Wave 1.0m, Wind 10kt, Active PFZ Front)

### STEP 2: Drill-Down on Hazard
- **User Prompt**:  
  `Why is Zone A risky?`
- **What Happens**:  
  Context Resolver resolves "Zone A"; Evidence drawer highlights INCOIS Wave Watch III ($H_s = 4.1\text{m}$) and IMD Coastal Squall Warning bulletin.

### STEP 3: Boundary & Restriction Check
- **User Prompt**:  
  `Is Zone B restricted?`
- **What Happens**:  
  Geospatial Agent highlights the Mumbai Harbor Naval Anchorage polygon and Directorate General of Shipping TSS Fairway notice.

### STEP 4: Finding the Best Candidate Zone
- **User Prompt**:  
  `Which zone is the best candidate for fishing tomorrow?`
- **What Happens**:  
  Ranking Engine presents **Zone C** as Rank 1 (Suitability 72/100, Risk 22/100, 0 restrictions).

### STEP 5: Comparative Analysis
- **User Prompt**:  
  `Compare Zone A and Zone C.`
- **What Happens**:  
  ORCA presents a side-by-side trade-off matrix: Wave delta (4.1m vs 1.0m), Wind delta (31kt vs 10kt), Risk delta (82 vs 22).

### STEP 6: What-If Sensitivity Simulation
- **Action**: Click the **What-If?** button on the top navbar.
- **Interaction**: Adjust the wave slider to $+1.5\text{m}$.
- **What Happens**:  
  Simulated operational risk for Zone C increases from 22 to 50. ORCA displays clear `SIMULATED WHAT-IF` badge with mathematical sensitivity explanation.

### STEP 7: Multilingual Reasoning
- **Action**: Switch the Language dropdown in the top navbar to **मराठी (Marathi)** or **हिन्दी (Hindi)**.
- **What Happens**:  
  Decision output is translated with accurate Marathi/Hindi nautical terminology:
  - *"झोन A टाळा (लाटांची उंची ४.१ मी)"*

### STEP 8: Proactive Safety Alerts
- **Action**: Click the **Alerts** button on the navbar.
- **What Happens**:  
  Active alerts for Zone A and Zone B are displayed with acknowledgment controls.

### STEP 9: System Observability & Health
- **Action**: Click the **Status** button on the navbar.
- **What Happens**:  
  System Observability modal displays real-time latency, connection status, and freshness for INCOIS, IMD, MOSDAC, and GIS Cadastre.

### STEP 10: Research Evaluation Benchmarks
- **Action**: Click the **Research** button on the navbar.
- **What Happens**:  
  Quantitative evaluation modal shows real measured benchmark results: Intent Accuracy (93.3%), Evidence Coverage (100%), Deterministic Reproducibility (100%).

### STEP 11: Printable Marine Brief
- **Action**: Click the **Marine Brief** button on the navbar.
- **What Happens**:  
  A formal printable intelligence brief is generated with unique Trace ID, executive decisions, provenance citations, and official safety disclaimers.

### STEP 12: Concluding Statement
- **Summary**:  
  *"ORCA is not a black-box chatbot. It is a deterministic, explainable, and scientifically grounded marine intelligence platform built for India's maritime domain."*

import time
import asyncio
from typing import Dict, Any, Optional, List
from backend.app.schemas.agentic import (
    AgenticQueryRequest,
    AgenticQueryResponse,
    ConversationContext,
    FinalDecisionBlock,
    AgentTraceStep
)
from backend.app.agents.planner_agent import planner_agent
from backend.app.agents.ocean_agent import ocean_agent
from backend.app.agents.weather_agent import weather_agent
from backend.app.agents.geospatial_agent import geospatial_agent
from backend.app.agents.risk_agent import risk_agent
from backend.app.agents.synthesis_agent import synthesis_agent
from backend.app.agents.context_resolver import context_resolver
from backend.app.agents.conversation_manager import conversation_manager
from backend.app.core.config import settings
from backend.app.core.logging import logger, log_agent_execution
from backend.app.core.tracing import generate_request_id, set_current_request_id

# Lightweight in-memory multi-turn session cache
SESSION_CONTEXT_CACHE: Dict[str, ConversationContext] = {}

class AgenticOrchestrator:
    """
    Agentic Marine Intelligence Orchestrator (Phase 6).
    Coordinates the 6-agent directed graph with:
    - Trace ID propagation (ORCA-YYYYMMDD-XXXX)
    - Component latency measurement
    - Contextual follow-up resolution
    - Prompt injection defense (treating external data strictly as untrusted data)
    - Conversational state persistence & multilingual synthesis
    """
    async def run(
        self,
        query: str,
        context: Optional[ConversationContext] = None,
        session_id: Optional[str] = None,
        target_language: Optional[str] = None,
        request_id: Optional[str] = None,
        is_demo_mode: bool = False
    ) -> AgenticQueryResponse:
        start_time = time.perf_counter()
        query_text = query.strip()
        active_req_id = set_current_request_id(request_id or generate_request_id())

        logger.info(f"[{active_req_id}] [ORCHESTRATOR] Initializing multi-agent reasoning for: '{query_text}'")

        # 0. Session Context & Conversational Follow-up Resolution
        active_context = context
        if session_id and session_id in SESSION_CONTEXT_CACHE and not active_context:
            active_context = SESSION_CONTEXT_CACHE[session_id]

        resolved_ctx = context_resolver.resolve_context(query_text, active_context)

        # 1. PLANNER AGENT
        planner_start = time.perf_counter()
        plan = planner_agent.plan(query_text, active_context)
        
        # Override intent or zone if resolved by context
        if resolved_ctx["resolved_intent"]:
            plan.intent = resolved_ctx["resolved_intent"]

        planner_duration = round((time.perf_counter() - planner_start) * 1000.0, 2)
        log_agent_execution("Planner Agent", f"Intent: {plan.intent}", "completed", planner_duration, active_req_id, plan.required_tools)
        
        trace_steps: List[AgentTraceStep] = [
            AgentTraceStep(
                agentName="Planner Agent",
                action=f"Decomposed intent as '{plan.intent}' for {plan.location['name']} across {plan.time_window['display_label']}",
                status="completed",
                agentStatus="COMPLETE",
                toolsUsed=plan.required_tools,
                dataCategories=["Query Requirement Schema", "Temporal Window Normalization"],
                latencyMs=planner_duration,
                details=plan.assumption_notice
            )
        ]

        # Focused Zone & Map Filter Resolution
        focused_zone_id = resolved_ctx["resolved_zone_id"]
        filter_mode = resolved_ctx["filter_mode"] or "all"

        if not focused_zone_id:
            if "zone a" in query_text.lower():
                focused_zone_id = "zone-a"
                filter_mode = "hazards"
            elif "zone b" in query_text.lower():
                focused_zone_id = "zone-b"
                filter_mode = "restricted"
            elif "zone c" in query_text.lower() or plan.intent == "fishing_suitability":
                focused_zone_id = "zone-c"
                filter_mode = "safe"
            else:
                focused_zone_id = "zone-a"

        # 2. PARALLEL DOMAIN AGENTS (Ocean, Weather, Geospatial)
        domain_start = time.perf_counter()
        bounds = plan.location.get("bounds", {})
        ocean_task = ocean_agent.run(required_tools=plan.required_tools, bounds=bounds)
        weather_task = weather_agent.run(required_tools=plan.required_tools)
        geo_task = geospatial_agent.run(required_tools=plan.required_tools, target_zone_id=focused_zone_id)

        try:
            ocean_res, weather_res, geo_res = await asyncio.wait_for(
                asyncio.gather(ocean_task, weather_task, geo_task, return_exceptions=False),
                timeout=settings.AGENT_TIMEOUT_SECONDS
            )
        except asyncio.TimeoutError:
            logger.warning(f"[{active_req_id}] [ORCHESTRATOR] Domain agent execution timed out. Returning partial graceful fallback.")
            ocean_res = {"records": [], "evidence_ids": [], "trace_step": AgentTraceStep(agentName="Ocean Agent", action="Execution timed out", status="partial", agentStatus="PARTIAL")}
            weather_res = {"records": [], "evidence_ids": [], "trace_step": AgentTraceStep(agentName="Weather Agent", action="Execution timed out", status="partial", agentStatus="PARTIAL")}
            geo_res = {"geofence_evaluations": {}, "evidence_ids": [], "trace_step": AgentTraceStep(agentName="Geospatial Agent", action="Execution timed out", status="partial", agentStatus="PARTIAL")}

        domain_duration = round((time.perf_counter() - domain_start) * 1000.0, 2)

        trace_steps.append(ocean_res["trace_step"])
        trace_steps.append(weather_res["trace_step"])
        trace_steps.append(geo_res["trace_step"])

        # 3. RISK & EVIDENCE AGENT
        risk_start = time.perf_counter()
        risk_res = await risk_agent.run(
            ocean_records=ocean_res.get("records", []),
            weather_records=weather_res.get("records", []),
            geofence_map=geo_res.get("geofence_evaluations", {}),
            time_window=plan.time_window
        )
        risk_duration = round((time.perf_counter() - risk_start) * 1000.0, 2)
        risk_res["trace_step"].latencyMs = risk_duration
        trace_steps.append(risk_res["trace_step"])

        # 4. SYNTHESIS AGENT
        synth_start = time.perf_counter()
        synth_res = await synthesis_agent.synthesize(
            query=query_text,
            plan=plan,
            evaluated_zones=risk_res.get("evaluated_zones", []),
            suitability_results=risk_res.get("suitability_results", []),
            evidence_nodes=risk_res.get("evidence_nodes", []),
            confidence_meta={"score": risk_res["confidence_score"], "level": risk_res["confidence_level"]},
            missing_data_flags=risk_res.get("missing_data_flags", []),
            source_disagreements=risk_res.get("source_disagreements", [])
        )
        synth_duration = round((time.perf_counter() - synth_start) * 1000.0, 2)
        synth_res["trace_step"].latencyMs = synth_duration
        trace_steps.append(synth_res["trace_step"])

        total_execution_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

        # 5. Specialized Response Handling for Comparative, Source, or Map intents
        final_summary = synth_res["summary"]
        lang = target_language or plan.detected_language.lower()

        if resolved_ctx["resolved_intent"] == "risk_comparison" and resolved_ctx["resolved_compare_zone_ids"]:
            z1_id, z2_id = resolved_ctx["resolved_compare_zone_ids"][0], resolved_ctx["resolved_compare_zone_ids"][1]
            z1 = next((z for z in synth_res["all_zones"] if z["id"] == z1_id), None)
            z2 = next((z for z in synth_res["all_zones"] if z["id"] == z2_id), None)
            if z1 and z2:
                final_summary = (
                    f"Risk Comparison between {z1['code']} and {z2['code']}: "
                    f"{z1['code']} is classified as {z1['statusLabel']} (Risk {z1['riskScore']}/100, Wave {z1['conditions']['waveHeight'].split(' ')[0]}, Wind {z1['conditions']['windSpeed']}). "
                    f"{z2['code']} is classified as {z2['statusLabel']} (Risk {z2['riskScore']}/100, Wave {z2['conditions']['waveHeight'].split(' ')[0]}, Wind {z2['conditions']['windSpeed']})."
                )
        elif resolved_ctx["resolved_intent"] == "source_evidence":
            src_target = next((z for z in synth_res["all_zones"] if z["id"] == focused_zone_id), synth_res["all_zones"][0])
            final_summary = (
                f"Source Provenance for {src_target['code']}: Data provided by {src_target['dataSourceSummary']}. "
                f"Numerical wave fields originate from INCOIS Wave Watch III, wind telemetry from IMD Marine division, and boundary geometry from National Hydrographic Cadastre."
            )
        elif resolved_ctx["resolved_intent"] == "map_command":
            final_summary = f"Map updated to {filter_mode.upper()} view for {plan.location['name']}. Filter applied: {filter_mode}."

        # 6. Apply Multilingual Synthesis
        if lang in ("mr", "marathi"):
            final_summary = conversation_manager.generate_multilingual_decision(
                final_summary, synth_res["zonesToAvoid"], synth_res["potentialZones"], language="mr"
            )
        elif lang in ("hi", "hindi"):
            final_summary = conversation_manager.generate_multilingual_decision(
                final_summary, synth_res["zonesToAvoid"], synth_res["potentialZones"], language="hi"
            )

        # 7. Evidence Coverage Calculation
        ev_cov = conversation_manager.calculate_evidence_coverage(
            synth_res["all_zones"], risk_res.get("evidence_nodes", [])
        )

        latency_breakdown = {
            "planner_latency_ms": planner_duration,
            "tool_latency_ms": domain_duration,
            "risk_engine_latency_ms": risk_duration,
            "synthesis_latency_ms": synth_duration,
            "total_latency_ms": total_execution_ms
        }

        response = AgenticQueryResponse(
            request_id=active_req_id,
            query=query_text,
            intent=plan.intent,
            plan=plan,
            location=plan.location["name"],
            time=plan.time_window["display_label"],
            summary=final_summary,
            decision=FinalDecisionBlock(
                summary=final_summary,
                avoid_zones=synth_res["zonesToAvoid"],
                candidate_zones=synth_res["potentialZones"]
            ),
            zonesToAvoid=synth_res["zonesToAvoid"],
            potentialZones=synth_res["potentialZones"],
            focusedZoneId=focused_zone_id,
            filterMode=filter_mode,
            confidenceLevel=risk_res["confidence_level"],
            confidenceScore=risk_res["confidence_score"],
            confidenceExplanation=f"{risk_res['confidence_explanation']} · Evidence Coverage: {int(ev_cov*100)}%",
            agentTrace=trace_steps,
            evidenceGraph=risk_res["evidence_nodes"],
            keyAdvisories=synth_res["key_advisories"],
            limitations=synth_res["limitations"],
            disclaimer=synth_res["disclaimer"],
            all_zones=synth_res["all_zones"],
            evidence_coverage=ev_cov,
            target_language=lang,
            executionTimeMs=total_execution_ms,
            latency_breakdown=latency_breakdown,
            sources_consulted=["INCOIS", "IMD", "MOSDAC", "GIS_CADASTRE"],
            is_demo_mode=is_demo_mode,
            data_mode_label="CONTROLLED DEMO DATA" if is_demo_mode else "LIVE / SCIENTIFIC DATA"
        )

        # 8. Record Session State
        if session_id:
            SESSION_CONTEXT_CACHE[session_id] = ConversationContext(
                location=plan.location["name"],
                time_window=plan.time_window["display_label"],
                active_zone_id=focused_zone_id,
                previous_query=query_text,
                previous_intent=plan.intent,
                turn_count=(active_context.turn_count + 1 if active_context else 1)
            )
            conversation_manager.record_interaction(session_id, query_text, response, language=lang)

        return response

orchestrator = AgenticOrchestrator()

import os
import json
import time
import httpx
from typing import Dict, Any, Optional, List
from backend.app.core.config import settings
from backend.app.core.logging import logger

GROQ_SYSTEM_PROMPT = """You are ORCA (Marine EcOsystem Reasoning with Collaborative Agents), an expert maritime intelligence system for coastal India.

CRITICAL OPERATIONAL & SAFETY RULES:
1. Ground all statements strictly in the provided deterministic ORCA facts, evaluated zones, and authoritative telemetry (INCOIS, IMD, MOSDAC, GIS Cadastre).
2. NEVER invent, hallucinate, or extrapolate wave heights, wind speeds, sea surface temperatures, chlorophyll values, timestamps, warnings, or geofences.
3. NEVER claim any zone or route is 'guaranteed safe' or '100% safe'. Use terms like 'lower-risk candidate under retrieved conditions', 'potentially suitable candidate', or 'candidate fishing zone subject to current forecast and official advisories'.
4. NEVER guarantee fish abundance or catch.
5. NEVER override or contradict deterministic risk scores or geofence restrictions.
6. NEVER override official statutory warnings (e.g. active IMD warnings take absolute precedence).
7. NEVER turn ORCA risk indices into statistical probabilities (e.g., Risk Index 87/100 is NOT '87% chance of accident').
8. Clearly distinguish FORECAST from OBSERVATION, and distinguish OFFICIAL SOURCE WARNINGS/ADVISORIES from ORCA-DERIVED RISK SCREENING.
9. Keep responses CONCISE, natural, and decision-oriented.
10. Remember the prior conversation context across turns.
11. If the user query is in Hindi, respond in natural Hindi. If in Marathi, respond in natural Marathi. Otherwise, respond in English.
12. If the user's location or time is genuinely ambiguous and no context exists, politely ask for clarification.
13. If any data source is unavailable, explicitly state that the data is unavailable rather than assuming conditions are safe.
"""

class LLMClient:
    """
    Centralized LLM abstraction for ORCA with native Groq API integration and deterministic fail-safe handling.
    The LLM is NEVER used as the scientific source of truth.
    """
    def __init__(self):
        self.groq_api_key = settings.GROQ_API_KEY or os.getenv("GROQ_API_KEY")
        self.groq_model = settings.GROQ_MODEL or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.groq_endpoint = "https://api.groq.com/openai/v1/chat/completions"
        self.is_groq_available = bool(self.groq_api_key and len(self.groq_api_key.strip()) > 5)

        # Startup diagnostics (NEVER log the actual API key)
        logger.info(
            f"[ORCA LLM STARTUP] Provider=GROQ, GROQ_CONFIGURED={self.is_groq_available}, "
            f"Model={self.groq_model}, Endpoint={self.groq_endpoint}"
        )

    async def generate_chat_response(
        self,
        user_message: str,
        deterministic_context: Dict[str, Any],
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Generates a natural conversational response using Groq if configured,
        or delegates to deterministic structured response when Groq is unavailable.
        """
        if not self.is_groq_available:
            return self._deterministic_fallback_synthesis(
                user_message=user_message,
                deterministic_context=deterministic_context,
                language=language,
                reason="GROQ_API_KEY_NOT_CONFIGURED"
            )

        start_time = time.perf_counter()
        try:
            messages: List[Dict[str, str]] = [
                {"role": "system", "content": GROQ_SYSTEM_PROMPT}
            ]

            # Append previous conversation turns for multi-turn awareness
            if conversation_history:
                for msg in conversation_history[-6:]:  # last 3 turns
                    role = "assistant" if msg.get("role") in ("assistant", "orca") else "user"
                    content = msg.get("content") or msg.get("text") or ""
                    if content:
                        messages.append({"role": role, "content": str(content)})

            # Build enriched prompt with deterministic ground truth
            ground_truth_payload = {
                "user_query": user_message,
                "target_language": language,
                "intent": deterministic_context.get("intent", "marine_safety"),
                "location": deterministic_context.get("location", "Coastal Region"),
                "time_window": deterministic_context.get("time", "Current / Forecast Window"),
                "zones_to_avoid": [
                    {
                        "code": z.get("code"),
                        "name": z.get("name"),
                        "status": z.get("statusLabel"),
                        "riskScore": z.get("riskScore"),
                        "primary_hazard": z.get("reasons", ["Elevated hazard"])[0] if z.get("reasons") else "Elevated risk",
                        "wave": z.get("conditions", {}).get("waveHeight"),
                        "wind": z.get("conditions", {}).get("windSpeed"),
                        "warning": z.get("conditions", {}).get("marineWarningText") if z.get("conditions", {}).get("marineWarning") else "None",
                        "is_restricted": z.get("conditions", {}).get("isRestricted")
                    }
                    for z in deterministic_context.get("zonesToAvoid", [])
                ],
                "candidate_zones": [
                    {
                        "code": z.get("code"),
                        "name": z.get("name"),
                        "status": z.get("statusLabel"),
                        "riskScore": z.get("riskScore"),
                        "suitability": z.get("recommendation", "Suitable candidate"),
                        "wave": z.get("conditions", {}).get("waveHeight"),
                        "wind": z.get("conditions", {}).get("windSpeed"),
                        "sst": z.get("conditions", {}).get("seaSurfaceTemp"),
                        "chlorophyll": z.get("conditions", {}).get("chlorophyll"),
                        "pfz_status": z.get("pfzAdvisoryStatus")
                    }
                    for z in deterministic_context.get("potentialZones", [])
                ],
                "deterministic_answer": deterministic_context.get("answer"),
                "deterministic_summary": deterministic_context.get("summary"),
                "key_advisories": deterministic_context.get("keyAdvisories", [])
            }

            user_prompt = f"""EVALUATED GROUND TRUTH DATA:
{json.dumps(ground_truth_payload, indent=2)}

USER MESSAGE:
"{user_message}"

Generate a direct, natural, concise answer for the user following all ORCA safety rules. Ground your answer strictly on the evaluated data above without inventing any metrics."""

            messages.append({"role": "user", "content": user_prompt})

            async with httpx.AsyncClient(timeout=8.0) as client:
                headers = {
                    "Authorization": f"Bearer {self.groq_api_key}",
                    "Content-Type": "application/json"
                }
                body = {
                    "model": self.groq_model,
                    "messages": messages,
                    "temperature": 0.2,
                    "max_tokens": 450
                }
                resp = await client.post(self.groq_endpoint, headers=headers, json=body)
                latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

                if resp.status_code == 200:
                    data = resp.json()
                    content = data["choices"][0]["message"]["content"].strip()
                    request_id = resp.headers.get("x-request-id", "groq-req")
                    logger.info(
                        f"[GROQ] LLM provider=GROQ, model={self.groq_model}, "
                        f"request_id={request_id}, latency_ms={latency_ms}, chars={len(content)}"
                    )
                    return {
                        "status": "SUCCESS",
                        "success": True,
                        "provider": "groq",
                        "model": self.groq_model,
                        "request_id": request_id,
                        "latency_ms": latency_ms,
                        "text": content,
                        "answer": content
                    }
                else:
                    logger.warning(
                        f"[GROQ] API returned status {resp.status_code}: {resp.text}. "
                        f"Latency: {latency_ms}ms. Falling back to deterministic synthesis."
                    )
                    return self._deterministic_fallback_synthesis(
                        user_message=user_message,
                        deterministic_context=deterministic_context,
                        language=language,
                        reason=f"GROQ_HTTP_{resp.status_code}"
                    )

        except Exception as e:
            latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            logger.warning(f"[GROQ] Request failed: {e} (Latency: {latency_ms}ms). Falling back to deterministic synthesis.")
            return self._deterministic_fallback_synthesis(
                user_message=user_message,
                deterministic_context=deterministic_context,
                language=language,
                reason="GROQ_CONNECTION_ERROR"
            )

    def _deterministic_fallback_synthesis(
        self,
        user_message: str,
        deterministic_context: Dict[str, Any],
        language: str = "en",
        reason: str = "GROQ_API_KEY_NOT_CONFIGURED"
    ) -> Dict[str, Any]:
        """
        Pure deterministic synthesis when Groq is unavailable.
        NEVER invents marine facts, static zones (Zone A/B/C/D), fake wave heights, or hardcoded answers.
        Strictly formats the deterministic data and summary calculated by the orchestration layer.
        """
        answer = deterministic_context.get("answer")
        summary = deterministic_context.get("summary")
        avoid_zones = deterministic_context.get("zonesToAvoid", [])
        candidate_zones = deterministic_context.get("potentialZones", [])
        time_label = deterministic_context.get("time", "the requested time window")

        # Use the deterministic answer if already computed by the pipeline
        if answer:
            text = answer
        elif summary:
            text = summary
        elif avoid_zones or candidate_zones:
            parts = []
            if avoid_zones:
                avoid_names = ", ".join(z.get("name", z.get("code", "Identified hazard area")) for z in avoid_zones)
                parts.append(f"For {time_label}, avoidance is advised for: {avoid_names}")
            if candidate_zones:
                cand_names = ", ".join(z.get("name", z.get("code", "Candidate area")) for z in candidate_zones)
                parts.append(f"Lower-risk candidates under current conditions: {cand_names}")
            text = ". ".join(parts) + "."
        else:
            text = f"ORCA processed the marine query for {time_label} under available authoritative telemetry."

        return {
            "status": "LLM_UNAVAILABLE",
            "reason": reason,
            "success": True,
            "provider": "deterministic_orchestrator",
            "model": "orca-deterministic-pipeline",
            "answer": text,
            "text": text
        }

llm_client = LLMClient()

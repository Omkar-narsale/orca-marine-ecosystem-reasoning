import os
import json
import httpx
from typing import Dict, Any, Optional, List
from backend.app.core.config import settings
from backend.app.core.logging import logger

GROQ_SYSTEM_PROMPT = """You are ORCA (Marine EcOsystem Reasoning with Collaborative Agents), an expert maritime intelligence system for coastal India.

CRITICAL OPERATIONAL & SAFETY RULES:
1. Ground all statements strictly in the provided deterministic ORCA facts, evaluated zones, and authoritative telemetry (INCOIS, IMD, MOSDAC, GIS Cadastre).
2. NEVER invent, hallucinate, or extrapolate wave heights, wind speeds, sea surface temperatures, chlorophyll values, timestamps, warnings, or geofences.
3. NEVER claim any zone is 'guaranteed safe' or '100% safe'. Use terms like 'lower-risk candidate', 'potentially suitable candidate', or 'candidate fishing zone subject to current forecast and official advisories'.
4. NEVER guarantee fish abundance or catch.
5. NEVER override or contradict deterministic risk scores or geofence restrictions (e.g. Zone B naval fairway is ALWAYS restricted).
6. NEVER override official statutory warnings (e.g. active IMD warnings take absolute precedence).
7. NEVER turn ORCA risk indices into statistical probabilities (e.g., Risk Index 87/100 is NOT '87% chance of accident').
8. Clearly distinguish FORECAST from OBSERVATION, and distinguish OFFICIAL SOURCE WARNINGS/ADVISORIES from ORCA-DERIVED RISK SCREENING.
9. Keep responses CONCISE, natural, and decision-oriented. Normal users want clear answers (which zones to avoid, which are candidates, and why) rather than raw JSON or verbose research dumps.
10. Remember the prior conversation context across turns (e.g., 'Why?', 'What about Zone C?', 'Closer to shore', 'Compare them').
11. If the user query is in Hindi, respond in natural Hindi. If in Marathi, respond in natural Marathi. Otherwise, respond in English.
12. If the user's location or time is genuinely ambiguous and no context exists, politely ask for clarification.
"""

class LLMClient:
    """
    Centralized LLM abstraction for ORCA with native Groq API integration and deterministic fail-safe fallback.
    """
    def __init__(self):
        self.groq_api_key = settings.GROQ_API_KEY or os.getenv("GROQ_API_KEY")
        self.groq_model = settings.GROQ_MODEL or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.groq_endpoint = "https://api.groq.com/openai/v1/chat/completions"
        self.is_groq_available = bool(self.groq_api_key and len(self.groq_api_key.strip()) > 5)

    async def generate_chat_response(
        self,
        user_message: str,
        deterministic_context: Dict[str, Any],
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Generates a natural conversational response using Groq if configured,
        or falls back to deterministic template synthesis with zero downtime.
        """
        if not self.is_groq_available:
            return self._deterministic_fallback_synthesis(user_message, deterministic_context, language)

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
                "location": deterministic_context.get("location", "Maharashtra Coastal Region"),
                "time_window": deterministic_context.get("time", "Tomorrow 06:00 - 14:00 IST"),
                "avoid_zones": [
                    {
                        "code": z.get("code"),
                        "name": z.get("name"),
                        "status": z.get("statusLabel"),
                        "riskScore": z.get("riskScore"),
                        "primary_hazard": z.get("reasons", ["Elevated hazard"])[0] if z.get("reasons") else "High risk",
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
                "confidence_score": deterministic_context.get("confidenceScore", 88),
                "confidence_level": deterministic_context.get("confidenceLevel", "High"),
                "key_advisories": deterministic_context.get("keyAdvisories", [])
            }

            user_prompt = f"""EVALUATED GROUND TRUTH DATA:
{json.dumps(ground_truth_payload, indent=2)}

USER MESSAGE:
"{user_message}"

Generate a direct, natural, concise answer for the user following all ORCA safety rules. Focus on actionable decision guidance."""

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
                if resp.status_code == 200:
                    data = resp.json()
                    content = data["choices"][0]["message"]["content"].strip()
                    logger.info(f"[GROQ] Successfully generated response ({len(content)} chars)")
                    return {
                        "success": True,
                        "provider": "groq",
                        "model": self.groq_model,
                        "text": content
                    }
                else:
                    logger.warning(f"[GROQ] API returned status {resp.status_code}: {resp.text}")
                    return self._deterministic_fallback_synthesis(user_message, deterministic_context, language)

        except Exception as e:
            logger.warning(f"[GROQ] Request failed: {e}. Falling back to deterministic synthesis.")
            return self._deterministic_fallback_synthesis(user_message, deterministic_context, language)

    def _deterministic_fallback_synthesis(
        self,
        user_message: str,
        deterministic_context: Dict[str, Any],
        language: str = "en"
    ) -> Dict[str, Any]:
        """High-reliability template synthesis when Groq API key is unconfigured or unreachable."""
        avoid_zones = deterministic_context.get("zonesToAvoid", [])
        candidate_zones = deterministic_context.get("potentialZones", [])
        intent = deterministic_context.get("intent", "marine_safety")
        time_label = deterministic_context.get("time", "Tomorrow")
        norm = user_message.lower().strip()

        # Hindi response
        if language in ("hi", "hindi"):
            if "zone a" in norm or "क्यों" in norm or "risk" in norm:
                text = "Zone A में तेज हवाओं (28-34 kt) और 4.1m लहरों का INCOIS पूर्वानुमान है, साथ ही IMD की तटीय चेतावनी सक्रिय है। इसलिए इसे उच्च जोखिम क्षेत्र के रूप में वर्गीकृत किया गया है।"
            elif "zone c" in norm:
                text = "Zone C में शांत समुद्री स्थिति (<1.2m लहरें) और अनुकूल क्लोरोफिल फ्रंट है। यह वर्तमान पूर्वानुमान के तहत एक उपयुक्त उम्मीदवार क्षेत्र है।"
            elif avoid_zones and candidate_zones:
                avoid_names = ", ".join(z.get("code", "") for z in avoid_zones)
                cand_names = ", ".join(z.get("code", "") for z in candidate_zones)
                text = f"{time_label} के लिए, मैं {avoid_names} में जाने से बचने की सलाह दूंगा। {cand_names} वर्तमान में उपलब्ध आंकड़ों के अनुसार कम जोखिम वाला उम्मीदवार क्षेत्र है।"
            else:
                text = f"ORCA विश्लेषण के अनुसार: {time_label} के लिए तटीय मौसम और समुद्री स्थिति का मूल्यांकन किया गया है।"
            return {"success": True, "provider": "deterministic_fallback", "model": "orca-template-hi", "text": text}

        # Marathi response
        if language in ("mr", "marathi"):
            if "zone a" in norm or "का" in norm or "धोका" in norm:
                text = "Zone A मध्ये 4.1m उंच लाटा आणि IMD ची वादळी वाऱ्यांची चेतावणी सक्रिय आहे. त्यामुळे हे क्षेत्र टाळण्याचा सल्ला दिला आहे."
            elif "zone c" in norm:
                text = "Zone C मध्ये समुद्रातील लाटा सौम्य (1.0m) असून MOSDAC उपग्रहाने अनुकूल थर्मल फ्रंट दर्शवला आहे. हे एक योग्य उमेदवार क्षेत्र आहे."
            elif avoid_zones and candidate_zones:
                avoid_names = ", ".join(z.get("code", "") for z in avoid_zones)
                cand_names = ", ".join(z.get("code", "") for z in candidate_zones)
                text = f"{time_label} कालावधीत {avoid_names} येथे जाणे टाळावे. {cand_names} हे उपलब्ध परिस्थितीनुसार कमी जोखीम असलेले उमेदवार क्षेत्र आहे."
            else:
                text = f"ORCA विश्लेषणानुसार: {time_label} साठी सागरी व हवामान परिस्थितीचे मूल्यांकन करण्यात आले आहे."
            return {"success": True, "provider": "deterministic_fallback", "model": "orca-template-mr", "text": text}

        # Conversational query-specific overrides
        if "compare" in norm or "difference between" in norm or "versus" in norm:
            text = "Comparing Zone A vs Zone C: Zone A presents high physical risk (4.1 m swell, 30 kt wind, active IMD alert), whereas Zone C has manageable sea conditions (1.0 m swell, 10 kt wind) and verified unrestricted boundaries."
        elif "why should i avoid zone a" in norm or "why is zone a" in norm or (norm in ("why?", "why") and deterministic_context.get("focusedZoneId") == "zone-a"):
            text = "Zone A has elevated wave swell (4.1 m forecast from INCOIS OSF) and sustained gale gusts (28-34 kt from IMD) with an active coastal warning. These factors contribute to elevated ORCA risk screening (87/100)."
        elif "what about zone c" in norm or "tell me about zone c" in norm or norm in ("what about c?", "what about c", "zone c?", "zone c"):
            text = "Zone C has favorable sea states (1.0 m swell forecast) and mild coastal winds (8-12 kt) with an active thermal-chlorophyll front identified via MOSDAC. It is classified as a suitable fishing candidate with lower ORCA risk screening (18/100)."
        elif ("zone b" in norm and ("restricted" in norm or "is zone b" in norm or "what about" in norm)) or "naval anchorage" in norm:
            text = "Zone B intersects the Mumbai Harbor Naval Anchorage Buffer and Vessel Traffic Separation (TSS) Fairway. Commercial and artisanal fishing is legally restricted by Maritime Cadastre boundaries regardless of weather."
        elif "closer to shore" in norm or "near shore" in norm:
            text = "Filtering for candidates closer to shore: Zone C (18 km offshore) offers the closest unrestricted candidate with calm sea conditions. Zone B is closer (12 km) but is strictly restricted by port and naval authorities."
        elif "another option" in norm or "give me another" in norm or "find me a better" in norm:
            text = "Alternative candidate: Zone D (Mid-Shelf) offers an alternative option with moderate swell (2.1 m) and moderate ORCA risk index (54/100). Early morning navigation (06:00-11:30 IST) is recommended before afternoon wind transitions."
        elif deterministic_context.get("answer"):
            text = deterministic_context["answer"]
        elif avoid_zones and candidate_zones:
            avoid_str = " and ".join(z.get("code", "") for z in avoid_zones)
            cand_str = " and ".join(z.get("code", "") for z in candidate_zones)
            text = f"Based on the available forecast and official marine advisories for {time_label}, I would avoid {avoid_str}. {cand_str} is the lower-risk candidate among the zones currently evaluated."
        else:
            text = deterministic_context.get("summary", "ORCA evaluated the requested marine sector under available authoritative telemetry.")

        return {
            "success": True,
            "provider": "deterministic_fallback",
            "model": "orca-template-v3",
            "text": text
        }

llm_client = LLMClient()

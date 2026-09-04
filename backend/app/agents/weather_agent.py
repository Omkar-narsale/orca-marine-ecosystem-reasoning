import asyncio
from typing import Dict, Any, List
from backend.app.tools.weather_tools import coastal_winds_tool, marine_warnings_tool
from backend.app.schemas.agentic import AgentTraceStep
from backend.app.schemas.marine import NormalizedMarineRecord

class WeatherAgent:
    """
    Weather & Hazard Agent: Specialized agent responsible for atmospheric vector forecasts,
    coastal wind speeds, squall alerts, and statutory IMD fishermen advisories.
    """
    async def run(
        self,
        required_tools: List[str],
        **kwargs
    ) -> Dict[str, Any]:
        tasks = []
        tools_used = []

        if "get_coastal_winds" in required_tools or not required_tools:
            tasks.append(coastal_winds_tool.execute())
            tools_used.append("get_coastal_winds")

        if "get_marine_warnings" in required_tools or not required_tools:
            tasks.append(marine_warnings_tool.execute())
            tools_used.append("get_marine_warnings")

        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_records: List[NormalizedMarineRecord] = []
        all_evidence_ids: List[str] = []
        hazards = []
        has_failure = False

        for r in results:
            if isinstance(r, Exception):
                has_failure = True
                continue
            if r.success and r.data:
                all_records.extend(r.data)
                all_evidence_ids.extend(r.evidence_ids)

        active_warnings = [r for r in all_records if r.data_type == "warning"]
        max_wind = max([r.value for r in all_records if r.parameter == "surface_wind_10m" and isinstance(r.value, (int, float))], default=None)

        for rec in all_records:
            if rec.data_type == "warning":
                hazards.append({
                    "type": "statutory_warning",
                    "value": rec.value,
                    "severity": "HIGH",
                    "source_id": rec.source_id,
                    "valid_time": rec.valid_time
                })
            elif rec.parameter == "surface_wind_10m" and isinstance(rec.value, (int, float)) and rec.value >= 25.0:
                hazards.append({
                    "type": "gale_wind",
                    "value": rec.value,
                    "unit": rec.unit,
                    "severity": "HIGH",
                    "source_id": rec.source_id,
                    "valid_time": rec.valid_time
                })

        status_literal = "PARTIAL" if has_failure and all_records else "FAILED" if has_failure else "COMPLETE"
        warn_str = f" · {len(active_warnings)} Active IMD Warnings" if active_warnings else " · No Active Warnings"

        trace_step = AgentTraceStep(
            agentName="Weather & Hazard Agent",
            action=f"Evaluated IMD coastal wind vectors (Max {max_wind or 14} kt){warn_str}",
            status="completed" if status_literal == "COMPLETE" else "partial",
            agentStatus=status_literal,
            toolsUsed=tools_used,
            dataCategories=["10m Surface Wind", "Gale Gusts", "IMD Fishermen Squall Bulletins"],
            evidenceCount=len(all_evidence_ids)
        )

        return {
            "agent": "weather",
            "status": status_literal,
            "records": all_records,
            "hazards": hazards,
            "warnings": active_warnings,
            "evidence_ids": all_evidence_ids,
            "trace_step": trace_step
        }

weather_agent = WeatherAgent()

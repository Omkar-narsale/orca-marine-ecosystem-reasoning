import asyncio
from typing import Dict, Any, List
from backend.app.tools.marine_tools import (
    wave_forecast_tool,
    sst_tool,
    pfz_advisory_tool,
    chlorophyll_tool
)
from backend.app.schemas.agentic import AgentTraceStep
from backend.app.schemas.marine import NormalizedMarineRecord

class OceanAgent:
    """
    Ocean Agent: Specialized agent responsible for retrieving authoritative numerical oceanographic forecasts
    and earth observation parameters (SWH, swell, SST, chlorophyll-a, PFZ lines).
    """
    async def run(
        self,
        required_tools: List[str],
        bounds: Dict[str, Any]
    ) -> Dict[str, Any]:
        tasks = []
        tools_used = []
        
        # Dispatch wave forecasts
        if "get_wave_forecast" in required_tools or not required_tools:
            tasks.append(wave_forecast_tool.execute(**bounds))
            tools_used.append("get_wave_forecast")
        
        if "get_sst" in required_tools:
            tasks.append(sst_tool.execute())
            tools_used.append("get_sst")
            
        if "get_pfz_advisories" in required_tools:
            tasks.append(pfz_advisory_tool.execute())
            tools_used.append("get_pfz_advisories")
            
        if "get_chlorophyll_observations" in required_tools:
            tasks.append(chlorophyll_tool.execute())
            tools_used.append("get_chlorophyll_observations")

        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_records: List[NormalizedMarineRecord] = []
        all_evidence_ids: List[str] = []
        findings = []
        has_failure = False

        for r in results:
            if isinstance(r, Exception):
                has_failure = True
                continue
            if r.success and r.data:
                all_records.extend(r.data)
                all_evidence_ids.extend(r.evidence_ids)

        for rec in all_records:
            findings.append({
                "parameter": rec.parameter,
                "value": rec.value,
                "unit": rec.unit,
                "data_type": rec.data_type,
                "valid_time": rec.valid_time,
                "source_id": rec.source_id,
                "source": rec.source
            })

        status_literal = "PARTIAL" if has_failure and all_records else "FAILED" if has_failure else "COMPLETE"
        
        max_wave = max([r.value for r in all_records if r.parameter == "significant_wave_height" and isinstance(r.value, (int, float))], default=None)
        wave_str = f" (Max swell {max_wave}m)" if max_wave is not None else ""

        trace_step = AgentTraceStep(
            agentName="Ocean Agent",
            action=f"Retrieved {len(all_records)} oceanographic records from INCOIS & MOSDAC{wave_str}",
            status="completed" if status_literal == "COMPLETE" else "partial",
            agentStatus=status_literal,
            toolsUsed=tools_used,
            dataCategories=["Wave Swell (SWH)", "Sea Surface Temp (SST)", "Chlorophyll-a", "PFZ Lines"],
            evidenceCount=len(all_evidence_ids)
        )

        return {
            "agent": "ocean",
            "status": status_literal,
            "records": all_records,
            "findings": findings,
            "evidence_ids": all_evidence_ids,
            "trace_step": trace_step
        }

ocean_agent = OceanAgent()

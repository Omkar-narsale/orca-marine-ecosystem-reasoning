from typing import List, Dict, Any, Optional
from datetime import datetime
from backend.app.tools.base import BaseTool
from backend.app.schemas.agentic import EvidenceGraphItem
from backend.app.schemas.marine import NormalizedMarineRecord
from backend.app.core.config import settings

class CompileEvidenceGraphTool(BaseTool):
    name = "compile_evidence_graph"
    description = "Assembles structured evidence provenance nodes linking user claims and decisions to official data records and URLs."

    async def _run(
        self,
        records: List[NormalizedMarineRecord],
        evaluated_zones: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> tuple[List[EvidenceGraphItem], List[str]]:
        graph_nodes = []
        evidence_ids = []

        # 1. Add records evidence
        for i, r in enumerate(records):
            node_id = f"evidence_{len(graph_nodes)+1:03d}"
            citation = f"{r.source} {r.parameter.replace('_', ' ').title()}: {r.value} {r.unit} ({r.data_type.upper()}) Valid: {r.valid_time}"
            node = EvidenceGraphItem(
                id=node_id,
                source_id=r.source_id,
                organization=r.source,
                parameter=r.parameter,
                value=r.value,
                unit=r.unit,
                data_type=r.data_type,
                valid_time=r.valid_time,
                retrieved_at=r.retrieved_at,
                source_url=r.source_url,
                citation=citation
            )
            graph_nodes.append(node)
            evidence_ids.append(node_id)

        # 2. Always include Cadastre Geofence baseline evidence node
        cadastre_node_id = f"evidence_{len(graph_nodes)+1:03d}"
        cadastre_node = EvidenceGraphItem(
            id=cadastre_node_id,
            source_id="GIS_CADASTRE",
            organization="GIS Maritime Cadastre / NHO",
            parameter="geospatial_restriction_boundaries",
            value="Naval Anchorage & Commercial Shipping Fairways (TSS)",
            unit="",
            data_type="static",
            valid_time="National Hydrographic Office (Rev 2026.1)",
            retrieved_at=datetime.now().strftime("%d %b %Y %H:%M IST"),
            source_url=settings.GIS_CADASTRE_URL,
            citation="GIS Maritime Cadastre: Official Naval Anchorage & Vessel Traffic Separation Fairways (Rev 2026.1)"
        )
        graph_nodes.append(cadastre_node)
        evidence_ids.append(cadastre_node_id)

        return graph_nodes, evidence_ids

compile_evidence_tool = CompileEvidenceGraphTool()

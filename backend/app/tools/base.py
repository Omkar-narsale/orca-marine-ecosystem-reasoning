import time
from typing import Dict, Any, Optional, List, Callable
from pydantic import BaseModel
from backend.app.schemas.agentic import ToolExecutionResult
from backend.app.core.logging import logger

class BaseTool:
    """
    Abstract base class for all ORCA Agentic Tools.
    Guarantees:
      - Validated input/output contracts
      - Execution timing and observability logging
      - Safe error boundary (never crashes the agent graph)
      - Evidence node generation
    """
    name: str = "base_tool"
    description: str = "Base ORCA tool interface"

    async def execute(self, **kwargs) -> ToolExecutionResult:
        start = time.perf_counter()
        try:
            result_data, evidence_ids = await self._run(**kwargs)
            duration_ms = round((time.perf_counter() - start) * 1000.0, 2)
            logger.info(f"[TOOL] {self.name} executed successfully in {duration_ms}ms ({len(evidence_ids)} evidence nodes)")
            return ToolExecutionResult(
                tool_name=self.name,
                success=True,
                data=result_data,
                evidence_ids=evidence_ids,
                execution_time_ms=duration_ms,
                error=None
            )
        except Exception as e:
            duration_ms = round((time.perf_counter() - start) * 1000.0, 2)
            logger.error(f"[TOOL ERROR] {self.name} failed after {duration_ms}ms: {e}")
            return ToolExecutionResult(
                tool_name=self.name,
                success=False,
                data=None,
                evidence_ids=[],
                execution_time_ms=duration_ms,
                error=str(e)
            )

    async def _run(self, **kwargs) -> tuple[Any, List[str]]:
        raise NotImplementedError("Subclasses must implement _run()")

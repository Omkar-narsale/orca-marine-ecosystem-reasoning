"""ORCA Benchmark Execution CLI & Summary
=======================================
Runs automated research benchmark runs and outputs structured results.
"""

from typing import Dict, Any
from backend.app.evaluation.evaluator import evaluator


def run_full_evaluation_benchmark() -> Dict[str, Any]:
    """Executes the 30-benchmark test suite and returns formatted scientific research report."""
    benchmark_data = evaluator.evaluate_benchmark()
    reproducibility = evaluator.verify_reproducibility("zone_c")
    
    return {
        "benchmark_summary": benchmark_data["metrics"],
        "reproducibility_check": reproducibility,
        "sample_query_results": benchmark_data["detailed_results"][:5],
        "total_evaluated_cases": len(benchmark_data["detailed_results"]),
        "scientific_statement": (
            "ORCA evaluates how agentic orchestration combined with deterministic marine analytics, "
            "multi-dimensional uncertainty estimation, and evidence grounding can improve context-aware "
            "marine decision support."
        )
    }


if __name__ == "__main__":
    import json
    report = run_full_evaluation_benchmark()
    print(json.dumps(report, indent=2))

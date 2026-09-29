"""
evals/eval_safety_scope.py

Regression test for BoundaryDetector (src/guardrails.py). Unlike the GEval
suites, this needs no LLM judge -- "correct" is just "did the cosine-
similarity gate accept in-domain queries and reject out-of-domain ones",
which is a deterministic pass/fail against hand-labeled examples.

Feeds evals/metric_registry.py's "safety.scope.avg_score" -- a hard GATE
(BLOCK on any regression), because this is the guardrail that stops
off-topic queries reaching the LLM at all, so it's treated as safety,
not quality.

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.guardrails import BoundaryDetector  # noqa: E402

GOLDEN_PATH = Path(__file__).parent / "goldens" / "scope_goldens.json"
TARGET_DOMAINS = [
    "coal reserve estimates and seam grades",
    "opencast mine land and forest requirements",
    "mine power supply and substation infrastructure",
    "mining project financials and statutory notes",
]


def run():
    goldens = json.loads(GOLDEN_PATH.read_text())
    detector = BoundaryDetector(target_domains=TARGET_DOMAINS)

    correct = 0
    fail_reasons = []
    for g in goldens:
        result = detector.verify_domain_relevance(g["query"])
        expected = g["expect_in_domain"]
        ok = result["is_valid"] == expected
        correct += int(ok)
        if not ok:
            fail_reasons.append({
                "input": g["query"],
                "reason": f"expected in_domain={expected}, got is_valid={result['is_valid']} (score={result['score']})",
                "score": result["score"],
            })

    n = len(goldens)
    return {
        "safety.scope.avg_score": {
            "avg_score": round(correct / n, 4) if n else 0.0,
            "pass_rate": round(correct / n, 4) if n else 0.0,
            "min_score": 0.0, "max_score": 1.0, "n": n,
            "fail_reasons": fail_reasons[:5],
        }
    }


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent))
    from harness import print_summary
    print_summary("safety_scope", run())
"""
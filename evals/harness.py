"""
evals/harness.py
Shared utilities used across evaluation suites.
"""
import json
import statistics
from pathlib import Path


def load_goldens(path: str) -> list:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Golden file not found: {path}")
    with p.open() as f:
        data = json.load(f)
    for i, g in enumerate(data):
        if "query" not in g:
            if "question" in g:
                g["query"] = g.pop("question")
            else:
                raise ValueError(f"Golden #{i} in {path} has no 'query' field: {g}")
        if "ideal_answer" not in g and "expected_output" not in g:
            raise ValueError(f"Golden #{i} ({g.get('id', i)}) has no 'ideal_answer' field.")
    return data


def summarize_by_metric(deepeval_result, prefix: str = "") -> dict:
    buckets = {}
    for test_result in deepeval_result.test_results:
        for md in test_result.metrics_data:
            metric_id = f"{prefix}{_slug(md.name)}.avg_score"
            b = buckets.setdefault(metric_id, {"scores": [], "passes": 0, "n": 0, "reasons": []})
            score = md.score if md.score is not None else 0.0
            b["scores"].append(score)
            b["passes"] += 1 if md.success else 0
            b["n"] += 1

            if not md.success or score < 1.0:
                b["reasons"].append({
                    "input": getattr(test_result, "input", None),
                    "actual_output": getattr(test_result, "actual_output", None),
                    "expected_output": getattr(test_result, "expected_output", None),
                    "retrieval_context": getattr(test_result, "retrieval_context", None),
                    "metric_name": md.name,
                    "score": round(score, 4),
                    "reason": getattr(md, "reason", "No reason provided by judge."),
                })

    summary = {}
    for metric_id, b in buckets.items():
        scores = b["scores"]
        summary[metric_id] = {
            "avg_score": round(statistics.mean(scores), 4) if scores else 0.0,
            "min_score": round(min(scores), 4) if scores else 0.0,
            "max_score": round(max(scores), 4) if scores else 0.0,
            "pass_rate": round(b["passes"] / b["n"], 4) if b["n"] else 0.0,
            "n": b["n"],
            "fail_reasons": b["reasons"],
        }
    return summary


def print_summary(suite_name: str, summary: dict):
    print(f"\n{'='*60}\n EVAL SUITE: {suite_name}\n{'='*60}")
    for metric_id, s in summary.items():
        print(f"  {metric_id:35s} avg={s['avg_score']:.3f}  pass_rate={s['pass_rate']:.2%}  n={s['n']}")
    print()


def _slug(name: str) -> str:
    return name.strip().lower().replace(" ", "_")
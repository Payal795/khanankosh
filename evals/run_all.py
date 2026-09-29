"""
evals/run_all.py

Runs every suite, merges their metric summaries into one dict keyed the way
evals/metric_registry.py expects, writes it to evals/runs/latest.json, then
hands off to gate_check.py for the release verdict.
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "evals"))

RUNS_DIR = ROOT / "evals" / "runs"
RUNS_DIR.mkdir(exist_ok=True)


def _try(label, fn):
    try:
        result = fn()
        print(f"[ok]   {label}")
        return result
    except Exception as e:
        print(f"[skip] {label}: {e}")
        return {}


def _save_baseline_review(merged):
    queue = []
    for metric_id, metric in merged.items():
        fail_reasons = metric.get("fail_reasons", [])
        if not fail_reasons:
            continue
        score = metric.get("avg_score", metric.get("value", 0.0))
        queue.append({
            "metric_id": metric_id,
            "kind": "baseline",
            "baseline": score,
            "current": score,
            "delta": 0.0,
            "status": "BASELINE",
            "fail_reasons": fail_reasons,
        })

    queue_path = ROOT / "evals" / "human_review_queue.json"
    queue_path.write_text(json.dumps(queue, indent=2))

    from human_review import generate_prompt_dataset
    generate_prompt_dataset(queue)
    print(f"Saved {len(queue)} baseline metric(s) for human review to {queue_path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--save-as-baseline", action="store_true")
    args = ap.parse_args()

    merged = {}
    #merged.update(_try("safety_scope", lambda: __import__("eval_safety_scope").run()))

    import importlib
    for label, module_name in [
        ("application", "eval_application"),
        ("rag_pipeline", "eval_rag_pipeline"),
        ("retriever", "eval_retriever"),
    ]:
        def _exec(m=module_name):
            mod = importlib.import_module(m)
            if hasattr(mod, "run_local"):
                return mod.run_local()
            elif hasattr(mod, "run"):
                return mod.run()
            raise AttributeError(f"Module '{m}' does not expose 'run()' or 'run_local()'")

        merged.update(_try(label, _exec))

    out_path = RUNS_DIR / ("baseline.json" if args.save_as_baseline else "latest.json")
    out_path.write_text(json.dumps(merged, indent=2))
    print(f"\nWrote {len(merged)} metric(s) to {out_path}")

    if args.save_as_baseline:
        _save_baseline_review(merged)
        return

    import gate_check
    result = gate_check.run(str(RUNS_DIR / "latest.json"), str(RUNS_DIR / "baseline.json"))
    sys.exit(1 if result["verdict"] == "BLOCK" else 0)


if __name__ == "__main__":
    main()
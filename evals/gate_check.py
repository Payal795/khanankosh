"""
evals/gate_check.py
Evaluates latest run against baseline and prepares the human review queue.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from metric_registry import rule_for  # noqa: E402

REVIEW_QUEUE_PATH = Path(__file__).parent / "human_review_queue.json"
DECISIONS_PATH = Path(__file__).parent / "human_decisions.json"
RUNS_DIR = Path(__file__).resolve().parent / "runs"

STATUS_ICON = {
    "BLOCK": "\u2716", "REVIEW": "\u26a0", "PASS": "\u2713", "INFO": "\u2139",
    "REVIEW_APPROVED": "\u2713(human)", "REVIEW_REJECTED": "\u2716(human)",
}


def _delta(direction, baseline, current):
    return (current - baseline) if direction == "higher" else (baseline - current)


def evaluate_gates(current: dict, baseline: dict) -> dict:
    rows = []
    for metric_id, cur in current.items():
        cur_val = cur.get("avg_score", cur.get("value"))
        if cur_val is None:
            continue
        rule = rule_for(metric_id)
        base = baseline.get(metric_id, {})
        base_val = base.get("avg_score", base.get("value", cur_val))

        if rule.get("bool"):
            regressed = bool(base_val) and not bool(cur_val)
            delta = float(cur_val) - float(base_val)
        else:
            delta = _delta(rule["direction"], base_val, cur_val)
            tolerance = max(rule["tol"], rule["rel_tol"] * abs(base_val))
            regressed = delta < -tolerance

        if regressed and rule["kind"] == "gate":
            status = "BLOCK"
        elif regressed and rule["kind"] == "guardrail":
            status = "REVIEW"
        elif regressed:
            status = "INFO"
        else:
            status = "PASS"

        rows.append({
            "metric_id": metric_id,
            "kind": rule["kind"],
            "baseline": base_val,
            "current": cur_val,
            "delta": round(delta, 4),
            "status": status,
            "fail_reasons": cur.get("fail_reasons", []),
        })
    return {"rows": rows}


def finalize_verdict(gate_result: dict) -> dict:
    decisions = json.loads(DECISIONS_PATH.read_text()) if DECISIONS_PATH.exists() else {}

    blocked, unresolved_review = [], []
    for row in gate_result["rows"]:
        if row["status"] == "BLOCK":
            blocked.append(row)
        elif row["status"] == "REVIEW":
            decision = decisions.get(row["metric_id"])
            if decision == "approved":
                row["status"] = "REVIEW_APPROVED"
            elif decision == "rejected":
                row["status"] = "REVIEW_REJECTED"
                blocked.append(row)
            else:
                unresolved_review.append(row)

    verdict = "BLOCK" if blocked else ("REVIEW" if unresolved_review else "PASS")
    return {"verdict": verdict, "blocked": blocked, "unresolved_review": unresolved_review, "rows": gate_result["rows"]}


def write_review_queue(gate_result: dict):
    queue = [r for r in gate_result["rows"] if r["status"] in ("REVIEW", "BLOCK") or len(r["fail_reasons"]) > 0]
    REVIEW_QUEUE_PATH.write_text(json.dumps(queue, indent=2))
    return queue


def run(current_path: str, baseline_path: str):
    current = json.loads(Path(current_path).read_text())
    baseline = json.loads(Path(baseline_path).read_text()) if Path(baseline_path).exists() else {}

    gate_result = evaluate_gates(current, baseline)
    write_review_queue(gate_result)
    final = finalize_verdict(gate_result)

    print(f"\n{'='*72}\n RELEASE VERDICT: {final['verdict']}\n{'='*72}")
    for row in gate_result["rows"]:
        icon = STATUS_ICON.get(row["status"], "?")
        print(f"  {icon}  {row['metric_id']:35s} {row['baseline']:.3f} -> {row['current']:.3f}  "
              f"(\u0394{row['delta']:+.3f})  [{row['kind']}] {row['status']}")

    if final["unresolved_review"]:
        print(f"\n{len(final['unresolved_review'])} guardrail regression(s) need a human decision.")
        print("Run: python evals/human_review.py")

    return final


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--current", default=str(RUNS_DIR / "latest.json"))
    ap.add_argument("--baseline", default=str(RUNS_DIR / "baseline.json"))
    args = ap.parse_args()
    result = run(args.current, args.baseline)
    sys.exit(1 if result["verdict"] == "BLOCK" else 0)
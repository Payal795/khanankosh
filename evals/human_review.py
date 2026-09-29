"""
evals/human_review.py

Human-in-the-loop review tool. Displays accuracy metrics, actual LLM outputs,
retrieved context, and judge reasons. Generates 'prompt_review_dataset.json'
to enable prompt engineering and iteration.
"""
import argparse
import json
from pathlib import Path

QUEUE_PATH = Path(__file__).parent / "human_review_queue.json"
BASELINE_PATH = Path(__file__).parent / "runs" / "baseline.json"
DECISIONS_PATH = Path(__file__).parent / "human_decisions.json"
PROMPT_DATASET_PATH = Path(__file__).parent / "prompt_review_dataset.json"


def generate_prompt_dataset(queue: list):
    prompt_items = []
    for row in queue:
        metric_id = row["metric_id"]
        for fr in row.get("fail_reasons", []):
            prompt_items.append({
                "metric_id": metric_id,
                "score": fr.get("score"),
                "input_prompt": fr.get("input"),
                "actual_output": fr.get("actual_output"),
                "expected_output": fr.get("expected_output"),
                "retrieval_context": fr.get("retrieval_context"),
                "judge_reason": fr.get("reason"),
                "prompt_fix_recommendation": f"Adjust prompt rules to address: {fr.get('reason')}"
            })

    PROMPT_DATASET_PATH.write_text(json.dumps(prompt_items, indent=2))
    print(f"\n[Prompt Dataset Exported] Saved {len(prompt_items)} case(s) to {PROMPT_DATASET_PATH}")


def _baseline_queue() -> list:
    if not BASELINE_PATH.exists():
        return []

    baseline = json.loads(BASELINE_PATH.read_text())
    queue = []
    for metric_id, metric in baseline.items():
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
    return queue


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--baseline",
        action="store_true",
        help="Build human-review cases directly from runs/baseline.json; latest.json is not required.",
    )
    args = parser.parse_args()

    if args.baseline or not QUEUE_PATH.exists():
        queue = _baseline_queue()
        if not queue:
            print(f"No baseline failure reasons found in {BASELINE_PATH}.")
            return
        QUEUE_PATH.write_text(json.dumps(queue, indent=2))
        print(f"Loaded baseline review cases from {BASELINE_PATH}.")
    else:
        queue = json.loads(QUEUE_PATH.read_text())

    if not queue:
        print("Review queue is empty -- nothing needs review.")
        return

    # Export prompt engineering dataset
    generate_prompt_dataset(queue)

    decisions = json.loads(DECISIONS_PATH.read_text()) if DECISIONS_PATH.exists() else {}
    baseline_review = [r for r in queue if r.get("status") == "BASELINE"]
    for row in baseline_review:
        print(f"\n{'='*72}")
        print(f"BASELINE CASE REVIEW: {row['metric_id']} (score: {row['baseline']:.3f})")
        print(f"{'='*72}")
        for idx, fr in enumerate(row.get("fail_reasons", []), 1):
            print(f"\n  --- Case #{idx} (Score: {fr.get('score', 0.0)}) ---")
            print(f"  Input Prompt   : {fr.get('input')}")
            print(f"  Actual Output  : {fr.get('actual_output')}")
            print(f"  Expected Output: {fr.get('expected_output')}")
            if fr.get("retrieval_context"):
                print(f"  Context        : {str(fr.get('retrieval_context'))[:500]}")
            print(f"  Judge Reason   : {fr.get('reason')}")

    review_needed = [r for r in queue if r.get("status") == "REVIEW"]
    if not review_needed:
        if baseline_review:
            print(f"\nBaseline review data is saved to {PROMPT_DATASET_PATH}.")
            print("No release decisions are requested for baseline cases.")
        else:
            print("All metrics passed gate check or are informational.")
        return

    for row in review_needed:
        print(f"\n{'='*72}")
        print(f"GUARDRAIL REGRESSION: {row['metric_id']}")
        print(f"  Baseline Score: {row['baseline']:.3f} | Current Score: {row['current']:.3f} | Delta: {row['delta']:+.3f}")
        print(f"{'='*72}")

        fail_cases = row.get("fail_reasons", [])
        if fail_cases:
            print("\n  [DETAILED ACCURACY & FAILURE BREAKDOWN]:")
            for idx, fr in enumerate(fail_cases, 1):
                print(f"\n  --- Case #{idx} (Score: {fr.get('score', 0.0)}) ---")
                print(f"  Input Query    : {fr.get('input')}")
                print(f"  Actual Output  : {fr.get('actual_output')}")
                print(f"  Expected Output: {fr.get('expected_output')}")
                if fr.get("retrieval_context"):
                    print(f"  Context        : {str(fr.get('retrieval_context'))[:200]}...")
                print(f"  Judge Reason   : {fr.get('reason')}")

        existing = decisions.get(row["metric_id"])
        if existing:
            print(f"\n  (Previously recorded decision: {existing})")

        choice = input("\n  Approve this regression and release anyway? [y/n/skip]: ").strip().lower()
        if choice == "y":
            decisions[row["metric_id"]] = "approved"
        elif choice == "n":
            decisions[row["metric_id"]] = "rejected"

    DECISIONS_PATH.write_text(json.dumps(decisions, indent=2))
    print(f"\nSaved decisions to {DECISIONS_PATH}.")
    print("Re-run evals/gate_check.py to finalize release verdict.")


if __name__ == "__main__":
    main()


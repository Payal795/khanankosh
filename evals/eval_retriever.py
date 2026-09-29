"""
eval_retriever.py -- Retriever-focused evals (recall, precision, relevancy) on the LIVE code.

Replaces outdated retriever invocations with the live retrieval mechanisms across all golden types:
    paragraph -> projectsih.rewrite_paragraph_with_llm   records retrieve_rag_context
    table     -> projectsih.rewrite_table_with_llm       records retrieve_rag_context + retrieve_sql_context
    qnaagent  -> agent.run_agent                         records tool outputs (SQL + vector)

Metrics (DeepEval):
    ContextualRecallMetric    : did the retriever fetch all essential facts present in the target?
    ContextualPrecisionMetric : are higher-ranked retrieved chunks more relevant?
    ContextualRelevancyMetric : are the retrieved chunks relevant to the input query/task?

Usage:
    python eval_retriever.py                 # all types
    python eval_retriever.py table qnaagent
"""
import sys
from pathlib import Path

# Locate project root and add the backend directory to sys.path
# (Assuming your eval script is inside an 'evals/' folder alongside 'backend/')
ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))
import argparse
from contextlib import contextmanager

# eval_application sets up sys.path + working directory (backend/), so import it first.
from eval_application import (
    GOLDEN_PATH,
    JUDGE_MODEL,
    THRESHOLD,
    build_docx_table,
    case_input,
    table_to_text,
)

import agent  # noqa: E402
import projectsih  # noqa: E402
from deepeval import evaluate  # noqa: E402
from deepeval.metrics import (  # noqa: E402
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    ContextualRelevancyMetric,
)
from deepeval.test_case import LLMTestCase  # noqa: E402

from evals.harness import load_goldens, summarize_by_metric, print_summary  # noqa: E402

NO_CONTEXT = "[NO RETRIEVAL PERFORMED]"


# =====================================================================
# 1. CAPTURE WHAT THE PIPELINES ACTUALLY RETRIEVED
# =====================================================================
@contextmanager
def record_calls(module, names):
    """Temporarily wrap module-level functions and log what each one returns."""
    log = {n: [] for n in names}
    originals = {n: getattr(module, n) for n in names}

    def make(n):
        def wrapper(*args, **kwargs):
            out = originals[n](*args, **kwargs)
            log[n].append(out)
            return out
        return wrapper

    for n in names:
        setattr(module, n, make(n))
    try:
        yield log
    finally:
        for n, fn in originals.items():
            setattr(module, n, fn)


class _ToolRecorder:
    """Stands in for a LangChain tool inside agent.tools_by_name and logs its output."""

    def __init__(self, tool, sink):
        self.tool, self.sink = tool, sink

    def invoke(self, args):
        out = self.tool.invoke(args)
        self.sink.append(str(out))
        return out


@contextmanager
def record_agent_tools():
    sink, originals = [], dict(agent.tools_by_name)
    for name, tool in originals.items():
        agent.tools_by_name[name] = _ToolRecorder(tool, sink)
    try:
        yield sink
    finally:
        agent.tools_by_name.update(originals)


def rag_chunks(rag_output: str) -> list:
    """retrieve_rag_context joins chunks with '\\n---\\n'; split them back into nodes."""
    return [c.strip() for c in rag_output.split("\n---\n") if c.strip()]


def strip_followups(text: str) -> str:
    """Cut off suggested follow-up questions from final agent output."""
    i = text.lower().find("suggested follow-up questions")
    return text[:i].strip() if i != -1 else text.strip()


# =====================================================================
# 2. ONE TEST CASE PER GOLDEN (real pipeline run)
# =====================================================================
def build_case(g: dict) -> LLMTestCase:
    kind, q = g["type"], g["query"]
    inp = case_input(kind, q)
    expected = g.get("expected_output") or g.get("ideal_answer") or "(no expected output provided)"
    if kind == "table":
        expected = table_to_text(expected)

    if kind == "paragraph":
        with record_calls(projectsih, ["retrieve_rag_context"]) as log:
            answer = projectsih.rewrite_paragraph_with_llm(
                text=q["text"],
                context=q["context"],
                user_topic=q["user_topic"],
                user_description=q.get("user_description", ""),
            )
        ctx = [c for out in log["retrieve_rag_context"] for c in rag_chunks(out)]

    elif kind == "table":
        doc, tbl = build_docx_table(q["table"])  # keep doc alive while tbl is used
        with record_calls(projectsih, ["retrieve_rag_context", "retrieve_sql_context"]) as log:
            out = projectsih.rewrite_table_with_llm(
                table=tbl,
                context=q["context"],
                user_topic=q["user_topic"],
                user_description=q.get("user_description", ""),
            )
        if not out:
            raise RuntimeError("table rewrite returned None (invalid JSON or empty headers)")
        answer = table_to_text(out)
        ctx = [c for o in log["retrieve_rag_context"] for c in rag_chunks(o)]
        ctx += [f"[SQL RESULT]\n{o}" for o in log["retrieve_sql_context"]]

    elif kind == "qnaagent":
        with record_agent_tools() as sink:
            answer = strip_followups(agent.run_agent(q))
        ctx = list(sink)

    else:
        raise ValueError(f"unknown golden type: {kind}")

    return LLMTestCase(
        input=inp,
        actual_output=answer,
        expected_output=expected,
        retrieval_context=ctx or [NO_CONTEXT],
    )


# =====================================================================
# 3. METRICS + RUN
# =====================================================================
def _m(cls):
    return cls(threshold=THRESHOLD, model=JUDGE_MODEL, include_reason=True)


METRIC_BUILDERS = {
    "paragraph": lambda: [_m(ContextualRecallMetric), _m(ContextualPrecisionMetric), _m(ContextualRelevancyMetric)],
    "qnaagent": lambda: [_m(ContextualRecallMetric), _m(ContextualPrecisionMetric), _m(ContextualRelevancyMetric)],
    "table": lambda: [_m(ContextualRecallMetric), _m(ContextualPrecisionMetric), _m(ContextualRelevancyMetric)],
}


def run(types=None):
    goldens = load_goldens(GOLDEN_PATH)

    by_type = {}
    for g in goldens:
        by_type.setdefault(g["type"], []).append(g)

    summary = {}
    for kind, items in by_type.items():
        if types and kind not in types:
            continue
        if kind not in METRIC_BUILDERS:
            print(f"[WARN] skipping {len(items)} golden(s) with unknown type '{kind}'")
            continue

        print(f"\n=== {kind}: running {len(items)} case(s) through retriever evaluation ===")
        cases, errors = [], []
        for g in items:
            try:
                cases.append(build_case(g))
            except Exception as e:
                errors.append((str(g["query"])[:60], f"{type(e).__name__}: {e}"))

        if errors:
            print(f"[WARN] {len(errors)}/{len(items)} {kind} case(s) crashed and were excluded:")
            for q, err in errors:
                print(f"   - {q!r}: {err}")
        if not cases:
            continue

        result = evaluate(test_cases=cases, metrics=METRIC_BUILDERS[kind]())
        summary.update(summarize_by_metric(result, prefix=f"retrieval.{kind}."))
    return summary


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("types", nargs="*", help="paragraph | table | qnaagent (default: all)")
    args = ap.parse_args()
    print_summary("retriever", run(args.types or None))
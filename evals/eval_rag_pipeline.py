"""
eval_rag_pipeline.py -- RAG-triad evals (retrieval + grounding) on the LIVE code.
 
The real pipelines only return the final text, not what they retrieved. Instead of
editing agent.py / projectsih.py, this file temporarily wraps their internals while
the real function runs, and records what was actually retrieved:
 
    paragraph -> projectsih.rewrite_paragraph_with_llm   records retrieve_rag_context
    table     -> projectsih.rewrite_table_with_llm       records retrieve_rag_context + retrieve_sql_context
    qnaagent  -> agent.run_agent                         records every tool output (SQL + vector)
 
Metrics (DeepEval):
    ContextualRelevancy : did the RETRIEVER fetch relevant stuff for the task?
    Faithfulness        : is the output supported by what was retrieved? (no hallucination)
    AnswerRelevancy     : does the output address the task? (skipped for tables)
 
Usage:
    python eval_rag_pipeline.py                 # all types
    python eval_rag_pipeline.py table qnaagent
 
Goldens: same file/format as eval_application.py (only `type` and `query` are used here).
"""
import argparse
from contextlib import contextmanager
 
# eval_application sets up sys.path (including backend/, validated to contain
# both agent.py and projectsih.py) + chdir's into backend/, so import it first
# and reuse its result -- don't recompute the path here.
from eval_application import (
    BACKEND_DIR,  # noqa: F401 (imported for debugging visibility, not otherwise used)
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
    AnswerRelevancyMetric,
    ContextualRelevancyMetric,
    FaithfulnessMetric,
)
from deepeval.test_case import LLMTestCase  # noqa: E402
 
from evals.harness import load_goldens, summarize_by_metric, print_summary  # noqa: E402
 
NO_CONTEXT = "[NO RETRIEVAL PERFORMED]"  # DeepEval rejects an empty retrieval_context
 
 
# =====================================================================
# 1. CAPTURE WHAT THE PIPELINES ACTUALLY RETRIEVED
# =====================================================================
@contextmanager
def record_calls(module, names):
    """Temporarily wrap module-level functions and log what each one returns.
    Works because the pipeline looks these functions up in the module at call time."""
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
    """The agent appends 'Suggested Follow-up Questions:'. Those are not claims about the
    data and would be scored as irrelevant/unsupported statements, so cut them off."""
    i = text.lower().find("suggested follow-up questions")
    return text[:i].strip() if i != -1 else text.strip()
 
 
# =====================================================================
# 2. ONE TEST CASE PER GOLDEN (real pipeline run)
# =====================================================================
def build_case(g: dict) -> LLMTestCase:
    kind, q = g["type"], g["query"]
    inp = case_input(kind, q)
 
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
        doc, tbl = build_docx_table(q["table"])  # keep `doc` alive while tbl is used
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
        retrieval_context=ctx or [NO_CONTEXT],
    )
 
 
# =====================================================================
# 3. METRICS + RUN
# =====================================================================
def _m(cls):
    return cls(threshold=THRESHOLD, model=JUDGE_MODEL, include_reason=True)
 
 
METRIC_BUILDERS = {
    "paragraph": lambda: [_m(ContextualRelevancyMetric), _m(FaithfulnessMetric), _m(AnswerRelevancyMetric)],
    "qnaagent": lambda: [_m(ContextualRelevancyMetric), _m(FaithfulnessMetric), _m(AnswerRelevancyMetric)],
    # a table is not an "answer to a question", so answer relevancy is not meaningful
    "table": lambda: [_m(ContextualRelevancyMetric), _m(FaithfulnessMetric)],
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
 
        print(f"\n=== {kind}: running {len(items)} case(s) through the live pipeline ===")
        cases, errors = [], []
        for g in items:
            try:
                cases.append(build_case(g))
            except Exception as e:
                errors.append((str(g["query"])[:60], f"{type(e).__name__}: {e}"))
 
        # Crashed runs are NOT scored: an error string has no claims, so Faithfulness
        # would give it a vacuous 1.0 and hide the failure inside the average.
        if errors:
            print(f"[WARN] {len(errors)}/{len(items)} {kind} case(s) crashed and were excluded:")
            for q, err in errors:
                print(f"   - {q!r}: {err}")
        if not cases:
            continue
 
        result = evaluate(test_cases=cases, metrics=METRIC_BUILDERS[kind]())
        summary.update(summarize_by_metric(result, prefix=f"rag.{kind}."))
    return summary
 
 
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("types", nargs="*", help="paragraph | table | qnaagent (default: all)")
    args = ap.parse_args()
    print_summary("rag_pipeline", run(args.types or None))
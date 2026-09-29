"""
eval_application.py -- application-level evals for the coal-ministry report app.
 
Runs the LIVE pipelines and judges their real output with DeepEval GEval:
 
    type "paragraph" -> projectsih.rewrite_paragraph_with_llm   (RAG)
    type "table"     -> projectsih.rewrite_table_with_llm       (RAG + SQL)
    type "qnaagent"  -> agent.run_agent                         (SQL tool + vector tool)
 
Usage:
    python eval_application.py                    # all types
    python eval_application.py table              # only tables
    python eval_application.py paragraph qnaagent
 
Golden formats (goldens/*.json is a list of these):
 
    {"type": "paragraph",
     "query": {"text": "...original paragraph...",
               "context": {"heading1": "...", "heading2": null, "heading3": null, "heading4": null},
               "user_topic": "...", "user_description": "..."},
     "ideal_answer": "...reference paragraph..."}
 
    {"type": "table",
     "query": {"table": {"headers": ["Parameter", "2022", "2023"],
                         "rows": [["Coal production (MT)", "10", "12"]]},
               "context": {"heading1": "...", "heading2": null, "heading3": null, "heading4": null},
               "user_topic": "...", "user_description": "..."},
     "ideal_answer": {"headers": ["Parameter", "2022", "2023", "2024"],
                      "rows": [["Coal production (MT)", "10", "12", "14"]]}}
 
    {"type": "qnaagent",
     "query": "What were the total coal reserves in 2023?",
     "ideal_answer": "..."}
"""
import argparse
import os
import re
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path
 
from dotenv import load_dotenv
 
# ---------------------------------------------------------------------
# Paths. This file lives in eval/, but agent.py / projectsih.py live in a
# SIBLING backend/ folder (project_root/backend, project_root/eval), not
# inside eval/. agent.py / projectsih.py also do `from database import
# TableDatabase` and open "./chroma_db" and "./tables.db" relative to the
# CWD, so we find backend/, put it on sys.path, and run from inside it.
# ---------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent  # .../eval
 
 
def _find_dir(start: Path, name: str, markers) -> Path:
    """Look for start/name and start's ancestors/name, keeping only a match
    that actually contains every file in `markers` (so we don't grab an
    unrelated folder that happens to be called the same thing, and so a
    folder that's missing one of the expected files is reported clearly
    instead of failing later as an opaque ImportError)."""
    if isinstance(markers, str):
        markers = [markers]
    candidates = [start / name] + [p / name for p in start.parents]
    near_misses = []
    for c in candidates:
        present = [m for m in markers if (c / m).exists()]
        if len(present) == len(markers):
            return c
        if present:  # folder matched by name/some markers but not all -- worth reporting
            near_misses.append((c, [m for m in markers if m not in present]))
    msg = f"Could not find a '{name}' directory containing all of {markers} near {start}."
    if near_misses:
        for c, missing in near_misses:
            msg += f"\n  {c} exists but is missing: {missing}"
    raise FileNotFoundError(msg)
 
 
def _find_golden(start: Path) -> Path:
    for c in (start / "golden" / "golden.json", start / "goldens" / "kuju_goldens.json"):
        if c.exists():
            return c
    raise FileNotFoundError(f"No golden file found under {start} (looked for golden/golden.json)")
 
 
BACKEND_DIR = _find_dir(ROOT, "backend", ["agent.py", "projectsih.py"])
 
# agent.py alone isn't proof this is the right backend/ -- projectsih.py must
# be right there too, or every import past this point fails in a confusing way.
if not (BACKEND_DIR / "projectsih.py").exists():
    raise FileNotFoundError(
        f"Found backend/ at {BACKEND_DIR} (has agent.py) but it has no "
        f"projectsih.py. Is projectsih.py in a different folder, or under "
        f"a different name?"
    )
 
GOLDEN_PATH = str(_find_golden(ROOT))  # resolved BEFORE chdir, path is relative to ROOT
 
# `evals` is the harness PACKAGE (evals/harness.py), so what must go on
# sys.path is its PARENT, not evals/ itself.
EVALS_DIR = _find_dir(ROOT, "evals", "harness.py")
EVALS_PARENT = EVALS_DIR.parent
 
for _p in (str(BACKEND_DIR), str(ROOT), str(EVALS_PARENT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)
 
load_dotenv()
os.chdir(BACKEND_DIR)
 
import docx  # noqa: E402
from deepeval import evaluate  # noqa: E402
from deepeval.metrics import GEval  # noqa: E402
from deepeval.metrics.g_eval import Rubric  # noqa: E402
from deepeval.models import OllamaModel  # noqa: E402
from deepeval.test_case import LLMTestCase, LLMTestCaseParams  # noqa: E402
 
from agent import run_agent  # noqa: E402
 
try:
    from projectsih import rewrite_paragraph_with_llm, rewrite_table_with_llm  # noqa: E402
except ImportError as e:
    # projectsih.py was found on disk (checked above), so this is either a
    # broken import INSIDE projectsih.py (missing package, bad reference) or
    # the function names below no longer match what's defined there.
    raise ImportError(
        f"Found {BACKEND_DIR / 'projectsih.py'} but could not import "
        f"rewrite_paragraph_with_llm / rewrite_table_with_llm from it.\n"
        f"Underlying error: {type(e).__name__}: {e}\n"
        f"Check: (1) every package projectsih.py itself imports is installed "
        f"in this environment, (2) those two function names still exist in "
        f"projectsih.py."
    ) from e
 
from evals.harness import load_goldens, summarize_by_metric, print_summary  # noqa: E402
 
JUDGE_MODEL = OllamaModel(model="qwen2.5:7b", base_url="http://localhost:11434")
THRESHOLD = 0.6  # minimum score considered a pass
 
P = LLMTestCaseParams
REF_PARAMS = [P.INPUT, P.ACTUAL_OUTPUT, P.EXPECTED_OUTPUT]  # reference-based
FREE_PARAMS = [P.INPUT, P.ACTUAL_OUTPUT]                    # reference-free
 
# Pipeline crashes are turned into a marker string; every metric must score it 0
# (otherwise "no wrong claims" would give a crashed run a perfect Correctness).
FAIL_MARKERS = "[PIPELINE ERROR] or [TABLE REWRITE FAILED]"
FAIL_STEP = (
    f"If the actual output starts with {FAIL_MARKERS}, the pipeline failed: "
    "score 0 and ignore every other step."
)
 
 
# =====================================================================
# 1. TEST-CASE BUILDERS (call the real pipelines)
# =====================================================================
def table_to_text(t) -> str:
    """{'headers': [...], 'rows': [[...]]} -> markdown text the judge can read."""
    if isinstance(t, str):
        return t
    if not t:
        return "(empty table)"
    headers = [str(h) for h in t.get("headers", [])]
    lines = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    for row in t.get("rows", []):
        lines.append("| " + " | ".join(str(c) for c in row) + " |")
    return "\n".join(lines)


def _parse_markdown_table(text: str) -> dict:
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|") or not line.endswith("|"):
            continue
        cells = [cell.strip() for cell in line[1:-1].split("|")]
        if cells and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        rows.append(cells)
    if not rows:
        return {"headers": [], "rows": []}
    width = len(rows[0])
    return {
        "headers": rows[0],
        "rows": [row + [""] * (width - len(row)) for row in rows[1:]],
    }


def _cell_key(value: str) -> str:
    value = " ".join(str(value).strip().casefold().split())
    try:
        return str(Decimal(value.replace(",", "")).normalize())
    except InvalidOperation:
        return value


def _is_na_cell(value: str) -> bool:
    return " ".join(str(value).strip().casefold().split()) in {
        "n/a", "na", "not applicable", "not available", "null", "none"
    }


def deterministic_table_correctness(actual: str, expected: str) -> tuple[float, list[str]]:
    """Compare cells by normalized row labels and column headers."""
    if actual.startswith(("[PIPELINE ERROR]", "[TABLE REWRITE FAILED]")):
        return 0.0, [actual]

    actual_table = _parse_markdown_table(actual)
    expected_table = _parse_markdown_table(expected)
    actual_headers = {_cell_key(header): i for i, header in enumerate(actual_table["headers"])}
    if not expected_table["headers"]:
        return 0.0, ["Expected table has no headers to compare."]

    label_header = _cell_key(expected_table["headers"][0])
    actual_label_column = actual_headers.get(label_header, 0)
    expected_headers = {
        _cell_key(header): i
        for i, header in enumerate(expected_table["headers"])
        if i != 0
    }
    expected_rows = {
        _cell_key(row[0]): row
        for row in expected_table["rows"]
        if row and row[0].strip()
    }
    actual_rows = {
        _cell_key(row[actual_label_column]): row
        for row in actual_table["rows"]
        if len(row) > actual_label_column and row[actual_label_column].strip()
    }

    checked = 0
    correct = 0
    errors = []

    for row_key, expected_row in expected_rows.items():
        actual_row = actual_rows.get(row_key)
        for header_key, expected_column in expected_headers.items():
            expected_value = expected_row[expected_column] if expected_column < len(expected_row) else ""
            actual_column = actual_headers.get(header_key)
            actual_value = (
                actual_row[actual_column]
                if actual_row is not None and actual_column is not None and actual_column < len(actual_row)
                else ""
            )
            if (
                not expected_value.strip()
                or _is_na_cell(expected_value)
                or not actual_value.strip()
                or _is_na_cell(actual_value)
            ):
                continue
            checked += 1
            if _cell_key(expected_value) == _cell_key(actual_value):
                correct += 1
            else:
                errors.append(
                    f"{expected_row[0]} / {expected_table['headers'][expected_column]}: "
                    f"expected {expected_value or 'blank'!r}, got {actual_value or 'missing'!r}"
                )

    return (correct / checked if checked else 0.0), errors
 
 
def build_docx_table(table_data: dict):
    """rewrite_table_with_llm expects a python-docx Table, so build one in memory.
    Returns (doc, table); keep `doc` referenced while the table is in use."""
    headers, rows = table_data["headers"], table_data["rows"]
    doc = docx.Document()
    tbl = doc.add_table(rows=1 + len(rows), cols=len(headers))
    for j, h in enumerate(headers):
        tbl.cell(0, j).text = str(h)
    for i, row in enumerate(rows, start=1):
        for j, v in enumerate(row):
            tbl.cell(i, j).text = str(v)
    return doc, tbl
 
 
def section_line(context: dict) -> str:
    parts = [context.get(f"heading{i}") for i in (1, 2, 3, 4)]
    return " > ".join(p for p in parts if p) or "N/A"
 
 
def case_input(kind: str, q) -> str:
    """The task description the judge sees as `input` (shared with eval_rag_pipeline.py)."""
    if kind == "paragraph":
        return (
            f"Topic: {q['user_topic']}\nDescription: {q.get('user_description', '')}\n"
            f"Section: {section_line(q['context'])}\nParagraph to rewrite: {q['text']}"
        )
    if kind == "table":
        return (
            f"Topic: {q['user_topic']}\nDescription: {q.get('user_description', '')}\n"
            f"Section: {section_line(q['context'])}\n"
            "Scoring rule: blank and N/A cells are excluded from all table metrics; "
            "do not count them as correct, incorrect, missing evidence, or unsupported claims.\n"
            f"Table to update:\n{table_to_text(q['table'])}"
        )
    return q  # qnaagent: the question itself
 
 
def build_case(g: dict) -> LLMTestCase:
    kind, q = g["type"], g["query"]
    expected = table_to_text(g["ideal_answer"]) if kind == "table" else g["ideal_answer"]
    inp = case_input(kind, q)
 
    try:
        if kind == "paragraph":
            actual = rewrite_paragraph_with_llm(
                text=q["text"],
                context=q["context"],
                user_topic=q["user_topic"],
                user_description=q.get("user_description", ""),
            )
        elif kind == "table":
            doc, tbl = build_docx_table(q["table"])
            out = rewrite_table_with_llm(
                table=tbl,
                context=q["context"],
                user_topic=q["user_topic"],
                user_description=q.get("user_description", ""),
            )
            actual = table_to_text(out) if out else "[TABLE REWRITE FAILED] empty result or invalid JSON"
        elif kind == "qnaagent":
            actual = run_agent(q)
        else:
            raise ValueError(f"unknown golden type: {kind}")
    except Exception as e:  # one bad query must not kill the whole run
        actual = f"[PIPELINE ERROR] {type(e).__name__}: {e}"
 
    return LLMTestCase(input=inp, actual_output=actual, expected_output=expected)
 
 
# =====================================================================
# 2. METRICS
# =====================================================================
def _geval(name, steps, rubric, params):
    return GEval(
        name=name,
        evaluation_steps=steps + [FAIL_STEP],
        rubric=rubric,
        evaluation_params=params,
        threshold=THRESHOLD,
        model=JUDGE_MODEL,
        strict_mode=False,
    )
 
 
def correctness_text():
    """Reference-based, judges TRUTH (not coverage or length). Paragraph + QnA."""
    return _geval(
        "Correctness",
        [
            "Compare only the factual claims in the actual output against the expected output.",
            "A claim is wrong only if it CONTRADICTS the expected output or is factually false. Judge truth, not completeness.",
            "A factually accurate answer must score at least 0.9 even if it is shorter or covers fewer points than the expected output.",
            "Do NOT deduct for brevity or omitted points; omissions are not errors here.",
            "Additional correct information must NEVER lower the score.",
            "Ignore any 'Suggested Follow-up Questions' section; it contains no factual claims.",
        ],
        [
            Rubric(score_range=(9, 10), expected_outcome="All stated claims are factually correct and consistent. No contradictions. Brevity is fine."),
            Rubric(score_range=(5, 8), expected_outcome="Mostly correct but one minor inaccuracy."),
            Rubric(score_range=(0, 4), expected_outcome="Contains a clear factual error or a claim that contradicts the expected output."),
        ],
        REF_PARAMS,
    )
 
 
def completeness_text():
    """Reference-based, judges COVERAGE (not correctness). Paragraph + QnA."""
    return _geval(
        "Completeness",
        [
            "Identify the key points contained in the expected output.",
            "Check how many of those key points are addressed in the actual output.",
            "Penalize the actual output for each key point from the expected output that it omits or only partially covers.",
            "Judge coverage only. Do NOT lower the score because a covered point is stated incorrectly.",
            "Do NOT penalize extra information beyond the expected output.",
            "Ignore any 'Suggested Follow-up Questions' section.",
        ],
        [
            Rubric(score_range=(9, 10), expected_outcome="Addresses essentially all key points in the expected output."),
            Rubric(score_range=(5, 8), expected_outcome="Covers the main key points but misses one or more."),
            Rubric(score_range=(0, 4), expected_outcome="Misses several key points; only partially covers the expected output."),
        ],
        REF_PARAMS,
    )
 
 
def correctness_table():
    """Cell-level truth, excluding blank and N/A cells from the score denominator."""
    return _geval(
        "Table Correctness",
        [
            "Match rows of the actual table to the expected table by parameter name, and columns by header (e.g. year).",
            "A cell is wrong only if its value contradicts the expected cell, or it is a number that appears nowhere in the expected table (invented value).",
            "Exclude every cell where either actual or expected value is blank or N/A from both numerator and denominator. Do not count these cells as correct, incorrect, or invented.",
            "Extra correct rows or columns must never lower the score. Judge truth, not coverage.",
            "If no cell is wrong, score at least 0.9.",
        ],
        [
            Rubric(score_range=(9, 10), expected_outcome="Every filled cell is consistent with the expected table. No invented numbers."),
            Rubric(score_range=(5, 8), expected_outcome="Mostly correct with one or two wrong or invented cells."),
            Rubric(score_range=(0, 4), expected_outcome="Several wrong or invented values, or values contradicting the expected table."),
        ],
        REF_PARAMS,
    )
 
 
def completeness_table():
    """Coverage of scored, non-blank expected table cells."""
    return _geval(
        "Table Completeness",
        [
            "List the rows and columns in the expected table, including any newly added year/column or newly added row.",
            "Check that each expected row and column exists in the actual table.",
            "Exclude every cell where either actual or expected value is blank or N/A from both numerator and denominator.",
            "For remaining comparable cells, score whether the expected row, column, and value are present.",
            "Judge coverage only; do NOT lower the score because a filled value is slightly wrong, and do NOT penalize extra rows/columns.",
        ],
        [
            Rubric(score_range=(9, 10), expected_outcome="All scored, non-blank/non-N/A expected rows, columns and values are present."),
            Rubric(score_range=(5, 8), expected_outcome="Most scored expected rows, columns and values are present."),
            Rubric(score_range=(0, 4), expected_outcome="Many scored expected rows, columns or values are missing or incorrect."),
        ],
        REF_PARAMS,
    )
 
 
def style_paragraph():
    """Reference-free tone check for rewritten report paragraphs."""
    return _geval(
        "Style",
        [
            "Judge only tone and writing quality of the actual output, not factual correctness or completeness.",
            "Reward a professional, formal technical-report register: clear, concise, well-flowing prose.",
            "The output must be ONLY the rewritten paragraph. Penalize meta-commentary such as 'Here is the rewritten paragraph' or 'Sure, ...'.",
            "Penalize bullet lists, markdown headings, chatty tone, or unexplained jargon.",
            "Do NOT reward or penalize based on length or facts.",
        ],
        [
            Rubric(score_range=(9, 10), expected_outcome="Polished professional report prose with no meta-commentary."),
            Rubric(score_range=(7, 8), expected_outcome="Professional and clear; minor awkwardness."),
            Rubric(score_range=(4, 6), expected_outcome="Understandable but chatty, flat, or list-like in places."),
            Rubric(score_range=(0, 3), expected_outcome="Contains meta-commentary, bullets/markdown, or reads robotic or unprofessional."),
        ],
        FREE_PARAMS,
    )
 
 
def style_qna():
    """Reference-free tone + format check for the analyst agent."""
    return _geval(
        "Style",
        [
            "Judge only tone and format of the actual output, not factual correctness or completeness.",
            "Reward a clear, professional analyst voice in plain language that explains figures rather than dumping raw rows or SQL.",
            "The response must end with a section labeled 'Suggested Follow-up Questions:' containing 2-3 brief questions. Penalize if it is missing or has the wrong count.",
            "Penalize exposing internal tool details (raw SQL, tool names, 'Executed Query') to the user.",
            "Do NOT reward or penalize based on correctness or length.",
        ],
        [
            Rubric(score_range=(9, 10), expected_outcome="Clear analyst voice AND a proper 'Suggested Follow-up Questions:' section with 2-3 questions."),
            Rubric(score_range=(7, 8), expected_outcome="Clear and professional; follow-up section present but slightly off (e.g. 1 or 4 questions)."),
            Rubric(score_range=(4, 6), expected_outcome="Understandable but flat, or the follow-up section is missing."),
            Rubric(score_range=(0, 3), expected_outcome="Dumps raw SQL/tool output, or is robotic and unstructured."),
        ],
        FREE_PARAMS,
    )
 
 
# fresh metric objects per group
METRIC_BUILDERS = {
    "paragraph": lambda: [correctness_text(), completeness_text(), style_paragraph()],
    "table": lambda: [correctness_table(), completeness_table()],
    "qnaagent": lambda: [correctness_text(), completeness_text(), style_qna()],
}
 
 
# =====================================================================
# 3. RUN
# =====================================================================
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
        cases = [build_case(g) for g in items]
        result = evaluate(test_cases=cases, metrics=METRIC_BUILDERS[kind]())
        summary.update(summarize_by_metric(result, prefix=f"app.{kind}."))

        if kind == "table":
            golden_by_input = {case.input: golden for case, golden in zip(cases, items)}
            deterministic_scores = []
            best_scores = []
            deterministic_failures = []

            for test_result in result.test_results:
                golden = golden_by_input.get(test_result.input)
                if golden is None:
                    continue

                actual = str(test_result.actual_output)
                deterministic_score, errors = deterministic_table_correctness(
                    actual,
                    table_to_text(golden["ideal_answer"]),
                )
                llm_metric = next(
                    (metric for metric in test_result.metrics_data if metric.name == "Table Correctness"),
                    None,
                )
                llm_score = llm_metric.score if llm_metric and llm_metric.score is not None else 0.0
                failed = actual.startswith(("[PIPELINE ERROR]", "[TABLE REWRITE FAILED]"))
                best_score = 0.0 if failed else max(llm_score, deterministic_score)

                deterministic_scores.append(deterministic_score)
                best_scores.append(best_score)
                if errors:
                    deterministic_failures.append({
                        "input": test_result.input,
                        "actual_output": actual,
                        "expected_output": test_result.expected_output,
                        "metric_name": "Deterministic Table Correctness",
                        "score": round(deterministic_score, 4),
                        "reason": "; ".join(errors[:10]),
                    })

            count = len(deterministic_scores)
            summary["app.table.deterministic_correctness.avg_score"] = {
                "avg_score": round(sum(deterministic_scores) / count, 4) if count else 0.0,
                "pass_rate": round(sum(score >= THRESHOLD for score in deterministic_scores) / count, 4) if count else 0.0,
                "n": count,
                "fail_reasons": deterministic_failures,
            }
            summary["app.table.best_correctness.avg_score"] = {
                "avg_score": round(sum(best_scores) / count, 4) if count else 0.0,
                "pass_rate": round(sum(score >= THRESHOLD for score in best_scores) / count, 4) if count else 0.0,
                "n": count,
                "fail_reasons": [],
            }
    return summary
 
 
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("types", nargs="*", help="paragraph | table | qnaagent (default: all)")
    args = ap.parse_args()
    print_summary("application", run(args.types or None))
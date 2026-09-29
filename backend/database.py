"""
database.py  -  the SQL half of the hybrid store.
 
    Chroma  : "find the right table / passage"   (semantic retrieval, chunks.py)
    SQLite  : "compute exact numbers on it"      (SUM / AVG / MAX / GROUP BY / JOIN)
 
Every joined table from pdf_tables.py becomes its OWN SQLite table with REAL
typed columns, so aggregates work directly:
 
    SELECT SUM(reserves_mt_measured) FROM t_ab12cd_000_table_3_1 WHERE _is_total = 0;
 
Layout
------
tables_catalog   one row per table: id, source pdf, pages, caption, SQL table name
table_columns    one row per column: SQL name, ORIGINAL header text, inferred type
t_<src>_<n>_...  the data. Extra bookkeeping columns start with "_":
                    _row_idx   order inside the joined table
                    _page_no   PDF page the row came from
                    _is_total  1 for 'Total' / 'Sub-total' / 'Grand total' rows
                               (exclude them before SUM or you double count)
                    _raw_json  original cell strings, lossless fallback
 
Rules that protect accuracy
---------------------------
* Numbers are parsed ("1,23,456.7", "(12.5)", "12%", "Rs 5*") into REAL/INTEGER.
* Missing markers ("-", "NA", blank) become NULL, never 0.0, so AVG/COUNT stay honest.
* A column becomes numeric only if >= 80% of its non-empty cells parse.
* The raw text is always kept in _raw_json.
"""
 
from __future__ import annotations
 
import json
import re
import sqlite3
from collections import defaultdict
from typing import Any, Dict, List, Optional, Sequence, Tuple
 
from pdf_tables import LogicalTable, NULL_MARKERS, clean_cell, parse_number
 
NUMERIC_THRESHOLD = 0.80
_TOTAL_RE = re.compile(r"^\s*(?:grand\s+total|sub[\s-]*total|total)\b", re.I)
 
 
def _slug(text: str, maxlen: int = 40) -> str:
    return re.sub(r"[^a-z0-9]+", "_", (text or "").lower()).strip("_")[:maxlen].strip("_")
 
 
def _sql_column_names(headers: Sequence[str]) -> List[str]:
    """Header text -> safe, unique SQL identifiers ('Reserves (Mt) Measured' -> reserves_mt_measured)."""
    used: Dict[str, int] = {}
    names = []
    for i, h in enumerate(headers):
        name = _slug(h) or f"col_{i + 1}"
        if name[0].isdigit():
            name = "c_" + name
        if name in used:
            used[name] += 1
            name = f"{name}_{used[name]}"
        else:
            used[name] = 1
        names.append(name)
    return names
 
 
def _infer_type(cells: Sequence[str]) -> str:
    vals = [c for c in cells if c and c.strip().lower() not in NULL_MARKERS]
    if not vals:
        return "TEXT"
    parsed = [parse_number(c) for c in vals]
    ok = [p for p in parsed if p is not None]
    if len(ok) / len(vals) < NUMERIC_THRESHOLD:
        return "TEXT"
    if all(float(p).is_integer() for p in ok) and not any("." in c for c in vals):
        return "INTEGER"
    return "REAL"
 
 
def _is_total_row(row: Sequence[str]) -> int:
    for cell in row[:2]:                         # label is in col 0, or col 1 after 'Sl. No.'
        if cell and parse_number(cell) is None:
            return 1 if _TOTAL_RE.match(cell) else 0
    return 0
 
 
def _q(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'
 
 
class TableDatabase:
    def __init__(self, path: str = "./tables.db"):
        self.path = path
        self.conn = sqlite3.connect(path)
        self._init_schema()
 
    # ------------------------------------------------------------------ setup
    def _init_schema(self) -> None:
        with self.conn:
            self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS tables_catalog (
                table_id    TEXT PRIMARY KEY,
                source_id   TEXT NOT NULL,
                source      TEXT NOT NULL,
                sql_table   TEXT NOT NULL UNIQUE,
                caption     TEXT,
                page_start  INTEGER,
                page_end    INTEGER,
                n_rows      INTEGER,
                n_cols      INTEGER,
                created_at  TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS table_columns (
                table_id        TEXT NOT NULL,
                col_idx         INTEGER NOT NULL,
                sql_name        TEXT NOT NULL,
                original_header TEXT,
                sql_type        TEXT,
                PRIMARY KEY (table_id, col_idx)
            );
            CREATE INDEX IF NOT EXISTS idx_catalog_source ON tables_catalog(source_id);
            """)
 
    def close(self) -> None:
        self.conn.close()
 
    def __enter__(self) -> "TableDatabase":
        return self
 
    def __exit__(self, *exc) -> None:
        self.close()
 
    # ------------------------------------------------------------------ write
    def delete_source(self, source_id: str) -> int:
        """Remove every table that came from this PDF (makes re-indexing idempotent)."""
        rows = self.conn.execute(
            "SELECT table_id, sql_table FROM tables_catalog WHERE source_id = ?", (source_id,)
        ).fetchall()
        with self.conn:
            for table_id, sql_table in rows:
                self.conn.execute(f"DROP TABLE IF EXISTS {_q(sql_table)}")
                self.conn.execute("DELETE FROM table_columns WHERE table_id = ?", (table_id,))
            self.conn.execute("DELETE FROM tables_catalog WHERE source_id = ?", (source_id,))
        return len(rows)
 
    def save_table(self, tbl: LogicalTable, source: str, source_id: str) -> Tuple[str, str]:
        """Store one joined table. Returns (table_id, sql_table)."""
        table_id = f"{source_id}_t{tbl.index:03d}"
        cap_slug = _slug(tbl.caption, 30)
        sql_table = f"t_{source_id[:6]}_{tbl.index:03d}" + (f"_{cap_slug}" if cap_slug else "")
 
        col_names = _sql_column_names(tbl.headers)
        col_types = [_infer_type([r[i] for r in tbl.rows]) for i in range(len(col_names))]
 
        ddl_cols = ", ".join(f"{_q(n)} {t}" for n, t in zip(col_names, col_types))
        insert_sql = (
            f"INSERT INTO {_q(sql_table)} "
            f"(_row_idx, _page_no, _is_total, {', '.join(_q(n) for n in col_names)}, _raw_json) "
            f"VALUES ({', '.join('?' * (len(col_names) + 4))})"
        )
 
        data = []
        for r_idx, (row, page_no) in enumerate(zip(tbl.rows, tbl.row_pages)):
            values: List[Any] = []
            for cell, typ in zip(row, col_types):
                if typ == "TEXT":
                    values.append(clean_cell(cell) or None)
                else:
                    n = parse_number(cell)
                    values.append(None if n is None else (int(n) if typ == "INTEGER" else n))
            data.append((r_idx, page_no, _is_total_row(row), *values, json.dumps(row, ensure_ascii=False)))
 
        with self.conn:
            self.conn.execute(f"DROP TABLE IF EXISTS {_q(sql_table)}")
            self.conn.execute(
                f"CREATE TABLE {_q(sql_table)} (_row_idx INTEGER, _page_no INTEGER, "
                f"_is_total INTEGER, {ddl_cols}, _raw_json TEXT)"
            )
            self.conn.executemany(insert_sql, data)
            self.conn.execute("DELETE FROM table_columns WHERE table_id = ?", (table_id,))
            self.conn.execute("DELETE FROM tables_catalog WHERE table_id = ?", (table_id,))
            self.conn.execute(
                "INSERT INTO tables_catalog (table_id, source_id, source, sql_table, caption, "
                "page_start, page_end, n_rows, n_cols) VALUES (?,?,?,?,?,?,?,?,?)",
                (table_id, source_id, source, sql_table, tbl.caption, tbl.page_start,
                 tbl.page_end, tbl.n_rows, len(col_names)),
            )
            self.conn.executemany(
                "INSERT INTO table_columns (table_id, col_idx, sql_name, original_header, sql_type) "
                "VALUES (?,?,?,?,?)",
                [(table_id, i, n, tbl.headers[i], t) for i, (n, t) in enumerate(zip(col_names, col_types))],
            )
        return table_id, sql_table
 
    # ------------------------------------------------------------------- read
    def query(self, sql: str, params: Sequence[Any] = (), max_rows: int = 500) -> Tuple[List[str], List[tuple]]:
        """Run ONE read-only SELECT/WITH statement (safe to expose to an LLM text-to-SQL step)."""
        stmt = sql.strip().rstrip(";").strip()
        if not re.match(r"(?is)^(select|with)\b", stmt) or ";" in stmt:
            raise ValueError("Only a single SELECT / WITH statement is allowed.")
        self.conn.execute("PRAGMA query_only = ON")
        try:
            cur = self.conn.execute(stmt, tuple(params))
            cols = [d[0] for d in cur.description or []]
            return cols, cur.fetchmany(max_rows)
        finally:
            self.conn.execute("PRAGMA query_only = OFF")
 
    def describe_schema(self, source_id: Optional[str] = None, sample_rows: int = 2) -> str:
        """Plain-text catalog: table names, captions, columns (with the ORIGINAL header text
        and type) and a couple of sample rows. Paste this into a text-to-SQL prompt."""
        where, args = ("WHERE source_id = ?", (source_id,)) if source_id else ("", ())
        catalog = self.conn.execute(
            f"SELECT table_id, sql_table, source, caption, page_start, page_end, n_rows "
            f"FROM tables_catalog {where} ORDER BY source, page_start, table_id", args
        ).fetchall()
        blocks = []
        for table_id, sql_table, source, caption, p0, p1, n_rows in catalog:
            pages = f"p{p0}" if p0 == p1 else f"p{p0}-{p1}"
            cols = self.conn.execute(
                "SELECT sql_name, original_header, sql_type FROM table_columns "
                "WHERE table_id = ? ORDER BY col_idx", (table_id,)
            ).fetchall()
            lines = [f'TABLE {_q(sql_table)}  -- {source} {pages}, {n_rows} rows'
                     + (f', "{caption}"' if caption else "")]
            lines += [f'  {_q(n)} {t}  -- header: "{h}"' for n, h, t in cols]
            lines.append('  _is_total INTEGER  -- 1 = Total/Sub-total row (filter with _is_total = 0 before SUM)')
            if sample_rows:
                names = ", ".join(_q(n) for n, _, _ in cols)
                for row in self.conn.execute(
                    f"SELECT {names} FROM {_q(sql_table)} ORDER BY _row_idx LIMIT ?", (sample_rows,)
                ):
                    lines.append("  e.g. " + " | ".join("NULL" if v is None else str(v) for v in row))
            blocks.append("\n".join(lines))
        return "\n\n".join(blocks)
 
    def join_candidates(self) -> List[Dict[str, Any]]:
        """Columns whose header text appears in 2+ tables (e.g. 'Year', 'Coalfield').
        PDF tables have no foreign keys, so a join is only possible on shared descriptive
        columns like these - and a human/LLM should still confirm the values really match."""
        groups: Dict[str, List[Dict[str, str]]] = defaultdict(list)
        for table_id, sql_name, header, typ in self.conn.execute(
            "SELECT table_id, sql_name, original_header, sql_type FROM table_columns"
        ):
            key = re.sub(r"[^a-z0-9]", "", (header or "").lower())
            if key:
                groups[key].append({"table_id": table_id, "column": sql_name, "type": typ})
        return [
            {"header_key": k, "tables": v}
            for k, v in groups.items()
            if len({x["table_id"] for x in v}) >= 2
        ]
 
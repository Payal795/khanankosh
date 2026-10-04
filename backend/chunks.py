"""
chunks.py

PDF -> (1) open + FIX TABLES (join multi-page tables, drop repeated headers)
    -> (2) chunk  narrative text + whole tables
    -> (3) embed  into Chroma          (retrieval for projectsih.py, same as before)
    -> (4) store  typed tables in SQLite (exact SUM / AVG / GROUP BY / JOIN)

The table joining itself lives in pdf_tables.py (same rules as heading_normalizer.py).
"""

import hashlib
import logging
import os
from typing import Any, Dict, List, Optional

import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter

from database import TableDatabase
from pdf_tables import LogicalTable, extract_document

log = logging.getLogger(__name__)

TABLE_CHUNK_CHARS = 1500     # a table larger than this is split by ROW GROUPS (header repeated)
EMBED_BATCH = 64


def _file_id(path: str) -> str:
    """Content hash -> same PDF always maps to the same id (re-indexing replaces, never duplicates)."""
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()[:10]


class DocumentVectorIndexer:
    def __init__(
        self,
        pdf_path: str,
        collection_name: str = "pdf_report",
        persist_directory: str = "./chroma_db",
        sqlite_path: Optional[str] = "./tables.db",
        embedding_fn: Any = None,
        table_strategy: Optional[str] = None,
    ):
        self.pdf_path = pdf_path
        self.filename = pdf_path.split("/")[-1].split("\\")[-1]
        self.source_id = _file_id(pdf_path)
        self.sqlite_path = sqlite_path
        self.table_strategy = table_strategy      # "text" helps with borderless tables

        # Persistent client so projectsih.py's langchain_chroma.Chroma(persist_directory=...) sees it.
        self.chroma_client = chromadb.PersistentClient(path=persist_directory)
        if embedding_fn is None:
            from model_clients import create_embeddings
            embedding_fn = create_embeddings()
        self.embedding_fn = embedding_fn
        self.collection = self.chroma_client.get_or_create_collection(name=collection_name)

        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        self.stats: Dict[str, int] = {}

    # ---------------------------------------------------------------- tables
    @staticmethod
    def _row_line(row: List[str]) -> str:
        return " | ".join(row)

    def _table_chunks(self, tbl: LogicalTable, table_id: str, sql_table: str) -> List[Dict[str, Any]]:
        """Split ONE joined table into self-describing chunks: every chunk repeats the
        caption + header so a row group is never a bare list of numbers."""
        pages = str(tbl.page_start) if not tbl.is_multipage else f"{tbl.page_start}-{tbl.page_end}"
        header_line = self._row_line(tbl.headers)
        row_lines = [self._row_line(r) for r in tbl.rows]
        budget = max(TABLE_CHUNK_CHARS - len(header_line) - 200, 300)

        out: List[Dict[str, Any]] = []
        i = 0
        while i < len(row_lines):
            start, size = i, 0
            while i < len(row_lines) and (i == start or size + len(row_lines[i]) + 1 <= budget):
                size += len(row_lines[i]) + 1
                i += 1
            first_page = tbl.row_pages[start]
            text = (
                f"[Table] {tbl.caption or 'untitled table'}\n"
                f"Source: {self.filename}, pages {pages}, rows {start + 1}-{i} of {tbl.n_rows}\n"
                f"{header_line}\n" + "\n".join(row_lines[start:i])
            )
            meta = {
                "type": "table",
                "source": self.filename,
                "source_id": self.source_id,
                "page_no": first_page,
                "page_start": tbl.page_start,
                "page_end": tbl.page_end,
                "is_multipage": tbl.is_multipage,
                "is_continuation": first_page > tbl.page_start,
                "table_id": table_id,
                "row_start": start + 1,
                "row_end": i,
                "n_rows": tbl.n_rows,
                "caption": tbl.caption or "",
            }
            if sql_table:
                meta["sql_table"] = sql_table
            out.append({"text": text, "meta": meta, "id": f"{self.source_id}_table_{tbl.index:03d}_{len(out):03d}"})
        return out

    # ------------------------------------------------------------ main entry
    def process_and_index(self) -> int:
        """Returns the number of chunks indexed into Chroma."""
        parsed = extract_document(self.pdf_path, table_strategy=self.table_strategy)

        documents: List[str] = []
        metadatas: List[Dict[str, Any]] = []
        ids: List[str] = []

        # 1) narrative text (table areas already removed by pdf_tables)
        for page_no, text in parsed.pages_text.items():
            for k, chunk in enumerate(self.text_splitter.split_text(text) if text else []):
                documents.append(chunk)
                metadatas.append({"type": "text", "source": self.filename,
                                  "source_id": self.source_id, "page_no": page_no})
                ids.append(f"{self.source_id}_text_p{page_no:04d}_{k:03d}")
        n_text = len(documents)

        # 2) joined tables -> SQLite (typed) + Chroma (whole-table chunks)
        db: Optional[TableDatabase] = TableDatabase(self.sqlite_path) if self.sqlite_path else None
        n_sql_tables = 0
        try:
            if db:
                db.delete_source(self.source_id)
            for tbl in parsed.tables:
                table_id = f"{self.source_id}_t{tbl.index:03d}"
                sql_table = ""
                if db:
                    try:
                        table_id, sql_table = db.save_table(tbl, self.filename, self.source_id)
                        n_sql_tables += 1
                    except Exception as exc:          # a weird table must not kill the whole index
                        log.warning("SQLite store failed for table %s (p%s): %s", tbl.index, tbl.page_start, exc)
                for ch in self._table_chunks(tbl, table_id, sql_table):
                    documents.append(ch["text"])
                    metadatas.append(ch["meta"])
                    ids.append(ch["id"])
        finally:
            if db:
                db.close()

        # 3) Chroma: replace this PDF's old chunks, then embed in batches
        self.collection.delete(where={"source_id": self.source_id})
        if documents:
            embeddings: List[List[float]] = []
            for i in range(0, len(documents), EMBED_BATCH):
                embeddings.extend(self.embedding_fn.embed_documents(documents[i:i + EMBED_BATCH]))
            self.collection.upsert(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)

        self.stats = {
            "text_chunks": n_text,
            "table_chunks": len(documents) - n_text,
            "tables_found": len(parsed.tables),
            "tables_joined_multipage": sum(1 for t in parsed.tables if t.is_multipage),
            "tables_in_sqlite": n_sql_tables,
        }
        return len(documents)

    def query(self, query_text: str, n_results: int = 3):
        query_embedding = self.embedding_fn.embed_query(query_text)
        return self.collection.query(query_embeddings=[query_embedding], n_results=n_results)


# ---------------------------------------------------------
# Pipeline entry point (called from main.py) - signature kept backward compatible
# ---------------------------------------------------------
def index_pdf_for_rag(
    pdf_path: str,
    collection_name: str = "pdf_report",
    persist_directory: str = "./chroma_db",
    sqlite_path: Optional[str] = "./tables.db",
) -> Dict[str, Any]:
    """
    Full extraction + embedding for a single PDF. Chroma store is shared with
    projectsih.process_and_rewrite_document (same persist_directory/collection_name).
    Pass sqlite_path=None to skip the SQL table store.
    """
    indexer = DocumentVectorIndexer(
        pdf_path,
        collection_name=collection_name,
        persist_directory=persist_directory,
        sqlite_path=sqlite_path,
    )
    chunks_indexed = indexer.process_and_index()
    return {
        "pdf_path": pdf_path,
        "collection_name": collection_name,
        "persist_directory": persist_directory,
        "sqlite_path": sqlite_path,
        "chunks_indexed": chunks_indexed,
        **indexer.stats,
    }
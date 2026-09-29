import os
import sqlite3
from chunks import _file_id, index_pdf_for_rag
import inspect_data

PDF_DIR = "sample_pdfs"

def run_pipeline():
    os.makedirs(PDF_DIR, exist_ok=True)
    
    # 1. Check existing files by Hash
    existing_ids = set()
    if os.path.exists("tables.db"):
        try:
            conn = sqlite3.connect("tables.db")
            existing_ids = set(r[0] for r in conn.execute("SELECT DISTINCT source_id FROM tables_catalog").fetchall())
            conn.close()
        except Exception:
            pass

    new_files_processed = False

    # 2. Process only new/changed PDFs
    for filename in os.listdir(PDF_DIR):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(PDF_DIR, filename)
            file_hash = _file_id(pdf_path)

            if file_hash in existing_ids:
                print(f"[SKIP] {filename} (Already indexed)")
                continue

            print(f"[INGEST] Processing {filename}...")
            # This single function call populates BOTH ChromaDB and SQLite tables.db
            stats = index_pdf_for_rag(
                pdf_path=pdf_path,
                collection_name="coal_ministry_docs",
                persist_directory="./chroma_db",
                sqlite_path="./tables.db"
            )
            print(f"   -> Embedded {stats.get('chunks_indexed')} chunks, {stats.get('tables_in_sqlite')} SQL tables.")
            new_files_processed = True

    # 3. Auto-run inspection if database changed
    if new_files_processed:
        print("\n[✔️] Ingestion complete. Running database health check...\n")
        inspect_data.run_inspection()
    else:
        print("\n[✔️] All PDFs are up to date. No new data to process.")


if __name__ == "__main__":
    run_pipeline()
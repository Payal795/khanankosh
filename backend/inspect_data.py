import sqlite3
import chromadb

def run_inspection():
    print("=== 1. SQLITE RECORDS (tables.db) ===")
    try:
        conn = sqlite3.connect("tables.db")
        catalog = conn.execute("SELECT sql_table, source, caption, n_rows FROM tables_catalog LIMIT 5").fetchall()
        for t_name, src, cap, rows in catalog:
            print(f"Table: {t_name} | Source: {src} | Rows: {rows} | Caption: {cap}")
        if not catalog:
            print("No dynamic tables found in tables.db.")
        conn.close()
    except Exception as e:
        print(f"SQLite Error: {e}")

    print("\n=== 2. CHROMADB SAMPLE (coal_ministry_docs) ===")
    try:
        client = chromadb.PersistentClient(path="./chroma_db")
        collection = client.get_collection("coal_ministry_docs")
        doc_count = collection.count()
        print(f"Total semantic chunks indexed: {doc_count}")
        if doc_count > 0:
            sample = collection.peek(limit=1)
            print(f"Sample Metadata: {sample['metadatas'][0]}")
    except Exception as e:
        print(f"ChromaDB Error: {e}")

if __name__ == "__main__":
    run_inspection()
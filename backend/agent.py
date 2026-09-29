import os
from dotenv import load_dotenv

import chromadb
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama, OllamaEmbeddings
from database import TableDatabase

load_dotenv()

llm = ChatOllama(model="qwen2.5:7b", temperature=0.0)

@tool
def query_dynamic_database(question: str) -> str:
    """
    Executes SQL to fetch exact quantitative metrics from tables.
    Use this when the user asks for exact reserves, financial metrics, sums, or averages.
    """
    try:
        db = TableDatabase("./tables.db")
        schema = db.describe_schema()
        
        sql_prompt = f"""
        You are an expert SQLite data analyst. Based on this schema:
        {schema}
        
        Write a SQLite query to answer: "{question}"
        Rules:
        1. Always include `WHERE _is_total = 0` when using SUM() or AVG() to avoid double counting.
        2. Return ONLY the raw SQL query string. No markdown, no explanations.
        """
        sql_query = llm.invoke([HumanMessage(content=sql_prompt)]).content.strip()
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()

        cols, rows = db.query(sql_query)
        db.close()

        if not rows: return "SQL query returned 0 rows. Data might not exist."

        result = [f"Executed Query: {sql_query}\nColumns: {cols}"]
        for r in rows[:15]: result.append(str(r))
        return "\n".join(result)
        
    except Exception as e:
        return f"Database Execution Error: {e}"

@tool
def search_vector_db(query: str) -> str:
    """Performs semantic retrieval across unstructured narratives, ESG policies, and reports."""
    try:
        client = chromadb.PersistentClient(path="./chroma_db")
        coll = client.get_collection("coal_ministry_docs")
        embed_model = OllamaEmbeddings(model="nomic-embed-text")

        res = coll.query(query_embeddings=[embed_model.embed_query(query)], n_results=3)
        docs, metas = res.get("documents", [[]])[0], res.get("metadatas", [[]])[0]

        if not docs: return "No matching narrative passages found in vector database."
        return "\n\n".join([f"[Source: {m.get('source', '?')} | Page: {m.get('page_no', '?')}]\n{d.strip()[:600]}..." for d, m in zip(docs, metas)])
    except Exception as e:
        return f"ChromaDB Query Error: {e}"

tools = [query_dynamic_database, search_vector_db]
tools_by_name = {t.name: t for t in tools}
llm_with_tools = llm.bind_tools(tools)

SYSTEM_PROMPT = """You are an expert AI Mining and Financial Analyst assistant.
You have access to two tools:
1. `query_dynamic_database`: Use for deterministic calculations, coal reserve estimates, or financial metrics.
2. `search_vector_db`: Use for policy narratives, worker safety standards, and general text.

Instructions:
- Keep answers strictly grounded in retrieved tool outputs.
- At the very end of your final response, provide a section labeled 'Suggested Follow-up Questions:' with 2-3 brief follow-ups.
"""

def run_agent(query: str) -> str:
    messages = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=query)]
    
    for _ in range(5):
        ai_response = llm_with_tools.invoke(messages)
        messages.append(ai_response)
        if not ai_response.tool_calls: return str(ai_response.content)

        for call in ai_response.tool_calls:
            tool_name = call["name"]
            selected_tool = tools_by_name.get(tool_name)
            tool_output = selected_tool.invoke(call["args"]) if selected_tool else f"Error: Tool '{tool_name}' not recognized."
            messages.append(ToolMessage(content=str(tool_output), name=tool_name, tool_call_id=call["id"]))

    return "Agent reached maximum tool iterations without finishing."
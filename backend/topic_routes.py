import base64
import io
import json
import os
from contextlib import asynccontextmanager

from bertopic import BERTopic
from fastapi import APIRouter, FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from wordcloud import WordCloud

# Global state container for the loaded model / doc store.
# Populated by `topic_lifespan` below and read by the route handlers.
ml_models = {}

router = APIRouter(prefix="/api/v1", tags=["Topic Modeling"])


@asynccontextmanager
async def topic_lifespan(app: FastAPI):
    """Startup/shutdown hook for the BERTopic model + document store.

    Pass this into the top-level FastAPI(lifespan=...) call in main.py —
    a router can't own a lifespan on its own, only the app can.
    """
    print("Loading pre-trained BERTopic model...")
    try:
        ml_models["topic_model"] = BERTopic.load("cmpdi_bertopic_model")
        print("BERTopic model loaded successfully.")
    except Exception as e:
        print(f"Warning: Could not load 'cmpdi_bertopic_model': {e}")
        ml_models["topic_model"] = None

    try:
        with open("document_store.json", "r", encoding="utf-8") as f:
            ml_models["doc_store"] = json.load(f)
        print(f"Loaded {len(ml_models['doc_store'])} indexed document chunks.")
    except Exception as e:
        print(f"Warning: Could not load 'document_store.json': {e}")
        ml_models["doc_store"] = []

    yield

    ml_models.clear()
    print("Cleaned up model resources on shutdown.")


@router.get("/wordcloud")
def get_wordcloud_data():
    """Returns term-frequency JSON for the interactive word cloud."""
    topic_model = ml_models.get("topic_model")
    if not topic_model:
        raise HTTPException(status_code=503, detail="Topic model not initialized")

    topic_info = topic_model.get_topic_info()
    aggregate_frequencies = {}

    for topic_id in topic_info["Topic"].unique():
        if topic_id == -1:
            continue
        for word, weight in topic_model.get_topic(topic_id):
            term = word.title()
            score = round(float(weight) * 1000, 2)
            aggregate_frequencies[term] = aggregate_frequencies.get(term, 0.0) + score

    payload = [
        {"text": k, "value": round(v, 1)}
        for k, v in sorted(aggregate_frequencies.items(), key=lambda x: x[1], reverse=True)[:60]
    ]
    return {"status": "success", "total_words": len(payload), "data": payload}


@router.get("/drill-down")
def drill_down_documents(
    keyword: str = Query(..., description="The term clicked by the user in the word cloud"),
    limit: int = Query(5, ge=1, le=20),
):
    """Returns original document snippets matching a clicked term."""
    doc_store = ml_models.get("doc_store", [])
    keyword_clean = keyword.lower()
    matches = []

    for item in doc_store:
        if keyword_clean in item["text"].lower():
            matches.append({
                "chunk_id": item["chunk_id"],
                "content": item["text"],
            })
            if len(matches) >= limit:
                break

    return {
        "keyword": keyword,
        "matched_count": len(matches),
        "results": matches,
    }


@router.get("/export-cloud-image")
def export_cloud_image():
    """Returns a Base64-encoded PNG image for automated PDF report generation."""
    topic_model = ml_models.get("topic_model")
    if not topic_model:
        raise HTTPException(status_code=503, detail="Topic model not initialized")

    topic_info = topic_model.get_topic_info()
    aggregate_frequencies = {}

    for topic_id in topic_info["Topic"].unique():
        if topic_id == -1:
            continue
        for word, weight in topic_model.get_topic(topic_id):
            aggregate_frequencies[word.title()] = aggregate_frequencies.get(word.title(), 0.0) + (weight * 1000)

    wc = WordCloud(
        width=1000,
        height=500,
        background_color="#0b1329",
        colormap="copper",
        max_words=50,
        prefer_horizontal=0.85,
    ).generate_from_frequencies(aggregate_frequencies)

    buffer = io.BytesIO()
    wc.to_image().save(buffer, format="PNG")
    buffer.seek(0)
    img_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return {
        "format": "png",
        "encoding": "base64",
        "data": f"data:image/png;base64,{img_b64}",
    }


@router.get("/charts/{chart_name}")
def get_chart(chart_name: str):
    """Serves generated BERTopic Plotly interactive charts, if you export any."""
    chart_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{chart_name}.html")
    if not os.path.exists(chart_path):
        raise HTTPException(status_code=404, detail=f"Chart '{chart_name}.html' not found")
    return FileResponse(chart_path)
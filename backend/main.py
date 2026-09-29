from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from chat_routes import router as chat_router
from map_routes import router as map_router
from report_routes import router as report_router
from topic_routes import router as topic_router, topic_lifespan

app = FastAPI(
    title="National Coal Intelligence System (NCIS)",
    lifespan=topic_lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route modules
app.include_router(chat_router)
app.include_router(report_router)
app.include_router(topic_router)
app.include_router(map_router)


@app.get("/")
def health_check():
    return {
        "status": "online",
        "system": "National Coal Intelligence System (NCIS)",
    }
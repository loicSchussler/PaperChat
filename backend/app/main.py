from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import papers, chat, monitoring, conversations

app = FastAPI(
    title="PaperChat RAG API",
    description="API for analysis and querying of scientific papers",
    version="1.0.0"
)

# CORS configuration
# En développement, on autorise toutes les origins pour les tests (curl, Postman, etc.)
# En production, limiter à allow_origins=["http://localhost:4200", "https://votre-domaine.com"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Autorise toutes les origins en dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(papers.router)
app.include_router(chat.router)
app.include_router(conversations.router)
app.include_router(monitoring.router)

@app.get("/")
async def root():
    return {
        "message": "PaperChat RAG API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

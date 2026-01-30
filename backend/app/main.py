from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import papers, chat, monitoring

app = FastAPI(
    title="PaperChat RAG API",
    description="API pour l'analyse et l'interrogation d'articles scientifiques",
    version="1.0.0"
)

# Configuration CORS pour le frontend Angular
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Frontend Angular
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(papers.router)
app.include_router(chat.router)
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

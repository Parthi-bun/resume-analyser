import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.analyzer import router as analyzer_router

app = FastAPI(
    title="AI Resume Analyzer API",
    version="1.0.0",
    description="Analyze resumes against job descriptions using NLP and machine learning.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyzer_router)


@app.get("/")
def root():
    return {
        "message": "AI Resume Analyzer API is running.",
        "docs": "/docs",
    }

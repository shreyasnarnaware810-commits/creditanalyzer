import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.auth.router import router as auth_router
from app.routers.applications import router as applications_router
from app.routers.analysis import router as analysis_router
from app.routers.fairness import router as fairness_router
from app.routers.audit import router as audit_router
from app.routers.demo import router as demo_router, seed_demo_data

app = FastAPI(
    title="Credence AI — Alternative Credit Scoring & Income Synthesizer API",
    description="Explainable alternative credit scoring, genuine SHAP explanations, counterfactual what-if simulation, and loan officer decision trail.",
    version="1.0.0"
)

# Enable CORS for local Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    init_db()
    print("Credence AI Database initialized.")

# Include API Routers
app.include_router(auth_router)
app.include_router(applications_router)
app.include_router(analysis_router)
app.include_router(fairness_router)
app.include_router(audit_router)
app.include_router(demo_router)

@app.get("/")
def root():
    return {
        "name": "Credence AI API",
        "status": "online",
        "version": "1.0.0",
        "docs": "/docs"
    }

"""
DESHMRITTIKA / BHUMI-SYNC — Smart Cadastral Mapping & Land Record Verification Platform
FastAPI Application Entry Point
"""

import os
from pathlib import Path
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from backend.app.config import BASE_DIR, DATABASE_PATH
from backend.app.database import get_db
from backend.app.api import (
    auth,
    search,
    parcels,
    verification,
    due_diligence,
    mutations,
    documents,
    officer,
    admin_users,
    citizen,
    buyer,
)
from backend.app.database import get_db, get_db_connection, init_auth_tables

app = FastAPI(
    title="দেশমৃত্তিকা | DeshMrittika / Bhumi-Sync API",
    description=(
        "Smart Cadastral Mapping & Fraud-Resilient Land Record Verification Platform for Bangladesh. "
        "Built for the LandTech 2026 Innovation Hackathon (v1.2) addressing tracks P1 through P6."
    ),
    version="2.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Initialize Authentication Tables and Seed Accounts on startup
@app.on_event("startup")
def startup_event():
    try:
        conn = get_db_connection()
        init_auth_tables(conn)
        conn.close()
    except Exception as e:
        print(f"[Startup Warning - Auth Init]: {e}")

# Enable CORS for local development and browser frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API v1 Router Registration
API_PREFIX = "/api/v1"

app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(search.router, prefix=API_PREFIX)
app.include_router(parcels.router, prefix=API_PREFIX)
app.include_router(verification.router, prefix=API_PREFIX)
app.include_router(due_diligence.router, prefix=API_PREFIX)
app.include_router(mutations.router, prefix=API_PREFIX)
app.include_router(documents.router, prefix=API_PREFIX)
app.include_router(officer.router, prefix=API_PREFIX)
app.include_router(admin_users.router, prefix=API_PREFIX)
app.include_router(citizen.router, prefix=API_PREFIX)
app.include_router(buyer.router, prefix=API_PREFIX)


@app.get("/api/v1/health", tags=["System"])
def health_check():
    """System health check and database connectivity confirmation."""
    db_exists = os.path.exists(DATABASE_PATH)
    db_size_mb = round(os.path.getsize(DATABASE_PATH) / (1024 * 1024), 2) if db_exists else 0.0
    return {
        "status": "HEALTHY",
        "service": "deshmrittika-api",
        "version": "2.0.0",
        "database": {
            "path": DATABASE_PATH,
            "connected": db_exists,
            "size_mb": db_size_mb
        },
        "tracks_supported": ["P1", "P2", "P3", "P4", "P5", "P6"]
    }


# Static Frontend Hosting (if frontend directory exists)
FRONTEND_DIR = BASE_DIR / "frontend"
DATA_DIR = BASE_DIR / "data"

if DATA_DIR.exists():
    app.mount("/data", StaticFiles(directory=str(DATA_DIR)), name="data")
    app.mount("/static/data", StaticFiles(directory=str(DATA_DIR)), name="static_data")

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/", include_in_schema=False)
    def serve_index():
        index_file = FRONTEND_DIR / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return JSONResponse({"message": "দেশমৃত্তিকা API Server running. Visit /docs for OpenAPI specifications."})
else:
    @app.get("/", include_in_schema=False)
    def root():
        return {
            "platform": "দেশমৃত্তিকা | DeshMrittika / Bhumi-Sync",
            "tagline": "Your Land, Our Responsibility (আপনার জমি, আমাদের দায়িত্ব)",
            "api_documentation": "/docs",
            "health_check": "/api/v1/health",
            "version": "2.0.0"
        }

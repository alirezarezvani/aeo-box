"""
AEO Multi-Agent REST API

FastAPI server providing programmatic access to AEO workflows.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.models import HealthCheckResponse, ErrorResponse
from api.routes import campaigns, status

# Initialize FastAPI app
app = FastAPI(
    title="AEO Multi-Agent API",
    description="REST API for Answer Engine Optimization automation",
    version="1.5.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            detail=str(exc),
            timestamp=datetime.now()
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc),
            timestamp=datetime.now()
        ).dict()
    )


# Health check endpoint
@app.get("/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Returns API status, version, and agent information.
    """
    return HealthCheckResponse(
        status="healthy",
        version="1.5.0",
        timestamp=datetime.now(),
        agents_registered=6  # Will be dynamic when orchestrator is integrated
    )


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": "AEO Multi-Agent API",
        "version": "1.5.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "campaigns": "/api/campaigns",
            "status": "/api/status/{campaign_id}",
            "competitive": "/api/competitive",
            "monitoring": "/api/monitoring"
        }
    }


# Include routers
app.include_router(campaigns.router, prefix="/api", tags=["Campaigns"])
app.include_router(status.router, prefix="/api", tags=["Status"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

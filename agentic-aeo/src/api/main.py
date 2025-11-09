"""
AEO Multi-Agent REST API

FastAPI server providing programmatic access to AEO workflows.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import sys
import os
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.models import HealthCheckResponse, ErrorResponse
from api.routes import campaigns, status
from utils.logging import get_logger

# Initialize API logger
logger = get_logger("api")

# Initialize FastAPI app
app = FastAPI(
    title="AEO Multi-Agent API",
    description="""
## Answer Engine Optimization Multi-Agent System REST API

This API provides programmatic access to comprehensive AEO workflows powered by a
multi-agent system. Optimize your content for AI-powered answer engines like ChatGPT,
Claude, Perplexity, and Gemini.

### ⚠️ IMPORTANT: Data Persistence Limitation

**IN-MEMORY STORAGE ONLY**: Workflow status is stored in memory and will be LOST on API restart.
For production deployments requiring persistence, use the CampaignStore filesystem storage
(available in CLI mode) or migrate to a database (planned v1.6).

**Impact**: After restarting the API server, you cannot recover in-progress campaigns.
Complete campaigns are saved to `.aeo-agent-data/` but the API cannot query them.

### Features

* **AEO Campaigns**: Complete content optimization workflows (E-E-A-T audit, query research, optimization, tracking)
* **Competitive Analysis**: Analyze competitor content for AEO performance and identify opportunities
* **Citation Monitoring**: Track how often your content is cited by AI models
* **Multi-Agent Orchestration**: Coordinated execution by 6 specialized agents
* **Async Execution**: Non-blocking workflow execution with real-time status tracking

### Workflow Modes

* **Minimal**: Quick audit and basic recommendations (15-30 min)
* **Balanced**: Comprehensive optimization with tracking setup (45-90 min)
* **Comprehensive**: Full analysis, optimization, and extended monitoring (2-4 hours)

### Getting Started

1. Create a campaign: `POST /api/campaigns`
2. Check status: `GET /api/status/{campaign_id}`
3. Review results when completed

All workflows return immediately with a workflow ID. Use the status endpoint to track progress
and retrieve results.
    """,
    version="1.5.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "AEO Multi-Agent System",
        "url": "https://github.com/yourusername/aeo-suite",
    },
    license_info={
        "name": "MIT",
    },
    openapi_tags=[
        {
            "name": "Root",
            "description": "API root and information endpoints"
        },
        {
            "name": "Health",
            "description": "Health check and system status endpoints"
        },
        {
            "name": "Campaigns",
            "description": "AEO campaign workflows - create and manage optimization campaigns"
        },
        {
            "name": "Status",
            "description": "Workflow status tracking - check progress and retrieve results"
        }
    ]
)

# Configure CORS with explicit allowed origins (security fix)
# Read from environment variable or use secure localhost default
cors_origins_env = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8080")
allowed_origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Explicit origins only (no wildcard)
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],  # Explicit methods
    allow_headers=["Content-Type", "Authorization"],  # Explicit headers
)


# Exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with secure error logging"""
    error_id = str(uuid.uuid4())

    # Log full details internally
    logger.error(
        "HTTP exception occurred",
        error_id=error_id,
        status_code=exc.status_code,
        request_path=request.url.path,
        request_method=request.method,
        detail=exc.detail,
    )

    # Return safe error message to user (no internal details)
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail if exc.status_code < 500 else "Internal server error",
            detail=f"Error ID: {error_id}",
            timestamp=datetime.now()
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions with secure error logging"""
    error_id = str(uuid.uuid4())

    # Log full exception details internally (with stack trace)
    logger.error(
        "Unhandled exception occurred",
        exc_info=True,
        error_id=error_id,
        request_path=request.url.path,
        request_method=request.method,
        exception_type=type(exc).__name__,
    )

    # Return generic error message to user (NO internal details or stack traces)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail=f"An unexpected error occurred. Error ID: {error_id}",
            timestamp=datetime.now()
        ).dict()
    )


# Health check endpoint
@app.get(
    "/health",
    response_model=HealthCheckResponse,
    tags=["Health"],
    summary="Check API health status",
    response_description="API health status with system information"
)
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.

    Returns:
    - **status**: API health status (healthy/degraded/unhealthy)
    - **version**: Current API version
    - **timestamp**: Current server time
    - **agents_registered**: Number of registered agents in the orchestrator

    Use this endpoint to verify the API is running and check system status.
    """
    return HealthCheckResponse(
        status="healthy",
        version="1.5.0",
        timestamp=datetime.now(),
        agents_registered=6  # Will be dynamic when orchestrator is integrated
    )


@app.get(
    "/",
    tags=["Root"],
    summary="API root information",
    response_description="API metadata and available endpoints"
)
async def root():
    """
    API root endpoint with service information and available endpoints.

    Returns:
    - **message**: API name and welcome message
    - **version**: Current API version
    - **docs**: Interactive API documentation URL (Swagger UI)
    - **redoc**: Alternative documentation URL (ReDoc)
    - **health**: Health check endpoint URL
    - **endpoints**: Map of available API endpoints

    Use this to discover available endpoints and access API documentation.
    """
    return {
        "message": "AEO Multi-Agent API",
        "version": "1.5.0",
        "docs": "/docs",
        "redoc": "/redoc",
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

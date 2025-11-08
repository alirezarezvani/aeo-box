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
    description="""
## Answer Engine Optimization Multi-Agent System REST API

This API provides programmatic access to comprehensive AEO workflows powered by a
multi-agent system. Optimize your content for AI-powered answer engines like ChatGPT,
Claude, Perplexity, and Gemini.

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

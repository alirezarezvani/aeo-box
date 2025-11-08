"""
API Models - Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class CampaignMode(str, Enum):
    """Campaign execution modes"""
    minimal = "minimal"
    balanced = "balanced"
    comprehensive = "comprehensive"


class OptimizationLevel(str, Enum):
    """Content optimization levels"""
    conservative = "conservative"
    balanced = "balanced"
    aggressive = "aggressive"


class WorkflowStatus(str, Enum):
    """Workflow execution status"""
    pending = "pending"
    running = "running"
    completed = "completed"
    partial = "partial"
    failed = "failed"


# Campaign Workflow Models

class CampaignCreateRequest(BaseModel):
    """Request to create AEO campaign"""
    url: HttpUrl = Field(..., description="URL of content to optimize")
    mode: CampaignMode = Field(CampaignMode.balanced, description="Campaign mode")
    industry: Optional[str] = Field(None, description="Industry vertical")
    optimization_level: OptimizationLevel = Field(
        OptimizationLevel.balanced,
        description="Content optimization level"
    )
    tracking_duration_days: int = Field(
        30,
        ge=1,
        le=365,
        description="Citation tracking duration"
    )
    queries: Optional[List[str]] = Field(None, description="Target queries")

    class Config:
        schema_extra = {
            "example": {
                "url": "https://example.com/article",
                "mode": "balanced",
                "industry": "SaaS",
                "optimization_level": "balanced",
                "tracking_duration_days": 30,
                "queries": ["AEO best practices", "content optimization"]
            }
        }


class CampaignResponse(BaseModel):
    """Response after creating campaign"""
    campaign_id: str = Field(..., description="Unique campaign ID")
    status: WorkflowStatus = Field(..., description="Current workflow status")
    created_at: datetime = Field(..., description="Creation timestamp")
    message: str = Field(..., description="Status message")

    class Config:
        schema_extra = {
            "example": {
                "campaign_id": "campaign_20250108_001",
                "status": "running",
                "created_at": "2025-01-08T10:30:00Z",
                "message": "Campaign workflow started successfully"
            }
        }


class CampaignStatusResponse(BaseModel):
    """Campaign status and results"""
    campaign_id: str = Field(..., description="Unique campaign identifier")
    status: WorkflowStatus = Field(..., description="Current workflow status")
    created_at: datetime = Field(..., description="Campaign creation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp if finished")
    progress: Dict[str, Any] = Field(
        default_factory=dict,
        description="Progress tracking with task completion percentage"
    )
    results: Optional[Dict[str, Any]] = Field(None, description="Workflow results if completed")
    errors: List[str] = Field(default_factory=list, description="Error messages if any")

    class Config:
        schema_extra = {
            "example": {
                "campaign_id": "campaign_20250108_001",
                "status": "completed",
                "created_at": "2025-01-08T10:30:00Z",
                "completed_at": "2025-01-08T12:15:00Z",
                "progress": {
                    "total_tasks": 8,
                    "completed_tasks": 8,
                    "completion_percentage": 100,
                    "tasks": {
                        "audit": "completed",
                        "research": "completed",
                        "optimize": "completed",
                        "tracking": "completed",
                        "report": "completed"
                    }
                },
                "results": {
                    "workflow_state": {
                        "status": "completed",
                        "total_tasks": 8,
                        "completed_tasks": 8
                    },
                    "task_results": [
                        {
                            "task_type": "audit",
                            "status": "completed",
                            "summary": "E-E-A-T audit completed with 7/10 score"
                        }
                    ]
                },
                "errors": []
            }
        }


# Competitive Analysis Models

class CompetitiveAnalysisRequest(BaseModel):
    """Request for competitive AEO analysis"""
    topic: str = Field(..., min_length=3, description="Topic or industry to analyze")
    competitor_urls: List[HttpUrl] = Field(
        ...,
        min_items=1,
        max_items=10,
        description="Competitor URLs to analyze"
    )
    region: str = Field("US", description="Geographic region")
    include_citations: bool = Field(True, description="Include citation analysis")

    class Config:
        schema_extra = {
            "example": {
                "topic": "project management",
                "competitor_urls": [
                    "https://competitor1.com",
                    "https://competitor2.com"
                ],
                "region": "US",
                "include_citations": True
            }
        }


class CompetitiveAnalysisResponse(BaseModel):
    """Response after creating competitive analysis"""
    analysis_id: str = Field(..., description="Unique analysis identifier")
    status: WorkflowStatus = Field(..., description="Current analysis status")
    created_at: datetime = Field(..., description="Analysis creation timestamp")
    message: str = Field(..., description="Status message")

    class Config:
        schema_extra = {
            "example": {
                "analysis_id": "analysis_20250108_002",
                "status": "running",
                "created_at": "2025-01-08T11:00:00Z",
                "message": "Competitive analysis started. Check status at /api/status/{analysis_id}"
            }
        }


# Monitoring Models

class MonitoringSetupRequest(BaseModel):
    """Request to setup citation monitoring"""
    url: HttpUrl = Field(..., description="URL to monitor")
    duration_days: int = Field(
        90,
        ge=1,
        le=365,
        description="Monitoring duration in days"
    )
    queries: Optional[List[str]] = Field(None, description="Specific queries to track")
    alert_on_changes: bool = Field(True, description="Send alerts on changes")
    weekly_reports: bool = Field(True, description="Generate weekly reports")

    class Config:
        schema_extra = {
            "example": {
                "url": "https://example.com/article",
                "duration_days": 90,
                "queries": ["topic 1", "topic 2"],
                "alert_on_changes": True,
                "weekly_reports": True
            }
        }


class MonitoringSetupResponse(BaseModel):
    """Response after setting up monitoring"""
    monitor_id: str = Field(..., description="Unique monitoring identifier")
    status: WorkflowStatus = Field(..., description="Current monitoring status")
    created_at: datetime = Field(..., description="Monitoring setup timestamp")
    message: str = Field(..., description="Status message")

    class Config:
        schema_extra = {
            "example": {
                "monitor_id": "monitor_20250108_003",
                "status": "running",
                "created_at": "2025-01-08T11:30:00Z",
                "message": "Monitoring setup started. Check status at /api/status/{monitor_id}"
            }
        }


# Health Check Models

class HealthCheckResponse(BaseModel):
    """API health check response"""
    status: str = Field("healthy", description="API health status (healthy/degraded/unhealthy)")
    version: str = Field("1.5.0", description="API version")
    timestamp: datetime = Field(default_factory=datetime.now, description="Current server timestamp")
    agents_registered: int = Field(0, description="Number of registered agents in orchestrator")

    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.5.0",
                "timestamp": "2025-01-08T12:00:00Z",
                "agents_registered": 6
            }
        }


# Error Models

class ErrorResponse(BaseModel):
    """Error response"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        schema_extra = {
            "example": {
                "error": "Invalid request",
                "detail": "URL must start with http:// or https://",
                "timestamp": "2025-01-08T10:30:00Z"
            }
        }

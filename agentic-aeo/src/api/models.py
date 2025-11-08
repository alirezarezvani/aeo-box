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
    campaign_id: str
    status: WorkflowStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    progress: Dict[str, Any] = Field(default_factory=dict)
    results: Optional[Dict[str, Any]] = None
    errors: List[str] = Field(default_factory=list)


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
    analysis_id: str
    status: WorkflowStatus
    created_at: datetime
    message: str


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
    monitor_id: str
    status: WorkflowStatus
    created_at: datetime
    message: str


# Health Check Models

class HealthCheckResponse(BaseModel):
    """API health check response"""
    status: str = Field("healthy", description="API health status")
    version: str = Field("1.5.0", description="API version")
    timestamp: datetime = Field(default_factory=datetime.now)
    agents_registered: int = Field(0, description="Number of registered agents")


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

"""
Campaign Endpoints

REST API endpoints for AEO campaign workflows.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from datetime import datetime
import asyncio
import sys
from pathlib import Path
from typing import Dict

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from api.models import (
    CampaignCreateRequest,
    CampaignResponse,
    CompetitiveAnalysisRequest,
    CompetitiveAnalysisResponse,
    MonitoringSetupRequest,
    MonitoringSetupResponse,
    WorkflowStatus
)
from agents.orchestrator_agent import OrchestratorAgent
from agents.auditor_agent import AuditorAgent
from agents.optimizer_agent import OptimizerAgent
from agents.citation_tracker_agent import CitationTrackerAgent
from agents.researcher_agent import ResearcherAgent
from agents.reporter_agent import ReporterAgent
from agents.learning_agent import LearningAgent
from workflows.campaign_workflow import CampaignWorkflow
from workflows.competitive_workflow import CompetitiveWorkflow
from workflows.monitoring_workflow import MonitoringWorkflow
from communication.protocol import AgentType

router = APIRouter()

# In-memory storage for campaign status (would use database in production)
campaigns_store: Dict[str, Dict] = {}


def get_orchestrator():
    """Initialize orchestrator with all agents"""
    orchestrator = OrchestratorAgent()
    orchestrator.register_agent(AgentType.AUDITOR, AuditorAgent())
    orchestrator.register_agent(AgentType.OPTIMIZER, OptimizerAgent())
    orchestrator.register_agent(AgentType.CITATION_TRACKER, CitationTrackerAgent())
    orchestrator.register_agent(AgentType.RESEARCHER, ResearcherAgent())
    orchestrator.register_agent(AgentType.REPORTER, ReporterAgent())
    orchestrator.register_agent(AgentType.LEARNING, LearningAgent())
    return orchestrator


async def run_campaign_workflow(campaign_id: str, request: CampaignCreateRequest):
    """Execute campaign workflow in background"""
    try:
        # Update status to running
        campaigns_store[campaign_id]["status"] = WorkflowStatus.running

        # Execute workflow
        orchestrator = get_orchestrator()
        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-campaign",
            workflow_params={
                "url": str(request.url),
                "mode": request.mode.value,
                "industry": request.industry,
                "optimization_level": request.optimization_level.value,
                "tracking_duration_days": request.tracking_duration_days,
                "queries": request.queries
            }
        )

        # Update campaign status
        campaigns_store[campaign_id]["status"] = WorkflowStatus(
            manifest.workflow_state.status.value
        )
        campaigns_store[campaign_id]["completed_at"] = datetime.now()
        campaigns_store[campaign_id]["results"] = {
            "workflow_state": manifest.workflow_state.dict(),
            "task_results": [r.dict() for r in manifest.task_results],
            "total_tasks": manifest.workflow_state.total_tasks,
            "completed_tasks": manifest.workflow_state.completed_tasks
        }

    except Exception as e:
        campaigns_store[campaign_id]["status"] = WorkflowStatus.failed
        campaigns_store[campaign_id]["errors"] = [str(e)]
        campaigns_store[campaign_id]["completed_at"] = datetime.now()


@router.post("/campaigns", response_model=CampaignResponse, status_code=202)
async def create_campaign(
    request: CampaignCreateRequest,
    background_tasks: BackgroundTasks
):
    """
    Create and execute AEO campaign workflow.

    Launches a complete optimization workflow including:
    - Content audit (E-E-A-T analysis)
    - Query research
    - Content optimization
    - Citation tracking setup
    - Report generation

    Returns immediately with campaign ID. Check status at /api/status/{campaign_id}
    """
    # Generate campaign ID
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    campaign_id = f"campaign_{timestamp}"

    # Validate input
    workflow = CampaignWorkflow()
    is_valid, error = workflow.validate_input(str(request.url), request.mode.value)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)

    # Store campaign info
    campaigns_store[campaign_id] = {
        "campaign_id": campaign_id,
        "status": WorkflowStatus.pending,
        "created_at": datetime.now(),
        "completed_at": None,
        "request": request.dict(),
        "results": None,
        "errors": []
    }

    # Start workflow in background
    background_tasks.add_task(run_campaign_workflow, campaign_id, request)

    return CampaignResponse(
        campaign_id=campaign_id,
        status=WorkflowStatus.running,
        created_at=datetime.now(),
        message="Campaign workflow started successfully. Check status at /api/status/{campaign_id}"
    )


async def run_competitive_workflow(analysis_id: str, request: CompetitiveAnalysisRequest):
    """Execute competitive analysis workflow in background"""
    try:
        campaigns_store[analysis_id]["status"] = WorkflowStatus.running

        orchestrator = get_orchestrator()
        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-compete",
            workflow_params={
                "topic": request.topic,
                "competitor_urls": [str(url) for url in request.competitor_urls],
                "region": request.region,
                "include_citations": request.include_citations
            }
        )

        campaigns_store[analysis_id]["status"] = WorkflowStatus(
            manifest.workflow_state.status.value
        )
        campaigns_store[analysis_id]["completed_at"] = datetime.now()
        campaigns_store[analysis_id]["results"] = {
            "workflow_state": manifest.workflow_state.dict(),
            "task_results": [r.dict() for r in manifest.task_results]
        }

    except Exception as e:
        campaigns_store[analysis_id]["status"] = WorkflowStatus.failed
        campaigns_store[analysis_id]["errors"] = [str(e)]
        campaigns_store[analysis_id]["completed_at"] = datetime.now()


@router.post("/competitive", response_model=CompetitiveAnalysisResponse, status_code=202)
async def create_competitive_analysis(
    request: CompetitiveAnalysisRequest,
    background_tasks: BackgroundTasks
):
    """
    Create competitive AEO analysis.

    Analyzes competitor content for AEO performance and identifies opportunities.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    analysis_id = f"analysis_{timestamp}"

    # Validate input
    workflow = CompetitiveWorkflow()
    is_valid, error = workflow.validate_input(
        request.topic,
        [str(url) for url in request.competitor_urls]
    )
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)

    campaigns_store[analysis_id] = {
        "analysis_id": analysis_id,
        "status": WorkflowStatus.pending,
        "created_at": datetime.now(),
        "completed_at": None,
        "request": request.dict(),
        "results": None,
        "errors": []
    }

    background_tasks.add_task(run_competitive_workflow, analysis_id, request)

    return CompetitiveAnalysisResponse(
        analysis_id=analysis_id,
        status=WorkflowStatus.running,
        created_at=datetime.now(),
        message="Competitive analysis started. Check status at /api/status/{analysis_id}"
    )


async def run_monitoring_workflow(monitor_id: str, request: MonitoringSetupRequest):
    """Execute monitoring setup workflow in background"""
    try:
        campaigns_store[monitor_id]["status"] = WorkflowStatus.running

        orchestrator = get_orchestrator()
        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-monitor",
            workflow_params={
                "url": str(request.url),
                "duration_days": request.duration_days,
                "queries": request.queries,
                "alert_on_changes": request.alert_on_changes,
                "weekly_reports": request.weekly_reports
            }
        )

        campaigns_store[monitor_id]["status"] = WorkflowStatus(
            manifest.workflow_state.status.value
        )
        campaigns_store[monitor_id]["completed_at"] = datetime.now()
        campaigns_store[monitor_id]["results"] = {
            "workflow_state": manifest.workflow_state.dict(),
            "task_results": [r.dict() for r in manifest.task_results]
        }

    except Exception as e:
        campaigns_store[monitor_id]["status"] = WorkflowStatus.failed
        campaigns_store[monitor_id]["errors"] = [str(e)]
        campaigns_store[monitor_id]["completed_at"] = datetime.now()


@router.post("/monitoring", response_model=MonitoringSetupResponse, status_code=202)
async def setup_monitoring(
    request: MonitoringSetupRequest,
    background_tasks: BackgroundTasks
):
    """
    Setup citation monitoring.

    Configures continuous monitoring to track how often content is cited by AI models.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    monitor_id = f"monitor_{timestamp}"

    # Validate input
    workflow = MonitoringWorkflow()
    is_valid, error = workflow.validate_input(str(request.url), request.duration_days)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)

    campaigns_store[monitor_id] = {
        "monitor_id": monitor_id,
        "status": WorkflowStatus.pending,
        "created_at": datetime.now(),
        "completed_at": None,
        "request": request.dict(),
        "results": None,
        "errors": []
    }

    background_tasks.add_task(run_monitoring_workflow, monitor_id, request)

    return MonitoringSetupResponse(
        monitor_id=monitor_id,
        status=WorkflowStatus.running,
        created_at=datetime.now(),
        message="Monitoring setup started. Check status at /api/status/{monitor_id}"
    )

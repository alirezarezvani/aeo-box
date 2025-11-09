"""
Status Endpoints

REST API endpoints for checking workflow status.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from api.models import CampaignStatusResponse
from api.routes.campaigns import campaigns_store

router = APIRouter()


@router.get("/status/{workflow_id}", response_model=CampaignStatusResponse)
async def get_workflow_status(workflow_id: str):
    """
    Get workflow status and results.

    Retrieves the current status of any workflow (campaign, competitive analysis,
    or monitoring setup).

    ⚠️ **DATA LOSS WARNING**: Workflow status is stored IN-MEMORY ONLY.
    All campaign data is LOST on API restart. For production use with persistence,
    use the CampaignStore filesystem storage or migrate to a database (planned v1.6).

    **Parameters:**
    - workflow_id: Campaign ID, analysis ID, or monitor ID

    **Returns:**
    - status: Current workflow status (pending, running, completed, partial, failed)
    - progress: Task completion progress
    - results: Final results (if completed)
    - errors: Error messages (if failed)
    """
    if workflow_id not in campaigns_store:
        raise HTTPException(
            status_code=404,
            detail=f"Workflow {workflow_id} not found"
        )

    workflow_data = campaigns_store[workflow_id]

    # Calculate progress
    results = workflow_data.get("results")
    progress = {}

    if results and isinstance(results, dict):
        workflow_state = results.get("workflow_state", {})
        total_tasks = workflow_state.get("total_tasks", 0)
        completed_tasks = workflow_state.get("completed_tasks", 0)

        if total_tasks > 0:
            progress = {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "completion_percentage": int((completed_tasks / total_tasks) * 100),
                "tasks": workflow_state.get("task_status", {})
            }

    return CampaignStatusResponse(
        campaign_id=workflow_id,
        status=workflow_data["status"],
        created_at=workflow_data["created_at"],
        completed_at=workflow_data.get("completed_at"),
        progress=progress,
        results=workflow_data.get("results"),
        errors=workflow_data.get("errors", [])
    )


@router.get("/campaigns", response_model=list)
async def list_campaigns():
    """
    List all campaigns.

    Returns a list of all campaign IDs with their current status.
    """
    campaigns = []
    for workflow_id, data in campaigns_store.items():
        campaigns.append({
            "id": workflow_id,
            "status": data["status"].value,
            "created_at": data["created_at"],
            "completed_at": data.get("completed_at"),
            "type": "campaign" if workflow_id.startswith("campaign_")
                    else "analysis" if workflow_id.startswith("analysis_")
                    else "monitor"
        })

    return sorted(campaigns, key=lambda x: x["created_at"], reverse=True)


@router.delete("/campaigns/{workflow_id}")
async def delete_campaign(workflow_id: str):
    """
    Delete a campaign.

    Removes campaign data from storage.
    """
    if workflow_id not in campaigns_store:
        raise HTTPException(
            status_code=404,
            detail=f"Workflow {workflow_id} not found"
        )

    del campaigns_store[workflow_id]

    return {
        "message": f"Workflow {workflow_id} deleted successfully",
        "timestamp": datetime.now()
    }

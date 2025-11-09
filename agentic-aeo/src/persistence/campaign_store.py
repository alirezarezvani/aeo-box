"""
Campaign Data Store

Manages persistent storage of campaign data, tasks, and results using
campaign-based directory organization with atomic file operations.
"""

import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

from ..communication.protocol import (
    CampaignManifest,
    TaskMessage,
    TaskResult,
    WorkflowState,
)
from ..utils.config import get_config
from ..utils.logging import get_logger
from .file_ops import write_json, read_json, append_to_jsonl, read_jsonl


class CampaignStore:
    """
    Persistent storage manager for AEO campaigns.

    Provides:
    - Campaign-based directory organization
    - Atomic file operations with locking
    - Campaign manifest management
    - Task result tracking
    - Campaign listing and search

    Directory Structure:
        .aeo-agent-data/
        └── campaigns/
            └── camp_20250108_123456_abc123/
                ├── manifest.json         # Campaign manifest
                ├── tasks.jsonl          # Task execution log
                ├── results/             # Individual task results
                │   ├── task_1.json
                │   └── task_2.json
                └── outputs/             # Generated outputs (reports, etc.)
                    └── report.md

    Example:
        >>> store = CampaignStore()
        >>> campaign_id = store.create_campaign("aeo-campaign", {...})
        >>> store.save_task_result(campaign_id, result)
        >>> manifest = store.load_campaign(campaign_id)
    """

    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize campaign store.

        Args:
            data_dir: Optional data directory override (uses config default if None)
        """
        config = get_config()
        self.data_dir = data_dir or config.data.data_dir
        self.campaigns_dir = self.data_dir / "campaigns"
        self.logger = get_logger("campaign_store")

        # Ensure directories exist
        self.campaigns_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info(f"Initialized campaign store at {self.data_dir}")

    def generate_campaign_id(self, workflow_name: str) -> str:
        """
        Generate unique campaign ID with collision-resistant UUID.

        Format: {workflow}_{timestamp}_{uuid}
        Example: campaign_20250108_123456_a1b2c3d4e5f6

        Uses:
        - Timestamp with microsecond precision (no collision within same second)
        - 12 characters from UUID (collision probability: 1 in 16^12 = ~281 trillion)

        Args:
            workflow_name: Name of workflow (aeo-campaign, aeo-compete, etc.)

        Returns:
            Unique campaign identifier
        """
        # Use microseconds for higher precision (no collision within same second)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S%f")[:17]  # YYYYmmdd_HHMMSS_mmm (milliseconds)

        # Use 12 characters from UUID for collision resistance
        # Collision probability: 1 in 16^12 = ~281 trillion
        uuid_part = str(uuid.uuid4()).replace('-', '')[:12]

        return f"{workflow_name}_{timestamp}_{uuid_part}"

    def create_campaign(
        self,
        workflow_name: str,
        parameters: Dict[str, Any],
        total_tasks: int = 0,
    ) -> str:
        """
        Create new campaign with manifest.

        Args:
            workflow_name: Workflow type (aeo-campaign, aeo-compete, etc.)
            parameters: Campaign input parameters
            total_tasks: Total number of tasks in workflow

        Returns:
            Campaign ID

        Example:
            >>> store = CampaignStore()
            >>> campaign_id = store.create_campaign(
            ...     "aeo-campaign",
            ...     {"url": "https://example.com", "queries": ["query1"]},
            ...     total_tasks=5
            ... )
        """
        # Generate campaign ID
        campaign_id = self.generate_campaign_id(workflow_name)

        # Create campaign directory structure
        campaign_dir = self.campaigns_dir / campaign_id
        campaign_dir.mkdir(parents=True, exist_ok=True)
        (campaign_dir / "results").mkdir(exist_ok=True)
        (campaign_dir / "outputs").mkdir(exist_ok=True)

        # Create workflow state
        workflow_state = WorkflowState(
            workflow_name=workflow_name,
            campaign_id=campaign_id,
            total_tasks=total_tasks,
            status="pending",
        )

        # Create campaign manifest
        manifest = CampaignManifest(
            campaign_id=campaign_id,
            workflow_name=workflow_name,
            parameters=parameters,
            workflow_state=workflow_state,
        )

        # Save manifest
        manifest_path = campaign_dir / "manifest.json"
        write_json(manifest_path, manifest.to_json_file())

        self.logger.info(
            "Created campaign",
            campaign_id=campaign_id,
            workflow=workflow_name,
            total_tasks=total_tasks,
        )

        return campaign_id

    def load_campaign(self, campaign_id: str) -> CampaignManifest:
        """
        Load campaign manifest.

        Args:
            campaign_id: Campaign identifier

        Returns:
            CampaignManifest object

        Raises:
            FileNotFoundError: If campaign doesn't exist

        Example:
            >>> store = CampaignStore()
            >>> manifest = store.load_campaign("campaign_20250108_123456_abc123")
            >>> print(manifest.workflow_state.progress_percentage)
        """
        campaign_dir = self.campaigns_dir / campaign_id

        if not campaign_dir.exists():
            raise FileNotFoundError(f"Campaign not found: {campaign_id}")

        manifest_path = campaign_dir / "manifest.json"
        data = read_json(manifest_path)

        return CampaignManifest.from_json_file(data)

    def save_campaign(self, manifest: CampaignManifest) -> None:
        """
        Save campaign manifest (update existing).

        Args:
            manifest: Updated campaign manifest

        Example:
            >>> manifest = store.load_campaign(campaign_id)
            >>> manifest.workflow_state.completed_tasks += 1
            >>> store.save_campaign(manifest)
        """
        campaign_dir = self.campaigns_dir / manifest.campaign_id
        manifest_path = campaign_dir / "manifest.json"

        # Update timestamp
        manifest.updated_at = datetime.now(timezone.utc)

        # Save
        write_json(manifest_path, manifest.to_json_file())

        self.logger.debug(
            "Saved campaign manifest",
            campaign_id=manifest.campaign_id,
        )

    def save_task_result(
        self,
        campaign_id: str,
        result: TaskResult,
        update_manifest: bool = True,
    ) -> None:
        """
        Save task result to campaign.

        Args:
            campaign_id: Campaign identifier
            result: Task result to save
            update_manifest: Whether to update campaign manifest

        Example:
            >>> result = TaskResult(
            ...     task_id="task_123",
            ...     status=TaskStatus.COMPLETED,
            ...     output_data={...}
            ... )
            >>> store.save_task_result(campaign_id, result)
        """
        campaign_dir = self.campaigns_dir / campaign_id

        # Save individual result file
        result_path = campaign_dir / "results" / f"{result.task_id}.json"
        write_json(result_path, result.model_dump())

        # Append to task log
        tasks_log_path = campaign_dir / "tasks.jsonl"
        append_to_jsonl(tasks_log_path, {
            "task_id": result.task_id,
            "status": result.status.value,
            "agent_type": result.agent_type.value,
            "execution_time": result.execution_time_seconds,
            "completed_at": result.completed_at.isoformat(),
        })

        # Update manifest if requested
        if update_manifest:
            manifest = self.load_campaign(campaign_id)
            manifest.results[result.task_id] = result

            # Update workflow state
            if result.status.value == "completed":
                manifest.workflow_state.completed_tasks += 1
            elif result.status.value == "failed":
                manifest.workflow_state.failed_tasks += 1

            # Update status
            if manifest.workflow_state.is_complete:
                manifest.workflow_state.status = "completed"
                manifest.workflow_state.completed_at = datetime.now(timezone.utc)

            self.save_campaign(manifest)

        self.logger.info(
            "Saved task result",
            campaign_id=campaign_id,
            task_id=result.task_id,
            status=result.status.value,
        )

    def load_task_result(
        self,
        campaign_id: str,
        task_id: str,
    ) -> Optional[TaskResult]:
        """
        Load specific task result.

        Args:
            campaign_id: Campaign identifier
            task_id: Task identifier

        Returns:
            TaskResult if found, None otherwise

        Example:
            >>> result = store.load_task_result(campaign_id, "task_123")
            >>> if result:
            ...     print(result.output_data)
        """
        result_path = self.campaigns_dir / campaign_id / "results" / f"{task_id}.json"

        if not result_path.exists():
            return None

        data = read_json(result_path)
        return TaskResult(**data)

    def _validate_filename(self, filename: str) -> str:
        """
        Validate filename to prevent path traversal attacks.

        Args:
            filename: Filename to validate

        Returns:
            Safe filename (basename only)

        Raises:
            ValueError: If filename contains path traversal sequences or invalid characters

        Security:
            Prevents directory traversal attacks like "../../../etc/passwd"
        """
        import os

        # Get basename only (removes any directory components)
        safe_filename = os.path.basename(filename)

        # Check for empty filename after cleaning
        if not safe_filename or safe_filename in ('.', '..'):
            raise ValueError(f"Invalid filename: '{filename}'")

        # Check for path traversal attempts
        if '..' in filename or '/' in filename or '\\' in filename:
            raise ValueError(f"Filename contains invalid path characters: '{filename}'")

        # Check for null bytes (security)
        if '\x00' in safe_filename:
            raise ValueError(f"Filename contains null bytes: '{filename}'")

        return safe_filename

    def save_output_file(
        self,
        campaign_id: str,
        filename: str,
        content: str,
    ) -> Path:
        """
        Save output file (report, markdown, etc.) to campaign.

        Args:
            campaign_id: Campaign identifier
            filename: Output filename (will be validated for security)
            content: File content

        Returns:
            Path to saved file

        Raises:
            ValueError: If filename contains path traversal sequences

        Example:
            >>> path = store.save_output_file(
            ...     campaign_id,
            ...     "report.md",
            ...     "# AEO Campaign Report\\n\\n..."
            ... )

        Security:
            Filename is validated to prevent directory traversal attacks.
            Only safe basenames are allowed (no "../" or absolute paths).
        """
        # Validate filename for security (prevent path traversal)
        safe_filename = self._validate_filename(filename)

        output_path = self.campaigns_dir / campaign_id / "outputs" / safe_filename

        # Write content
        output_path.write_text(content, encoding='utf-8')

        self.logger.info(
            "Saved output file",
            campaign_id=campaign_id,
            filename=filename,
            size_bytes=len(content),
        )

        return output_path

    def list_campaigns(
        self,
        workflow_name: Optional[str] = None,
        limit: int = 100,
    ) -> List[CampaignManifest]:
        """
        List campaigns, optionally filtered by workflow.

        Args:
            workflow_name: Optional workflow filter
            limit: Maximum number to return

        Returns:
            List of campaign manifests, sorted by creation time (newest first)

        Example:
            >>> campaigns = store.list_campaigns(workflow_name="aeo-campaign")
            >>> for campaign in campaigns:
            ...     print(f"{campaign.campaign_id}: {campaign.workflow_state.status}")
        """
        campaigns = []

        # Iterate through campaign directories
        for campaign_dir in sorted(
            self.campaigns_dir.iterdir(),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        ):
            if not campaign_dir.is_dir():
                continue

            # Load manifest
            try:
                manifest = self.load_campaign(campaign_dir.name)

                # Filter by workflow if specified
                if workflow_name and manifest.workflow_name != workflow_name:
                    continue

                campaigns.append(manifest)

                # Check limit
                if len(campaigns) >= limit:
                    break

            except Exception as e:
                self.logger.warning(
                    f"Failed to load campaign {campaign_dir.name}: {e}"
                )
                continue

        return campaigns

    def get_campaign_stats(self, campaign_id: str) -> Dict[str, Any]:
        """
        Get campaign statistics.

        Args:
            campaign_id: Campaign identifier

        Returns:
            Dictionary with campaign statistics

        Example:
            >>> stats = store.get_campaign_stats(campaign_id)
            >>> print(f"Completed: {stats['completed_tasks']}/{stats['total_tasks']}")
        """
        manifest = self.load_campaign(campaign_id)
        state = manifest.workflow_state

        return {
            "campaign_id": campaign_id,
            "workflow_name": manifest.workflow_name,
            "status": state.status,
            "total_tasks": state.total_tasks,
            "completed_tasks": state.completed_tasks,
            "failed_tasks": state.failed_tasks,
            "progress_percentage": state.progress_percentage,
            "is_complete": state.is_complete,
            "created_at": manifest.created_at.isoformat(),
            "updated_at": manifest.updated_at.isoformat(),
            "duration_seconds": (
                (manifest.updated_at - manifest.created_at).total_seconds()
            ),
        }

    def delete_campaign(self, campaign_id: str) -> None:
        """
        Delete campaign and all associated data.

        Args:
            campaign_id: Campaign to delete

        Example:
            >>> store.delete_campaign("old_campaign_123")
        """
        import shutil

        campaign_dir = self.campaigns_dir / campaign_id

        if campaign_dir.exists():
            shutil.rmtree(campaign_dir)
            self.logger.info(f"Deleted campaign", campaign_id=campaign_id)
        else:
            self.logger.warning(f"Campaign not found for deletion", campaign_id=campaign_id)


# Singleton instance for convenience
_store: Optional[CampaignStore] = None


def get_campaign_store() -> CampaignStore:
    """
    Get global campaign store instance (singleton).

    Returns:
        CampaignStore instance

    Example:
        >>> from agentic_aeo.persistence import get_campaign_store
        >>> store = get_campaign_store()
        >>> campaigns = store.list_campaigns()
    """
    global _store
    if _store is None:
        _store = CampaignStore()
    return _store


# Example usage
if __name__ == "__main__":
    # Create test campaign
    store = CampaignStore(data_dir=Path("/tmp/aeo_test_data"))

    campaign_id = store.create_campaign(
        "aeo-campaign",
        {"url": "https://example.com", "queries": ["test query"]},
        total_tasks=3,
    )

    print(f"Created campaign: {campaign_id}")

    # Save some task results
    from ..communication.protocol import TaskResult, TaskStatus, AgentType

    for i in range(3):
        result = TaskResult(
            task_id=f"task_{i}",
            status=TaskStatus.COMPLETED,
            agent_type=AgentType.AUDITOR,
            output_data={"score": 85 + i, "task_number": i},
        )
        store.save_task_result(campaign_id, result)

    # Save output file
    store.save_output_file(
        campaign_id,
        "report.md",
        "# Test Report\n\nCampaign completed successfully!"
    )

    # Get stats
    stats = store.get_campaign_stats(campaign_id)
    print(f"\nCampaign stats: {stats}")

    # List campaigns
    campaigns = store.list_campaigns()
    print(f"\nTotal campaigns: {len(campaigns)}")

    # Cleanup
    import shutil
    shutil.rmtree("/tmp/aeo_test_data")
    print("\nTest complete!")

"""
Workflow Store

Manages workflow definitions and templates for the multi-agent orchestration system.
Provides storage and retrieval of reusable workflow configurations.
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

from ..communication.protocol import WorkflowState
from ..utils.config import get_config
from ..utils.logging import get_logger
from .file_ops import write_json, read_json


class WorkflowStore:
    """
    Persistent storage manager for workflow templates and configurations.

    Provides:
    - Workflow template storage
    - Active workflow state tracking
    - Workflow history
    - Template versioning

    Directory Structure:
        .aeo-agent-data/
        └── workflows/
            ├── templates/
            │   ├── aeo-campaign.json
            │   ├── aeo-compete.json
            │   └── aeo-monitor.json
            └── active/
                └── workflow_123_state.json

    Example:
        >>> store = WorkflowStore()
        >>> template = store.load_template("aeo-campaign")
        >>> store.save_workflow_state(workflow_id, state)
    """

    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize workflow store.

        Args:
            data_dir: Optional data directory override (uses config default if None)
        """
        config = get_config()
        self.data_dir = data_dir or config.data.data_dir
        self.workflows_dir = self.data_dir / "workflows"
        self.templates_dir = self.workflows_dir / "templates"
        self.active_dir = self.workflows_dir / "active"
        self.logger = get_logger("workflow_store")

        # Ensure directories exist
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.active_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info(f"Initialized workflow store at {self.workflows_dir}")

    def save_template(
        self,
        workflow_name: str,
        template: Dict[str, Any],
        version: str = "1.0.0",
    ) -> None:
        """
        Save or update workflow template.

        Args:
            workflow_name: Name of workflow (aeo-campaign, aeo-compete, etc.)
            template: Workflow template configuration
            version: Template version string

        Example:
            >>> template = {
            ...     "name": "aeo-campaign",
            ...     "steps": [
            ...         {"agent": "auditor", "depends_on": []},
            ...         {"agent": "optimizer", "depends_on": ["auditor"]},
            ...     ],
            ...     "parameters": {...}
            ... }
            >>> store.save_template("aeo-campaign", template)
        """
        template_file = self.templates_dir / f"{workflow_name}.json"

        template_data = {
            "name": workflow_name,
            "version": version,
            "template": template,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        write_json(template_file, template_data)
        self.logger.info(f"Saved workflow template: {workflow_name} v{version}")

    def load_template(self, workflow_name: str) -> Dict[str, Any]:
        """
        Load workflow template by name.

        Args:
            workflow_name: Name of workflow to load

        Returns:
            Workflow template configuration

        Raises:
            FileNotFoundError: If template doesn't exist
        """
        template_file = self.templates_dir / f"{workflow_name}.json"

        if not template_file.exists():
            raise FileNotFoundError(f"Workflow template not found: {workflow_name}")

        template_data = read_json(template_file)
        self.logger.debug(f"Loaded workflow template: {workflow_name}")

        return template_data["template"]

    def list_templates(self) -> List[Dict[str, Any]]:
        """
        List all available workflow templates.

        Returns:
            List of template metadata dictionaries

        Example:
            >>> templates = store.list_templates()
            >>> for tmpl in templates:
            ...     print(f"{tmpl['name']} v{tmpl['version']}")
        """
        templates = []

        for template_file in self.templates_dir.glob("*.json"):
            try:
                template_data = read_json(template_file)
                templates.append({
                    "name": template_data["name"],
                    "version": template_data["version"],
                    "created_at": template_data["created_at"],
                    "updated_at": template_data["updated_at"],
                })
            except Exception as e:
                self.logger.warning(
                    f"Failed to load template {template_file}: {e}"
                )

        return templates

    def save_workflow_state(
        self,
        workflow_id: str,
        state: WorkflowState,
    ) -> None:
        """
        Save active workflow state.

        Args:
            workflow_id: Unique workflow execution ID
            state: Current workflow state

        Example:
            >>> state = WorkflowState(
            ...     workflow_id="wf_123",
            ...     current_step=2,
            ...     status="running",
            ...     ...
            ... )
            >>> store.save_workflow_state("wf_123", state)
        """
        state_file = self.active_dir / f"{workflow_id}_state.json"

        write_json(state_file, state.model_dump())
        self.logger.debug(f"Saved workflow state: {workflow_id}")

    def load_workflow_state(self, workflow_id: str) -> WorkflowState:
        """
        Load active workflow state.

        Args:
            workflow_id: Workflow execution ID

        Returns:
            WorkflowState object

        Raises:
            FileNotFoundError: If workflow state doesn't exist
        """
        state_file = self.active_dir / f"{workflow_id}_state.json"

        if not state_file.exists():
            raise FileNotFoundError(f"Workflow state not found: {workflow_id}")

        state_data = read_json(state_file)
        return WorkflowState(**state_data)

    def delete_workflow_state(self, workflow_id: str) -> None:
        """
        Delete workflow state (called when workflow completes).

        Args:
            workflow_id: Workflow execution ID
        """
        state_file = self.active_dir / f"{workflow_id}_state.json"

        if state_file.exists():
            state_file.unlink()
            self.logger.info(f"Deleted workflow state: {workflow_id}")

    def list_active_workflows(self) -> List[WorkflowState]:
        """
        List all currently active workflows.

        Returns:
            List of WorkflowState objects

        Example:
            >>> active = store.list_active_workflows()
            >>> for wf in active:
            ...     print(f"{wf.workflow_id}: {wf.status}")
        """
        workflows = []

        for state_file in self.active_dir.glob("*_state.json"):
            try:
                state_data = read_json(state_file)
                workflows.append(WorkflowState(**state_data))
            except Exception as e:
                self.logger.warning(
                    f"Failed to load workflow state {state_file}: {e}"
                )

        return workflows

    def get_workflow_by_campaign(self, campaign_id: str) -> Optional[WorkflowState]:
        """
        Find workflow associated with campaign.

        Args:
            campaign_id: Campaign identifier

        Returns:
            WorkflowState if found, None otherwise
        """
        for workflow in self.list_active_workflows():
            if workflow.campaign_id == campaign_id:
                return workflow

        return None

    def cleanup_old_states(self, max_age_days: int = 7) -> int:
        """
        Clean up old workflow states from active directory.

        Args:
            max_age_days: Delete states older than this many days

        Returns:
            Number of states deleted
        """
        deleted_count = 0
        max_age_seconds = max_age_days * 24 * 60 * 60

        for state_file in self.active_dir.glob("*_state.json"):
            try:
                file_age = datetime.now(timezone.utc).timestamp() - state_file.stat().st_mtime

                if file_age > max_age_seconds:
                    state_file.unlink()
                    deleted_count += 1
                    self.logger.debug(f"Cleaned up old state: {state_file.name}")

            except Exception as e:
                self.logger.warning(f"Failed to clean up {state_file}: {e}")

        if deleted_count > 0:
            self.logger.info(f"Cleaned up {deleted_count} old workflow states")

        return deleted_count


# Convenience function for global workflow store
_workflow_store = None


def get_workflow_store() -> WorkflowStore:
    """
    Get singleton workflow store instance.

    Returns:
        Global WorkflowStore instance
    """
    global _workflow_store
    if _workflow_store is None:
        _workflow_store = WorkflowStore()
    return _workflow_store

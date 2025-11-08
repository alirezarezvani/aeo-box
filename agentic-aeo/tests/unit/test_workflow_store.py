"""
Unit Tests for WorkflowStore

Tests the workflow template and state persistence.
"""

import pytest
from pathlib import Path
import tempfile
import shutil
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from persistence.workflow_store import WorkflowStore
from communication.protocol import WorkflowState, WorkflowStatus


class TestWorkflowStore:
    """Test WorkflowStore functionality"""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing"""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        # Cleanup
        shutil.rmtree(temp_path)

    @pytest.fixture
    def store(self, temp_dir):
        """Create WorkflowStore with temp directory"""
        return WorkflowStore(data_dir=temp_dir)

    def test_init(self, store, temp_dir):
        """Test store initialization"""
        assert store.data_dir == temp_dir
        assert (store.workflows_dir / "templates").exists()
        assert (store.workflows_dir / "active").exists()

    def test_save_template(self, store):
        """Test saving workflow template"""
        template = {
            "name": "aeo-campaign",
            "steps": [
                {"agent": "auditor", "depends_on": []},
                {"agent": "optimizer", "depends_on": ["auditor"]},
            ],
            "parameters": {
                "timeout_seconds": 300,
            },
        }

        store.save_template("aeo-campaign", template, version="1.0.0")

        # Verify file exists
        template_file = store.templates_dir / "aeo-campaign.json"
        assert template_file.exists()

    def test_load_template(self, store):
        """Test loading workflow template"""
        template = {
            "name": "test-workflow",
            "steps": [{"agent": "auditor"}],
        }

        store.save_template("test-workflow", template)
        loaded = store.load_template("test-workflow")

        assert loaded == template
        assert loaded["name"] == "test-workflow"

    def test_load_template_not_found(self, store):
        """Test loading non-existent template"""
        with pytest.raises(FileNotFoundError):
            store.load_template("nonexistent")

    def test_list_templates(self, store):
        """Test listing all templates"""
        # Save multiple templates
        store.save_template("workflow1", {"name": "workflow1"}, "1.0.0")
        store.save_template("workflow2", {"name": "workflow2"}, "1.1.0")

        templates = store.list_templates()

        assert len(templates) == 2
        names = [t["name"] for t in templates]
        assert "workflow1" in names
        assert "workflow2" in names

    def test_save_workflow_state(self, store):
        """Test saving workflow state"""
        state = WorkflowState(
            workflow_id="wf_123",
            workflow_name="aeo-campaign",
            campaign_id="camp_456",
            status=WorkflowStatus.RUNNING,
            current_step=2,
            total_steps=6,
            completed_tasks=[],
            pending_tasks=[],
        )

        store.save_workflow_state("wf_123", state)

        # Verify file exists
        state_file = store.active_dir / "wf_123_state.json"
        assert state_file.exists()

    def test_load_workflow_state(self, store):
        """Test loading workflow state"""
        original_state = WorkflowState(
            workflow_id="wf_456",
            workflow_name="aeo-compete",
            campaign_id="camp_789",
            status=WorkflowStatus.RUNNING,
            current_step=3,
            total_steps=5,
            completed_tasks=[],
            pending_tasks=[],
        )

        store.save_workflow_state("wf_456", original_state)
        loaded_state = store.load_workflow_state("wf_456")

        assert loaded_state.workflow_id == "wf_456"
        assert loaded_state.workflow_name == "aeo-compete"
        assert loaded_state.status == WorkflowStatus.RUNNING
        assert loaded_state.current_step == 3

    def test_delete_workflow_state(self, store):
        """Test deleting workflow state"""
        state = WorkflowState(
            workflow_id="wf_delete",
            workflow_name="test",
            campaign_id="camp_test",
            status=WorkflowStatus.COMPLETED,
            current_step=5,
            total_steps=5,
            completed_tasks=[],
            pending_tasks=[],
        )

        store.save_workflow_state("wf_delete", state)
        assert (store.active_dir / "wf_delete_state.json").exists()

        store.delete_workflow_state("wf_delete")
        assert not (store.active_dir / "wf_delete_state.json").exists()

    def test_list_active_workflows(self, store):
        """Test listing active workflows"""
        # Create multiple workflow states
        for i in range(3):
            state = WorkflowState(
                workflow_id=f"wf_{i}",
                workflow_name="test",
                campaign_id=f"camp_{i}",
                status=WorkflowStatus.RUNNING,
                current_step=i,
                total_steps=5,
                completed_tasks=[],
                pending_tasks=[],
            )
            store.save_workflow_state(f"wf_{i}", state)

        active = store.list_active_workflows()

        assert len(active) == 3
        ids = [wf.workflow_id for wf in active]
        assert "wf_0" in ids
        assert "wf_2" in ids

    def test_get_workflow_by_campaign(self, store):
        """Test finding workflow by campaign ID"""
        state = WorkflowState(
            workflow_id="wf_find_me",
            workflow_name="test",
            campaign_id="camp_special",
            status=WorkflowStatus.RUNNING,
            current_step=1,
            total_steps=3,
            completed_tasks=[],
            pending_tasks=[],
        )

        store.save_workflow_state("wf_find_me", state)

        found = store.get_workflow_by_campaign("camp_special")

        assert found is not None
        assert found.workflow_id == "wf_find_me"
        assert found.campaign_id == "camp_special"

    def test_get_workflow_by_campaign_not_found(self, store):
        """Test finding non-existent workflow"""
        result = store.get_workflow_by_campaign("nonexistent")
        assert result is None


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])

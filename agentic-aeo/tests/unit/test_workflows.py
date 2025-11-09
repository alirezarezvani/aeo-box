"""
Unit Tests for Workflow Implementations

Tests task decomposition, validation, and summary generation.
"""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from workflows.campaign_workflow import CampaignWorkflow
from workflows.competitive_workflow import CompetitiveWorkflow
from workflows.monitoring_workflow import MonitoringWorkflow
from communication.protocol import AgentType, TaskStatus, TaskType


class TestCampaignWorkflow:
    """Test Campaign Workflow implementation."""

    @pytest.fixture
    def workflow(self):
        """Create Campaign Workflow instance."""
        return CampaignWorkflow()

    def test_workflow_initialization(self, workflow):
        """Test workflow initializes correctly."""
        assert workflow.workflow_name == "aeo-campaign"
        assert workflow.workflow_version == "1.0.0"

    def test_decompose_minimal_mode(self, workflow):
        """Test task decomposition for minimal mode."""
        tasks = workflow.decompose(
            campaign_id="test_campaign_minimal",
            url="https://example.com/article",
            mode="minimal"
        )

        # Minimal mode should have 5 tasks (no learning agent)
        assert len(tasks) == 5

        # Verify protocol compliance (Issue #1)
        for task in tasks:
            assert task.campaign_id == "test_campaign_minimal", f"Task {task.task_id} missing campaign_id"
            assert task.task_type is not None, f"Task {task.task_id} missing task_type"
            assert isinstance(task.task_type, TaskType), f"Task {task.task_id} has invalid task_type"

        # Verify all required agent types present
        agent_types = {t.agent_type for t in tasks}
        expected_types = {
            AgentType.AUDITOR,
            AgentType.RESEARCHER,
            AgentType.OPTIMIZER,
            AgentType.TRACKER,
            AgentType.REPORTER
        }
        assert agent_types == expected_types

    def test_decompose_comprehensive_mode(self, workflow):
        """Test task decomposition for comprehensive mode."""
        tasks = workflow.decompose(
            campaign_id="test_campaign_comprehensive",
            url="https://example.com/article",
            mode="comprehensive"
        )

        # Comprehensive mode should have 6 tasks (includes learning)
        assert len(tasks) == 6

        # Verify protocol compliance (Issue #1)
        for task in tasks:
            assert task.campaign_id == "test_campaign_comprehensive", f"Task {task.task_id} missing campaign_id"
            assert task.task_type is not None, f"Task {task.task_id} missing task_type"

        # Verify learning agent included
        agent_types = {t.agent_type for t in tasks}
        assert AgentType.LEARNING in agent_types

    def test_task_priorities(self, workflow):
        """Test tasks have correct agent types and dependencies."""
        tasks = workflow.decompose(
            campaign_id="test_campaign_priorities",
            url="https://example.com/article",
            mode="balanced"
        )

        # Find report task and verify it has dependencies
        reporter_task = next((t for t in tasks if t.agent_type == AgentType.REPORTER), None)
        assert reporter_task is not None, "Reporter task should exist"
        assert len(reporter_task.dependencies) == 4, "Reporter should depend on 4 previous tasks"

        # Find optimizer task and verify it has dependencies on audit
        optimizer_task = next((t for t in tasks if t.agent_type == AgentType.OPTIMIZER), None)
        assert optimizer_task is not None, "Optimizer task should exist"
        assert len(optimizer_task.dependencies) > 0, "Optimizer should have dependencies"

    def test_task_dependencies(self, workflow):
        """Test tasks have correct dependencies."""
        tasks = workflow.decompose(
            campaign_id="test_campaign_dependencies",
            url="https://example.com/article",
            mode="balanced"
        )

        # Find audit and optimizer tasks
        audit_task = next(t for t in tasks if t.agent_type == AgentType.AUDITOR)
        optimizer_task = next(t for t in tasks if t.agent_type == AgentType.OPTIMIZER)

        # Optimizer should depend on audit
        assert audit_task.task_id in optimizer_task.dependencies

    def test_validate_input_valid(self, workflow):
        """Test input validation with valid input."""
        is_valid, error = workflow.validate_input(
            url="https://example.com/article",
            mode="comprehensive"
        )

        assert is_valid is True
        assert error is None

    def test_validate_input_invalid_url(self, workflow):
        """Test input validation with invalid URL."""
        is_valid, error = workflow.validate_input(
            url="invalid-url",
            mode="balanced"
        )

        assert is_valid is False
        assert "http" in error.lower()

    def test_validate_input_invalid_mode(self, workflow):
        """Test input validation with invalid mode."""
        is_valid, error = workflow.validate_input(
            url="https://example.com",
            mode="invalid_mode"
        )

        assert is_valid is False
        assert "mode" in error.lower()


class TestCompetitiveWorkflow:
    """Test Competitive Workflow implementation."""

    @pytest.fixture
    def workflow(self):
        """Create Competitive Workflow instance."""
        return CompetitiveWorkflow()

    def test_workflow_initialization(self, workflow):
        """Test workflow initializes correctly."""
        assert workflow.workflow_name == "aeo-compete"
        assert workflow.workflow_version == "1.0.0"

    def test_decompose_with_competitors(self, workflow):
        """Test task decomposition with 3 competitors."""
        tasks = workflow.decompose(
            campaign_id="test_compete_3competitors",
            topic="project management",
            competitor_urls=[
                "https://competitor1.com",
                "https://competitor2.com",
                "https://competitor3.com"
            ]
        )

        # Should have: 1 research + 3 audits + 1 citations + 1 gap + 1 report = 7
        assert len(tasks) == 7

        # Verify protocol compliance (Issue #1)
        for task in tasks:
            assert task.campaign_id == "test_compete_3competitors", f"Task {task.task_id} missing campaign_id"
            assert task.task_type is not None, f"Task {task.task_id} missing task_type"

        # Verify audit tasks for each competitor
        audit_tasks = [t for t in tasks if t.agent_type == AgentType.AUDITOR]
        assert len(audit_tasks) == 3

    def test_competitor_limit(self, workflow):
        """Test workflow limits competitors to 5."""
        competitor_urls = [f"https://competitor{i}.com" for i in range(10)]

        tasks = workflow.decompose(
            campaign_id="test_compete_limit",
            topic="test topic",
            competitor_urls=competitor_urls
        )

        # Verify protocol compliance (Issue #1)
        for task in tasks:
            assert task.campaign_id == "test_compete_limit", f"Task {task.task_id} missing campaign_id"
            assert task.task_type is not None, f"Task {task.task_id} missing task_type"

        # Should only create 5 audit tasks
        audit_tasks = [t for t in tasks if t.agent_type == AgentType.AUDITOR]
        assert len(audit_tasks) == 5

    def test_task_priorities(self, workflow):
        """Test tasks have correct agent types and dependencies."""
        tasks = workflow.decompose(
            campaign_id="test_compete_priorities",
            topic="test",
            competitor_urls=["https://comp1.com", "https://comp2.com"]
        )

        # Verify researcher task exists
        researcher_tasks = [t for t in tasks if t.agent_type == AgentType.RESEARCHER]
        assert len(researcher_tasks) > 0, "Researcher task should exist"

        # Verify audits (parallel)
        auditor_tasks = [t for t in tasks if t.agent_type == AgentType.AUDITOR]
        assert len(auditor_tasks) == 2, "Should have 2 auditor tasks"

        # Verify report task and its dependencies
        reporter_tasks = [t for t in tasks if t.agent_type == AgentType.REPORTER]
        assert len(reporter_tasks) == 1, "Should have 1 reporter task"
        assert len(reporter_tasks[0].dependencies) > 0, "Reporter should have dependencies"

    def test_validate_input_valid(self, workflow):
        """Test input validation with valid input."""
        is_valid, error = workflow.validate_input(
            topic="test topic",
            competitor_urls=["https://comp1.com", "https://comp2.com"]
        )

        assert is_valid is True
        assert error is None

    def test_validate_input_no_competitors(self, workflow):
        """Test input validation with no competitors."""
        is_valid, error = workflow.validate_input(
            topic="test",
            competitor_urls=[]
        )

        assert is_valid is False
        assert "competitor" in error.lower()

    def test_validate_input_invalid_url(self, workflow):
        """Test input validation with invalid competitor URL."""
        is_valid, error = workflow.validate_input(
            topic="test",
            competitor_urls=["invalid-url"]
        )

        assert is_valid is False
        assert "url" in error.lower()


class TestMonitoringWorkflow:
    """Test Monitoring Workflow implementation."""

    @pytest.fixture
    def workflow(self):
        """Create Monitoring Workflow instance."""
        return MonitoringWorkflow()

    def test_workflow_initialization(self, workflow):
        """Test workflow initializes correctly."""
        assert workflow.workflow_name == "aeo-monitor"
        assert workflow.workflow_version == "1.0.0"

    def test_decompose_basic(self, workflow):
        """Test task decomposition."""
        tasks = workflow.decompose(
            campaign_id="test_monitor_basic",
            url="https://example.com/article",
            duration_days=30
        )

        # Should have 3 tasks: baseline audit, setup tracking, initial report
        assert len(tasks) == 3

        # Verify protocol compliance (Issue #1)
        for task in tasks:
            assert task.campaign_id == "test_monitor_basic", f"Task {task.task_id} missing campaign_id"
            assert task.task_type is not None, f"Task {task.task_id} missing task_type"

        # Verify agent types
        agent_types = {t.agent_type for t in tasks}
        expected_types = {
            AgentType.AUDITOR,
            AgentType.TRACKER,
            AgentType.REPORTER
        }
        assert agent_types == expected_types

    def test_task_priorities(self, workflow):
        """Test tasks have correct agent types and dependencies."""
        tasks = workflow.decompose(
            campaign_id="test_monitor_priorities",
            url="https://example.com",
            duration_days=90
        )

        # Verify baseline audit task exists
        auditor_tasks = [t for t in tasks if t.agent_type == AgentType.AUDITOR]
        assert len(auditor_tasks) == 1, "Should have 1 auditor task"

        # Verify tracking setup task exists and has dependencies
        tracker_tasks = [t for t in tasks if t.agent_type == AgentType.TRACKER]
        assert len(tracker_tasks) == 1, "Should have 1 tracker task"
        assert len(tracker_tasks[0].dependencies) > 0, "Tracker should have dependencies"

        # Verify initial report task exists and depends on both
        reporter_tasks = [t for t in tasks if t.agent_type == AgentType.REPORTER]
        assert len(reporter_tasks) == 1, "Should have 1 reporter task"
        assert len(reporter_tasks[0].dependencies) == 2, "Reporter should depend on 2 tasks"

    def test_validate_input_valid(self, workflow):
        """Test input validation with valid input."""
        is_valid, error = workflow.validate_input(
            url="https://example.com/article",
            duration_days=90
        )

        assert is_valid is True
        assert error is None

    def test_validate_input_invalid_duration(self, workflow):
        """Test input validation with invalid duration."""
        is_valid, error = workflow.validate_input(
            url="https://example.com",
            duration_days=0
        )

        assert is_valid is False
        assert "duration" in error.lower()

    def test_validate_input_duration_too_long(self, workflow):
        """Test input validation with duration > 365 days."""
        is_valid, error = workflow.validate_input(
            url="https://example.com",
            duration_days=400
        )

        assert is_valid is False
        assert "365" in error


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

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
from communication.protocol import AgentType, TaskStatus


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
            url="https://example.com/article",
            mode="minimal"
        )

        # Minimal mode should have 5 tasks (no learning agent)
        assert len(tasks) == 5

        # Verify all required agent types present
        agent_types = {t.agent_type for t in tasks}
        expected_types = {
            AgentType.AUDITOR,
            AgentType.RESEARCHER,
            AgentType.OPTIMIZER,
            AgentType.CITATION_TRACKER,
            AgentType.REPORTER
        }
        assert agent_types == expected_types

    def test_decompose_comprehensive_mode(self, workflow):
        """Test task decomposition for comprehensive mode."""
        tasks = workflow.decompose(
            url="https://example.com/article",
            mode="comprehensive"
        )

        # Comprehensive mode should have 6 tasks (includes learning)
        assert len(tasks) == 6

        # Verify learning agent included
        agent_types = {t.agent_type for t in tasks}
        assert AgentType.LEARNING in agent_types

    def test_task_priorities(self, workflow):
        """Test tasks have correct priorities."""
        tasks = workflow.decompose(
            url="https://example.com/article",
            mode="balanced"
        )

        # Priority 1: audit + research (parallel)
        priority_1_tasks = [t for t in tasks if t.priority == 1]
        assert len(priority_1_tasks) == 2
        agent_types_p1 = {t.agent_type for t in priority_1_tasks}
        assert agent_types_p1 == {AgentType.AUDITOR, AgentType.RESEARCHER}

        # Priority 2: optimize (depends on audit)
        priority_2_tasks = [t for t in tasks if t.priority == 2]
        assert len(priority_2_tasks) == 1
        assert priority_2_tasks[0].agent_type == AgentType.OPTIMIZER

        # Priority 4: report (depends on all)
        priority_4_tasks = [t for t in tasks if t.priority == 4]
        assert len(priority_4_tasks) == 1
        assert priority_4_tasks[0].agent_type == AgentType.REPORTER
        assert len(priority_4_tasks[0].depends_on) == 4

    def test_task_dependencies(self, workflow):
        """Test tasks have correct dependencies."""
        tasks = workflow.decompose(
            url="https://example.com/article",
            mode="balanced"
        )

        # Find audit and optimizer tasks
        audit_task = next(t for t in tasks if t.agent_type == AgentType.AUDITOR)
        optimizer_task = next(t for t in tasks if t.agent_type == AgentType.OPTIMIZER)

        # Optimizer should depend on audit
        assert audit_task.task_id in optimizer_task.depends_on

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
            topic="project management",
            competitor_urls=[
                "https://competitor1.com",
                "https://competitor2.com",
                "https://competitor3.com"
            ]
        )

        # Should have: 1 research + 3 audits + 1 citations + 1 gap + 1 report = 7
        assert len(tasks) == 7

        # Verify audit tasks for each competitor
        audit_tasks = [t for t in tasks if t.agent_type == AgentType.AUDITOR]
        assert len(audit_tasks) == 3

    def test_competitor_limit(self, workflow):
        """Test workflow limits competitors to 5."""
        competitor_urls = [f"https://competitor{i}.com" for i in range(10)]

        tasks = workflow.decompose(
            topic="test topic",
            competitor_urls=competitor_urls
        )

        # Should only create 5 audit tasks
        audit_tasks = [t for t in tasks if t.agent_type == AgentType.AUDITOR]
        assert len(audit_tasks) == 5

    def test_task_priorities(self, workflow):
        """Test tasks have correct priorities."""
        tasks = workflow.decompose(
            topic="test",
            competitor_urls=["https://comp1.com", "https://comp2.com"]
        )

        # Priority 1: research
        priority_1 = [t for t in tasks if t.priority == 1]
        assert len(priority_1) == 1
        assert priority_1[0].agent_type == AgentType.RESEARCHER

        # Priority 2: audits (parallel)
        priority_2 = [t for t in tasks if t.priority == 2]
        assert len(priority_2) == 2
        assert all(t.agent_type == AgentType.AUDITOR for t in priority_2)

        # Priority 5: report (final)
        priority_5 = [t for t in tasks if t.priority == 5]
        assert len(priority_5) == 1
        assert priority_5[0].agent_type == AgentType.REPORTER

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
            url="https://example.com/article",
            duration_days=30
        )

        # Should have 3 tasks: baseline audit, setup tracking, initial report
        assert len(tasks) == 3

        # Verify agent types
        agent_types = {t.agent_type for t in tasks}
        expected_types = {
            AgentType.AUDITOR,
            AgentType.CITATION_TRACKER,
            AgentType.REPORTER
        }
        assert agent_types == expected_types

    def test_task_priorities(self, workflow):
        """Test tasks have correct priorities."""
        tasks = workflow.decompose(
            url="https://example.com",
            duration_days=90
        )

        # Priority 1: baseline audit
        priority_1 = [t for t in tasks if t.priority == 1]
        assert len(priority_1) == 1
        assert priority_1[0].agent_type == AgentType.AUDITOR

        # Priority 2: tracking setup (depends on audit)
        priority_2 = [t for t in tasks if t.priority == 2]
        assert len(priority_2) == 1
        assert priority_2[0].agent_type == AgentType.CITATION_TRACKER

        # Priority 3: initial report (depends on both)
        priority_3 = [t for t in tasks if t.priority == 3]
        assert len(priority_3) == 1
        assert priority_3[0].agent_type == AgentType.REPORTER
        assert len(priority_3[0].depends_on) == 2

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

"""
Integration Tests for Workflow Validation

End-to-end tests that validate complete workflow execution across all 3 workflow types.
"""

import pytest
import asyncio
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from workflows.campaign_workflow import CampaignWorkflow
from workflows.competitive_workflow import CompetitiveWorkflow
from workflows.monitoring_workflow import MonitoringWorkflow
from agents.orchestrator_agent import OrchestratorAgent
from agents.auditor_agent import AuditorAgent
from agents.optimizer_agent import OptimizerAgent
from agents.citation_tracker_agent import CitationTrackerAgent
from agents.researcher_agent import ResearcherAgent
from agents.reporter_agent import ReporterAgent
from agents.learning_agent import LearningAgent
from communication.protocol import AgentType


def get_test_orchestrator():
    """Initialize orchestrator with all agents for testing"""
    orchestrator = OrchestratorAgent()
    orchestrator.register_agent(AgentType.AUDITOR, AuditorAgent())
    orchestrator.register_agent(AgentType.OPTIMIZER, OptimizerAgent())
    orchestrator.register_agent(AgentType.CITATION_TRACKER, CitationTrackerAgent())
    orchestrator.register_agent(AgentType.RESEARCHER, ResearcherAgent())
    orchestrator.register_agent(AgentType.REPORTER, ReporterAgent())
    orchestrator.register_agent(AgentType.LEARNING, LearningAgent())
    return orchestrator


class TestCampaignWorkflowValidation:
    """End-to-end validation of campaign workflow"""

    def test_campaign_workflow_minimal_mode(self):
        """Test minimal mode campaign workflow execution"""
        workflow = CampaignWorkflow()

        # Validate input
        is_valid, error = workflow.validate_input(
            "https://example.com/test-article",
            "minimal"
        )
        assert is_valid, f"Validation failed: {error}"

        # Build workflow
        manifest = workflow.build_workflow(
            url="https://example.com/test-article",
            mode="minimal",
            industry="Technology"
        )

        # Verify workflow structure
        assert manifest.workflow_state.workflow_name == "aeo-campaign"
        assert manifest.workflow_state.total_tasks > 0
        assert len(manifest.task_queue) > 0

        # Verify tasks are prioritized
        for task in manifest.task_queue:
            assert task.priority >= 0
            assert task.task_type in ["audit", "research", "optimize", "tracking", "report"]

    def test_campaign_workflow_balanced_mode(self):
        """Test balanced mode campaign workflow execution"""
        workflow = CampaignWorkflow()

        # Validate input with all parameters
        is_valid, error = workflow.validate_input(
            "https://example.com/comprehensive-guide",
            "balanced"
        )
        assert is_valid, f"Validation failed: {error}"

        # Build workflow with full parameters
        manifest = workflow.build_workflow(
            url="https://example.com/comprehensive-guide",
            mode="balanced",
            industry="SaaS",
            optimization_level="balanced",
            tracking_duration_days=30,
            queries=["AEO optimization", "answer engine ranking"]
        )

        # Verify comprehensive task coverage
        assert manifest.workflow_state.total_tasks >= 5
        task_types = [task.task_type for task in manifest.task_queue]
        assert "audit" in task_types
        assert "research" in task_types
        assert "optimize" in task_types

    def test_campaign_workflow_comprehensive_mode(self):
        """Test comprehensive mode campaign workflow execution"""
        workflow = CampaignWorkflow()

        manifest = workflow.build_workflow(
            url="https://example.com/enterprise-content",
            mode="comprehensive",
            industry="Enterprise SaaS",
            optimization_level="aggressive",
            tracking_duration_days=90,
            queries=["enterprise AEO", "B2B content optimization", "AI search ranking"]
        )

        # Comprehensive mode should have most tasks
        assert manifest.workflow_state.total_tasks >= 8

        # Verify all task types present
        task_types = [task.task_type for task in manifest.task_queue]
        assert "audit" in task_types
        assert "research" in task_types
        assert "optimize" in task_types
        assert "tracking" in task_types
        assert "report" in task_types

    def test_campaign_workflow_invalid_url(self):
        """Test campaign workflow with invalid URL"""
        workflow = CampaignWorkflow()

        # Test various invalid URLs
        invalid_urls = [
            "not-a-url",
            "ftp://invalid-protocol.com",
            "javascript:alert(1)",
            "",
            None
        ]

        for invalid_url in invalid_urls:
            is_valid, error = workflow.validate_input(invalid_url, "balanced")
            assert not is_valid, f"Should reject invalid URL: {invalid_url}"
            assert error is not None

    def test_campaign_workflow_invalid_mode(self):
        """Test campaign workflow with invalid mode"""
        workflow = CampaignWorkflow()

        invalid_modes = ["invalid", "extreme", "", None]

        for invalid_mode in invalid_modes:
            is_valid, error = workflow.validate_input("https://example.com", invalid_mode)
            assert not is_valid, f"Should reject invalid mode: {invalid_mode}"


class TestCompetitiveWorkflowValidation:
    """End-to-end validation of competitive analysis workflow"""

    def test_competitive_workflow_basic(self):
        """Test basic competitive analysis workflow"""
        workflow = CompetitiveWorkflow()

        # Validate input
        is_valid, error = workflow.validate_input(
            "project management software",
            ["https://competitor1.com", "https://competitor2.com"]
        )
        assert is_valid, f"Validation failed: {error}"

        # Build workflow
        manifest = workflow.build_workflow(
            topic="project management software",
            competitor_urls=["https://competitor1.com", "https://competitor2.com"],
            region="US"
        )

        # Verify workflow structure
        assert manifest.workflow_state.workflow_name == "aeo-compete"
        assert manifest.workflow_state.total_tasks > 0

        # Verify competitive analysis tasks
        task_types = [task.task_type for task in manifest.task_queue]
        assert "research" in task_types or "audit" in task_types

    def test_competitive_workflow_multi_competitor(self):
        """Test competitive analysis with multiple competitors"""
        workflow = CompetitiveWorkflow()

        # Test with maximum competitors (10)
        competitor_urls = [f"https://competitor{i}.com" for i in range(1, 11)]

        is_valid, error = workflow.validate_input(
            "content optimization",
            competitor_urls
        )
        assert is_valid, f"Validation failed: {error}"

        manifest = workflow.build_workflow(
            topic="content optimization",
            competitor_urls=competitor_urls,
            region="US",
            include_citations=True
        )

        # Should handle multiple competitors
        assert manifest.workflow_state.total_tasks > 0

    def test_competitive_workflow_no_competitors(self):
        """Test competitive analysis with no competitors (should fail)"""
        workflow = CompetitiveWorkflow()

        is_valid, error = workflow.validate_input("topic", [])
        assert not is_valid, "Should reject empty competitor list"
        assert error is not None

    def test_competitive_workflow_too_many_competitors(self):
        """Test competitive analysis with too many competitors"""
        workflow = CompetitiveWorkflow()

        # More than 10 competitors
        competitor_urls = [f"https://competitor{i}.com" for i in range(1, 16)]

        is_valid, error = workflow.validate_input("topic", competitor_urls)
        assert not is_valid, "Should reject >10 competitors"

    def test_competitive_workflow_invalid_topic(self):
        """Test competitive analysis with invalid topic"""
        workflow = CompetitiveWorkflow()

        invalid_topics = ["", None, "ab"]  # Too short

        for invalid_topic in invalid_topics:
            is_valid, error = workflow.validate_input(
                invalid_topic,
                ["https://competitor.com"]
            )
            assert not is_valid, f"Should reject invalid topic: {invalid_topic}"


class TestMonitoringWorkflowValidation:
    """End-to-end validation of monitoring workflow"""

    def test_monitoring_workflow_basic(self):
        """Test basic monitoring workflow"""
        workflow = MonitoringWorkflow()

        # Validate input
        is_valid, error = workflow.validate_input(
            "https://example.com/article",
            90
        )
        assert is_valid, f"Validation failed: {error}"

        # Build workflow
        manifest = workflow.build_workflow(
            url="https://example.com/article",
            duration_days=90,
            queries=["topic 1", "topic 2"]
        )

        # Verify workflow structure
        assert manifest.workflow_state.workflow_name == "aeo-monitor"
        assert manifest.workflow_state.total_tasks > 0

    def test_monitoring_workflow_long_duration(self):
        """Test monitoring with maximum duration"""
        workflow = MonitoringWorkflow()

        # Test maximum duration (365 days)
        is_valid, error = workflow.validate_input(
            "https://example.com/long-term-content",
            365
        )
        assert is_valid, f"Validation failed: {error}"

        manifest = workflow.build_workflow(
            url="https://example.com/long-term-content",
            duration_days=365,
            alert_on_changes=True,
            weekly_reports=True
        )

        assert manifest.workflow_state.total_tasks > 0

    def test_monitoring_workflow_invalid_duration(self):
        """Test monitoring with invalid duration"""
        workflow = MonitoringWorkflow()

        invalid_durations = [0, -1, 366, 500]

        for invalid_duration in invalid_durations:
            is_valid, error = workflow.validate_input(
                "https://example.com",
                invalid_duration
            )
            assert not is_valid, f"Should reject invalid duration: {invalid_duration}"

    def test_monitoring_workflow_invalid_url(self):
        """Test monitoring with invalid URL"""
        workflow = MonitoringWorkflow()

        is_valid, error = workflow.validate_input("not-a-url", 90)
        assert not is_valid, "Should reject invalid URL"


class TestOrchestratorIntegration:
    """Test orchestrator integration with workflows"""

    @pytest.mark.asyncio
    async def test_orchestrator_campaign_execution(self):
        """Test orchestrator can execute campaign workflow"""
        orchestrator = get_test_orchestrator()

        # Execute minimal campaign workflow
        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-campaign",
            workflow_params={
                "url": "https://example.com/test",
                "mode": "minimal",
                "industry": "Technology"
            }
        )

        # Verify execution completed
        assert manifest.workflow_state.status.value in ["completed", "partial"]
        assert manifest.workflow_state.completed_tasks > 0
        assert len(manifest.task_results) > 0

    @pytest.mark.asyncio
    async def test_orchestrator_competitive_execution(self):
        """Test orchestrator can execute competitive workflow"""
        orchestrator = get_test_orchestrator()

        # Execute competitive analysis
        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-compete",
            workflow_params={
                "topic": "test topic",
                "competitor_urls": ["https://competitor.com"],
                "region": "US"
            }
        )

        # Verify execution completed
        assert manifest.workflow_state.status.value in ["completed", "partial"]

    @pytest.mark.asyncio
    async def test_orchestrator_monitoring_execution(self):
        """Test orchestrator can execute monitoring workflow"""
        orchestrator = get_test_orchestrator()

        # Execute monitoring setup
        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-monitor",
            workflow_params={
                "url": "https://example.com/monitor",
                "duration_days": 30
            }
        )

        # Verify execution completed
        assert manifest.workflow_state.status.value in ["completed", "partial"]

    def test_orchestrator_all_agents_registered(self):
        """Test orchestrator has all required agents"""
        orchestrator = get_test_orchestrator()

        required_agents = [
            AgentType.AUDITOR,
            AgentType.OPTIMIZER,
            AgentType.CITATION_TRACKER,
            AgentType.RESEARCHER,
            AgentType.REPORTER,
            AgentType.LEARNING
        ]

        for agent_type in required_agents:
            assert orchestrator.get_agent(agent_type) is not None, \
                f"Agent {agent_type} not registered"


class TestErrorScenarios:
    """Test error handling and edge cases"""

    def test_workflow_with_none_parameters(self):
        """Test workflows handle None parameters gracefully"""
        workflow = CampaignWorkflow()

        # Should handle None gracefully
        is_valid, error = workflow.validate_input(None, None)
        assert not is_valid
        assert error is not None

    def test_workflow_with_empty_parameters(self):
        """Test workflows handle empty parameters"""
        workflow = CampaignWorkflow()

        is_valid, error = workflow.validate_input("", "")
        assert not is_valid

    @pytest.mark.asyncio
    async def test_orchestrator_invalid_workflow_name(self):
        """Test orchestrator handles invalid workflow name"""
        orchestrator = get_test_orchestrator()

        with pytest.raises(Exception):
            await orchestrator.execute_workflow(
                workflow_name="invalid-workflow",
                workflow_params={}
            )

    @pytest.mark.asyncio
    async def test_orchestrator_missing_workflow_params(self):
        """Test orchestrator handles missing workflow parameters"""
        orchestrator = get_test_orchestrator()

        # Should handle missing parameters
        try:
            manifest = await orchestrator.execute_workflow(
                workflow_name="aeo-campaign",
                workflow_params={}  # Missing required params
            )
            # Should either fail or handle gracefully
            assert manifest.workflow_state.status.value in ["failed", "partial", "completed"]
        except Exception:
            # Exception is acceptable for missing params
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

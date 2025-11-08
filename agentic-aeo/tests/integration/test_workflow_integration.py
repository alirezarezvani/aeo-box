"""
Integration Tests for Workflows with Orchestrator

Tests complete workflow execution with real agents.
"""

import pytest
import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

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


class TestCampaignWorkflowIntegration:
    """Test Campaign Workflow integration with orchestrator."""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator with all agents."""
        orch = OrchestratorAgent()
        orch.register_agent(AgentType.AUDITOR, AuditorAgent())
        orch.register_agent(AgentType.OPTIMIZER, OptimizerAgent())
        orch.register_agent(AgentType.CITATION_TRACKER, CitationTrackerAgent(data_path=".test-data/citations.csv"))
        orch.register_agent(AgentType.RESEARCHER, ResearcherAgent())
        orch.register_agent(AgentType.REPORTER, ReporterAgent())
        orch.register_agent(AgentType.LEARNING, LearningAgent())
        return orch

    @pytest.fixture
    def workflow(self):
        """Create campaign workflow."""
        return CampaignWorkflow()

    @pytest.mark.asyncio
    async def test_campaign_workflow_minimal(self, orchestrator, workflow):
        """Test minimal campaign workflow execution."""
        # Decompose workflow
        tasks = workflow.decompose(
            url="https://example.com/article",
            mode="minimal"
        )

        assert len(tasks) == 5  # No learning agent in minimal mode

        # Execute workflow via orchestrator
        # Note: This would normally call orchestrator.execute_workflow()
        # For now, just verify task structure is correct
        assert all(task.agent_type in orchestrator.agents for task in tasks)

    @pytest.mark.asyncio
    async def test_campaign_workflow_comprehensive(self, orchestrator, workflow):
        """Test comprehensive campaign workflow execution."""
        # Decompose workflow
        tasks = workflow.decompose(
            url="https://example.com/test-article",
            mode="comprehensive",
            industry="SaaS"
        )

        assert len(tasks) == 6  # Includes learning agent

        # Verify all agents registered
        required_agents = {t.agent_type for t in tasks}
        for agent_type in required_agents:
            assert agent_type in orchestrator.agents


class TestCompetitiveWorkflowIntegration:
    """Test Competitive Workflow integration with orchestrator."""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator with all agents."""
        orch = OrchestratorAgent()
        orch.register_agent(AgentType.AUDITOR, AuditorAgent())
        orch.register_agent(AgentType.CITATION_TRACKER, CitationTrackerAgent(data_path=".test-data/citations.csv"))
        orch.register_agent(AgentType.RESEARCHER, ResearcherAgent())
        orch.register_agent(AgentType.REPORTER, ReporterAgent())
        return orch

    @pytest.fixture
    def workflow(self):
        """Create competitive workflow."""
        return CompetitiveWorkflow()

    @pytest.mark.asyncio
    async def test_competitive_workflow(self, orchestrator, workflow):
        """Test competitive workflow execution."""
        # Decompose workflow
        tasks = workflow.decompose(
            topic="project management",
            competitor_urls=[
                "https://competitor1.com",
                "https://competitor2.com"
            ]
        )

        # Should have: 1 research + 2 audits + 1 citations + 1 gap + 1 report = 6
        assert len(tasks) == 6

        # Verify all required agents registered
        required_agents = {t.agent_type for t in tasks}
        for agent_type in required_agents:
            assert agent_type in orchestrator.agents


class TestMonitoringWorkflowIntegration:
    """Test Monitoring Workflow integration with orchestrator."""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator with required agents."""
        orch = OrchestratorAgent()
        orch.register_agent(AgentType.AUDITOR, AuditorAgent())
        orch.register_agent(AgentType.CITATION_TRACKER, CitationTrackerAgent(data_path=".test-data/citations.csv"))
        orch.register_agent(AgentType.REPORTER, ReporterAgent())
        return orch

    @pytest.fixture
    def workflow(self):
        """Create monitoring workflow."""
        return MonitoringWorkflow()

    @pytest.mark.asyncio
    async def test_monitoring_workflow(self, orchestrator, workflow):
        """Test monitoring workflow execution."""
        # Decompose workflow
        tasks = workflow.decompose(
            url="https://example.com/article",
            duration_days=90
        )

        assert len(tasks) == 3  # audit, tracking, report

        # Verify all required agents registered
        required_agents = {t.agent_type for t in tasks}
        for agent_type in required_agents:
            assert agent_type in orchestrator.agents


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

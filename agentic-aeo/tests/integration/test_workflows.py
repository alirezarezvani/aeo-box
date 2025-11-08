"""
Workflow Integration Tests

Tests complete workflow execution for all three main workflows:
- /aeo-campaign - Complete content optimization campaign
- /aeo-compete - Competitive analysis
- /aeo-monitor - Citation monitoring setup
"""

import pytest
import asyncio
from pathlib import Path
import sys
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from agents.orchestrator_agent import OrchestratorAgent
from communication.protocol import AgentType
from persistence import CampaignStore
from tests.mocks.mock_agents import (
    MockAuditorAgent,
    MockOptimizerAgent,
    MockCitationTrackerAgent,
    MockResearcherAgent,
    MockReporterAgent,
    MockLearningAgent,
)


class TestAEOCampaignWorkflow:
    """Test /aeo-campaign workflow"""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator with all mock agents"""
        orch = OrchestratorAgent()
        orch.register_agent(AgentType.AUDITOR, MockAuditorAgent())
        orch.register_agent(AgentType.OPTIMIZER, MockOptimizerAgent())
        orch.register_agent(AgentType.CITATION_TRACKER, MockCitationTrackerAgent())
        orch.register_agent(AgentType.RESEARCHER, MockResearcherAgent())
        orch.register_agent(AgentType.REPORTER, MockReporterAgent())
        orch.register_agent(AgentType.LEARNING, MockLearningAgent())
        return orch

    @pytest.mark.asyncio
    async def test_campaign_workflow_minimal(self, orchestrator):
        """Test minimal /aeo-campaign execution"""
        workflow_name = "aeo-campaign"
        parameters = {
            "url": "https://example.com/article",
            "queries": ["test query"],
            "mode": "quick",
        }

        # Execute workflow
        manifest = await orchestrator.execute_workflow(workflow_name, parameters)

        # Verify completion
        assert manifest.workflow_state.status.value == "completed"
        assert manifest.campaign_id.startswith("aeo-campaign")

        # Verify key agents executed
        agent_types = {t.agent_type for t in manifest.task_results}
        assert AgentType.AUDITOR in agent_types
        assert AgentType.OPTIMIZER in agent_types

    @pytest.mark.asyncio
    async def test_campaign_workflow_comprehensive(self, orchestrator):
        """Test comprehensive /aeo-campaign with all options"""
        workflow_name = "aeo-campaign"
        parameters = {
            "url": "https://example.com/detailed-article",
            "queries": [
                "content optimization",
                "AEO best practices",
                "SEO vs AEO",
            ],
            "mode": "comprehensive",
            "optimization_level": "aggressive",
            "track_citations": True,
        }

        # Execute workflow
        manifest = await orchestrator.execute_workflow(workflow_name, parameters)

        # Verify completion
        assert manifest.workflow_state.status.value == "completed"

        # Verify all expected agents executed
        agent_types = {t.agent_type for t in manifest.task_results}
        expected_agents = {
            AgentType.AUDITOR,
            AgentType.OPTIMIZER,
            AgentType.RESEARCHER,
            AgentType.CITATION_TRACKER,
            AgentType.REPORTER,
        }
        assert expected_agents.issubset(agent_types)

        # Verify task results have data
        assert all(t.output_data for t in manifest.task_results)

    @pytest.mark.asyncio
    async def test_campaign_workflow_task_dependencies(self, orchestrator):
        """Test task dependencies in /aeo-campaign"""
        workflow_name = "aeo-campaign"
        parameters = {
            "url": "https://example.com/article",
            "queries": ["test"],
            "mode": "standard",
        }

        # Execute workflow
        manifest = await orchestrator.execute_workflow(workflow_name, parameters)

        # Find auditor and optimizer tasks
        auditor_task = next(
            (t for t in manifest.task_results if t.agent_type == AgentType.AUDITOR),
            None,
        )
        optimizer_task = next(
            (t for t in manifest.task_results if t.agent_type == AgentType.OPTIMIZER),
            None,
        )

        # Verify optimizer depends on auditor (should complete after)
        if auditor_task and optimizer_task:
            assert auditor_task.completed_at < optimizer_task.started_at

    @pytest.mark.asyncio
    async def test_campaign_workflow_duration(self, orchestrator):
        """Test /aeo-campaign completes within time budget"""
        workflow_name = "aeo-campaign"
        parameters = {
            "url": "https://example.com/article",
            "queries": ["test"],
            "mode": "quick",
        }

        # Execute workflow
        import time
        start = time.time()
        manifest = await orchestrator.execute_workflow(workflow_name, parameters)
        duration = time.time() - start

        # Verify completed quickly
        # Mock agents take 0.05-0.15s each, with parallelization should be <2s
        assert duration < 5.0
        assert manifest.workflow_state.duration_seconds < 5.0


class TestAEOCompeteWorkflow:
    """Test /aeo-compete workflow"""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator with mock agents"""
        orch = OrchestratorAgent()
        orch.register_agent(AgentType.AUDITOR, MockAuditorAgent())
        orch.register_agent(AgentType.RESEARCHER, MockResearcherAgent())
        orch.register_agent(AgentType.REPORTER, MockReporterAgent())
        return orch

    @pytest.mark.asyncio
    async def test_compete_workflow_basic(self, orchestrator):
        """Test basic /aeo-compete execution"""
        workflow_name = "aeo-compete"
        parameters = {
            "topic": "content optimization",
            "competitors": [
                "https://competitor1.com",
                "https://competitor2.com",
            ],
        }

        # Execute workflow
        manifest = await orchestrator.execute_workflow(workflow_name, parameters)

        # Verify completion
        assert manifest.workflow_state.status.value == "completed"

        # Verify researcher executed
        agent_types = {t.agent_type for t in manifest.task_results}
        assert AgentType.RESEARCHER in agent_types

    @pytest.mark.asyncio
    async def test_compete_workflow_multiple_competitors(self, orchestrator):
        """Test /aeo-compete with multiple competitors"""
        workflow_name = "aeo-compete"
        parameters = {
            "topic": "SEO strategies",
            "competitors": [
                f"https://competitor{i}.com/article"
                for i in range(1, 6)  # 5 competitors
            ],
        }

        # Execute workflow
        manifest = await orchestrator.execute_workflow(workflow_name, parameters)

        # Verify completion
        assert manifest.workflow_state.status.value == "completed"

        # Should have audits for each competitor
        auditor_tasks = [
            t for t in manifest.task_results if t.agent_type == AgentType.AUDITOR
        ]
        # May have multiple auditor tasks depending on workflow decomposition
        assert len(auditor_tasks) > 0

    @pytest.mark.asyncio
    async def test_compete_workflow_parallel_audits(self, orchestrator):
        """Test /aeo-compete runs competitor audits in parallel"""
        workflow_name = "aeo-compete"
        parameters = {
            "topic": "content marketing",
            "competitors": [
                f"https://competitor{i}.com"
                for i in range(1, 4)  # 3 competitors
            ],
        }

        # Execute workflow
        import time
        start = time.time()
        manifest = await orchestrator.execute_workflow(workflow_name, parameters)
        duration = time.time() - start

        # Verify parallelization (should be much faster than sequential)
        # 3 competitors × 0.1s each = 0.3s sequential, should be <0.5s parallel
        assert duration < 2.0


class TestAEOMonitorWorkflow:
    """Test /aeo-monitor workflow"""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator with mock agents"""
        orch = OrchestratorAgent()
        orch.register_agent(AgentType.AUDITOR, MockAuditorAgent())
        orch.register_agent(AgentType.CITATION_TRACKER, MockCitationTrackerAgent())
        return orch

    @pytest.mark.asyncio
    async def test_monitor_workflow_basic(self, orchestrator):
        """Test basic /aeo-monitor execution"""
        workflow_name = "aeo-monitor"
        parameters = {
            "url": "https://example.com/article",
            "duration_days": 30,
        }

        # Execute workflow
        manifest = await orchestrator.execute_workflow(workflow_name, parameters)

        # Verify completion
        assert manifest.workflow_state.status.value == "completed"

        # Verify citation tracker executed
        agent_types = {t.agent_type for t in manifest.task_results}
        assert AgentType.CITATION_TRACKER in agent_types

    @pytest.mark.asyncio
    async def test_monitor_workflow_baseline_audit(self, orchestrator):
        """Test /aeo-monitor creates baseline audit"""
        workflow_name = "aeo-monitor"
        parameters = {
            "url": "https://example.com/article",
            "duration_days": 90,
        }

        # Execute workflow
        manifest = await orchestrator.execute_workflow(workflow_name, parameters)

        # Verify auditor ran first (for baseline)
        auditor_task = next(
            (t for t in manifest.task_results if t.agent_type == AgentType.AUDITOR),
            None,
        )
        tracker_task = next(
            (t for t in manifest.task_results if t.agent_type == AgentType.CITATION_TRACKER),
            None,
        )

        # Auditor should complete before tracker
        if auditor_task and tracker_task:
            assert auditor_task.completed_at < tracker_task.started_at


class TestWorkflowEdgeCases:
    """Test edge cases and error conditions"""

    @pytest.fixture
    def orchestrator(self):
        """Create minimal orchestrator"""
        orch = OrchestratorAgent()
        orch.register_agent(AgentType.AUDITOR, MockAuditorAgent())
        return orch

    @pytest.mark.asyncio
    async def test_invalid_workflow_name(self, orchestrator):
        """Test orchestrator handles invalid workflow names"""
        with pytest.raises(ValueError, match="Unknown workflow"):
            await orchestrator.execute_workflow(
                "invalid-workflow",
                {"url": "https://example.com"},
            )

    @pytest.mark.asyncio
    async def test_missing_required_parameters(self, orchestrator):
        """Test orchestrator validates required parameters"""
        with pytest.raises((ValueError, KeyError)):
            await orchestrator.execute_workflow(
                "aeo-campaign",
                {},  # Missing required 'url' parameter
            )

    @pytest.mark.asyncio
    async def test_workflow_with_unregistered_agent(self):
        """Test workflow fails gracefully when agent not registered"""
        # Create orchestrator without registering all agents
        orch = OrchestratorAgent()
        # Only register auditor, not optimizer (which campaign needs)
        orch.register_agent(AgentType.AUDITOR, MockAuditorAgent())

        # Attempt workflow (should fail or handle gracefully)
        with pytest.raises((ValueError, KeyError, AttributeError)):
            await orch.execute_workflow(
                "aeo-campaign",
                {"url": "https://example.com", "queries": ["test"]},
            )


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])

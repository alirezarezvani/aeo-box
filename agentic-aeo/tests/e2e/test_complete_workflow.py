"""
End-to-End Workflow Tests

Tests complete AEO campaigns with all 6 agents working together.
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
from communication.protocol import AgentType


class TestCompleteAEOWorkflow:
    """Test complete AEO campaign workflow"""

    @pytest.fixture
    def orchestrator(self):
        """Create fully configured orchestrator with all 6 agents"""
        orch = OrchestratorAgent()
        orch.register_agent(AgentType.AUDITOR, AuditorAgent())
        orch.register_agent(AgentType.OPTIMIZER, OptimizerAgent())
        orch.register_agent(AgentType.CITATION_TRACKER, CitationTrackerAgent(data_path=".test-data/citations.csv"))
        orch.register_agent(AgentType.RESEARCHER, ResearcherAgent())
        orch.register_agent(AgentType.REPORTER, ReporterAgent())
        orch.register_agent(AgentType.LEARNING, LearningAgent())
        return orch

    @pytest.mark.asyncio
    async def test_aeo_campaign_workflow(self, orchestrator):
        """Test complete /aeo-campaign workflow"""
        # Execute full campaign workflow
        manifest = await orchestrator.execute_workflow(
            "aeo-campaign",
            {
                "url": "https://example.com/article",
                "queries": ["AEO best practices"],
                "mode": "minimal"
            }
        )

        # Verify workflow completed
        assert manifest is not None
        assert manifest.workflow_state.status.value in ["completed", "partial"]

        # Verify agents executed
        agent_types = {t.agent_type for t in manifest.task_results}
        assert AgentType.AUDITOR in agent_types

    @pytest.mark.asyncio
    async def test_all_six_agents_registered(self, orchestrator):
        """Verify all 6 specialized agents are registered"""
        required_agents = [
            AgentType.AUDITOR,
            AgentType.OPTIMIZER,
            AgentType.CITATION_TRACKER,
            AgentType.RESEARCHER,
            AgentType.REPORTER,
            AgentType.LEARNING
        ]

        for agent_type in required_agents:
            assert agent_type in orchestrator.agents, f"{agent_type} not registered"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

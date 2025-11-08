"""Integration Tests for Researcher and Reporter Agents"""
import pytest
import asyncio
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from agents.researcher_agent import ResearcherAgent
from agents.reporter_agent import ReporterAgent
from agents.orchestrator_agent import OrchestratorAgent
from communication.protocol import AgentType, TaskMessage, TaskStatus

class TestResearcherIntegration:
    @pytest.mark.asyncio
    async def test_real_research(self):
        agent = ResearcherAgent()
        task = TaskMessage(task_id="ri1", task_type="research", agent_type=AgentType.RESEARCHER,
                           campaign_id="ic1", input_data={"topic": "AEO best practices"})
        result = await agent.execute_task(task)
        assert "target_queries" in result
        assert len(result["target_queries"]) > 0

class TestReporterIntegration:
    @pytest.mark.asyncio
    async def test_real_report_generation(self):
        agent = ReporterAgent()
        data = {"url": "https://example.com", "scores": {"overall": 75, "eeat": 70, "structure": 80, "citations": 65, "readability": 75}, "recommendations": []}
        task = TaskMessage(task_id="rpi1", task_type="generate_report", agent_type=AgentType.REPORTER,
                           campaign_id="ic1", input_data={"report_type": "audit", "data": data})
        result = await agent.execute_task(task)
        assert "report" in result
        assert len(result["report"]) > 0

class TestOrchestratorIntegration:
    @pytest.mark.asyncio
    async def test_orchestrator_with_both_agents(self):
        orch = OrchestratorAgent()
        orch.register_agent(AgentType.RESEARCHER, ResearcherAgent())
        orch.register_agent(AgentType.REPORTER, ReporterAgent())
        campaign_id = orch.campaign_store.create_campaign("test", {}, 2)
       
        tasks = [
            TaskMessage(task_id="oi1", task_type="research", agent_type=AgentType.RESEARCHER,
                        campaign_id=campaign_id, input_data={"topic": "AEO"}),
            TaskMessage(task_id="oi2", task_type="report", agent_type=AgentType.REPORTER,
                        campaign_id=campaign_id, input_data={"report_type": "audit", "data": {"scores": {}}})
        ]
        results = await orch._execute_parallel_tasks(campaign_id, tasks)
        assert len(results) == 2
        assert all(r.status == TaskStatus.COMPLETED for r in results)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

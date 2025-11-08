"""Combined Unit Tests for Researcher and Reporter Agents"""
import pytest
import asyncio
from unittest.mock import Mock, patch
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from agents.researcher_agent import ResearcherAgent
from agents.reporter_agent import ReporterAgent
from communication.protocol import AgentType, TaskMessage

# Researcher Tests
class TestResearcherAgent:
    def test_init(self):
        agent = ResearcherAgent()
        assert agent.agent_type == AgentType.RESEARCHER

    @pytest.mark.asyncio
    async def test_execute_valid_task(self):
        agent = ResearcherAgent()
        mock_result = {"topic": "AEO", "target_queries": [{"query": "test", "priority": "high"}]}
        with patch.object(agent.researcher, 'research_topic', return_value=mock_result):
            task = TaskMessage(task_id="r1", task_type="research", agent_type=AgentType.RESEARCHER,
                               campaign_id="c1", input_data={"topic": "AEO"})
            result = await agent.execute_task(task)
            assert "target_queries" in result

    @pytest.mark.asyncio
    async def test_missing_topic_raises_error(self):
        agent = ResearcherAgent()
        task = TaskMessage(task_id="r2", task_type="research", agent_type=AgentType.RESEARCHER,
                           campaign_id="c1", input_data={})
        with pytest.raises(ValueError, match="Missing required input: 'topic'"):
            await agent.execute_task(task)

# Reporter Tests
class TestReporterAgent:
    def test_init(self):
        agent = ReporterAgent()
        assert agent.agent_type == AgentType.REPORTER

    @pytest.mark.asyncio
    async def test_generate_audit_report(self):
        agent = ReporterAgent()
        mock_report = "# AEO Report"
        with patch.object(agent.generator, 'generate_audit_report', return_value=mock_report):
            task = TaskMessage(task_id="rep1", task_type="generate_report", agent_type=AgentType.REPORTER,
                               campaign_id="c1", input_data={"report_type": "audit", "data": {"scores": {}}})
            result = await agent.execute_task(task)
            assert "report" in result
            assert result["report_type"] == "audit"

    @pytest.mark.asyncio
    async def test_missing_report_type_raises_error(self):
        agent = ReporterAgent()
        task = TaskMessage(task_id="rep2", task_type="generate_report", agent_type=AgentType.REPORTER,
                           campaign_id="c1", input_data={"data": {}})
        with pytest.raises(ValueError, match="Missing required input: 'report_type'"):
            await agent.execute_task(task)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

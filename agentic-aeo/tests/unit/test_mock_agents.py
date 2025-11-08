"""
Unit Tests for Mock Agents

Tests the mock agent implementations used for testing.
"""

import pytest
import asyncio
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from communication.protocol import TaskMessage, AgentType
from tests.mocks.mock_agents import (
    MockAuditorAgent,
    MockOptimizerAgent,
    MockCitationTrackerAgent,
    MockResearcherAgent,
    MockReporterAgent,
    MockLearningAgent,
)


class TestMockAuditorAgent:
    """Test MockAuditorAgent"""

    @pytest.mark.asyncio
    async def test_execute_task(self):
        """Test audit task execution"""
        agent = MockAuditorAgent()

        task = TaskMessage(
            task_id="test_audit_1",
            task_type="audit_content",
            agent_type=AgentType.AUDITOR,
            campaign_id="camp_test",
            input_data={
                "url": "https://example.com",
                "content": "Test content",
            },
        )

        result = await agent.execute_task(task)

        # Verify result structure
        assert "overall_score" in result
        assert "scores" in result
        assert "issues" in result
        assert "recommendations" in result

        # Verify score types
        assert isinstance(result["overall_score"], int)
        assert isinstance(result["scores"], dict)
        assert isinstance(result["issues"], list)

    @pytest.mark.asyncio
    async def test_execute_with_retry(self):
        """Test agent retry logic"""
        agent = MockAuditorAgent()

        task = TaskMessage(
            task_id="test_retry_1",
            task_type="audit_content",
            agent_type=AgentType.AUDITOR,
            campaign_id="camp_test",
            input_data={"url": "https://example.com", "content": "Test"},
        )

        task_result = await agent.execute_with_retry(task)

        assert task_result.status.value == "completed"
        assert task_result.task_id == "test_retry_1"
        assert "overall_score" in task_result.output_data


class TestMockOptimizerAgent:
    """Test MockOptimizerAgent"""

    @pytest.mark.asyncio
    async def test_execute_task(self):
        """Test optimization task execution"""
        agent = MockOptimizerAgent()

        task = TaskMessage(
            task_id="test_opt_1",
            task_type="optimize_content",
            agent_type=AgentType.OPTIMIZER,
            campaign_id="camp_test",
            input_data={"content": "Original content"},
            parameters={"optimization_level": "balanced"},
        )

        result = await agent.execute_task(task)

        assert "original_content" in result
        assert "optimized_content" in result
        assert "before_score" in result
        assert "after_score" in result

        # Verify optimization applied
        assert result["optimized_content"] != result["original_content"]
        assert "[OPTIMIZED:balanced]" in result["optimized_content"]


class TestMockCitationTrackerAgent:
    """Test MockCitationTrackerAgent"""

    @pytest.mark.asyncio
    async def test_execute_task(self):
        """Test citation tracking task execution"""
        agent = MockCitationTrackerAgent()

        task = TaskMessage(
            task_id="test_cite_1",
            task_type="track_citations",
            agent_type=AgentType.CITATION_TRACKER,
            campaign_id="camp_test",
            input_data={
                "url": "https://example.com",
                "queries": ["query1", "query2"],
            },
            parameters={"llms": ["ChatGPT", "Claude", "Perplexity"]},
        )

        result = await agent.execute_task(task)

        assert "citations" in result
        assert "summary" in result
        assert len(result["citations"]) == 3  # 3 LLMs

        # Verify summary
        assert "citation_rate" in result["summary"]
        assert result["summary"]["total_llms"] == 3


class TestMockResearcherAgent:
    """Test MockResearcherAgent"""

    @pytest.mark.asyncio
    async def test_execute_task(self):
        """Test research task execution"""
        agent = MockResearcherAgent()

        task = TaskMessage(
            task_id="test_research_1",
            task_type="research_queries",
            agent_type=AgentType.RESEARCHER,
            campaign_id="camp_test",
            input_data={"topic": "content optimization"},
        )

        result = await agent.execute_task(task)

        assert "target_queries" in result
        assert "competitors" in result
        assert "opportunities" in result

        # Verify data types
        assert isinstance(result["target_queries"], list)
        assert isinstance(result["competitors"], list)
        assert len(result["competitors"]) > 0


class TestMockReporterAgent:
    """Test MockReporterAgent"""

    @pytest.mark.asyncio
    async def test_execute_task(self):
        """Test report generation task execution"""
        agent = MockReporterAgent()

        task = TaskMessage(
            task_id="test_report_1",
            task_type="generate_report",
            agent_type=AgentType.REPORTER,
            campaign_id="camp_test",
            input_data={"campaign_data": {}},
            parameters={"report_type": "comprehensive"},
        )

        result = await agent.execute_task(task)

        assert "markdown_report" in result
        assert "summary" in result

        # Verify markdown format
        assert result["markdown_report"].startswith("# AEO Campaign Report")
        assert "## Executive Summary" in result["markdown_report"]


class TestMockLearningAgent:
    """Test MockLearningAgent"""

    @pytest.mark.asyncio
    async def test_execute_task(self):
        """Test learning optimization task execution"""
        agent = MockLearningAgent()

        task = TaskMessage(
            task_id="test_learn_1",
            task_type="analyze_patterns",
            agent_type=AgentType.LEARNING,
            campaign_id="camp_test",
            input_data={"campaign_results": [{}]},
        )

        result = await agent.execute_task(task)

        assert "patterns_identified" in result
        assert "recommendations" in result
        assert "confidence_scores" in result

        # Verify patterns
        assert isinstance(result["patterns_identified"], list)
        assert len(result["patterns_identified"]) > 0


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])

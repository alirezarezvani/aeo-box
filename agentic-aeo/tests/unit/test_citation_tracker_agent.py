"""
Unit Tests for Citation Tracker Agent

Tests the CitationTrackerAgent class in isolation with mocked CitationTracker.
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from agents.citation_tracker_agent import CitationTrackerAgent, track_citations
from communication.protocol import AgentType, TaskMessage, TaskStatus


class TestCitationTrackerAgentInitialization:
    """Test citation tracker agent initialization"""

    def test_init_without_data_path(self):
        """Test agent initializes with default data path"""
        agent = CitationTrackerAgent()

        assert agent.agent_type == AgentType.CITATION_TRACKER
        assert agent.tracker is not None
        assert hasattr(agent, 'logger')
        assert hasattr(agent, 'config')

    def test_init_with_custom_data_path(self):
        """Test agent initializes with custom data path"""
        custom_path = ".test-data/citations.csv"
        agent = CitationTrackerAgent(data_path=custom_path)

        assert agent.agent_type == AgentType.CITATION_TRACKER
        assert agent.tracker is not None


class TestCitationTrackerAgentExecution:
    """Test citation tracker agent task execution"""

    @pytest.fixture
    def agent(self):
        """Create citation tracker agent with mocked tracker"""
        agent = CitationTrackerAgent()
        return agent

    @pytest.fixture
    def mock_tracking_result(self):
        """Mock tracking result from CitationTracker"""
        return {
            "url": "https://example.com/article",
            "timestamp": datetime.now().isoformat(),
            "llms_checked": ["ChatGPT", "Perplexity", "Claude", "Gemini", "Mistral"],
            "queries_tested": 5,
            "citations_found": 2,
            "citation_details": [
                {
                    "llm": "ChatGPT",
                    "query": "AEO best practices",
                    "cited": True,
                    "rank": 1,
                    "context": "According to example.com, AEO best practices include..."
                },
                {
                    "llm": "Perplexity",
                    "query": "Answer engine optimization",
                    "cited": True,
                    "rank": 2,
                    "context": "Example.com describes AEO as..."
                }
            ]
        }

    @pytest.mark.asyncio
    async def test_execute_task_success(self, agent, mock_tracking_result):
        """Test successful task execution"""
        with patch.object(agent.tracker, 'track_url', return_value=mock_tracking_result):
            task = TaskMessage(
                task_id="test_track_1",
                task_type="track_citations",
                agent_type=AgentType.CITATION_TRACKER,
                campaign_id="test_campaign",
                input_data={
                    "url": "https://example.com/article",
                }
            )

            result = await agent.execute_task(task)

            # Verify result structure
            assert "url" in result
            assert "llms_checked" in result
            assert "citations_found" in result
            assert result["citations_found"] == 2
            assert len(result["llms_checked"]) == 5

    @pytest.mark.asyncio
    async def test_execute_task_with_queries(self, agent, mock_tracking_result):
        """Test task execution with specific queries"""
        with patch.object(agent.tracker, 'track_url', return_value=mock_tracking_result):
            task = TaskMessage(
                task_id="test_track_2",
                task_type="track_citations",
                agent_type=AgentType.CITATION_TRACKER,
                campaign_id="test_campaign",
                input_data={
                    "url": "https://example.com/article",
                    "queries": [
                        "AEO best practices",
                        "Answer engine optimization",
                        "LLM citation strategies"
                    ]
                }
            )

            result = await agent.execute_task(task)

            assert result is not None
            assert "citations_found" in result

    @pytest.mark.asyncio
    async def test_execute_task_with_target_llms(self, agent, mock_tracking_result):
        """Test task execution with specific LLMs"""
        mock_tracking_result["llms_checked"] = ["ChatGPT", "Claude"]
        with patch.object(agent.tracker, 'track_url', return_value=mock_tracking_result):
            task = TaskMessage(
                task_id="test_track_3",
                task_type="track_citations",
                agent_type=AgentType.CITATION_TRACKER,
                campaign_id="test_campaign",
                input_data={
                    "url": "https://example.com/article",
                    "target_llms": ["ChatGPT", "Claude"]
                }
            )

            result = await agent.execute_task(task)

            assert result is not None
            assert len(result["llms_checked"]) == 2

    @pytest.mark.asyncio
    async def test_execute_task_no_citations_found(self, agent):
        """Test task execution when no citations are found"""
        mock_result = {
            "url": "https://example.com/article",
            "timestamp": datetime.now().isoformat(),
            "llms_checked": ["ChatGPT", "Perplexity"],
            "queries_tested": 3,
            "citations_found": 0,
            "citation_details": []
        }

        with patch.object(agent.tracker, 'track_url', return_value=mock_result):
            task = TaskMessage(
                task_id="test_track_4",
                task_type="track_citations",
                agent_type=AgentType.CITATION_TRACKER,
                campaign_id="test_campaign",
                input_data={"url": "https://example.com/article"}
            )

            result = await agent.execute_task(task)

            assert result is not None
            assert result["citations_found"] == 0


class TestCitationTrackerAgentValidation:
    """Test citation tracker agent input validation"""

    @pytest.fixture
    def agent(self):
        """Create citation tracker agent"""
        return CitationTrackerAgent()

    @pytest.mark.asyncio
    async def test_missing_url_raises_error(self, agent):
        """Test that missing URL raises ValueError"""
        task = TaskMessage(
            task_id="test_invalid_1",
            task_type="track_citations",
            agent_type=AgentType.CITATION_TRACKER,
            campaign_id="test_campaign",
            input_data={}  # Missing URL
        )

        with pytest.raises(ValueError, match="Missing required input: 'url'"):
            await agent.execute_task(task)

    @pytest.mark.asyncio
    async def test_empty_url_raises_error(self, agent):
        """Test that empty URL raises ValueError"""
        task = TaskMessage(
            task_id="test_invalid_2",
            task_type="track_citations",
            agent_type=AgentType.CITATION_TRACKER,
            campaign_id="test_campaign",
            input_data={"url": ""}  # Empty URL
        )

        with pytest.raises(ValueError, match="Invalid URL"):
            await agent.execute_task(task)

    @pytest.mark.asyncio
    async def test_invalid_url_type_raises_error(self, agent):
        """Test that non-string URL raises ValueError"""
        task = TaskMessage(
            task_id="test_invalid_3",
            task_type="track_citations",
            agent_type=AgentType.CITATION_TRACKER,
            campaign_id="test_campaign",
            input_data={"url": 123}  # Invalid type
        )

        with pytest.raises(ValueError, match="Invalid URL"):
            await agent.execute_task(task)


class TestCitationTrackerAgentErrorHandling:
    """Test citation tracker agent error handling"""

    @pytest.fixture
    def agent(self):
        """Create citation tracker agent"""
        return CitationTrackerAgent()

    @pytest.mark.asyncio
    async def test_tracking_exception_raises_runtime_error(self, agent):
        """Test that CitationTracker exception is wrapped in RuntimeError"""
        with patch.object(agent.tracker, 'track_url', side_effect=Exception("Tracking failed")):
            task = TaskMessage(
                task_id="test_error_1",
                task_type="track_citations",
                agent_type=AgentType.CITATION_TRACKER,
                campaign_id="test_campaign",
                input_data={"url": "https://example.com"}
            )

            with pytest.raises(RuntimeError, match="Citation tracking failed"):
                await agent.execute_task(task)

    @pytest.mark.asyncio
    async def test_tracker_error_result_raises_runtime_error(self, agent):
        """Test that error in tracker result is handled"""
        error_result = {"error": "Invalid URL"}

        with patch.object(agent.tracker, 'track_url', return_value=error_result):
            task = TaskMessage(
                task_id="test_error_2",
                task_type="track_citations",
                agent_type=AgentType.CITATION_TRACKER,
                campaign_id="test_campaign",
                input_data={"url": "https://invalid.url"}
            )

            with pytest.raises(RuntimeError, match="Invalid URL"):
                await agent.execute_task(task)


class TestCitationTrackerAgentQualityValidation:
    """Test citation tracker agent quality validation"""

    @pytest.fixture
    def agent(self):
        """Create citation tracker agent"""
        return CitationTrackerAgent()

    def test_validate_quality_complete_result(self, agent):
        """Test quality validation with complete result"""
        result = {
            "url": "https://example.com",
            "timestamp": datetime.now().isoformat(),
            "llms_checked": ["ChatGPT", "Claude"],
            "queries_tested": 5,
            "citations_found": 2,
            "citation_details": []
        }

        assert agent._validate_quality(result) is True

    def test_validate_quality_missing_keys(self, agent):
        """Test quality validation fails with missing keys"""
        result = {
            "url": "https://example.com",
            "timestamp": datetime.now().isoformat()
            # Missing llms_checked, queries_tested, etc.
        }

        assert agent._validate_quality(result) is False

    def test_validate_quality_invalid_counts(self, agent):
        """Test quality validation fails with invalid counts"""
        result = {
            "url": "https://example.com",
            "timestamp": datetime.now().isoformat(),
            "llms_checked": ["ChatGPT"],
            "queries_tested": -5,  # Invalid: negative
            "citations_found": 2,
            "citation_details": []
        }

        assert agent._validate_quality(result) is False


class TestCitationTrackerAgentHistoryRetrieval:
    """Test citation history retrieval"""

    @pytest.fixture
    def agent(self):
        """Create citation tracker agent"""
        return CitationTrackerAgent()

    @pytest.mark.asyncio
    async def test_get_citation_history_success(self, agent):
        """Test successful history retrieval"""
        mock_history = {
            "total_records": 50,
            "records": [
                {"timestamp": "2025-01-01", "url": "https://example.com", "citations": 5},
                {"timestamp": "2025-01-05", "url": "https://example.com", "citations": 8}
            ]
        }

        with patch.object(agent.tracker, 'get_history', return_value=mock_history):
            result = await agent.get_citation_history(url="https://example.com", days=30)

            assert result is not None
            assert "total_records" in result

    @pytest.mark.asyncio
    async def test_get_citation_history_with_llm_filter(self, agent):
        """Test history retrieval with LLM filter"""
        mock_history = {
            "total_records": 20,
            "records": []
        }

        with patch.object(agent.tracker, 'get_history', return_value=mock_history):
            result = await agent.get_citation_history(llm="ChatGPT", days=30)

            assert result is not None


class TestTrackCitationsHelper:
    """Test track_citations convenience function"""

    @pytest.mark.asyncio
    async def test_track_citations_quick_helper(self):
        """Test quick helper function"""
        mock_result = {
            "url": "https://example.com",
            "timestamp": datetime.now().isoformat(),
            "llms_checked": ["ChatGPT"],
            "queries_tested": 3,
            "citations_found": 1,
            "citation_details": []
        }

        with patch('agents.citation_tracker_agent.CitationTracker') as MockTracker:
            mock_tracker_instance = Mock()
            mock_tracker_instance.track_url.return_value = mock_result
            mock_tracker_instance.data_path = ".test/citations.csv"
            MockTracker.return_value = mock_tracker_instance

            result = await track_citations("https://example.com")

            assert result is not None
            assert result["citations_found"] >= 0


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])

"""
Unit Tests for Auditor Agent

Tests the AuditorAgent class in isolation with mocked ContentAnalyzer.
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from agents.auditor_agent import AuditorAgent, audit_content
from communication.protocol import AgentType, TaskMessage, TaskStatus


class TestAuditorAgentInitialization:
    """Test auditor agent initialization"""

    def test_init_without_api_manager(self):
        """Test agent initializes without API manager"""
        agent = AuditorAgent()

        assert agent.agent_type == AgentType.AUDITOR
        assert agent.content_analyzer is not None
        assert hasattr(agent, 'logger')
        assert hasattr(agent, 'config')

    def test_init_with_api_manager(self):
        """Test agent initializes with API manager"""
        mock_api_manager = Mock()
        agent = AuditorAgent(api_manager=mock_api_manager)

        assert agent.agent_type == AgentType.AUDITOR
        assert agent.content_analyzer is not None


class TestAuditorAgentExecution:
    """Test auditor agent task execution"""

    @pytest.fixture
    def agent(self):
        """Create auditor agent with mocked content analyzer"""
        agent = AuditorAgent()
        return agent

    @pytest.fixture
    def mock_analysis_result(self):
        """Mock analysis result from ContentAnalyzer"""
        return {
            "timestamp": datetime.now().isoformat(),
            "url": "https://example.com",
            "content_length": 1000,
            "word_count": 200,
            "scores": {
                "overall": 75,
                "eeat": 70,
                "structure": 80,
                "citations": 65,
                "readability": 75,
            },
            "analysis": {
                "eeat_signals": {
                    "experience_indicators": ["case study", "real-world example"],
                    "expertise_indicators": ["research", "analysis"],
                    "authority_indicators": ["published", "cited"],
                    "trust_indicators": ["sources", "references"],
                },
                "structure_analysis": {
                    "headings": 5,
                    "lists": 3,
                    "tables": 1,
                },
                "readability_metrics": {
                    "flesch_reading_ease": 75,
                    "avg_sentence_length": 15,
                },
                "entities": ["AI", "machine learning", "optimization"],
            },
            "recommendations": [
                {
                    "type": "eeat",
                    "priority": "high",
                    "message": "Add more author credentials",
                },
                {
                    "type": "structure",
                    "priority": "medium",
                    "message": "Break up long paragraphs",
                },
            ],
        }

    @pytest.mark.asyncio
    async def test_execute_task_success(self, agent, mock_analysis_result):
        """Test successful task execution"""
        # Mock ContentAnalyzer.analyze
        with patch.object(agent.content_analyzer, 'analyze', return_value=mock_analysis_result):
            task = TaskMessage(
                task_id="test_audit_1",
                task_type="audit_content",
                agent_type=AgentType.AUDITOR,
                campaign_id="test_campaign",
                input_data={
                    "content": "Test content for analysis",
                    "url": "https://example.com",
                }
            )

            result = await agent.execute_task(task)

            # Verify result structure
            assert "scores" in result
            assert "overall" in result["scores"]
            assert result["scores"]["overall"] == 75
            assert "eeat" in result["scores"]
            assert "recommendations" in result

    @pytest.mark.asyncio
    async def test_execute_task_with_minimal_input(self, agent, mock_analysis_result):
        """Test task execution with only required content input"""
        with patch.object(agent.content_analyzer, 'analyze', return_value=mock_analysis_result):
            task = TaskMessage(
                task_id="test_audit_2",
                task_type="audit_content",
                agent_type=AgentType.AUDITOR,
                campaign_id="test_campaign",
                input_data={
                    "content": "Minimal test content",
                }
            )

            result = await agent.execute_task(task)

            assert result is not None
            assert "scores" in result

    @pytest.mark.asyncio
    async def test_execute_task_with_context(self, agent, mock_analysis_result):
        """Test task execution with additional context"""
        with patch.object(agent.content_analyzer, 'analyze', return_value=mock_analysis_result):
            task = TaskMessage(
                task_id="test_audit_3",
                task_type="audit_content",
                agent_type=AgentType.AUDITOR,
                campaign_id="test_campaign",
                input_data={
                    "content": "Test content",
                    "url": "https://example.com",
                    "context": {
                        "industry": "technology",
                        "region": "US",
                    }
                }
            )

            result = await agent.execute_task(task)

            assert result is not None
            assert result["scores"]["overall"] == 75


class TestAuditorAgentValidation:
    """Test auditor agent input validation"""

    @pytest.fixture
    def agent(self):
        """Create auditor agent"""
        return AuditorAgent()

    @pytest.mark.asyncio
    async def test_missing_content_raises_error(self, agent):
        """Test that missing content raises ValueError"""
        task = TaskMessage(
            task_id="test_invalid_1",
            task_type="audit_content",
            agent_type=AgentType.AUDITOR,
            campaign_id="test_campaign",
            input_data={}  # Missing content
        )

        with pytest.raises(ValueError, match="Missing required input: 'content'"):
            await agent.execute_task(task)

    @pytest.mark.asyncio
    async def test_empty_content_raises_error(self, agent):
        """Test that empty content raises ValueError"""
        task = TaskMessage(
            task_id="test_invalid_2",
            task_type="audit_content",
            agent_type=AgentType.AUDITOR,
            campaign_id="test_campaign",
            input_data={"content": ""}  # Empty content
        )

        with pytest.raises(ValueError, match="Invalid content"):
            await agent.execute_task(task)

    @pytest.mark.asyncio
    async def test_invalid_content_type_raises_error(self, agent):
        """Test that non-string content raises ValueError"""
        task = TaskMessage(
            task_id="test_invalid_3",
            task_type="audit_content",
            agent_type=AgentType.AUDITOR,
            campaign_id="test_campaign",
            input_data={"content": 123}  # Invalid type
        )

        with pytest.raises(ValueError, match="Invalid content"):
            await agent.execute_task(task)


class TestAuditorAgentErrorHandling:
    """Test auditor agent error handling"""

    @pytest.fixture
    def agent(self):
        """Create auditor agent"""
        return AuditorAgent()

    @pytest.mark.asyncio
    async def test_analysis_exception_raises_runtime_error(self, agent):
        """Test that ContentAnalyzer exception is wrapped in RuntimeError"""
        # Mock ContentAnalyzer to raise exception
        with patch.object(agent.content_analyzer, 'analyze', side_effect=Exception("Analysis failed")):
            task = TaskMessage(
                task_id="test_error_1",
                task_type="audit_content",
                agent_type=AgentType.AUDITOR,
                campaign_id="test_campaign",
                input_data={"content": "Test content"}
            )

            with pytest.raises(RuntimeError, match="Content analysis failed"):
                await agent.execute_task(task)


class TestAuditorAgentQualityValidation:
    """Test auditor agent quality validation"""

    @pytest.fixture
    def agent(self):
        """Create auditor agent"""
        return AuditorAgent()

    def test_validate_quality_complete_result(self, agent):
        """Test quality validation with complete result"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "scores": {
                "overall": 75,
                "eeat": 70,
                "structure": 80,
                "citations": 65,
                "readability": 75,
            },
            "analysis": {"test": "data"},
            "recommendations": []
        }

        assert agent._validate_quality(result) is True

    def test_validate_quality_missing_keys(self, agent):
        """Test quality validation fails with missing keys"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "scores": {"overall": 75}
            # Missing analysis, recommendations
        }

        assert agent._validate_quality(result) is False

    def test_validate_quality_missing_scores(self, agent):
        """Test quality validation fails with incomplete scores"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "scores": {
                "overall": 75,
                # Missing eeat, structure, citations, readability
            },
            "analysis": {},
            "recommendations": []
        }

        assert agent._validate_quality(result) is False

    def test_validate_quality_invalid_score_range(self, agent):
        """Test quality validation fails with out-of-range scores"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "scores": {
                "overall": 150,  # Invalid: > 100
                "eeat": 70,
                "structure": 80,
                "citations": 65,
                "readability": 75,
            },
            "analysis": {},
            "recommendations": []
        }

        assert agent._validate_quality(result) is False


class TestAuditContentHelper:
    """Test audit_content convenience function"""

    @pytest.mark.asyncio
    async def test_audit_content_quick_helper(self):
        """Test quick helper function"""
        mock_result = {
            "timestamp": datetime.now().isoformat(),
            "scores": {
                "overall": 80,
                "eeat": 75,
                "structure": 85,
                "citations": 70,
                "readability": 80,
            },
            "analysis": {},
            "recommendations": []
        }

        # Mock ContentAnalyzer
        with patch('agents.auditor_agent.ContentAnalyzer') as MockContentAnalyzer:
            mock_analyzer_instance = Mock()
            mock_analyzer_instance.analyze.return_value = mock_result
            MockContentAnalyzer.return_value = mock_analyzer_instance

            result = await audit_content("Test content")

            assert result is not None
            assert result["scores"]["overall"] == 80


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])

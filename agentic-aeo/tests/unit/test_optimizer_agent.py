"""
Unit Tests for Optimizer Agent

Tests the OptimizerAgent class in isolation with mocked ContentOptimizer.
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from agents.optimizer_agent import OptimizerAgent, optimize_content
from communication.protocol import AgentType, TaskMessage, TaskStatus


class TestOptimizerAgentInitialization:
    """Test optimizer agent initialization"""

    def test_init_without_analyzer(self):
        """Test agent initializes without ContentAnalyzer"""
        agent = OptimizerAgent()

        assert agent.agent_type == AgentType.OPTIMIZER
        assert agent.optimizer is not None
        assert hasattr(agent, 'logger')
        assert hasattr(agent, 'config')

    def test_init_with_analyzer(self):
        """Test agent initializes with ContentAnalyzer"""
        mock_analyzer = Mock()
        agent = OptimizerAgent(content_analyzer=mock_analyzer)

        assert agent.agent_type == AgentType.OPTIMIZER
        assert agent.optimizer is not None


class TestOptimizerAgentExecution:
    """Test optimizer agent task execution"""

    @pytest.fixture
    def agent(self):
        """Create optimizer agent with mocked optimizer"""
        agent = OptimizerAgent()
        return agent

    @pytest.fixture
    def mock_optimization_result(self):
        """Mock optimization result from ContentOptimizer"""
        return {
            "original": "Original content",
            "optimized": "Optimized content with E-E-A-T signals",
            "changes": [
                {
                    "type": "eeat",
                    "description": "Added author credentials",
                    "location": "Introduction"
                },
                {
                    "type": "structure",
                    "description": "Improved heading hierarchy",
                    "location": "Section 2"
                }
            ],
            "before_score": 65,
            "after_score": 85,
            "improvement": 20,
            "strategies_applied": ["enhance_eeat", "improve_headings", "add_citations"],
        }

    @pytest.mark.asyncio
    async def test_execute_task_success(self, agent, mock_optimization_result):
        """Test successful task execution"""
        with patch.object(agent.optimizer, 'optimize', return_value=mock_optimization_result):
            task = TaskMessage(
                task_id="test_optimize_1",
                task_type="optimize_content",
                agent_type=AgentType.OPTIMIZER,
                campaign_id="test_campaign",
                input_data={
                    "content": "Original content",
                    "level": "balanced",
                }
            )

            result = await agent.execute_task(task)

            # Verify result structure
            assert "optimized" in result
            assert "before_score" in result
            assert "after_score" in result
            assert "improvement" in result
            assert result["improvement"] == 20
            assert result["after_score"] > result["before_score"]

    @pytest.mark.asyncio
    async def test_execute_task_conservative_level(self, agent, mock_optimization_result):
        """Test task execution with conservative optimization"""
        mock_optimization_result["improvement"] = 5
        with patch.object(agent.optimizer, 'optimize', return_value=mock_optimization_result):
            task = TaskMessage(
                task_id="test_optimize_2",
                task_type="optimize_content",
                agent_type=AgentType.OPTIMIZER,
                campaign_id="test_campaign",
                input_data={
                    "content": "Test content",
                    "level": "conservative",
                }
            )

            result = await agent.execute_task(task)

            assert result is not None
            assert "optimized" in result

    @pytest.mark.asyncio
    async def test_execute_task_aggressive_level(self, agent, mock_optimization_result):
        """Test task execution with aggressive optimization"""
        mock_optimization_result["improvement"] = 30
        with patch.object(agent.optimizer, 'optimize', return_value=mock_optimization_result):
            task = TaskMessage(
                task_id="test_optimize_3",
                task_type="optimize_content",
                agent_type=AgentType.OPTIMIZER,
                campaign_id="test_campaign",
                input_data={
                    "content": "Test content",
                    "level": "aggressive",
                }
            )

            result = await agent.execute_task(task)

            assert result is not None
            assert result["improvement"] >= 0

    @pytest.mark.asyncio
    async def test_execute_task_with_focus_areas(self, agent, mock_optimization_result):
        """Test task execution with specific focus areas"""
        with patch.object(agent.optimizer, 'optimize', return_value=mock_optimization_result):
            task = TaskMessage(
                task_id="test_optimize_4",
                task_type="optimize_content",
                agent_type=AgentType.OPTIMIZER,
                campaign_id="test_campaign",
                input_data={
                    "content": "Test content",
                    "level": "balanced",
                    "focus_areas": ["citations", "structure"],
                }
            )

            result = await agent.execute_task(task)

            assert result is not None
            assert "strategies_applied" in result

    @pytest.mark.asyncio
    async def test_execute_task_with_context(self, agent, mock_optimization_result):
        """Test task execution with brand context"""
        with patch.object(agent.optimizer, 'optimize', return_value=mock_optimization_result):
            task = TaskMessage(
                task_id="test_optimize_5",
                task_type="optimize_content",
                agent_type=AgentType.OPTIMIZER,
                campaign_id="test_campaign",
                input_data={
                    "content": "Test content",
                    "context": {
                        "brand_voice": "professional",
                        "industry": "technology",
                    }
                }
            )

            result = await agent.execute_task(task)

            assert result is not None


class TestOptimizerAgentValidation:
    """Test optimizer agent input validation"""

    @pytest.fixture
    def agent(self):
        """Create optimizer agent"""
        return OptimizerAgent()

    @pytest.mark.asyncio
    async def test_missing_content_raises_error(self, agent):
        """Test that missing content raises ValueError"""
        task = TaskMessage(
            task_id="test_invalid_1",
            task_type="optimize_content",
            agent_type=AgentType.OPTIMIZER,
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
            task_type="optimize_content",
            agent_type=AgentType.OPTIMIZER,
            campaign_id="test_campaign",
            input_data={"content": ""}  # Empty content
        )

        with pytest.raises(ValueError, match="Invalid content"):
            await agent.execute_task(task)

    @pytest.mark.asyncio
    async def test_invalid_level_raises_error(self, agent):
        """Test that invalid optimization level raises ValueError"""
        task = TaskMessage(
            task_id="test_invalid_3",
            task_type="optimize_content",
            agent_type=AgentType.OPTIMIZER,
            campaign_id="test_campaign",
            input_data={
                "content": "Test content",
                "level": "extreme"  # Invalid level
            }
        )

        with pytest.raises(ValueError, match="Invalid level"):
            await agent.execute_task(task)


class TestOptimizerAgentErrorHandling:
    """Test optimizer agent error handling"""

    @pytest.fixture
    def agent(self):
        """Create optimizer agent"""
        return OptimizerAgent()

    @pytest.mark.asyncio
    async def test_optimization_exception_raises_runtime_error(self, agent):
        """Test that ContentOptimizer exception is wrapped in RuntimeError"""
        with patch.object(agent.optimizer, 'optimize', side_effect=Exception("Optimization failed")):
            task = TaskMessage(
                task_id="test_error_1",
                task_type="optimize_content",
                agent_type=AgentType.OPTIMIZER,
                campaign_id="test_campaign",
                input_data={"content": "Test content"}
            )

            with pytest.raises(RuntimeError, match="Content optimization failed"):
                await agent.execute_task(task)


class TestOptimizerAgentQualityValidation:
    """Test optimizer agent quality validation"""

    @pytest.fixture
    def agent(self):
        """Create optimizer agent"""
        return OptimizerAgent()

    def test_validate_quality_complete_result(self, agent):
        """Test quality validation with complete result"""
        result = {
            "original": "Original",
            "optimized": "Optimized",
            "changes": [],
            "before_score": 70,
            "after_score": 85,
            "improvement": 15,
            "strategies_applied": ["add_structure"]
        }

        assert agent._validate_quality(result) is True

    def test_validate_quality_missing_keys(self, agent):
        """Test quality validation fails with missing keys"""
        result = {
            "original": "Original",
            "optimized": "Optimized"
            # Missing changes, scores, etc.
        }

        assert agent._validate_quality(result) is False

    def test_validate_quality_invalid_score_range(self, agent):
        """Test quality validation fails with out-of-range scores"""
        result = {
            "original": "Original",
            "optimized": "Optimized",
            "changes": [],
            "before_score": 150,  # Invalid: > 100
            "after_score": 85,
            "improvement": -65,
            "strategies_applied": []
        }

        assert agent._validate_quality(result) is False

    def test_validate_quality_incorrect_improvement(self, agent):
        """Test quality validation fails with incorrect improvement calculation"""
        result = {
            "original": "Original",
            "optimized": "Optimized",
            "changes": [],
            "before_score": 70,
            "after_score": 85,
            "improvement": 10,  # Should be 15
            "strategies_applied": []
        }

        assert agent._validate_quality(result) is False


class TestOptimizeContentHelper:
    """Test optimize_content convenience function"""

    @pytest.mark.asyncio
    async def test_optimize_content_quick_helper(self):
        """Test quick helper function"""
        mock_result = {
            "original": "Test",
            "optimized": "Optimized Test",
            "changes": [],
            "before_score": 70,
            "after_score": 85,
            "improvement": 15,
            "strategies_applied": ["enhance_eeat"]
        }

        with patch('agents.optimizer_agent.ContentOptimizer') as MockOptimizer:
            mock_optimizer_instance = Mock()
            mock_optimizer_instance.optimize.return_value = mock_result
            MockOptimizer.return_value = mock_optimizer_instance

            result = await optimize_content("Test content")

            assert result is not None
            assert result["improvement"] == 15


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])

"""
Optimizer and Citation Tracker Integration Tests

Tests both agents with real modules and orchestrator integration.
"""

import pytest
import asyncio
from pathlib import Path
import sys
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from agents.optimizer_agent import OptimizerAgent, optimize_content
from agents.citation_tracker_agent import CitationTrackerAgent, track_citations
from agents.orchestrator_agent import OrchestratorAgent
from communication.protocol import AgentType, TaskMessage, TaskStatus


# Sample content for testing
SAMPLE_CONTENT = """
# Guide to AEO

Answer Engine Optimization helps content get cited by LLMs.

## Benefits

- More visibility
- Higher authority
"""


class TestOptimizerAgentRealOptimization:
    """Test optimizer agent with real ContentOptimizer"""

    @pytest.fixture
    def agent(self):
        """Create real optimizer agent"""
        return OptimizerAgent()

    @pytest.mark.asyncio
    async def test_optimize_real_content(self, agent):
        """Test optimizing real content"""
        task = TaskMessage(
            task_id="integration_optimize_1",
            task_type="optimize_content",
            agent_type=AgentType.OPTIMIZER,
            campaign_id="integration_campaign",
            input_data={
                "content": SAMPLE_CONTENT,
                "level": "balanced",
            }
        )

        result = await agent.execute_task(task)

        # Verify result structure
        assert "original" in result
        assert "optimized" in result
        assert "before_score" in result
        assert "after_score" in result
        assert "improvement" in result
        assert "strategies_applied" in result

        # Verify optimization occurred
        assert isinstance(result["improvement"], (int, float))

    @pytest.mark.asyncio
    async def test_optimize_conservative_level(self, agent):
        """Test conservative optimization"""
        task = TaskMessage(
            task_id="integration_optimize_2",
            task_type="optimize_content",
            agent_type=AgentType.OPTIMIZER,
            campaign_id="integration_campaign",
            input_data={
                "content": SAMPLE_CONTENT,
                "level": "conservative",
            }
        )

        result = await agent.execute_task(task)

        assert result is not None
        assert "optimized" in result

    @pytest.mark.asyncio
    async def test_optimize_aggressive_level(self, agent):
        """Test aggressive optimization"""
        task = TaskMessage(
            task_id="integration_optimize_3",
            task_type="optimize_content",
            agent_type=AgentType.OPTIMIZER,
            campaign_id="integration_campaign",
            input_data={
                "content": SAMPLE_CONTENT,
                "level": "aggressive",
            }
        )

        result = await agent.execute_task(task)

        assert result is not None
        assert result["after_score"] >= result["before_score"]


class TestCitationTrackerAgentRealTracking:
    """Test citation tracker agent with real CitationTracker"""

    @pytest.fixture
    def agent(self):
        """Create real citation tracker agent"""
        return CitationTrackerAgent(data_path=".test-data/citations.csv")

    @pytest.mark.asyncio
    async def test_track_real_url(self, agent):
        """Test tracking real URL"""
        task = TaskMessage(
            task_id="integration_track_1",
            task_type="track_citations",
            agent_type=AgentType.CITATION_TRACKER,
            campaign_id="integration_campaign",
            input_data={
                "url": "https://example.com/article",
            }
        )

        result = await agent.execute_task(task)

        # Verify result structure
        assert "url" in result
        assert "timestamp" in result
        assert "llms_checked" in result
        assert "queries_tested" in result
        assert "citations_found" in result
        assert "citation_details" in result

        # Verify tracking data
        assert isinstance(result["llms_checked"], list)
        assert len(result["llms_checked"]) > 0

    @pytest.mark.asyncio
    async def test_track_with_queries(self, agent):
        """Test tracking with specific queries"""
        task = TaskMessage(
            task_id="integration_track_2",
            task_type="track_citations",
            agent_type=AgentType.CITATION_TRACKER,
            campaign_id="integration_campaign",
            input_data={
                "url": "https://example.com/article",
                "queries": [
                    "AEO best practices",
                    "Answer engine optimization"
                ]
            }
        )

        result = await agent.execute_task(task)

        assert result is not None
        assert result["queries_tested"] >= 0


class TestOptimizerOrchestratorIntegration:
    """Test optimizer agent integration with orchestrator"""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator with real optimizer agent"""
        orch = OrchestratorAgent()
        orch.register_agent(AgentType.OPTIMIZER, OptimizerAgent())
        return orch

    @pytest.mark.asyncio
    async def test_orchestrator_calls_optimizer(self, orchestrator):
        """Test orchestrator can execute optimizer agent"""
        # Create campaign
        campaign_id = orchestrator.campaign_store.create_campaign(
            workflow_name="test-optimizer-integration",
            parameters={},
            total_tasks=1,
        )

        # Create optimization task
        task = TaskMessage(
            task_id="orch_optimize_1",
            task_type="optimize_content",
            agent_type=AgentType.OPTIMIZER,
            campaign_id=campaign_id,
            input_data={
                "content": SAMPLE_CONTENT,
                "level": "balanced",
            }
        )

        # Execute task through orchestrator
        result = await orchestrator._execute_single_task(campaign_id, task)

        # Verify result
        assert result.status == TaskStatus.COMPLETED
        assert result.output_data is not None
        assert "optimized" in result.output_data


class TestCitationTrackerOrchestratorIntegration:
    """Test citation tracker agent integration with orchestrator"""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator with real citation tracker agent"""
        orch = OrchestratorAgent()
        orch.register_agent(AgentType.CITATION_TRACKER, CitationTrackerAgent(data_path=".test-data/citations.csv"))
        return orch

    @pytest.mark.asyncio
    async def test_orchestrator_calls_citation_tracker(self, orchestrator):
        """Test orchestrator can execute citation tracker agent"""
        # Create campaign
        campaign_id = orchestrator.campaign_store.create_campaign(
            workflow_name="test-citation-integration",
            parameters={},
            total_tasks=1,
        )

        # Create tracking task
        task = TaskMessage(
            task_id="orch_track_1",
            task_type="track_citations",
            agent_type=AgentType.CITATION_TRACKER,
            campaign_id=campaign_id,
            input_data={
                "url": "https://example.com/article",
            }
        )

        # Execute task through orchestrator
        result = await orchestrator._execute_single_task(campaign_id, task)

        # Verify result
        assert result.status == TaskStatus.COMPLETED
        assert result.output_data is not None
        assert "llms_checked" in result.output_data


class TestBothAgentsParallelExecution:
    """Test both agents executing in parallel"""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator with both agents"""
        orch = OrchestratorAgent()
        orch.register_agent(AgentType.OPTIMIZER, OptimizerAgent())
        orch.register_agent(AgentType.CITATION_TRACKER, CitationTrackerAgent(data_path=".test-data/citations.csv"))
        return orch

    @pytest.mark.asyncio
    async def test_parallel_optimization_and_tracking(self, orchestrator):
        """Test running optimizer and citation tracker in parallel"""
        # Create campaign
        campaign_id = orchestrator.campaign_store.create_campaign(
            workflow_name="test-parallel-agents",
            parameters={},
            total_tasks=2,
        )

        # Create tasks for both agents
        tasks = [
            TaskMessage(
                task_id="parallel_optimize",
                task_type="optimize_content",
                agent_type=AgentType.OPTIMIZER,
                campaign_id=campaign_id,
                input_data={
                    "content": SAMPLE_CONTENT,
                    "level": "balanced",
                }
            ),
            TaskMessage(
                task_id="parallel_track",
                task_type="track_citations",
                agent_type=AgentType.CITATION_TRACKER,
                campaign_id=campaign_id,
                input_data={
                    "url": "https://example.com/article",
                }
            ),
        ]

        # Execute in parallel
        start = time.time()
        results = await orchestrator._execute_parallel_tasks(campaign_id, tasks)
        duration = time.time() - start

        # Verify all completed
        assert len(results) == 2
        assert all(r.status == TaskStatus.COMPLETED for r in results)

        # Verify parallel execution (should be faster than sequential)
        assert duration < 10.0  # Generous threshold


class TestHelperFunctions:
    """Test helper functions with real modules"""

    @pytest.mark.asyncio
    async def test_optimize_content_helper(self):
        """Test optimize_content helper function"""
        result = await optimize_content(SAMPLE_CONTENT, level="balanced")

        # Verify result
        assert "optimized" in result
        assert "improvement" in result

    @pytest.mark.asyncio
    async def test_track_citations_helper(self):
        """Test track_citations helper function"""
        result = await track_citations(
            "https://example.com/article",
            data_path=".test-data/citations.csv"
        )

        # Verify result
        assert "llms_checked" in result
        assert "citations_found" in result


class TestPerformanceCharacteristics:
    """Test performance characteristics of both agents"""

    @pytest.fixture
    def optimizer_agent(self):
        """Create optimizer agent"""
        return OptimizerAgent()

    @pytest.fixture
    def tracker_agent(self):
        """Create citation tracker agent"""
        return CitationTrackerAgent(data_path=".test-data/citations.csv")

    @pytest.mark.asyncio
    async def test_optimizer_completes_within_timeout(self, optimizer_agent):
        """Test optimizer completes within reasonable time"""
        task = TaskMessage(
            task_id="perf_optimize_1",
            task_type="optimize_content",
            agent_type=AgentType.OPTIMIZER,
            campaign_id="perf_campaign",
            input_data={
                "content": SAMPLE_CONTENT * 3,  # 3x longer content
                "level": "balanced",
            },
            timeout_seconds=30.0,
        )

        start = time.time()
        result = await optimizer_agent.execute_task(task)
        duration = time.time() - start

        # Should complete well within timeout
        assert result is not None
        assert duration < 10.0  # Should be much faster than 30s

    @pytest.mark.asyncio
    async def test_tracker_completes_within_timeout(self, tracker_agent):
        """Test tracker completes within reasonable time"""
        task = TaskMessage(
            task_id="perf_track_1",
            task_type="track_citations",
            agent_type=AgentType.CITATION_TRACKER,
            campaign_id="perf_campaign",
            input_data={
                "url": "https://example.com/article",
            },
            timeout_seconds=30.0,
        )

        start = time.time()
        result = await tracker_agent.execute_task(task)
        duration = time.time() - start

        # Should complete well within timeout
        assert result is not None
        assert duration < 10.0


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])

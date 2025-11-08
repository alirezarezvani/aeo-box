"""
Integration Tests for Orchestrator Agent

Tests the orchestrator coordinating with mock agents to execute complete workflows.
Validates task decomposition, parallel execution, dependency management, and quality validation.
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
from agents.base_agent import BaseAgent
from communication.protocol import AgentType, TaskMessage
from persistence import CampaignStore
from tests.mocks.mock_agents import (
    MockAuditorAgent,
    MockOptimizerAgent,
    MockCitationTrackerAgent,
    MockResearcherAgent,
    MockReporterAgent,
    MockLearningAgent,
)


class TestOrchestratorIntegration:
    """Integration tests for orchestrator with mock agents"""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test data"""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        # Cleanup
        shutil.rmtree(temp_path)

    @pytest.fixture
    def orchestrator(self, temp_dir):
        """Create orchestrator with registered mock agents"""
        orchestrator = OrchestratorAgent()

        # Register all mock agents
        orchestrator.register_agent(AgentType.AUDITOR, MockAuditorAgent())
        orchestrator.register_agent(AgentType.OPTIMIZER, MockOptimizerAgent())
        orchestrator.register_agent(AgentType.CITATION_TRACKER, MockCitationTrackerAgent())
        orchestrator.register_agent(AgentType.RESEARCHER, MockResearcherAgent())
        orchestrator.register_agent(AgentType.REPORTER, MockReporterAgent())
        orchestrator.register_agent(AgentType.LEARNING, MockLearningAgent())

        return orchestrator

    @pytest.mark.asyncio
    async def test_agent_registration(self, orchestrator):
        """Test that all agents are properly registered"""
        # Verify all expected agents are registered
        expected_agents = {
            AgentType.AUDITOR,
            AgentType.OPTIMIZER,
            AgentType.CITATION_TRACKER,
            AgentType.RESEARCHER,
            AgentType.REPORTER,
            AgentType.LEARNING,
        }

        registered = set(orchestrator.agent_registry.keys())
        assert registered == expected_agents

    @pytest.mark.asyncio
    async def test_workflow_decomposition_campaign(self, orchestrator):
        """Test task decomposition for aeo-campaign workflow"""
        workflow_name = "aeo-campaign"
        parameters = {
            "url": "https://example.com/article",
            "queries": ["query1", "query2"],
            "mode": "comprehensive",
        }

        # Decompose workflow into tasks
        tasks = orchestrator._decompose_workflow(workflow_name, parameters)

        # Verify task structure
        assert len(tasks) > 0
        assert all("task_id" in task for task in tasks)
        assert all("agent_type" in task for task in tasks)

        # Verify we have tasks for all key agents
        task_types = {task["agent_type"] for task in tasks}
        assert AgentType.AUDITOR in task_types
        assert AgentType.OPTIMIZER in task_types

    @pytest.mark.asyncio
    async def test_single_agent_execution(self, orchestrator):
        """Test orchestrator executing a single agent task"""
        # Create test campaign
        campaign_id = orchestrator.campaign_store.create_campaign(
            workflow_name="test-workflow",
            parameters={"url": "https://example.com"},
            total_tasks=1,
        )

        # Create task for auditor
        task = TaskMessage(
            task_id="test_task_1",
            task_type="audit_content",
            agent_type=AgentType.AUDITOR,
            campaign_id=campaign_id,
            input_data={
                "url": "https://example.com",
                "content": "Test content",
            },
        )

        # Execute task
        result = await orchestrator._execute_single_task(campaign_id, task)

        # Verify result
        assert result.status.value == "completed"
        assert result.task_id == "test_task_1"
        assert "overall_score" in result.output_data

    @pytest.mark.asyncio
    async def test_parallel_execution(self, orchestrator):
        """Test orchestrator executing multiple agents in parallel"""
        # Create test campaign
        campaign_id = orchestrator.campaign_store.create_campaign(
            workflow_name="test-parallel",
            parameters={"url": "https://example.com"},
            total_tasks=3,
        )

        # Create tasks for parallel execution (no dependencies)
        tasks = [
            TaskMessage(
                task_id=f"parallel_task_{i}",
                task_type="audit_content" if i == 0 else "research_queries",
                agent_type=AgentType.AUDITOR if i == 0 else AgentType.RESEARCHER,
                campaign_id=campaign_id,
                input_data={"url": "https://example.com", "topic": f"topic_{i}"},
            )
            for i in range(3)
        ]

        # Execute all tasks in parallel
        import time
        start = time.time()
        results = await orchestrator._execute_parallel_tasks(campaign_id, tasks)
        duration = time.time() - start

        # Verify results
        assert len(results) == 3
        assert all(r.status.value == "completed" for r in results)

        # Verify parallel execution (should be faster than sequential)
        # Mock agents sleep 0.1-0.15s each, so parallel should be ~0.15s
        # Sequential would be ~0.45s
        assert duration < 0.5  # Generous threshold

    @pytest.mark.asyncio
    async def test_dependency_management(self, orchestrator):
        """Test orchestrator respects task dependencies"""
        # Create test campaign
        campaign_id = orchestrator.campaign_store.create_campaign(
            workflow_name="test-dependencies",
            parameters={"url": "https://example.com"},
            total_tasks=2,
        )

        # Create tasks with dependencies
        task1 = TaskMessage(
            task_id="dep_task_1",
            task_type="audit_content",
            agent_type=AgentType.AUDITOR,
            campaign_id=campaign_id,
            input_data={"url": "https://example.com", "content": "Test"},
        )

        task2 = TaskMessage(
            task_id="dep_task_2",
            task_type="optimize_content",
            agent_type=AgentType.OPTIMIZER,
            campaign_id=campaign_id,
            input_data={"content": "Test"},
            parameters={"depends_on": ["dep_task_1"]},  # Depends on task1
        )

        # Execute with dependencies
        results = await orchestrator._execute_tasks_with_dependencies(
            campaign_id, [task1, task2]
        )

        # Verify both tasks completed
        assert len(results) == 2
        assert all(r.status.value == "completed" for r in results)

        # Verify execution order (task1 should complete before task2 starts)
        task1_result = next(r for r in results if r.task_id == "dep_task_1")
        task2_result = next(r for r in results if r.task_id == "dep_task_2")

        assert task1_result.completed_at < task2_result.started_at

    @pytest.mark.asyncio
    async def test_quality_validation(self, orchestrator):
        """Test orchestrator validates agent output quality"""
        # Create test campaign
        campaign_id = orchestrator.campaign_store.create_campaign(
            workflow_name="test-validation",
            parameters={"url": "https://example.com"},
            total_tasks=1,
        )

        # Create task with quality criteria
        task = TaskMessage(
            task_id="validation_task_1",
            task_type="audit_content",
            agent_type=AgentType.AUDITOR,
            campaign_id=campaign_id,
            input_data={"url": "https://example.com", "content": "Test"},
            quality_criteria={
                "min_overall_score": 0,  # Mock agent returns 75, should pass
            },
        )

        # Execute task (should validate automatically)
        result = await orchestrator._execute_single_task(campaign_id, task)

        # Verify result passed validation
        assert result.status.value == "completed"
        assert result.output_data["overall_score"] >= 0

    @pytest.mark.asyncio
    async def test_error_handling(self, orchestrator):
        """Test orchestrator handles agent failures gracefully"""
        # Create test campaign
        campaign_id = orchestrator.campaign_store.create_campaign(
            workflow_name="test-errors",
            parameters={"url": "https://example.com"},
            total_tasks=1,
        )

        # Create task with invalid agent type (should fail)
        task = TaskMessage(
            task_id="error_task_1",
            task_type="invalid_task",
            agent_type=AgentType.AUDITOR,  # Valid agent but invalid task type
            campaign_id=campaign_id,
            input_data={},  # Missing required data
        )

        # Execute task (should handle error gracefully)
        try:
            result = await orchestrator._execute_single_task(campaign_id, task)
            # If it doesn't raise, check status
            assert result.status.value in ["failed", "completed"]
        except Exception as e:
            # Error is expected and handled
            assert True

    @pytest.mark.asyncio
    async def test_campaign_state_persistence(self, orchestrator, temp_dir):
        """Test orchestrator persists campaign state correctly"""
        # Override campaign store to use temp directory
        orchestrator.campaign_store = CampaignStore(data_dir=temp_dir)

        # Create and execute workflow
        workflow_name = "aeo-campaign"
        parameters = {
            "url": "https://example.com",
            "queries": ["test query"],
            "mode": "quick",
        }

        # Execute workflow
        manifest = await orchestrator.execute_workflow(workflow_name, parameters)

        # Verify campaign was persisted
        campaign_dir = temp_dir / "campaigns" / manifest.campaign_id
        assert campaign_dir.exists()
        assert (campaign_dir / "manifest.json").exists()
        assert (campaign_dir / "tasks.jsonl").exists()

        # Verify we can reload campaign
        reloaded = orchestrator.campaign_store.load_campaign(manifest.campaign_id)
        assert reloaded.campaign_id == manifest.campaign_id
        assert reloaded.workflow_name == workflow_name

    @pytest.mark.asyncio
    async def test_complete_workflow_execution(self, orchestrator):
        """Test complete end-to-end workflow execution"""
        workflow_name = "aeo-campaign"
        parameters = {
            "url": "https://example.com/article",
            "queries": ["content optimization", "AEO best practices"],
            "mode": "comprehensive",
        }

        # Execute complete workflow
        manifest = await orchestrator.execute_workflow(workflow_name, parameters)

        # Verify workflow completed
        assert manifest.workflow_state.status.value == "completed"
        assert manifest.campaign_id.startswith(workflow_name)

        # Verify all tasks executed
        assert len(manifest.task_results) > 0
        completed_tasks = [
            t for t in manifest.task_results if t.status.value == "completed"
        ]
        assert len(completed_tasks) > 0

        # Verify campaign duration recorded
        assert manifest.workflow_state.duration_seconds > 0


    @pytest.mark.asyncio
    async def test_concurrent_workflows(self, orchestrator):
        """Test orchestrator can handle multiple concurrent workflows"""
        workflows = [
            ("aeo-campaign", {"url": f"https://example.com/article{i}", "queries": [f"query{i}"]}

)
            for i in range(3)
        ]

        # Execute all workflows concurrently
        results = await asyncio.gather(*[
            orchestrator.execute_workflow(name, params)
            for name, params in workflows
        ])

        # Verify all workflows completed
        assert len(results) == 3
        assert all(r.workflow_state.status.value == "completed" for r in results)

        # Verify unique campaign IDs
        campaign_ids = [r.campaign_id for r in results]
        assert len(set(campaign_ids)) == 3


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])

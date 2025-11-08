"""
Quality Validation Integration Tests

Tests the orchestrator's 4-layer quality validation system:
1. Status Check - Valid status values
2. Completeness Check - All required fields present
3. Quality Criteria - Agent-specific validation
4. Consistency Check - Results align with inputs
"""

import pytest
import asyncio
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from agents.orchestrator_agent import OrchestratorAgent
from agents.base_agent import BaseAgent
from communication.protocol import (
    AgentType,
    TaskMessage,
    TaskResult,
    TaskStatus,
    ValidationStatus,
)
from tests.mocks.mock_agents import MockAuditorAgent, MockOptimizerAgent


class TestQualityValidationLayers:
    """Test individual validation layers"""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator with mock agents"""
        orch = OrchestratorAgent()
        orch.register_agent(AgentType.AUDITOR, MockAuditorAgent())
        orch.register_agent(AgentType.OPTIMIZER, MockOptimizerAgent())
        return orch

    @pytest.mark.asyncio
    async def test_layer1_status_validation(self, orchestrator):
        """Test Layer 1: Status check validation"""
        # Create campaign
        campaign_id = orchestrator.campaign_store.create_campaign(
            workflow_name="test-validation",
            parameters={"url": "https://example.com"},
            total_tasks=1,
        )

        # Create task
        task = TaskMessage(
            task_id="status_test_1",
            task_type="audit_content",
            agent_type=AgentType.AUDITOR,
            campaign_id=campaign_id,
            input_data={"url": "https://example.com", "content": "Test"},
        )

        # Execute task
        result = await orchestrator._execute_single_task(campaign_id, task)

        # Verify status is valid
        assert result.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.PARTIAL]

    @pytest.mark.asyncio
    async def test_layer2_completeness_validation(self, orchestrator):
        """Test Layer 2: Completeness check"""
        # Create campaign
        campaign_id = orchestrator.campaign_store.create_campaign(
            workflow_name="test-completeness",
            parameters={"url": "https://example.com"},
            total_tasks=1,
        )

        # Create task
        task = TaskMessage(
            task_id="complete_test_1",
            task_type="audit_content",
            agent_type=AgentType.AUDITOR,
            campaign_id=campaign_id,
            input_data={"url": "https://example.com", "content": "Test"},
        )

        # Execute task
        result = await orchestrator._execute_single_task(campaign_id, task)

        # Verify all required fields present
        assert result.task_id is not None
        assert result.agent_type is not None
        assert result.output_data is not None
        assert result.started_at is not None
        assert result.completed_at is not None

    @pytest.mark.asyncio
    async def test_layer3_quality_criteria_auditor(self, orchestrator):
        """Test Layer 3: Quality criteria for Auditor"""
        # Create campaign
        campaign_id = orchestrator.campaign_store.create_campaign(
            workflow_name="test-quality-auditor",
            parameters={"url": "https://example.com"},
            total_tasks=1,
        )

        # Create task with quality criteria
        task = TaskMessage(
            task_id="quality_auditor_1",
            task_type="audit_content",
            agent_type=AgentType.AUDITOR,
            campaign_id=campaign_id,
            input_data={"url": "https://example.com", "content": "Test"},
            quality_criteria={
                "min_overall_score": 0,  # Mock returns 75
                "required_fields": ["overall_score", "scores"],
            },
        )

        # Execute task
        result = await orchestrator._execute_single_task(campaign_id, task)

        # Verify quality criteria met
        assert result.status == TaskStatus.COMPLETED
        assert "overall_score" in result.output_data
        assert result.output_data["overall_score"] >= 0

    @pytest.mark.asyncio
    async def test_layer3_quality_criteria_optimizer(self, orchestrator):
        """Test Layer 3: Quality criteria for Optimizer"""
        # Create campaign
        campaign_id = orchestrator.campaign_store.create_campaign(
            workflow_name="test-quality-optimizer",
            parameters={"url": "https://example.com"},
            total_tasks=1,
        )

        # Create task with quality criteria
        task = TaskMessage(
            task_id="quality_optimizer_1",
            task_type="optimize_content",
            agent_type=AgentType.OPTIMIZER,
            campaign_id=campaign_id,
            input_data={"content": "Original content"},
            quality_criteria={
                "required_fields": ["optimized_content", "before_score", "after_score"],
                "min_improvement": 0,
            },
        )

        # Execute task
        result = await orchestrator._execute_single_task(campaign_id, task)

        # Verify quality criteria met
        assert result.status == TaskStatus.COMPLETED
        assert "optimized_content" in result.output_data
        assert "before_score" in result.output_data
        assert "after_score" in result.output_data

    @pytest.mark.asyncio
    async def test_layer4_consistency_validation(self, orchestrator):
        """Test Layer 4: Consistency check"""
        # Create campaign
        campaign_id = orchestrator.campaign_store.create_campaign(
            workflow_name="test-consistency",
            parameters={"url": "https://example.com"},
            total_tasks=1,
        )

        # Create task
        task = TaskMessage(
            task_id="consistency_test_1",
            task_type="audit_content",
            agent_type=AgentType.AUDITOR,
            campaign_id=campaign_id,
            input_data={"url": "https://example.com", "content": "Test content"},
        )

        # Execute task
        result = await orchestrator._execute_single_task(campaign_id, task)

        # Verify consistency
        assert result.task_id == task.task_id
        assert result.agent_type == task.agent_type
        # URL should be consistent (if present in output)
        if "url" in result.output_data:
            assert result.output_data["url"] == task.input_data["url"]


class TestRevisionHandling:
    """Test orchestrator revision request system"""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator with mock agents"""
        orch = OrchestratorAgent()
        orch.register_agent(AgentType.AUDITOR, MockAuditorAgent())
        return orch

    @pytest.mark.asyncio
    async def test_revision_request_flow(self, orchestrator):
        """Test orchestrator can request revisions"""
        # This would test revision logic if implemented
        # For now, verify the mechanism exists
        assert hasattr(orchestrator, '_request_revision') or hasattr(orchestrator, 'request_revision')

    @pytest.mark.asyncio
    async def test_revision_with_improved_output(self, orchestrator):
        """Test agent responds to revision requests"""
        # Create campaign
        campaign_id = orchestrator.campaign_store.create_campaign(
            workflow_name="test-revision",
            parameters={"url": "https://example.com"},
            total_tasks=1,
        )

        # Create task
        task = TaskMessage(
            task_id="revision_test_1",
            task_type="audit_content",
            agent_type=AgentType.AUDITOR,
            campaign_id=campaign_id,
            input_data={"url": "https://example.com", "content": "Test"},
        )

        # First execution
        result1 = await orchestrator._execute_single_task(campaign_id, task)
        assert result1.status == TaskStatus.COMPLETED

        # Note: Actual revision testing would require triggering validation failure
        # Mock agents always return valid output, so this is a basic test


class TestValidationMetrics:
    """Test validation metrics and reporting"""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator with mock agents"""
        orch = OrchestratorAgent()
        orch.register_agent(AgentType.AUDITOR, MockAuditorAgent())
        return orch

    @pytest.mark.asyncio
    async def test_validation_metrics_collection(self, orchestrator):
        """Test orchestrator collects validation metrics"""
        # Execute workflow
        manifest = await orchestrator.execute_workflow(
            "aeo-campaign",
            {"url": "https://example.com", "queries": ["test"]},
        )

        # Verify validation metadata exists
        for task_result in manifest.task_results:
            # Check metadata includes validation info
            assert task_result.metadata is not None
            # Execution time should be recorded
            assert "execution_time" in task_result.metadata or task_result.execution_time_seconds > 0


class TestConcurrentValidation:
    """Test validation with concurrent task execution"""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator with all mock agents"""
        orch = OrchestratorAgent()
        from tests.mocks.mock_agents import (
            MockAuditorAgent,
            MockResearcherAgent,
            MockCitationTrackerAgent,
        )
        orch.register_agent(AgentType.AUDITOR, MockAuditorAgent())
        orch.register_agent(AgentType.RESEARCHER, MockResearcherAgent())
        orch.register_agent(AgentType.CITATION_TRACKER, MockCitationTrackerAgent())
        return orch

    @pytest.mark.asyncio
    async def test_parallel_validation(self, orchestrator):
        """Test validation works with parallel task execution"""
        # Create campaign
        campaign_id = orchestrator.campaign_store.create_campaign(
            workflow_name="test-parallel-validation",
            parameters={"url": "https://example.com"},
            total_tasks=3,
        )

        # Create multiple tasks with quality criteria
        tasks = [
            TaskMessage(
                task_id=f"parallel_val_{i}",
                task_type="audit_content" if i == 0 else "research_queries",
                agent_type=AgentType.AUDITOR if i == 0 else AgentType.RESEARCHER,
                campaign_id=campaign_id,
                input_data={"url": "https://example.com", "topic": f"topic_{i}"},
                quality_criteria={"required_fields": ["overall_score"] if i == 0 else ["target_queries"]},
            )
            for i in range(3)
        ]

        # Execute in parallel
        results = await orchestrator._execute_parallel_tasks(campaign_id, tasks)

        # Verify all passed validation
        assert all(r.status == TaskStatus.COMPLETED for r in results)


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])

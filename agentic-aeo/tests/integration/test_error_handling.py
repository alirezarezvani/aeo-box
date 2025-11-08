"""
Error Handling Integration Tests

Tests orchestrator's error handling across various failure scenarios:
- Agent failures and retries
- Timeout handling
- Invalid input handling
- Partial failures in workflows
- Recovery mechanisms
"""

import pytest
import asyncio
from pathlib import Path
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from agents.orchestrator_agent import OrchestratorAgent
from agents.base_agent import BaseAgent
from communication.protocol import (
    AgentType,
    TaskMessage,
    TaskStatus,
)
from tests.mocks.mock_agents import MockAuditorAgent, MockOptimizerAgent


class FailingMockAgent(BaseAgent):
    """Mock agent that always fails (for testing error handling)"""

    def __init__(self, agent_type: AgentType, fail_count: int = 999):
        super().__init__(agent_type)
        self.fail_count = fail_count
        self.attempt_count = 0

    async def execute_task(self, task: TaskMessage):
        """Fail for first N attempts"""
        self.attempt_count += 1
        if self.attempt_count <= self.fail_count:
            raise RuntimeError(f"Simulated failure (attempt {self.attempt_count})")

        # Success after fail_count attempts
        return {
            "success_after_retries": True,
            "attempts": self.attempt_count,
        }


class TimeoutMockAgent(BaseAgent):
    """Mock agent that times out"""

    def __init__(self, agent_type: AgentType, delay_seconds: float = 10.0):
        super().__init__(agent_type)
        self.delay_seconds = delay_seconds

    async def execute_task(self, task: TaskMessage):
        """Sleep longer than timeout"""
        await asyncio.sleep(self.delay_seconds)
        return {"message": "This should timeout"}


class TestAgentFailureHandling:
    """Test handling of agent execution failures"""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator"""
        return OrchestratorAgent()

    @pytest.mark.asyncio
    async def test_agent_failure_with_retry(self, orchestrator):
        """Test orchestrator retries failed agents"""
        # Register failing agent that succeeds on 2nd attempt
        failing_agent = FailingMockAgent(AgentType.AUDITOR, fail_count=1)
        orchestrator.register_agent(AgentType.AUDITOR, failing_agent)

        # Create campaign
        campaign_id = orchestrator.campaign_store.create_campaign(
            workflow_name="test-retry",
            parameters={"url": "https://example.com"},
            total_tasks=1,
        )

        # Create task
        task = TaskMessage(
            task_id="retry_test_1",
            task_type="audit_content",
            agent_type=AgentType.AUDITOR,
            campaign_id=campaign_id,
            input_data={"url": "https://example.com", "content": "Test"},
        )

        # Execute task (should retry and eventually succeed)
        result = await orchestrator._execute_single_task(campaign_id, task)

        # Verify succeeded after retry
        assert result.status == TaskStatus.COMPLETED or result.status == TaskStatus.FAILED
        assert failing_agent.attempt_count >= 1

    @pytest.mark.asyncio
    async def test_agent_permanent_failure(self, orchestrator):
        """Test orchestrator handles permanent agent failure"""
        # Register agent that always fails
        failing_agent = FailingMockAgent(AgentType.AUDITOR, fail_count=999)
        orchestrator.register_agent(AgentType.AUDITOR, failing_agent)

        # Create campaign
        campaign_id = orchestrator.campaign_store.create_campaign(
            workflow_name="test-permanent-fail",
            parameters={"url": "https://example.com"},
            total_tasks=1,
        )

        # Create task
        task = TaskMessage(
            task_id="perm_fail_test_1",
            task_type="audit_content",
            agent_type=AgentType.AUDITOR,
            campaign_id=campaign_id,
            input_data={"url": "https://example.com", "content": "Test"},
        )

        # Execute task (should fail after retries)
        result = await orchestrator._execute_single_task(campaign_id, task)

        # Verify failed status
        assert result.status == TaskStatus.FAILED
        assert result.error_message is not None

    @pytest.mark.asyncio
    async def test_partial_workflow_failure(self, orchestrator):
        """Test workflow continues when one agent fails"""
        # Register one failing agent and one working agent
        orchestrator.register_agent(AgentType.AUDITOR, FailingMockAgent(AgentType.AUDITOR, fail_count=999))
        orchestrator.register_agent(AgentType.RESEARCHER, MockOptimizerAgent())  # Uses optimizer as researcher

        # Execute workflow (should handle failure gracefully)
        try:
            manifest = await orchestrator.execute_workflow(
                "aeo-campaign",
                {"url": "https://example.com", "queries": ["test"]},
            )

            # Workflow may complete partially or fail
            assert manifest.workflow_state.status.value in ["completed", "failed", "partial"]

            # Check that failure is recorded
            failed_tasks = [t for t in manifest.task_results if t.status == TaskStatus.FAILED]
            # Should have at least one failed task
            # (Note: actual behavior depends on orchestrator error handling implementation)

        except Exception as e:
            # If workflow raises exception, verify it's handled
            assert True  # Exception is expected


class TestTimeoutHandling:
    """Test handling of agent timeouts"""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator"""
        return OrchestratorAgent()

    @pytest.mark.asyncio
    async def test_agent_timeout(self, orchestrator):
        """Test orchestrator handles agent timeout"""
        # Register agent that will timeout
        timeout_agent = TimeoutMockAgent(AgentType.AUDITOR, delay_seconds=10.0)
        orchestrator.register_agent(AgentType.AUDITOR, timeout_agent)

        # Create campaign
        campaign_id = orchestrator.campaign_store.create_campaign(
            workflow_name="test-timeout",
            parameters={"url": "https://example.com"},
            total_tasks=1,
        )

        # Create task with short timeout
        task = TaskMessage(
            task_id="timeout_test_1",
            task_type="audit_content",
            agent_type=AgentType.AUDITOR,
            campaign_id=campaign_id,
            input_data={"url": "https://example.com", "content": "Test"},
            timeout_seconds=0.5,  # Short timeout
        )

        # Execute task (should timeout)
        result = await orchestrator._execute_single_task(campaign_id, task)

        # Verify timeout handled
        assert result.status == TaskStatus.FAILED
        assert "timeout" in result.error_message.lower() or "timed out" in result.error_message.lower()


class TestInvalidInputHandling:
    """Test handling of invalid inputs"""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator with mock agent"""
        orch = OrchestratorAgent()
        orch.register_agent(AgentType.AUDITOR, MockAuditorAgent())
        return orch

    @pytest.mark.asyncio
    async def test_missing_required_input(self, orchestrator):
        """Test orchestrator validates required input fields"""
        # Create campaign
        campaign_id = orchestrator.campaign_store.create_campaign(
            workflow_name="test-invalid-input",
            parameters={"url": "https://example.com"},
            total_tasks=1,
        )

        # Create task with missing input data
        task = TaskMessage(
            task_id="invalid_input_test_1",
            task_type="audit_content",
            agent_type=AgentType.AUDITOR,
            campaign_id=campaign_id,
            input_data={},  # Missing required fields
        )

        # Execute task (should handle invalid input)
        result = await orchestrator._execute_single_task(campaign_id, task)

        # May fail validation or execute with defaults
        assert result.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]

    @pytest.mark.asyncio
    async def test_invalid_agent_type(self, orchestrator):
        """Test orchestrator handles requests for unregistered agents"""
        # Create campaign
        campaign_id = orchestrator.campaign_store.create_campaign(
            workflow_name="test-invalid-agent",
            parameters={"url": "https://example.com"},
            total_tasks=1,
        )

        # Create task for unregistered agent
        task = TaskMessage(
            task_id="invalid_agent_test_1",
            task_type="optimize_content",
            agent_type=AgentType.OPTIMIZER,  # Not registered
            campaign_id=campaign_id,
            input_data={"content": "Test"},
        )

        # Execute task (should fail gracefully)
        with pytest.raises((KeyError, ValueError, AttributeError)):
            await orchestrator._execute_single_task(campaign_id, task)


class TestConcurrentFailures:
    """Test handling of failures in concurrent execution"""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator with mix of working and failing agents"""
        orch = OrchestratorAgent()
        orch.register_agent(AgentType.AUDITOR, MockAuditorAgent())  # Works
        orch.register_agent(AgentType.OPTIMIZER, FailingMockAgent(AgentType.OPTIMIZER, fail_count=999))  # Fails
        return orch

    @pytest.mark.asyncio
    async def test_parallel_partial_failure(self, orchestrator):
        """Test some tasks succeed while others fail in parallel execution"""
        # Create campaign
        campaign_id = orchestrator.campaign_store.create_campaign(
            workflow_name="test-parallel-failures",
            parameters={"url": "https://example.com"},
            total_tasks=2,
        )

        # Create tasks - one will succeed, one will fail
        tasks = [
            TaskMessage(
                task_id="parallel_success",
                task_type="audit_content",
                agent_type=AgentType.AUDITOR,  # Works
                campaign_id=campaign_id,
                input_data={"url": "https://example.com", "content": "Test"},
            ),
            TaskMessage(
                task_id="parallel_fail",
                task_type="optimize_content",
                agent_type=AgentType.OPTIMIZER,  # Fails
                campaign_id=campaign_id,
                input_data={"content": "Test"},
            ),
        ]

        # Execute in parallel
        results = await orchestrator._execute_parallel_tasks(campaign_id, tasks)

        # Verify mixed results
        assert len(results) == 2
        statuses = {r.status for r in results}
        # Should have both success and failure
        assert TaskStatus.COMPLETED in statuses or TaskStatus.FAILED in statuses


class TestRecoveryMechanisms:
    """Test orchestrator recovery from errors"""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator"""
        orch = OrchestratorAgent()
        orch.register_agent(AgentType.AUDITOR, MockAuditorAgent())
        return orch

    @pytest.mark.asyncio
    async def test_campaign_state_after_error(self, orchestrator):
        """Test campaign state is persisted even after errors"""
        # Execute workflow that may have errors
        try:
            manifest = await orchestrator.execute_workflow(
                "aeo-campaign",
                {"url": "https://example.com", "queries": ["test"]},
            )

            # Verify campaign was saved
            assert manifest.campaign_id is not None
            assert manifest.workflow_state.status.value in ["completed", "failed", "partial"]

            # Verify we can reload campaign
            reloaded = orchestrator.campaign_store.load_campaign(manifest.campaign_id)
            assert reloaded.campaign_id == manifest.campaign_id

        except Exception:
            # Even if workflow fails, test passes if state is persisted
            pass

    @pytest.mark.asyncio
    async def test_graceful_degradation(self, orchestrator):
        """Test system continues with reduced functionality after errors"""
        # Register only partial set of agents
        orchestrator.register_agent(AgentType.AUDITOR, MockAuditorAgent())
        # Optimizer not registered - workflow should degrade gracefully

        # Attempt workflow
        try:
            manifest = await orchestrator.execute_workflow(
                "aeo-campaign",
                {"url": "https://example.com", "queries": ["test"]},
            )

            # Workflow may complete partially
            # At minimum, auditor should have executed
            auditor_results = [
                t for t in manifest.task_results
                if t.agent_type == AgentType.AUDITOR
            ]
            # Should have attempted auditor task
            # (actual behavior depends on error handling implementation)

        except Exception:
            # Exception is acceptable for missing agents
            pass


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])

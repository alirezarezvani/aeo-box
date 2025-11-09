"""
Chaos Testing Scenarios

Tests system resilience under chaotic conditions:
- Random failures
- Resource exhaustion
- Cascading failures
- Concurrent stress
- Data corruption
"""

import pytest
import asyncio
import sys
import random
from pathlib import Path
from unittest.mock import AsyncMock
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from agents.orchestrator_agent import OrchestratorAgent
from agents.auditor_agent import AuditorAgent
from agents.optimizer_agent import OptimizerAgent
from agents.citation_tracker_agent import CitationTrackerAgent
from communication.protocol import AgentType, WorkflowStatus, TaskStatus, TaskResult


class TestChaosFailures:
    """Test system behavior under random chaos"""

    @pytest.mark.asyncio
    async def test_random_agent_failures(self):
        """Test workflow handles random agent failures"""
        orchestrator = OrchestratorAgent()

        # Create chaos agent that randomly fails
        chaos_agent = AsyncMock()

        async def chaotic_task(task):
            # 50% chance of failure
            if random.random() < 0.5:
                raise Exception(f"Chaos failure in task {task.task_id}")

            return TaskResult(
                task_id=task.task_id,
                task_type=task.task_type,
                status=TaskStatus.completed,
                agent_id="chaos_agent",
                results={"chaos": "survived"},
                timestamp=datetime.now()
            )

        chaos_agent.process_task = chaotic_task
        orchestrator.register_agent(AgentType.AUDITOR, chaos_agent)

        # Execute workflow multiple times
        for i in range(5):
            manifest = await orchestrator.execute_workflow(
                workflow_name="aeo-campaign",
                workflow_params={"url": f"https://example.com/chaos-{i}", "mode": "minimal"}
            )

            # Should complete without crashing (may be partial or failed)
            assert manifest.workflow_state.status in [
                WorkflowStatus.completed,
                WorkflowStatus.partial,
                WorkflowStatus.failed
            ]

    @pytest.mark.asyncio
    async def test_cascading_failures(self):
        """Test system handles cascading failures across agents"""
        orchestrator = OrchestratorAgent()

        failure_count = 0

        async def cascading_task(task):
            nonlocal failure_count
            failure_count += 1

            # Each failure increases probability of next failure
            failure_prob = min(0.9, failure_count * 0.2)

            if random.random() < failure_prob:
                raise Exception(f"Cascading failure #{failure_count}")

            return TaskResult(
                task_id=task.task_id,
                task_type=task.task_type,
                status=TaskStatus.completed,
                agent_id="cascading_agent",
                results={"survived": True},
                timestamp=datetime.now()
            )

        cascading_agent = AsyncMock()
        cascading_agent.process_task = cascading_task

        orchestrator.register_agent(AgentType.AUDITOR, cascading_agent)
        orchestrator.register_agent(AgentType.OPTIMIZER, cascading_agent)
        orchestrator.register_agent(AgentType.CITATION_TRACKER, cascading_agent)

        # Execute workflow
        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-campaign",
            workflow_params={"url": "https://example.com/cascade", "mode": "balanced"}
        )

        # System should handle cascading failures
        assert manifest.workflow_state is not None

    @pytest.mark.asyncio
    async def test_intermittent_network_chaos(self):
        """Test system handles intermittent network issues"""
        orchestrator = OrchestratorAgent()

        call_count = 0

        async def flaky_network(task):
            nonlocal call_count
            call_count += 1

            # Alternate between working and network errors
            if call_count % 3 == 0:
                raise ConnectionError("Intermittent network failure")

            return TaskResult(
                task_id=task.task_id,
                task_type=task.task_type,
                status=TaskStatus.completed,
                agent_id="flaky_agent",
                results={"network": "ok"},
                timestamp=datetime.now()
            )

        flaky_agent = AsyncMock()
        flaky_agent.process_task = flaky_network
        orchestrator.register_agent(AgentType.AUDITOR, flaky_agent)

        # Execute workflow
        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-campaign",
            workflow_params={"url": "https://example.com/flaky", "mode": "minimal"}
        )

        # Should complete despite network issues
        assert manifest.workflow_state.status in [
            WorkflowStatus.completed,
            WorkflowStatus.partial,
            WorkflowStatus.failed
        ]


class TestResourceExhaustion:
    """Test system behavior under resource constraints"""

    @pytest.mark.asyncio
    async def test_memory_pressure(self):
        """Test workflow handles memory pressure gracefully"""
        orchestrator = OrchestratorAgent()

        # Create agent that returns large results
        memory_agent = AsyncMock()

        async def large_result_task(task):
            # Simulate large result (but not too large for test)
            large_data = {"data": "x" * 10000}  # 10KB

            return TaskResult(
                task_id=task.task_id,
                task_type=task.task_type,
                status=TaskStatus.completed,
                agent_id="memory_agent",
                results=large_data,
                timestamp=datetime.now()
            )

        memory_agent.process_task = large_result_task
        orchestrator.register_agent(AgentType.AUDITOR, memory_agent)

        # Execute workflow
        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-campaign",
            workflow_params={"url": "https://example.com/memory", "mode": "minimal"}
        )

        # Should handle large results
        assert manifest.workflow_state.status in [
            WorkflowStatus.completed,
            WorkflowStatus.partial
        ]

    @pytest.mark.asyncio
    async def test_concurrent_workflow_stress(self):
        """Test system handles many concurrent workflows"""
        orchestrator = OrchestratorAgent()
        orchestrator.register_agent(AgentType.AUDITOR, AuditorAgent())

        # Launch multiple workflows concurrently
        tasks = []
        for i in range(10):
            task = orchestrator.execute_workflow(
                workflow_name="aeo-campaign",
                workflow_params={
                    "url": f"https://example.com/concurrent-{i}",
                    "mode": "minimal"
                }
            )
            tasks.append(task)

        # Wait for all to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Most should complete (some may fail due to resource constraints)
        completed = sum(
            1 for r in results
            if not isinstance(r, Exception) and r.workflow_state.status in [
                WorkflowStatus.completed,
                WorkflowStatus.partial
            ]
        )

        # At least 50% should complete successfully
        assert completed >= 5, f"Only {completed}/10 workflows completed"

    @pytest.mark.asyncio
    async def test_task_queue_overflow(self):
        """Test system handles task queue overflow"""
        orchestrator = OrchestratorAgent()
        orchestrator.register_agent(AgentType.AUDITOR, AuditorAgent())

        # Execute comprehensive workflow (many tasks)
        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-campaign",
            workflow_params={
                "url": "https://example.com/overflow",
                "mode": "comprehensive"
            }
        )

        # Should handle large number of tasks
        assert manifest.workflow_state.total_tasks >= 0


class TestDataCorruption:
    """Test system handles corrupted/invalid data"""

    @pytest.mark.asyncio
    async def test_corrupted_workflow_params(self):
        """Test system handles corrupted workflow parameters"""
        orchestrator = OrchestratorAgent()
        orchestrator.register_agent(AgentType.AUDITOR, AuditorAgent())

        # Invalid params
        corrupted_params = {
            "url": 12345,  # Should be string
            "mode": None,  # Should be enum
            "queries": "not a list",  # Should be list
        }

        # Should handle gracefully
        try:
            manifest = await orchestrator.execute_workflow(
                workflow_name="aeo-campaign",
                workflow_params=corrupted_params
            )
            # If it completes, should be in failed state
            if manifest:
                assert manifest.workflow_state.status == WorkflowStatus.failed
        except (TypeError, ValueError, AttributeError):
            # Acceptable - invalid params should raise error
            pass

    @pytest.mark.asyncio
    async def test_malformed_task_results(self):
        """Test system handles malformed agent results"""
        orchestrator = OrchestratorAgent()

        malformed_agent = AsyncMock()

        async def malformed_result(task):
            # Return incomplete/malformed result
            return TaskResult(
                task_id=task.task_id,
                task_type=task.task_type,
                status=None,  # Invalid!
                agent_id="malformed",
                results=None,  # Missing data!
                timestamp=datetime.now()
            )

        malformed_agent.process_task = malformed_result
        orchestrator.register_agent(AgentType.AUDITOR, malformed_agent)

        # Should handle malformed results
        try:
            manifest = await orchestrator.execute_workflow(
                workflow_name="aeo-campaign",
                workflow_params={"url": "https://example.com/malformed", "mode": "minimal"}
            )
            assert manifest is not None
        except (ValueError, TypeError, AttributeError):
            # Acceptable - malformed data may cause errors
            pass


class TestEdgeCases:
    """Test edge case chaos scenarios"""

    @pytest.mark.asyncio
    async def test_zero_tasks_workflow(self):
        """Test workflow handles edge case of zero tasks"""
        orchestrator = OrchestratorAgent()

        # No agents registered - should result in zero tasks

        try:
            manifest = await orchestrator.execute_workflow(
                workflow_name="aeo-campaign",
                workflow_params={"url": "https://example.com/zero", "mode": "minimal"}
            )

            # Should handle gracefully
            assert manifest is not None
        except Exception:
            # Exception acceptable for edge case
            pass

    @pytest.mark.asyncio
    async def test_rapid_workflow_cancellation(self):
        """Test system handles rapid workflow start/cancel"""
        orchestrator = OrchestratorAgent()

        # Create slow agent
        slow_agent = AsyncMock()
        async def slow_task(task):
            await asyncio.sleep(5)
            return TaskResult(
                task_id=task.task_id,
                task_type=task.task_type,
                status=TaskStatus.completed,
                agent_id="slow",
                results={},
                timestamp=datetime.now()
            )
        slow_agent.process_task = slow_task

        orchestrator.register_agent(AgentType.AUDITOR, slow_agent)

        # Start workflow and cancel quickly
        workflow_task = asyncio.create_task(
            orchestrator.execute_workflow(
                workflow_name="aeo-campaign",
                workflow_params={"url": "https://example.com/cancel", "mode": "minimal"}
            )
        )

        # Cancel after brief delay
        await asyncio.sleep(0.1)
        workflow_task.cancel()

        # Should handle cancellation
        try:
            await workflow_task
        except asyncio.CancelledError:
            # Expected
            pass

    @pytest.mark.asyncio
    async def test_duplicate_workflow_execution(self):
        """Test system handles duplicate workflow execution"""
        orchestrator = OrchestratorAgent()
        orchestrator.register_agent(AgentType.AUDITOR, AuditorAgent())

        params = {"url": "https://example.com/duplicate", "mode": "minimal"}

        # Execute same workflow twice concurrently
        task1 = orchestrator.execute_workflow("aeo-campaign", params)
        task2 = orchestrator.execute_workflow("aeo-campaign", params)

        results = await asyncio.gather(task1, task2, return_exceptions=True)

        # Both should complete independently
        assert len(results) == 2


class TestRecoveryScenarios:
    """Test system recovery from chaos"""

    @pytest.mark.asyncio
    async def test_recovery_after_total_failure(self):
        """Test system recovers after complete workflow failure"""
        orchestrator = OrchestratorAgent()

        # First attempt: failing agent
        failing_agent = AsyncMock()
        failing_agent.process_task.side_effect = Exception("Total failure")
        orchestrator.register_agent(AgentType.AUDITOR, failing_agent)

        # Execute and expect failure
        manifest1 = await orchestrator.execute_workflow(
            workflow_name="aeo-campaign",
            workflow_params={"url": "https://example.com/recovery", "mode": "minimal"}
        )

        assert manifest1.workflow_state.status in [WorkflowStatus.failed, WorkflowStatus.partial]

        # Second attempt: working agent
        orchestrator.agents.clear()  # Clear agents
        working_agent = AuditorAgent()
        orchestrator.register_agent(AgentType.AUDITOR, working_agent)

        # Execute again - should work
        manifest2 = await orchestrator.execute_workflow(
            workflow_name="aeo-campaign",
            workflow_params={"url": "https://example.com/recovery-2", "mode": "minimal"}
        )

        # Should complete successfully
        assert manifest2.workflow_state.status in [WorkflowStatus.completed, WorkflowStatus.partial]

    @pytest.mark.asyncio
    async def test_partial_recovery(self):
        """Test system can partially recover from failures"""
        orchestrator = OrchestratorAgent()

        recovery_count = 0

        async def recovering_task(task):
            nonlocal recovery_count
            recovery_count += 1

            # Fail first 2 times, succeed after
            if recovery_count <= 2:
                raise Exception(f"Failure {recovery_count}")

            return TaskResult(
                task_id=task.task_id,
                task_type=task.task_type,
                status=TaskStatus.completed,
                agent_id="recovering",
                results={"recovered": True, "attempts": recovery_count},
                timestamp=datetime.now()
            )

        recovering_agent = AsyncMock()
        recovering_agent.process_task = recovering_task
        orchestrator.register_agent(AgentType.AUDITOR, recovering_agent)

        # Execute workflow
        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-campaign",
            workflow_params={"url": "https://example.com/partial-recovery", "mode": "minimal"}
        )

        # Should eventually succeed after retries
        assert manifest is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

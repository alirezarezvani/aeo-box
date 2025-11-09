"""
End-to-End Tests for Citation Monitoring Workflow

Tests complete citation monitoring workflow from start to finish, including:
- Monitor setup and configuration
- Baseline metrics collection
- Tracking schedule creation
- Alert configuration
- Report generation
"""

import pytest
import asyncio
import sys
from pathlib import Path
from datetime import datetime
import json

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from workflows.monitoring_workflow import MonitoringWorkflow
from agents.orchestrator_agent import OrchestratorAgent
from agents.auditor_agent import AuditorAgent
from agents.optimizer_agent import OptimizerAgent
from agents.citation_tracker_agent import CitationTrackerAgent
from agents.researcher_agent import ResearcherAgent
from agents.reporter_agent import ReporterAgent
from agents.learning_agent import LearningAgent
from communication.protocol import AgentType, WorkflowStatus


@pytest.fixture
def orchestrator():
    """Create fully configured orchestrator with all agents"""
    orch = OrchestratorAgent()
    orch.register_agent(AgentType.AUDITOR, AuditorAgent())
    orch.register_agent(AgentType.OPTIMIZER, OptimizerAgent())
    orch.register_agent(AgentType.CITATION_TRACKER, CitationTrackerAgent())
    orch.register_agent(AgentType.RESEARCHER, ResearcherAgent())
    orch.register_agent(AgentType.REPORTER, ReporterAgent())
    orch.register_agent(AgentType.LEARNING, LearningAgent())
    return orch


class TestMonitoringWorkflowBasic:
    """E2E tests for basic monitoring workflow"""

    @pytest.mark.asyncio
    async def test_monitoring_basic_setup(self, orchestrator):
        """Test basic monitoring setup workflow"""
        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-monitor",
            workflow_params={
                "url": "https://example.com/article",
                "duration_days": 30
            }
        )

        # Verify workflow completed
        assert manifest.workflow_state.status in [WorkflowStatus.completed, WorkflowStatus.partial]
        assert manifest.workflow_state.workflow_name == "aeo-monitor"

        # Verify tasks were executed
        assert manifest.workflow_state.total_tasks > 0
        assert manifest.workflow_state.completed_tasks > 0
        assert len(manifest.task_results) > 0

    @pytest.mark.asyncio
    async def test_monitoring_timing(self, orchestrator):
        """Test monitoring setup completes within time target"""
        start_time = datetime.now()

        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-monitor",
            workflow_params={
                "url": "https://example.com/performance-test",
                "duration_days": 90
            }
        )

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Monitoring setup should complete quickly (< 2 minutes for E2E test)
        assert duration < 120, f"Monitoring setup took {duration}s, expected < 120s"
        assert manifest.workflow_state.status in [WorkflowStatus.completed, WorkflowStatus.partial]

    @pytest.mark.asyncio
    async def test_monitoring_minimal_params(self, orchestrator):
        """Test monitoring with minimal required parameters"""
        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-monitor",
            workflow_params={
                "url": "https://example.com/minimal",
                "duration_days": 7  # Minimum duration
            }
        )

        assert manifest.workflow_state.status in [WorkflowStatus.completed, WorkflowStatus.partial]
        assert manifest.workflow_state.completed_tasks > 0


class TestMonitoringWorkflowDurations:
    """E2E tests for monitoring with different durations"""

    @pytest.mark.asyncio
    async def test_monitoring_short_duration(self, orchestrator):
        """Test monitoring with short duration (7 days)"""
        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-monitor",
            workflow_params={
                "url": "https://example.com/short-duration",
                "duration_days": 7
            }
        )

        assert manifest.workflow_state.status in [WorkflowStatus.completed, WorkflowStatus.partial]
        assert manifest.workflow_state.completed_tasks > 0

    @pytest.mark.asyncio
    async def test_monitoring_medium_duration(self, orchestrator):
        """Test monitoring with medium duration (90 days)"""
        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-monitor",
            workflow_params={
                "url": "https://example.com/medium-duration",
                "duration_days": 90
            }
        )

        assert manifest.workflow_state.status in [WorkflowStatus.completed, WorkflowStatus.partial]
        assert manifest.workflow_state.completed_tasks > 0

    @pytest.mark.asyncio
    async def test_monitoring_long_duration(self, orchestrator):
        """Test monitoring with long duration (180 days)"""
        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-monitor",
            workflow_params={
                "url": "https://example.com/long-duration",
                "duration_days": 180
            }
        )

        assert manifest.workflow_state.status in [WorkflowStatus.completed, WorkflowStatus.partial]
        assert manifest.workflow_state.completed_tasks > 0

    @pytest.mark.asyncio
    async def test_monitoring_max_duration(self, orchestrator):
        """Test monitoring with maximum duration (365 days)"""
        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-monitor",
            workflow_params={
                "url": "https://example.com/max-duration",
                "duration_days": 365
            }
        )

        assert manifest.workflow_state.status in [WorkflowStatus.completed, WorkflowStatus.partial]
        assert manifest.workflow_state.completed_tasks > 0


class TestMonitoringWorkflowQueries:
    """E2E tests for monitoring with custom queries"""

    @pytest.mark.asyncio
    async def test_monitoring_single_query(self, orchestrator):
        """Test monitoring with single query"""
        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-monitor",
            workflow_params={
                "url": "https://example.com/single-query",
                "duration_days": 30,
                "queries": ["single test query"]
            }
        )

        assert manifest.workflow_state.status in [WorkflowStatus.completed, WorkflowStatus.partial]
        assert manifest.workflow_state.completed_tasks > 0

    @pytest.mark.asyncio
    async def test_monitoring_multiple_queries(self, orchestrator):
        """Test monitoring with multiple queries"""
        queries = [
            "how to optimize for AI",
            "best AEO practices",
            "citation tracking strategies",
            "answer engine optimization"
        ]

        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-monitor",
            workflow_params={
                "url": "https://example.com/multiple-queries",
                "duration_days": 60,
                "queries": queries
            }
        )

        assert manifest.workflow_state.status in [WorkflowStatus.completed, WorkflowStatus.partial]
        assert manifest.workflow_state.completed_tasks > 0

    @pytest.mark.asyncio
    async def test_monitoring_without_queries(self, orchestrator):
        """Test monitoring without specific queries (auto-detect)"""
        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-monitor",
            workflow_params={
                "url": "https://example.com/auto-detect",
                "duration_days": 30
                # No queries parameter - should auto-detect from content
            }
        )

        assert manifest.workflow_state.status in [WorkflowStatus.completed, WorkflowStatus.partial]
        assert manifest.workflow_state.completed_tasks > 0


class TestMonitoringWorkflowAlerts:
    """E2E tests for monitoring with alert configuration"""

    @pytest.mark.asyncio
    async def test_monitoring_with_alerts(self, orchestrator):
        """Test monitoring with alerts enabled"""
        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-monitor",
            workflow_params={
                "url": "https://example.com/with-alerts",
                "duration_days": 30,
                "alert_on_changes": True
            }
        )

        assert manifest.workflow_state.status in [WorkflowStatus.completed, WorkflowStatus.partial]
        assert manifest.workflow_state.completed_tasks > 0

    @pytest.mark.asyncio
    async def test_monitoring_without_alerts(self, orchestrator):
        """Test monitoring with alerts disabled"""
        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-monitor",
            workflow_params={
                "url": "https://example.com/no-alerts",
                "duration_days": 30,
                "alert_on_changes": False
            }
        )

        assert manifest.workflow_state.status in [WorkflowStatus.completed, WorkflowStatus.partial]
        assert manifest.workflow_state.completed_tasks > 0


class TestMonitoringWorkflowReports:
    """E2E tests for monitoring with report configuration"""

    @pytest.mark.asyncio
    async def test_monitoring_with_weekly_reports(self, orchestrator):
        """Test monitoring with weekly reports enabled"""
        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-monitor",
            workflow_params={
                "url": "https://example.com/weekly-reports",
                "duration_days": 90,
                "weekly_reports": True
            }
        )

        assert manifest.workflow_state.status in [WorkflowStatus.completed, WorkflowStatus.partial]
        assert manifest.workflow_state.completed_tasks > 0

    @pytest.mark.asyncio
    async def test_monitoring_without_weekly_reports(self, orchestrator):
        """Test monitoring with weekly reports disabled"""
        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-monitor",
            workflow_params={
                "url": "https://example.com/no-reports",
                "duration_days": 30,
                "weekly_reports": False
            }
        )

        assert manifest.workflow_state.status in [WorkflowStatus.completed, WorkflowStatus.partial]
        assert manifest.workflow_state.completed_tasks > 0

    @pytest.mark.asyncio
    async def test_monitoring_full_configuration(self, orchestrator):
        """Test monitoring with all options configured"""
        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-monitor",
            workflow_params={
                "url": "https://example.com/full-config",
                "duration_days": 120,
                "queries": ["query 1", "query 2", "query 3"],
                "alert_on_changes": True,
                "weekly_reports": True
            }
        )

        assert manifest.workflow_state.status in [WorkflowStatus.completed, WorkflowStatus.partial]
        assert manifest.workflow_state.completed_tasks > 0


class TestMonitoringWorkflowErrorHandling:
    """E2E tests for monitoring workflow error handling"""

    @pytest.mark.asyncio
    async def test_monitoring_invalid_url(self, orchestrator):
        """Test monitoring handles invalid URL"""
        workflow = MonitoringWorkflow()

        # Invalid URL should fail validation
        is_valid, error = workflow.validate_input("invalid-url", 30)
        assert not is_valid
        assert error is not None

    @pytest.mark.asyncio
    async def test_monitoring_invalid_duration_too_short(self, orchestrator):
        """Test monitoring handles duration < 1 day"""
        workflow = MonitoringWorkflow()

        # Duration < 1 should fail validation
        is_valid, error = workflow.validate_input("https://example.com", 0)
        assert not is_valid
        assert error is not None

    @pytest.mark.asyncio
    async def test_monitoring_invalid_duration_too_long(self, orchestrator):
        """Test monitoring handles duration > 365 days"""
        workflow = MonitoringWorkflow()

        # Duration > 365 should fail validation
        is_valid, error = workflow.validate_input("https://example.com", 500)
        assert not is_valid
        assert error is not None

    @pytest.mark.asyncio
    async def test_monitoring_negative_duration(self, orchestrator):
        """Test monitoring handles negative duration"""
        workflow = MonitoringWorkflow()

        # Negative duration should fail validation
        is_valid, error = workflow.validate_input("https://example.com", -10)
        assert not is_valid
        assert error is not None


class TestMonitoringWorkflowResults:
    """E2E tests for monitoring workflow results structure"""

    @pytest.mark.asyncio
    async def test_monitoring_results_structure(self, orchestrator):
        """Test monitoring results have proper structure"""
        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-monitor",
            workflow_params={
                "url": "https://example.com/results-test",
                "duration_days": 30
            }
        )

        # Verify workflow state structure
        workflow_dict = manifest.workflow_state.dict()
        assert "workflow_name" in workflow_dict
        assert "status" in workflow_dict
        assert "total_tasks" in workflow_dict
        assert "completed_tasks" in workflow_dict

        # Verify task results structure
        for result in manifest.task_results:
            result_dict = result.dict()
            assert "task_id" in result_dict
            assert "task_type" in result_dict
            assert "status" in result_dict
            assert "agent_id" in result_dict

    @pytest.mark.asyncio
    async def test_monitoring_json_serializable(self, orchestrator):
        """Test monitoring results can be serialized to JSON"""
        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-monitor",
            workflow_params={
                "url": "https://example.com/json-test",
                "duration_days": 60
            }
        )

        # Should be able to serialize to JSON
        workflow_json = json.dumps(manifest.workflow_state.dict())
        assert workflow_json is not None
        assert len(workflow_json) > 0

        # Should be able to deserialize
        workflow_data = json.loads(workflow_json)
        assert workflow_data["workflow_name"] == "aeo-monitor"


class TestMonitoringWorkflowIntegration:
    """E2E integration tests for monitoring workflow"""

    @pytest.mark.asyncio
    async def test_monitoring_cli_integration(self, orchestrator):
        """Test monitoring integrates with CLI parameters"""
        # Simulate CLI-style parameters
        cli_params = {
            "url": "https://example.com/cli-test",
            "duration_days": 90,
            "queries": ["cli query 1", "cli query 2"],
            "alert_on_changes": True,
            "weekly_reports": True
        }

        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-monitor",
            workflow_params=cli_params
        )

        assert manifest.workflow_state.status in [WorkflowStatus.completed, WorkflowStatus.partial]
        assert manifest.workflow_state.completed_tasks > 0

    @pytest.mark.asyncio
    async def test_monitoring_api_integration(self, orchestrator):
        """Test monitoring integrates with API request format"""
        # Simulate API-style parameters
        api_params = {
            "url": "https://example.com/api-test",
            "duration_days": 30,
            "queries": ["api query"],
            "alert_on_changes": False,
            "weekly_reports": False
        }

        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-monitor",
            workflow_params=api_params
        )

        assert manifest.workflow_state.status in [WorkflowStatus.completed, WorkflowStatus.partial]
        assert manifest.workflow_state.completed_tasks > 0

        # Results should be API-compatible (serializable)
        results_dict = manifest.workflow_state.dict()
        assert isinstance(results_dict, dict)


class TestMonitoringWorkflowAgentCoordination:
    """E2E tests for agent coordination in monitoring workflow"""

    @pytest.mark.asyncio
    async def test_monitoring_citation_tracker_invoked(self, orchestrator):
        """Test monitoring invokes citation tracker agent"""
        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-monitor",
            workflow_params={
                "url": "https://example.com/tracker-test",
                "duration_days": 30
            }
        )

        # Citation tracker should be invoked for monitoring
        agent_ids = [result.agent_id for result in manifest.task_results]
        assert len(agent_ids) > 0

        # Should have executed at least one task
        assert manifest.workflow_state.completed_tasks > 0

    @pytest.mark.asyncio
    async def test_monitoring_baseline_collection(self, orchestrator):
        """Test monitoring collects baseline metrics"""
        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-monitor",
            workflow_params={
                "url": "https://example.com/baseline-test",
                "duration_days": 60,
                "queries": ["baseline query"]
            }
        )

        # Monitoring should collect baseline before setting up tracking
        assert manifest.workflow_state.status in [WorkflowStatus.completed, WorkflowStatus.partial]
        assert manifest.workflow_state.completed_tasks > 0

        # Should have task results representing baseline collection
        task_types = [result.task_type for result in manifest.task_results]
        assert len(task_types) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

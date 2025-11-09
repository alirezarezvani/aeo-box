"""
End-to-End Tests for Full Campaign Workflow

Tests complete AEO campaign workflow from start to finish, including:
- Orchestrator initialization
- All 6 agents execution
- Workflow task decomposition
- Result aggregation
- Report generation
"""

import pytest
import asyncio
import sys
from pathlib import Path
from datetime import datetime
import json

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from workflows.campaign_workflow import CampaignWorkflow
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


class TestCampaignWorkflowMinimalMode:
    """E2E tests for minimal mode campaign workflow"""

    @pytest.mark.asyncio
    async def test_minimal_campaign_complete_flow(self, orchestrator):
        """Test complete minimal campaign workflow from start to finish"""
        # Workflow parameters
        url = "https://example.com/test-article"
        mode = "minimal"
        industry = "Technology"

        # Execute workflow
        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-campaign",
            workflow_params={
                "url": url,
                "mode": mode,
                "industry": industry
            }
        )

        # Verify workflow completed
        assert manifest.workflow_state.status in [WorkflowStatus.completed, WorkflowStatus.partial]
        assert manifest.workflow_state.workflow_name == "aeo-campaign"

        # Verify tasks were executed
        assert manifest.workflow_state.total_tasks > 0
        assert manifest.workflow_state.completed_tasks > 0
        assert len(manifest.task_results) > 0

        # Verify at least audit task was executed (minimal mode)
        task_types = [result.task_type for result in manifest.task_results]
        assert "audit" in task_types

        # Verify results have required structure
        for result in manifest.task_results:
            assert result.task_id is not None
            assert result.task_type is not None
            assert result.status is not None
            assert result.agent_id is not None

    @pytest.mark.asyncio
    async def test_minimal_campaign_timing(self, orchestrator):
        """Test minimal campaign completes within time target"""
        start_time = datetime.now()

        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-campaign",
            workflow_params={
                "url": "https://example.com/performance-test",
                "mode": "minimal",
                "industry": "SaaS"
            }
        )

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Minimal mode should complete quickly (< 2 minutes for E2E test)
        assert duration < 120, f"Minimal campaign took {duration}s, expected < 120s"
        assert manifest.workflow_state.status in [WorkflowStatus.completed, WorkflowStatus.partial]

    @pytest.mark.asyncio
    async def test_minimal_campaign_audit_results(self, orchestrator):
        """Test minimal campaign produces valid audit results"""
        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-campaign",
            workflow_params={
                "url": "https://example.com/audit-test",
                "mode": "minimal"
            }
        )

        # Find audit result
        audit_results = [r for r in manifest.task_results if r.task_type == "audit"]
        assert len(audit_results) > 0, "No audit results found"

        audit_result = audit_results[0]
        assert audit_result.status == WorkflowStatus.completed
        assert audit_result.results is not None


class TestCampaignWorkflowBalancedMode:
    """E2E tests for balanced mode campaign workflow"""

    @pytest.mark.asyncio
    async def test_balanced_campaign_complete_flow(self, orchestrator):
        """Test complete balanced campaign workflow"""
        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-campaign",
            workflow_params={
                "url": "https://example.com/balanced-test",
                "mode": "balanced",
                "industry": "SaaS",
                "optimization_level": "balanced",
                "tracking_duration_days": 30,
                "queries": ["AEO optimization", "answer engine ranking"]
            }
        )

        # Verify workflow completed
        assert manifest.workflow_state.status in [WorkflowStatus.completed, WorkflowStatus.partial]

        # Balanced mode should execute more tasks than minimal
        assert manifest.workflow_state.total_tasks >= 5
        assert manifest.workflow_state.completed_tasks >= 3

        # Verify multiple task types executed
        task_types = [result.task_type for result in manifest.task_results]
        assert "audit" in task_types

        # At least one of research or optimize should be present in balanced mode
        assert any(t in task_types for t in ["research", "optimize", "tracking"])

    @pytest.mark.asyncio
    async def test_balanced_campaign_with_queries(self, orchestrator):
        """Test balanced campaign with custom queries"""
        queries = [
            "how to optimize for AI search",
            "best practices for AEO",
            "citation optimization strategies"
        ]

        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-campaign",
            workflow_params={
                "url": "https://example.com/query-test",
                "mode": "balanced",
                "queries": queries
            }
        )

        assert manifest.workflow_state.status in [WorkflowStatus.completed, WorkflowStatus.partial]
        assert manifest.workflow_state.completed_tasks > 0

        # Verify workflow processed queries parameter
        # (queries would be used in research task)
        task_types = [result.task_type for result in manifest.task_results]
        assert len(task_types) > 0

    @pytest.mark.asyncio
    async def test_balanced_campaign_optimization_levels(self, orchestrator):
        """Test balanced campaign with different optimization levels"""
        optimization_levels = ["conservative", "balanced", "aggressive"]

        for level in optimization_levels:
            manifest = await orchestrator.execute_workflow(
                workflow_name="aeo-campaign",
                workflow_params={
                    "url": f"https://example.com/opt-{level}",
                    "mode": "balanced",
                    "optimization_level": level
                }
            )

            assert manifest.workflow_state.status in [WorkflowStatus.completed, WorkflowStatus.partial]
            assert manifest.workflow_state.completed_tasks > 0


class TestCampaignWorkflowComprehensiveMode:
    """E2E tests for comprehensive mode campaign workflow"""

    @pytest.mark.asyncio
    async def test_comprehensive_campaign_complete_flow(self, orchestrator):
        """Test complete comprehensive campaign workflow"""
        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-campaign",
            workflow_params={
                "url": "https://example.com/comprehensive-test",
                "mode": "comprehensive",
                "industry": "Enterprise SaaS",
                "optimization_level": "aggressive",
                "tracking_duration_days": 90,
                "queries": [
                    "enterprise AEO",
                    "B2B content optimization",
                    "AI search ranking",
                    "citation building strategies"
                ]
            }
        )

        # Verify workflow completed
        assert manifest.workflow_state.status in [WorkflowStatus.completed, WorkflowStatus.partial]

        # Comprehensive mode should execute most tasks
        assert manifest.workflow_state.total_tasks >= 8
        assert manifest.workflow_state.completed_tasks >= 5

        # Verify comprehensive task coverage
        task_types = [result.task_type for result in manifest.task_results]
        assert "audit" in task_types

        # Should have multiple task types
        assert len(set(task_types)) >= 3, "Comprehensive mode should execute diverse tasks"

    @pytest.mark.asyncio
    async def test_comprehensive_campaign_all_agents_invoked(self, orchestrator):
        """Test comprehensive campaign invokes multiple agents"""
        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-campaign",
            workflow_params={
                "url": "https://example.com/all-agents-test",
                "mode": "comprehensive",
                "industry": "Technology"
            }
        )

        # Get unique agent IDs that were invoked
        agent_ids = set(result.agent_id for result in manifest.task_results)

        # Comprehensive mode should invoke multiple agents
        assert len(agent_ids) >= 3, f"Expected 3+ agents, got {len(agent_ids)}"

    @pytest.mark.asyncio
    async def test_comprehensive_campaign_extended_tracking(self, orchestrator):
        """Test comprehensive campaign with extended tracking duration"""
        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-campaign",
            workflow_params={
                "url": "https://example.com/extended-tracking",
                "mode": "comprehensive",
                "tracking_duration_days": 365  # Maximum duration
            }
        )

        assert manifest.workflow_state.status in [WorkflowStatus.completed, WorkflowStatus.partial]
        assert manifest.workflow_state.completed_tasks > 0


class TestCampaignWorkflowErrorHandling:
    """E2E tests for campaign workflow error handling"""

    @pytest.mark.asyncio
    async def test_campaign_invalid_url_handled(self, orchestrator):
        """Test campaign handles invalid URL gracefully"""
        # Workflow should validate URL before execution
        workflow = CampaignWorkflow()

        is_valid, error = workflow.validate_input("invalid-url", "balanced")
        assert not is_valid
        assert error is not None

    @pytest.mark.asyncio
    async def test_campaign_invalid_mode_handled(self, orchestrator):
        """Test campaign handles invalid mode gracefully"""
        workflow = CampaignWorkflow()

        is_valid, error = workflow.validate_input("https://example.com", "invalid")
        assert not is_valid
        assert error is not None

    @pytest.mark.asyncio
    async def test_campaign_partial_completion(self, orchestrator):
        """Test campaign handles partial task completion"""
        # Even if some tasks fail, workflow should complete with partial status
        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-campaign",
            workflow_params={
                "url": "https://example.com/partial-test",
                "mode": "balanced"
            }
        )

        # Should complete even if some tasks fail
        assert manifest.workflow_state.status in [
            WorkflowStatus.completed,
            WorkflowStatus.partial,
            WorkflowStatus.failed
        ]

        # Should have attempted tasks
        assert manifest.workflow_state.total_tasks > 0


class TestCampaignWorkflowDataPersistence:
    """E2E tests for campaign workflow data persistence"""

    @pytest.mark.asyncio
    async def test_campaign_results_structure(self, orchestrator):
        """Test campaign results have proper structure for persistence"""
        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-campaign",
            workflow_params={
                "url": "https://example.com/persistence-test",
                "mode": "minimal"
            }
        )

        # Verify workflow state can be serialized
        workflow_dict = manifest.workflow_state.dict()
        assert "workflow_name" in workflow_dict
        assert "status" in workflow_dict
        assert "total_tasks" in workflow_dict
        assert "completed_tasks" in workflow_dict

        # Verify task results can be serialized
        for result in manifest.task_results:
            result_dict = result.dict()
            assert "task_id" in result_dict
            assert "task_type" in result_dict
            assert "status" in result_dict
            assert "agent_id" in result_dict

    @pytest.mark.asyncio
    async def test_campaign_results_json_serializable(self, orchestrator):
        """Test campaign results can be serialized to JSON"""
        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-campaign",
            workflow_params={
                "url": "https://example.com/json-test",
                "mode": "minimal"
            }
        )

        # Should be able to serialize to JSON
        workflow_json = json.dumps(manifest.workflow_state.dict())
        assert workflow_json is not None
        assert len(workflow_json) > 0

        # Should be able to deserialize
        workflow_data = json.loads(workflow_json)
        assert workflow_data["workflow_name"] == "aeo-campaign"


class TestCampaignWorkflowIntegration:
    """E2E integration tests for campaign workflow with other components"""

    @pytest.mark.asyncio
    async def test_campaign_cli_integration(self, orchestrator):
        """Test campaign workflow integrates with CLI parameters"""
        # Simulate CLI-style parameters
        cli_params = {
            "url": "https://example.com/cli-test",
            "mode": "balanced",
            "industry": "SaaS",
            "optimization_level": "balanced",
            "tracking_duration_days": 30,
            "queries": ["cli test query"]
        }

        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-campaign",
            workflow_params=cli_params
        )

        assert manifest.workflow_state.status in [WorkflowStatus.completed, WorkflowStatus.partial]
        assert manifest.workflow_state.completed_tasks > 0

    @pytest.mark.asyncio
    async def test_campaign_api_integration(self, orchestrator):
        """Test campaign workflow integrates with API request format"""
        # Simulate API-style parameters
        api_params = {
            "url": "https://example.com/api-test",
            "mode": "balanced",
            "industry": "Technology",
            "optimization_level": "balanced",
            "tracking_duration_days": 60,
            "queries": ["api test query 1", "api test query 2"]
        }

        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-campaign",
            workflow_params=api_params
        )

        assert manifest.workflow_state.status in [WorkflowStatus.completed, WorkflowStatus.partial]
        assert manifest.workflow_state.completed_tasks > 0

        # Results should be API-compatible (serializable)
        results_dict = manifest.workflow_state.dict()
        assert isinstance(results_dict, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

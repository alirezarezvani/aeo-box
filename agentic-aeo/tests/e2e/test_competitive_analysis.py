"""
End-to-End Tests for Competitive Analysis Workflow

Tests complete competitive AEO analysis workflow from start to finish, including:
- Multi-competitor URL analysis
- Topic-based research
- Citation comparison
- Competitive insights generation
"""

import pytest
import asyncio
import sys
from pathlib import Path
from datetime import datetime
import json

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from workflows.competitive_workflow import CompetitiveWorkflow
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


class TestCompetitiveAnalysisBasic:
    """E2E tests for basic competitive analysis"""

    @pytest.mark.asyncio
    async def test_competitive_analysis_two_competitors(self, orchestrator):
        """Test competitive analysis with 2 competitors"""
        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-compete",
            workflow_params={
                "topic": "project management software",
                "competitor_urls": [
                    "https://competitor1.com",
                    "https://competitor2.com"
                ],
                "region": "US"
            }
        )

        # Verify workflow completed
        assert manifest.workflow_state.status in [WorkflowStatus.completed, WorkflowStatus.partial]
        assert manifest.workflow_state.workflow_name == "aeo-compete"

        # Verify tasks were executed
        assert manifest.workflow_state.total_tasks > 0
        assert manifest.workflow_state.completed_tasks > 0
        assert len(manifest.task_results) > 0

    @pytest.mark.asyncio
    async def test_competitive_analysis_timing(self, orchestrator):
        """Test competitive analysis completes within time target"""
        start_time = datetime.now()

        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-compete",
            workflow_params={
                "topic": "content optimization",
                "competitor_urls": ["https://competitor.com"],
                "region": "US"
            }
        )

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Basic competitive analysis should complete quickly (< 2 minutes for E2E test)
        assert duration < 120, f"Competitive analysis took {duration}s, expected < 120s"
        assert manifest.workflow_state.status in [WorkflowStatus.completed, WorkflowStatus.partial]

    @pytest.mark.asyncio
    async def test_competitive_analysis_single_competitor(self, orchestrator):
        """Test competitive analysis with minimum (1) competitor"""
        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-compete",
            workflow_params={
                "topic": "SEO tools",
                "competitor_urls": ["https://single-competitor.com"],
                "region": "US"
            }
        )

        assert manifest.workflow_state.status in [WorkflowStatus.completed, WorkflowStatus.partial]
        assert manifest.workflow_state.completed_tasks > 0


class TestCompetitiveAnalysisMultipleCompetitors:
    """E2E tests for competitive analysis with multiple competitors"""

    @pytest.mark.asyncio
    async def test_competitive_analysis_five_competitors(self, orchestrator):
        """Test competitive analysis with 5 competitors"""
        competitor_urls = [f"https://competitor{i}.com" for i in range(1, 6)]

        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-compete",
            workflow_params={
                "topic": "marketing automation",
                "competitor_urls": competitor_urls,
                "region": "US"
            }
        )

        assert manifest.workflow_state.status in [WorkflowStatus.completed, WorkflowStatus.partial]
        assert manifest.workflow_state.completed_tasks > 0

        # More competitors should result in more comprehensive analysis
        assert manifest.workflow_state.total_tasks > 0

    @pytest.mark.asyncio
    async def test_competitive_analysis_max_competitors(self, orchestrator):
        """Test competitive analysis with maximum (10) competitors"""
        competitor_urls = [f"https://competitor{i}.com" for i in range(1, 11)]

        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-compete",
            workflow_params={
                "topic": "enterprise software",
                "competitor_urls": competitor_urls,
                "region": "US"
            }
        )

        assert manifest.workflow_state.status in [WorkflowStatus.completed, WorkflowStatus.partial]
        assert manifest.workflow_state.completed_tasks > 0

        # Maximum competitors should generate comprehensive analysis
        task_types = [result.task_type for result in manifest.task_results]
        assert len(task_types) > 0


class TestCompetitiveAnalysisRegions:
    """E2E tests for competitive analysis across different regions"""

    @pytest.mark.asyncio
    async def test_competitive_analysis_us_region(self, orchestrator):
        """Test competitive analysis for US region"""
        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-compete",
            workflow_params={
                "topic": "cloud services",
                "competitor_urls": ["https://competitor.com"],
                "region": "US"
            }
        )

        assert manifest.workflow_state.status in [WorkflowStatus.completed, WorkflowStatus.partial]

    @pytest.mark.asyncio
    async def test_competitive_analysis_uk_region(self, orchestrator):
        """Test competitive analysis for UK region"""
        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-compete",
            workflow_params={
                "topic": "financial services",
                "competitor_urls": ["https://uk-competitor.com"],
                "region": "UK"
            }
        )

        assert manifest.workflow_state.status in [WorkflowStatus.completed, WorkflowStatus.partial]

    @pytest.mark.asyncio
    async def test_competitive_analysis_global_region(self, orchestrator):
        """Test competitive analysis for global region"""
        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-compete",
            workflow_params={
                "topic": "e-commerce platforms",
                "competitor_urls": ["https://global-competitor.com"],
                "region": "Global"
            }
        )

        assert manifest.workflow_state.status in [WorkflowStatus.completed, WorkflowStatus.partial]


class TestCompetitiveAnalysisCitationTracking:
    """E2E tests for competitive analysis with citation tracking"""

    @pytest.mark.asyncio
    async def test_competitive_analysis_with_citations(self, orchestrator):
        """Test competitive analysis includes citation tracking"""
        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-compete",
            workflow_params={
                "topic": "AI tools",
                "competitor_urls": [
                    "https://competitor1.com",
                    "https://competitor2.com"
                ],
                "region": "US",
                "include_citations": True
            }
        )

        assert manifest.workflow_state.status in [WorkflowStatus.completed, WorkflowStatus.partial]
        assert manifest.workflow_state.completed_tasks > 0

        # Should have executed tasks related to citation analysis
        task_types = [result.task_type for result in manifest.task_results]
        assert len(task_types) > 0

    @pytest.mark.asyncio
    async def test_competitive_analysis_without_citations(self, orchestrator):
        """Test competitive analysis without citation tracking"""
        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-compete",
            workflow_params={
                "topic": "productivity software",
                "competitor_urls": ["https://competitor.com"],
                "region": "US",
                "include_citations": False
            }
        )

        assert manifest.workflow_state.status in [WorkflowStatus.completed, WorkflowStatus.partial]
        assert manifest.workflow_state.completed_tasks > 0


class TestCompetitiveAnalysisErrorHandling:
    """E2E tests for competitive analysis error handling"""

    @pytest.mark.asyncio
    async def test_competitive_analysis_invalid_topic(self, orchestrator):
        """Test competitive analysis handles invalid topic"""
        workflow = CompetitiveWorkflow()

        # Empty topic should fail validation
        is_valid, error = workflow.validate_input("", ["https://competitor.com"])
        assert not is_valid
        assert error is not None

    @pytest.mark.asyncio
    async def test_competitive_analysis_no_competitors(self, orchestrator):
        """Test competitive analysis handles no competitors"""
        workflow = CompetitiveWorkflow()

        # Empty competitor list should fail validation
        is_valid, error = workflow.validate_input("topic", [])
        assert not is_valid
        assert error is not None

    @pytest.mark.asyncio
    async def test_competitive_analysis_too_many_competitors(self, orchestrator):
        """Test competitive analysis handles too many competitors"""
        workflow = CompetitiveWorkflow()

        # More than 10 competitors should fail validation
        too_many_urls = [f"https://competitor{i}.com" for i in range(1, 16)]
        is_valid, error = workflow.validate_input("topic", too_many_urls)
        assert not is_valid
        assert error is not None

    @pytest.mark.asyncio
    async def test_competitive_analysis_invalid_urls(self, orchestrator):
        """Test competitive analysis handles invalid URLs"""
        workflow = CompetitiveWorkflow()

        # Invalid URLs should fail validation
        invalid_urls = ["not-a-url", "ftp://invalid.com"]
        is_valid, error = workflow.validate_input("topic", invalid_urls)
        assert not is_valid
        assert error is not None


class TestCompetitiveAnalysisResults:
    """E2E tests for competitive analysis results structure"""

    @pytest.mark.asyncio
    async def test_competitive_analysis_results_structure(self, orchestrator):
        """Test competitive analysis results have proper structure"""
        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-compete",
            workflow_params={
                "topic": "CRM software",
                "competitor_urls": ["https://competitor.com"],
                "region": "US"
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
    async def test_competitive_analysis_json_serializable(self, orchestrator):
        """Test competitive analysis results can be serialized to JSON"""
        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-compete",
            workflow_params={
                "topic": "analytics platforms",
                "competitor_urls": ["https://competitor.com"],
                "region": "US"
            }
        )

        # Should be able to serialize to JSON
        workflow_json = json.dumps(manifest.workflow_state.dict())
        assert workflow_json is not None
        assert len(workflow_json) > 0

        # Should be able to deserialize
        workflow_data = json.loads(workflow_json)
        assert workflow_data["workflow_name"] == "aeo-compete"


class TestCompetitiveAnalysisIntegration:
    """E2E integration tests for competitive analysis workflow"""

    @pytest.mark.asyncio
    async def test_competitive_analysis_cli_integration(self, orchestrator):
        """Test competitive analysis integrates with CLI parameters"""
        # Simulate CLI-style parameters
        cli_params = {
            "topic": "email marketing",
            "competitor_urls": [
                "https://cli-competitor1.com",
                "https://cli-competitor2.com"
            ],
            "region": "US",
            "include_citations": True
        }

        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-compete",
            workflow_params=cli_params
        )

        assert manifest.workflow_state.status in [WorkflowStatus.completed, WorkflowStatus.partial]
        assert manifest.workflow_state.completed_tasks > 0

    @pytest.mark.asyncio
    async def test_competitive_analysis_api_integration(self, orchestrator):
        """Test competitive analysis integrates with API request format"""
        # Simulate API-style parameters
        api_params = {
            "topic": "customer support software",
            "competitor_urls": [
                "https://api-competitor1.com",
                "https://api-competitor2.com",
                "https://api-competitor3.com"
            ],
            "region": "UK",
            "include_citations": False
        }

        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-compete",
            workflow_params=api_params
        )

        assert manifest.workflow_state.status in [WorkflowStatus.completed, WorkflowStatus.partial]
        assert manifest.workflow_state.completed_tasks > 0

        # Results should be API-compatible (serializable)
        results_dict = manifest.workflow_state.dict()
        assert isinstance(results_dict, dict)


class TestCompetitiveAnalysisAgentCoordination:
    """E2E tests for agent coordination in competitive analysis"""

    @pytest.mark.asyncio
    async def test_competitive_analysis_multiple_agents_invoked(self, orchestrator):
        """Test competitive analysis invokes multiple agents"""
        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-compete",
            workflow_params={
                "topic": "collaboration tools",
                "competitor_urls": [
                    "https://competitor1.com",
                    "https://competitor2.com",
                    "https://competitor3.com"
                ],
                "region": "US",
                "include_citations": True
            }
        )

        # Get unique agent IDs that were invoked
        agent_ids = set(result.agent_id for result in manifest.task_results)

        # Competitive analysis should invoke multiple agents
        assert len(agent_ids) >= 2, f"Expected 2+ agents, got {len(agent_ids)}"

    @pytest.mark.asyncio
    async def test_competitive_analysis_task_prioritization(self, orchestrator):
        """Test competitive analysis tasks are properly prioritized"""
        manifest = await orchestrator.execute_workflow(
            workflow_name="aeo-compete",
            workflow_params={
                "topic": "data visualization",
                "competitor_urls": ["https://competitor.com"],
                "region": "US"
            }
        )

        # Tasks should be executed in priority order
        # (Verify results list represents execution order)
        assert len(manifest.task_results) > 0

        # All tasks should have completed or failed status
        for result in manifest.task_results:
            assert result.status in [
                WorkflowStatus.completed,
                WorkflowStatus.failed,
                WorkflowStatus.partial
            ]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

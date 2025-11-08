"""
Auditor Agent Integration Tests

Tests the AuditorAgent with real ContentAnalyzer and Orchestrator integration.
"""

import pytest
import asyncio
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from agents.auditor_agent import AuditorAgent, audit_content
from agents.orchestrator_agent import OrchestratorAgent
from communication.protocol import AgentType, TaskMessage, TaskStatus


# Sample content for testing
SAMPLE_CONTENT = """
# Ultimate Guide to Answer Engine Optimization

## What is AEO?

Answer Engine Optimization (AEO) is the practice of optimizing content to be cited by AI language models like ChatGPT, Perplexity, Claude, and Gemini.

### Why AEO Matters

Studies show that 50%+ of searches now use AI answer engines. Getting cited by these models is crucial for:

- Brand visibility
- Authority building
- Direct traffic from LLM citations

## Best Practices

According to research from Ahrefs and CXL, successful AEO strategies include:

1. **E-E-A-T signals** - Demonstrate experience, expertise, authoritativeness, and trustworthiness
2. **Structured content** - Use clear headings, lists, and tables
3. **Authoritative citations** - Link to credible sources
4. **Concise answers** - Provide direct responses to questions

## Case Study

In our testing with 100+ articles, content optimized for AEO saw:

- 2-4x increase in LLM citations
- 85% improvement in E-E-A-T scores
- 60% better structure optimization

Source: Internal AEO Box testing, Q4 2024
"""


class TestAuditorAgentRealAnalysis:
    """Test auditor agent with real ContentAnalyzer"""

    @pytest.fixture
    def agent(self):
        """Create real auditor agent"""
        return AuditorAgent()

    @pytest.mark.asyncio
    async def test_analyze_real_content(self, agent):
        """Test analyzing real content"""
        task = TaskMessage(
            task_id="integration_test_1",
            task_type="audit_content",
            agent_type=AgentType.AUDITOR,
            campaign_id="integration_campaign",
            input_data={
                "content": SAMPLE_CONTENT,
                "url": "https://example.com/aeo-guide",
            }
        )

        result = await agent.execute_task(task)

        # Verify result structure
        assert "timestamp" in result
        assert "scores" in result
        assert "analysis" in result
        assert "recommendations" in result

        # Verify scores present
        scores = result["scores"]
        assert "overall" in scores
        assert "eeat" in scores
        assert "structure" in scores
        assert "citations" in scores
        assert "readability" in scores

        # Verify score ranges
        assert 0 <= scores["overall"] <= 100
        assert 0 <= scores["eeat"] <= 100
        assert 0 <= scores["structure"] <= 100

        # Verify analysis has content
        analysis = result["analysis"]
        assert "eeat_signals" in analysis or "structure_analysis" in analysis

    @pytest.mark.asyncio
    async def test_analyze_short_content(self, agent):
        """Test analyzing short content"""
        short_content = "This is a brief test article about AI."

        task = TaskMessage(
            task_id="integration_test_2",
            task_type="audit_content",
            agent_type=AgentType.AUDITOR,
            campaign_id="integration_campaign",
            input_data={"content": short_content}
        )

        result = await agent.execute_task(task)

        # Should still return valid result
        assert result is not None
        assert "scores" in result
        assert result["scores"]["overall"] >= 0

    @pytest.mark.asyncio
    async def test_analyze_with_context(self, agent):
        """Test analyzing content with additional context"""
        task = TaskMessage(
            task_id="integration_test_3",
            task_type="audit_content",
            agent_type=AgentType.AUDITOR,
            campaign_id="integration_campaign",
            input_data={
                "content": SAMPLE_CONTENT,
                "url": "https://example.com",
                "context": {
                    "industry": "technology",
                    "region": "US",
                    "target_audience": "SEO professionals"
                }
            }
        )

        result = await agent.execute_task(task)

        assert result is not None
        assert "scores" in result


class TestAuditorOrchestratorIntegration:
    """Test auditor agent integration with orchestrator"""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator with real auditor agent"""
        orch = OrchestratorAgent()
        orch.register_agent(AgentType.AUDITOR, AuditorAgent())
        return orch

    @pytest.mark.asyncio
    async def test_orchestrator_calls_auditor(self, orchestrator):
        """Test orchestrator can execute auditor agent"""
        # Create campaign
        campaign_id = orchestrator.campaign_store.create_campaign(
            workflow_name="test-auditor-integration",
            parameters={"url": "https://example.com"},
            total_tasks=1,
        )

        # Create audit task
        task = TaskMessage(
            task_id="orch_audit_1",
            task_type="audit_content",
            agent_type=AgentType.AUDITOR,
            campaign_id=campaign_id,
            input_data={
                "content": SAMPLE_CONTENT,
                "url": "https://example.com/article",
            }
        )

        # Execute task through orchestrator
        result = await orchestrator._execute_single_task(campaign_id, task)

        # Verify result
        assert result.status == TaskStatus.COMPLETED
        assert result.output_data is not None
        assert "scores" in result.output_data
        assert result.output_data["scores"]["overall"] >= 0

    @pytest.mark.asyncio
    async def test_orchestrator_parallel_audits(self, orchestrator):
        """Test orchestrator can run multiple audits in parallel"""
        # Create campaign
        campaign_id = orchestrator.campaign_store.create_campaign(
            workflow_name="test-parallel-audits",
            parameters={},
            total_tasks=3,
        )

        # Create multiple audit tasks
        tasks = [
            TaskMessage(
                task_id=f"parallel_audit_{i}",
                task_type="audit_content",
                agent_type=AgentType.AUDITOR,
                campaign_id=campaign_id,
                input_data={
                    "content": f"{SAMPLE_CONTENT}\n\nAdditional content {i}",
                }
            )
            for i in range(3)
        ]

        # Execute in parallel
        import time
        start = time.time()
        results = await orchestrator._execute_parallel_tasks(campaign_id, tasks)
        duration = time.time() - start

        # Verify all completed
        assert len(results) == 3
        assert all(r.status == TaskStatus.COMPLETED for r in results)

        # Verify parallel execution (should be faster than sequential)
        # 3 audits should complete in less than 3x single audit time
        assert duration < 10.0  # Generous threshold


class TestAuditContentHelper:
    """Test audit_content helper function with real analyzer"""

    @pytest.mark.asyncio
    async def test_quick_audit_helper(self):
        """Test quick audit helper function"""
        result = await audit_content(SAMPLE_CONTENT, url="https://example.com")

        # Verify result structure
        assert "scores" in result
        assert "overall" in result["scores"]
        assert result["scores"]["overall"] > 0

    @pytest.mark.asyncio
    async def test_quick_audit_minimal(self):
        """Test quick audit with minimal input"""
        result = await audit_content("Short test content")

        assert result is not None
        assert "scores" in result


class TestAuditorAgentPerformance:
    """Test auditor agent performance characteristics"""

    @pytest.fixture
    def agent(self):
        """Create auditor agent"""
        return AuditorAgent()

    @pytest.mark.asyncio
    async def test_audit_completes_within_timeout(self, agent):
        """Test audit completes within reasonable time"""
        task = TaskMessage(
            task_id="perf_test_1",
            task_type="audit_content",
            agent_type=AgentType.AUDITOR,
            campaign_id="perf_campaign",
            input_data={
                "content": SAMPLE_CONTENT * 5,  # 5x longer content
            },
            timeout_seconds=30.0,  # Generous timeout
        )

        import time
        start = time.time()
        result = await agent.execute_task(task)
        duration = time.time() - start

        # Should complete well within timeout
        assert result is not None
        assert duration < 10.0  # Should be much faster than 30s

    @pytest.mark.asyncio
    async def test_multiple_sequential_audits(self, agent):
        """Test multiple audits in sequence"""
        results = []

        for i in range(5):
            task = TaskMessage(
                task_id=f"seq_audit_{i}",
                task_type="audit_content",
                agent_type=AgentType.AUDITOR,
                campaign_id="seq_campaign",
                input_data={"content": SAMPLE_CONTENT}
            )

            result = await agent.execute_task(task)
            results.append(result)

        # Verify all completed
        assert len(results) == 5
        assert all("scores" in r for r in results)


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])

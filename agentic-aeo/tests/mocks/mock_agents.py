"""
Mock Agent Implementations for Testing

Provides lightweight mock agents that simulate real agent behavior
without making external API calls or performing heavy computation.
"""

import asyncio
from typing import Dict, Any
from datetime import datetime

from ...src.agents.base_agent import BaseAgent
from ...src.communication.protocol import TaskMessage, AgentType


class MockAuditorAgent(BaseAgent):
    """
    Mock Content Auditor Agent for testing.

    Simulates content audit analysis without external API calls.
    Returns realistic-looking scores and recommendations.
    """

    def __init__(self):
        super().__init__(AgentType.AUDITOR)

    async def execute_task(self, task: TaskMessage) -> Dict[str, Any]:
        """Execute mock content audit"""
        # Simulate processing time
        await asyncio.sleep(0.1)

        url = task.input_data.get("url", "")
        content = task.input_data.get("content", "")

        # Generate mock scores
        return {
            "overall_score": 75,
            "scores": {
                "experience": 70,
                "expertise": 75,
                "authoritativeness": 80,
                "trustworthiness": 75,
                "structure": 80,
                "citations": 65,
                "readability": 85,
            },
            "issues": [
                "Missing author credentials",
                "Limited citation diversity",
                "Could improve heading hierarchy",
            ],
            "recommendations": [
                "Add author bio with credentials",
                "Include 2-3 more authoritative sources",
                "Break content into more subsections",
            ],
            "metadata": {
                "url": url,
                "content_length": len(content),
                "analysis_timestamp": datetime.utcnow().isoformat(),
            },
        }


class MockOptimizerAgent(BaseAgent):
    """
    Mock Content Optimizer Agent for testing.

    Simulates content optimization without Claude API calls.
    """

    def __init__(self):
        super().__init__(AgentType.OPTIMIZER)

    async def execute_task(self, task: TaskMessage) -> Dict[str, Any]:
        """Execute mock content optimization"""
        await asyncio.sleep(0.1)

        content = task.input_data.get("content", "")
        optimization_level = task.parameters.get("optimization_level", "balanced")

        # Mock optimized content (just add prefix for testing)
        optimized_content = f"[OPTIMIZED:{optimization_level}] {content}"

        return {
            "original_content": content,
            "optimized_content": optimized_content,
            "changes_made": [
                "Added E-E-A-T signals",
                "Improved heading structure",
                "Enhanced citations",
            ],
            "before_score": 65,
            "after_score": 85,
            "improvement_percentage": 30.8,
            "metadata": {
                "optimization_level": optimization_level,
                "changes_count": 3,
                "timestamp": datetime.utcnow().isoformat(),
            },
        }


class MockCitationTrackerAgent(BaseAgent):
    """
    Mock Citation Tracker Agent for testing.

    Simulates LLM citation tracking without actual API calls.
    """

    def __init__(self):
        super().__init__(AgentType.CITATION_TRACKER)

    async def execute_task(self, task: TaskMessage) -> Dict[str, Any]:
        """Execute mock citation tracking"""
        await asyncio.sleep(0.15)

        url = task.input_data.get("url", "")
        queries = task.input_data.get("queries", [])
        llms = task.parameters.get("llms", ["ChatGPT", "Claude", "Perplexity"])

        # Generate mock citation data
        citations = {}
        for llm in llms:
            citations[llm] = {
                "cited": True if llm != "Gemini" else False,  # Mock: Gemini doesn't cite
                "position": 2 if llm == "ChatGPT" else 3,
                "context": f"According to {url}...",
            }

        return {
            "url": url,
            "queries_tracked": queries,
            "llms_tracked": llms,
            "citations": citations,
            "summary": {
                "total_llms": len(llms),
                "cited_count": len([c for c in citations.values() if c["cited"]]),
                "citation_rate": 0.75,  # 75% citation rate
            },
            "metadata": {
                "tracking_timestamp": datetime.utcnow().isoformat(),
            },
        }


class MockResearcherAgent(BaseAgent):
    """
    Mock Query Researcher Agent for testing.

    Simulates query research without external API calls.
    """

    def __init__(self):
        super().__init__(AgentType.RESEARCHER)

    async def execute_task(self, task: TaskMessage) -> Dict[str, Any]:
        """Execute mock query research"""
        await asyncio.sleep(0.1)

        topic = task.input_data.get("topic", "")

        return {
            "topic": topic,
            "target_queries": [
                f"what is {topic}",
                f"how to {topic}",
                f"{topic} best practices",
            ],
            "competitors": [
                {
                    "url": "https://competitor1.com",
                    "citation_count": 8,
                    "domain_authority": 85,
                },
                {
                    "url": "https://competitor2.com",
                    "citation_count": 5,
                    "domain_authority": 75,
                },
            ],
            "opportunities": [
                "Competitor1 missing technical depth",
                "Gap in beginner-friendly content",
            ],
            "metadata": {
                "research_timestamp": datetime.utcnow().isoformat(),
            },
        }


class MockReporterAgent(BaseAgent):
    """
    Mock Report Generator Agent for testing.

    Simulates report generation without heavy processing.
    """

    def __init__(self):
        super().__init__(AgentType.REPORTER)

    async def execute_task(self, task: TaskMessage) -> Dict[str, Any]:
        """Execute mock report generation"""
        await asyncio.sleep(0.05)

        campaign_data = task.input_data.get("campaign_data", {})
        report_type = task.parameters.get("report_type", "comprehensive")

        # Generate mock markdown report
        markdown_report = f"""# AEO Campaign Report

## Executive Summary

Campaign completed successfully with overall score improvement from 65 to 85.

## Key Metrics

- **Initial Score**: 65/100
- **Final Score**: 85/100
- **Improvement**: +20 points (30.8%)
- **Citation Rate**: 75% (3/4 LLMs)

## Recommendations

1. Continue monitoring citations weekly
2. Optimize for Gemini (currently not citing)
3. Add more authoritative sources

---

*Report Type*: {report_type}
*Generated*: {datetime.utcnow().isoformat()}
"""

        return {
            "report_type": report_type,
            "markdown_report": markdown_report,
            "summary": {
                "initial_score": 65,
                "final_score": 85,
                "improvement": 20,
                "citation_rate": 0.75,
            },
            "metadata": {
                "generation_timestamp": datetime.utcnow().isoformat(),
            },
        }


class MockLearningAgent(BaseAgent):
    """
    Mock Learning Optimizer Agent for testing.

    Simulates pattern analysis without ML processing.
    """

    def __init__(self):
        super().__init__(AgentType.LEARNING)

    async def execute_task(self, task: TaskMessage) -> Dict[str, Any]:
        """Execute mock learning optimization"""
        await asyncio.sleep(0.1)

        campaign_results = task.input_data.get("campaign_results", [])

        return {
            "patterns_identified": [
                "Adding author credentials increases E-E-A-T by 12%",
                "Citations from .edu domains improve trustworthiness by 18%",
                "Structured content (H2/H3) improves LLM citation rate by 25%",
            ],
            "recommendations": [
                "Always include author bio",
                "Prioritize .edu/.gov citations",
                "Use clear heading hierarchy",
            ],
            "confidence_scores": {
                "author_credentials": 0.85,
                "citation_quality": 0.78,
                "structure": 0.92,
            },
            "metadata": {
                "campaigns_analyzed": len(campaign_results),
                "analysis_timestamp": datetime.utcnow().isoformat(),
            },
        }

"""
Competitive Workflow Implementation

Deep competitive analysis for AEO strategies.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from communication.protocol import TaskMessage, AgentType


class CompetitiveWorkflow:
    """
    Implements the /aeo-compete workflow.

    Workflow Steps:
    1. Query Research for topic (Researcher Agent) - priority 1
    2. Competitor Content Audit (Auditor Agent per competitor) - priority 2 (parallel)
    3. Citation Analysis (Tracker Agent) - priority 3
    4. Gap Analysis (Researcher Agent) - priority 4
    5. Strategy Report (Reporter Agent) - priority 5
    """

    def __init__(self):
        """Initialize Competitive Workflow."""
        self.workflow_name = "aeo-compete"
        self.workflow_version = "1.0.0"

    def decompose(
        self,
        topic: str,
        competitor_urls: List[str],
        region: str = "US",
        include_citations: bool = True
    ) -> List[TaskMessage]:
        """
        Decompose competitive analysis into tasks.

        Args:
            topic: Topic or industry to analyze
            competitor_urls: List of competitor URLs to analyze (1-5 URLs)
            region: Geographic region for queries
            include_citations: Whether to analyze citation data

        Returns:
            List of TaskMessage objects with priorities and dependencies
        """
        tasks = []
        timestamp = datetime.now().isoformat()

        # Validate competitor count
        if len(competitor_urls) > 5:
            competitor_urls = competitor_urls[:5]  # Limit to 5 for performance

        # Task 1: Query Research for topic (priority 1)
        tasks.append(TaskMessage(
            task_id=f"research_topic_{timestamp}",
            agent_type=AgentType.RESEARCHER,
            input_data={
                "topic": topic,
                "region": region,
                "include_competitors": True,
                "competitor_urls": competitor_urls
            },
            priority=1,
            depends_on=[],
            deadline=datetime.now() + timedelta(minutes=5)
        ))

        # Task 2: Competitor Content Audits (priority 2, parallel)
        audit_task_ids = []
        for idx, url in enumerate(competitor_urls):
            audit_task_id = f"audit_competitor_{idx}_{timestamp}"
            audit_task_ids.append(audit_task_id)

            tasks.append(TaskMessage(
                task_id=audit_task_id,
                agent_type=AgentType.AUDITOR,
                input_data={
                    "url": url,
                    "context": {
                        "topic": topic,
                        "competitor_index": idx,
                        "total_competitors": len(competitor_urls)
                    }
                },
                priority=2,
                depends_on=[],
                deadline=datetime.now() + timedelta(minutes=10)
            ))

        # Task 3: Citation Analysis (priority 3, depends on research)
        if include_citations:
            tasks.append(TaskMessage(
                task_id=f"citations_{timestamp}",
                agent_type=AgentType.CITATION_TRACKER,
                input_data={
                    "urls": competitor_urls,
                    "queries": [],  # Will be populated from research results
                    "analysis_type": "comparative"
                },
                priority=3,
                depends_on=[f"research_topic_{timestamp}"],
                deadline=datetime.now() + timedelta(minutes=12)
            ))

        # Task 4: Gap Analysis (priority 4, depends on audits + research)
        tasks.append(TaskMessage(
            task_id=f"gap_analysis_{timestamp}",
            agent_type=AgentType.RESEARCHER,
            input_data={
                "topic": topic,
                "analysis_type": "content_gaps",
                "audit_task_ids": audit_task_ids,
                "research_task_id": f"research_topic_{timestamp}"
            },
            priority=4,
            depends_on=[f"research_topic_{timestamp}"] + audit_task_ids,
            deadline=datetime.now() + timedelta(minutes=15)
        ))

        # Task 5: Strategy Report (priority 5, depends on all)
        report_dependencies = [f"research_topic_{timestamp}", f"gap_analysis_{timestamp}"] + audit_task_ids
        if include_citations:
            report_dependencies.append(f"citations_{timestamp}")

        tasks.append(TaskMessage(
            task_id=f"report_{timestamp}",
            agent_type=AgentType.REPORTER,
            input_data={
                "report_type": "competitive",
                "report_data": {
                    "topic": topic,
                    "competitor_count": len(competitor_urls),
                    "research_task_id": f"research_topic_{timestamp}",
                    "audit_task_ids": audit_task_ids,
                    "gap_analysis_task_id": f"gap_analysis_{timestamp}",
                    "citations_task_id": f"citations_{timestamp}" if include_citations else None
                }
            },
            priority=5,
            depends_on=report_dependencies,
            deadline=datetime.now() + timedelta(minutes=18)
        ))

        return tasks

    def validate_input(
        self,
        topic: str,
        competitor_urls: List[str]
    ) -> tuple[bool, Optional[str]]:
        """
        Validate workflow input parameters.

        Returns:
            (is_valid, error_message)
        """
        # Validate topic
        if not topic or not isinstance(topic, str):
            return False, "Topic is required and must be a string"

        if len(topic.strip()) < 3:
            return False, "Topic must be at least 3 characters"

        # Validate competitor URLs
        if not competitor_urls or not isinstance(competitor_urls, list):
            return False, "At least one competitor URL is required"

        if len(competitor_urls) == 0:
            return False, "At least one competitor URL is required"

        if len(competitor_urls) > 10:
            return False, "Maximum 10 competitor URLs allowed"

        # Validate each URL
        for url in competitor_urls:
            if not isinstance(url, str):
                return False, f"Invalid URL: {url} (must be string)"

            if not url.startswith(("http://", "https://")):
                return False, f"Invalid URL: {url} (must start with http:// or https://)"

        return True, None

    def create_executive_summary(
        self,
        results: Dict[str, Any],
        topic: str,
        competitor_count: int
    ) -> Dict[str, Any]:
        """
        Create executive summary from all task results.

        Args:
            results: Dictionary of task results keyed by task_id
            topic: Analysis topic
            competitor_count: Number of competitors analyzed

        Returns:
            Executive summary dictionary
        """
        summary = {
            "workflow": self.workflow_name,
            "topic": topic,
            "competitors_analyzed": competitor_count,
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "tasks_completed": len(results),
            "executive_summary": self._generate_summary_text(results, topic),
            "competitive_insights": self._extract_competitive_insights(results),
            "recommendations": self._generate_recommendations(results),
            "target_opportunities": self._extract_opportunities(results)
        }

        return summary

    def _generate_summary_text(
        self,
        results: Dict[str, Any],
        topic: str
    ) -> str:
        """Generate executive summary text."""
        summary_parts = [f"# Competitive AEO Analysis: {topic}\n"]

        # Count completed audits
        audit_count = sum(
            1 for task_id, result in results.items()
            if "audit_competitor_" in task_id and result.status.value == "completed"
        )

        summary_parts.append(f"**Competitors Analyzed**: {audit_count}")

        # Add key findings
        summary_parts.append("\n## Key Findings")
        summary_parts.append("- Comprehensive competitive analysis completed")
        summary_parts.append("- Content gaps identified")
        summary_parts.append("- Citation opportunities discovered")

        return "\n".join(summary_parts)

    def _extract_competitive_insights(
        self,
        results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract competitive insights from results."""
        insights = {
            "competitor_scores": [],
            "average_competitor_score": 0,
            "top_competitor": None,
            "weakest_competitor": None,
            "content_gaps": [],
            "citation_leaders": []
        }

        # Extract competitor scores from audits
        scores = []
        for task_id, result in results.items():
            if "audit_competitor_" in task_id and result.status.value == "completed":
                if result.output_data and "scores" in result.output_data:
                    overall_score = result.output_data["scores"].get("overall", 0)
                    competitor_idx = int(task_id.split("_")[2])
                    scores.append({
                        "competitor_index": competitor_idx,
                        "score": overall_score
                    })

        if scores:
            insights["competitor_scores"] = sorted(scores, key=lambda x: x["score"], reverse=True)
            insights["average_competitor_score"] = sum(s["score"] for s in scores) / len(scores)
            insights["top_competitor"] = insights["competitor_scores"][0] if scores else None
            insights["weakest_competitor"] = insights["competitor_scores"][-1] if scores else None

        # Extract content gaps from gap analysis
        for task_id, result in results.items():
            if "gap_analysis_" in task_id and result.status.value == "completed":
                if result.output_data and "content_gaps" in result.output_data:
                    insights["content_gaps"] = result.output_data["content_gaps"][:10]  # Top 10

        return insights

    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        # Analyze gap analysis results
        for task_id, result in results.items():
            if "gap_analysis_" in task_id and result.status.value == "completed":
                if result.output_data:
                    gaps = result.output_data.get("content_gaps", [])
                    if gaps:
                        recommendations.append(
                            f"Create content addressing {len(gaps)} identified gaps"
                        )

        # Default recommendations
        if not recommendations:
            recommendations = [
                "Develop content targeting underserved queries",
                "Improve E-E-A-T signals to compete with top performers",
                "Focus on citation-worthy content formats"
            ]

        return recommendations

    def _extract_opportunities(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract target opportunities from research."""
        opportunities = []

        for task_id, result in results.items():
            if "research_topic_" in task_id and result.status.value == "completed":
                if result.output_data and "target_queries" in result.output_data:
                    queries = result.output_data["target_queries"]
                    for query in queries[:10]:  # Top 10
                        opportunities.append({
                            "query": query,
                            "opportunity_type": "citation_target",
                            "priority": "high"
                        })

        return opportunities

"""
Campaign Workflow Implementation

Complete end-to-end AEO campaign workflow.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from communication.protocol import TaskMessage, AgentType, TaskType


class CampaignWorkflow:
    """
    Implements the /aeo-campaign workflow.

    Workflow Steps:
    1. Content Audit (Auditor Agent) - priority 1
    2. Query Research (Researcher Agent) - priority 1 (parallel with audit)
    3. Content Optimization (Optimizer Agent) - priority 2, depends on audit
    4. Citation Tracking Setup (Tracker Agent) - priority 3
    5. Report Generation (Reporter Agent) - priority 4, depends on all
    6. Pattern Learning (Learning Agent) - priority 5, analyzes campaign
    """

    def __init__(self):
        """Initialize Campaign Workflow."""
        self.workflow_name = "aeo-campaign"
        self.workflow_version = "1.0.0"

    def decompose(
        self,
        campaign_id: str,
        url: str,
        queries: Optional[List[str]] = None,
        mode: str = "comprehensive",
        industry: Optional[str] = None,
        optimization_level: str = "balanced",
        tracking_duration_days: int = 30
    ) -> List[TaskMessage]:
        """
        Decompose campaign into tasks.

        Args:
            campaign_id: Unique campaign identifier
            url: URL of content to optimize
            queries: Target queries (optional, will research if not provided)
            mode: Campaign mode (minimal, balanced, comprehensive)
            industry: Industry vertical
            optimization_level: conservative, balanced, aggressive
            tracking_duration_days: How long to track citations

        Returns:
            List of TaskMessage objects with priorities and dependencies
        """
        tasks = []
        timestamp = datetime.now().isoformat()

        # Task 1: Content Audit (priority 1)
        tasks.append(TaskMessage(
            task_id=f"audit_{timestamp}",
            campaign_id=campaign_id,
            task_type=TaskType.AUDIT_CONTENT,
            agent_type=AgentType.AUDITOR,
            input_data={
                "url": url,
                "context": {
                    "industry": industry,
                    "campaign_mode": mode
                }
            },
            dependencies=[]
        ))

        # Task 2: Query Research (priority 1, parallel with audit)
        if queries:
            # User provided queries, use them
            research_input = {
                "topic": f"Content from {url}",
                "queries": queries,
                "include_competitors": mode in ["balanced", "comprehensive"]
            }
        else:
            # Research queries from content
            research_input = {
                "topic": f"Content from {url}",
                "region": "US",
                "include_competitors": mode in ["balanced", "comprehensive"]
            }

        tasks.append(TaskMessage(
            task_id=f"research_{timestamp}",
            campaign_id=campaign_id,
            task_type=TaskType.RESEARCH_QUERIES,
            agent_type=AgentType.RESEARCHER,
            input_data=research_input,
            dependencies=[]
        ))

        # Task 3: Content Optimization (priority 2, depends on audit)
        tasks.append(TaskMessage(
            task_id=f"optimize_{timestamp}",
            campaign_id=campaign_id,
            task_type=TaskType.OPTIMIZE_CONTENT,
            agent_type=AgentType.OPTIMIZER,
            input_data={
                "level": optimization_level,
                "context": {
                    "industry": industry,
                    "campaign_mode": mode,
                    "audit_task_id": f"audit_{timestamp}"  # Reference to get audit results
                }
            },
            dependencies=[f"audit_{timestamp}"]
        ))

        # Task 4: Citation Tracking Setup (priority 3)
        tasks.append(TaskMessage(
            task_id=f"track_{timestamp}",
            campaign_id=campaign_id,
            task_type=TaskType.TRACK_CITATIONS,
            agent_type=AgentType.TRACKER,
            input_data={
                "url": url,
                "queries": queries or [],  # Will be populated from research results
                "duration_days": tracking_duration_days
            },
            dependencies=[f"research_{timestamp}"]
        ))

        # Task 5: Report Generation (priority 4, depends on all previous)
        tasks.append(TaskMessage(
            task_id=f"report_{timestamp}",
            campaign_id=campaign_id,
            task_type=TaskType.GENERATE_REPORT,
            agent_type=AgentType.REPORTER,
            input_data={
                "report_type": "campaign",
                "report_data": {
                    "url": url,
                    "campaign_mode": mode,
                    "audit_task_id": f"audit_{timestamp}",
                    "optimize_task_id": f"optimize_{timestamp}",
                    "track_task_id": f"track_{timestamp}",
                    "research_task_id": f"research_{timestamp}"
                }
            },
            dependencies=[
                f"audit_{timestamp}",
                f"optimize_{timestamp}",
                f"track_{timestamp}",
                f"research_{timestamp}"
            ]
        ))

        # Task 6: Pattern Learning (priority 5, optional for comprehensive mode)
        if mode == "comprehensive":
            tasks.append(TaskMessage(
                task_id=f"learn_{timestamp}",
                campaign_id=campaign_id,
                task_type=TaskType.LEARN_PATTERNS,
                agent_type=AgentType.LEARNING,
                input_data={
                    "campaign_data": {
                        "url": url,
                        "industry": industry,
                        "campaign_mode": mode,
                        "all_task_ids": [t.task_id for t in tasks]
                    },
                    "industry": industry
                },
                dependencies=[f"report_{timestamp}"]
            ))

        return tasks

    def validate_input(
        self,
        url: str,
        mode: str = "comprehensive"
    ) -> tuple[bool, Optional[str]]:
        """
        Validate workflow input parameters.

        Returns:
            (is_valid, error_message)
        """
        # Validate URL
        if not url or not isinstance(url, str):
            return False, "URL is required and must be a string"

        if not url.startswith(("http://", "https://")):
            return False, "URL must start with http:// or https://"

        # Validate mode
        valid_modes = ["minimal", "balanced", "comprehensive"]
        if mode not in valid_modes:
            return False, f"Mode must be one of: {', '.join(valid_modes)}"

        return True, None

    def create_executive_summary(
        self,
        results: Dict[str, Any],
        mode: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Create executive summary from all task results.

        Args:
            results: Dictionary of task results keyed by task_id
            mode: Campaign mode

        Returns:
            Executive summary dictionary
        """
        summary = {
            "workflow": self.workflow_name,
            "mode": mode,
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "tasks_completed": len(results),
            "executive_summary": self._generate_summary_text(results),
            "key_metrics": self._extract_key_metrics(results),
            "recommendations": self._generate_recommendations(results),
            "next_steps": self._generate_next_steps(results, mode)
        }

        return summary

    def _generate_summary_text(self, results: Dict[str, Any]) -> str:
        """Generate executive summary text."""
        audit_result = None
        optimize_result = None

        for task_id, result in results.items():
            if "audit_" in task_id and result.status.value == "completed":
                audit_result = result
            elif "optimize_" in task_id and result.status.value == "completed":
                optimize_result = result

        summary_parts = ["# AEO Campaign Executive Summary\n"]

        if audit_result and audit_result.output_data:
            scores = audit_result.output_data.get("scores", {})
            overall = scores.get("overall", 0)
            summary_parts.append(f"**Current AEO Score**: {overall}/100")

        if optimize_result and optimize_result.output_data:
            summary_parts.append("\n**Optimization**: Content successfully optimized for LLM citations")

        return "\n".join(summary_parts)

    def _extract_key_metrics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key metrics from results."""
        metrics = {
            "current_aeo_score": None,
            "optimization_improvements": [],
            "target_queries": [],
            "citations_tracked": 0
        }

        for task_id, result in results.items():
            if result.status.value != "completed":
                continue

            if "audit_" in task_id and result.output_data:
                scores = result.output_data.get("scores", {})
                metrics["current_aeo_score"] = scores.get("overall", 0)

            elif "optimize_" in task_id and result.output_data:
                changes = result.output_data.get("changes", [])
                metrics["optimization_improvements"] = changes[:5]  # Top 5

            elif "research_" in task_id and result.output_data:
                queries = result.output_data.get("target_queries", [])
                metrics["target_queries"] = queries[:10]  # Top 10

        return metrics

    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        # Analyze audit results
        for task_id, result in results.items():
            if "audit_" in task_id and result.output_data:
                scores = result.output_data.get("scores", {})
                eeat_score = scores.get("eeat", {}).get("overall", 0)

                if eeat_score < 70:
                    recommendations.append(
                        "Improve E-E-A-T signals: Add author credentials, external citations, and expertise indicators"
                    )

        # Default recommendations
        if not recommendations:
            recommendations = [
                "Continue optimizing content for target queries",
                "Monitor citation performance weekly",
                "Update content based on learning insights"
            ]

        return recommendations

    def _generate_next_steps(
        self,
        results: Dict[str, Any],
        mode: str
    ) -> List[str]:
        """Generate next steps based on mode."""
        if mode == "minimal":
            return [
                "Review audit report",
                "Apply suggested optimizations",
                "Track results for 7 days"
            ]
        elif mode == "balanced":
            return [
                "Review comprehensive audit and optimization reports",
                "Implement recommended changes",
                "Monitor citations for 30 days",
                "Run follow-up campaign in 30 days"
            ]
        else:  # comprehensive
            return [
                "Review all reports (audit, optimization, research, citation tracking)",
                "Implement all recommended optimizations",
                "Set up automated citation monitoring",
                "Review learning insights weekly",
                "Iterate based on pattern analysis",
                "Run competitive analysis quarterly"
            ]

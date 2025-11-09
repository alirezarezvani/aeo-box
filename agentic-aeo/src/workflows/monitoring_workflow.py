"""
Monitoring Workflow Implementation

Continuous citation monitoring with alerts and reporting.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from communication.protocol import TaskMessage, AgentType, TaskType


class MonitoringWorkflow:
    """
    Implements the /aeo-monitor workflow.

    Workflow Steps:
    1. Initial Baseline Audit (Auditor Agent) - priority 1
    2. Set up Citation Tracking (Tracker Agent) - priority 2
    3. Initial Report Generation (Reporter Agent) - priority 3

    Note: Ongoing monitoring (daily checks, alerts) is handled by the
    Citation Tracker Agent's internal scheduling.
    """

    def __init__(self):
        """Initialize Monitoring Workflow."""
        self.workflow_name = "aeo-monitor"
        self.workflow_version = "1.0.0"

    def decompose(
        self,
        campaign_id: str,
        url: str,
        duration_days: int = 90,
        queries: Optional[List[str]] = None,
        alert_on_changes: bool = True,
        weekly_reports: bool = True
    ) -> List[TaskMessage]:
        """
        Decompose monitoring workflow into tasks.

        Args:
            campaign_id: Unique campaign identifier
            url: URL to monitor
            duration_days: Monitoring duration (default: 90 days)
            queries: Specific queries to track (optional)
            alert_on_changes: Send alerts on citation changes
            weekly_reports: Generate weekly summary reports

        Returns:
            List of TaskMessage objects with priorities and dependencies
        """
        tasks = []
        timestamp = datetime.now().isoformat()

        # Task 1: Initial Baseline Audit (priority 1)
        tasks.append(TaskMessage(
            task_id=f"baseline_audit_{timestamp}",
            campaign_id=campaign_id,
            task_type=TaskType.AUDIT_CONTENT,
            agent_type=AgentType.AUDITOR,
            input_data={
                "url": url,
                "context": {
                    "monitoring_setup": True,
                    "duration_days": duration_days
                }
            },
            dependencies=[],
        ))

        # Task 2: Set up Citation Tracking (priority 2, depends on audit)
        tasks.append(TaskMessage(
            task_id=f"setup_tracking_{timestamp}",
            campaign_id=campaign_id,
            task_type=TaskType.TRACK_CITATIONS,
            agent_type=AgentType.TRACKER,
            input_data={
                "url": url,
                "queries": queries or [],
                "duration_days": duration_days,
                "monitoring_mode": True,
                "alert_on_changes": alert_on_changes,
                "check_frequency": "daily"
            },
            dependencies=[f"baseline_audit_{timestamp}"],
        ))

        # Task 3: Initial Monitoring Report (priority 3)
        tasks.append(TaskMessage(
            task_id=f"initial_report_{timestamp}",
            campaign_id=campaign_id,
            task_type=TaskType.GENERATE_REPORT,
            agent_type=AgentType.REPORTER,
            input_data={
                "report_type": "monitoring_setup",
                "report_data": {
                    "url": url,
                    "duration_days": duration_days,
                    "baseline_audit_task_id": f"baseline_audit_{timestamp}",
                    "tracking_task_id": f"setup_tracking_{timestamp}",
                    "alert_on_changes": alert_on_changes,
                    "weekly_reports": weekly_reports
                }
            },
            dependencies=[f"baseline_audit_{timestamp}", f"setup_tracking_{timestamp}"],
        ))

        return tasks

    def validate_input(
        self,
        url: str,
        duration_days: int = 90
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

        # Validate duration
        if not isinstance(duration_days, int):
            return False, "Duration must be an integer"

        if duration_days < 1:
            return False, "Duration must be at least 1 day"

        if duration_days > 365:
            return False, "Duration cannot exceed 365 days"

        return True, None

    def create_executive_summary(
        self,
        results: Dict[str, Any],
        url: str,
        duration_days: int
    ) -> Dict[str, Any]:
        """
        Create executive summary from monitoring setup results.

        Args:
            results: Dictionary of task results keyed by task_id
            url: URL being monitored
            duration_days: Monitoring duration

        Returns:
            Executive summary dictionary
        """
        summary = {
            "workflow": self.workflow_name,
            "url": url,
            "monitoring_duration_days": duration_days,
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "tasks_completed": len(results),
            "executive_summary": self._generate_summary_text(results, url, duration_days),
            "baseline_metrics": self._extract_baseline_metrics(results),
            "monitoring_schedule": self._create_monitoring_schedule(duration_days),
            "next_steps": self._generate_next_steps(duration_days)
        }

        return summary

    def _generate_summary_text(
        self,
        results: Dict[str, Any],
        url: str,
        duration_days: int
    ) -> str:
        """Generate executive summary text."""
        summary_parts = [f"# Citation Monitoring Setup: {url}\n"]

        # Extract baseline audit results
        baseline_score = None
        for task_id, result in results.items():
            if "baseline_audit_" in task_id and result.status.value == "completed":
                if result.output_data and "scores" in result.output_data:
                    baseline_score = result.output_data["scores"].get("overall", 0)

        if baseline_score is not None:
            summary_parts.append(f"**Baseline AEO Score**: {baseline_score}/100")

        summary_parts.append(f"\n**Monitoring Duration**: {duration_days} days")
        summary_parts.append("**Check Frequency**: Daily")

        # Add monitoring setup confirmation
        tracking_setup = False
        for task_id, result in results.items():
            if "setup_tracking_" in task_id and result.status.value == "completed":
                tracking_setup = True

        if tracking_setup:
            summary_parts.append("\n✅ Citation tracking successfully configured")

        return "\n".join(summary_parts)

    def _extract_baseline_metrics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract baseline metrics from audit."""
        metrics = {
            "baseline_aeo_score": None,
            "baseline_eeat_score": None,
            "baseline_structure_score": None,
            "baseline_citations_count": 0,
            "baseline_date": datetime.now().isoformat()
        }

        for task_id, result in results.items():
            if "baseline_audit_" in task_id and result.status.value == "completed":
                if result.output_data and "scores" in result.output_data:
                    scores = result.output_data["scores"]
                    metrics["baseline_aeo_score"] = scores.get("overall", 0)

                    eeat = scores.get("eeat", {})
                    if isinstance(eeat, dict):
                        metrics["baseline_eeat_score"] = eeat.get("overall", 0)

                    structure = scores.get("structure", {})
                    if isinstance(structure, dict):
                        metrics["baseline_structure_score"] = structure.get("overall", 0)

                if result.output_data and "citations" in result.output_data:
                    citations = result.output_data["citations"]
                    if isinstance(citations, list):
                        metrics["baseline_citations_count"] = len(citations)

        return metrics

    def _create_monitoring_schedule(self, duration_days: int) -> Dict[str, Any]:
        """Create monitoring schedule."""
        start_date = datetime.now()
        end_date = start_date + timedelta(days=duration_days)

        schedule = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "duration_days": duration_days,
            "check_frequency": "daily",
            "daily_checks": duration_days,
            "weekly_reports": duration_days // 7,
            "final_report_date": end_date.isoformat()
        }

        # Calculate milestone dates
        milestones = []
        for week in range(1, (duration_days // 7) + 1):
            milestone_date = start_date + timedelta(days=week * 7)
            if milestone_date <= end_date:
                milestones.append({
                    "week": week,
                    "date": milestone_date.isoformat(),
                    "type": "weekly_summary"
                })

        schedule["milestones"] = milestones

        return schedule

    def _generate_next_steps(self, duration_days: int) -> List[str]:
        """Generate next steps for monitoring."""
        next_steps = [
            "Citation tracking is now active",
            f"Daily citation checks will run for {duration_days} days",
            "Review initial baseline metrics"
        ]

        # Add weekly report reminders
        weekly_reports = duration_days // 7
        if weekly_reports > 0:
            next_steps.append(f"Expect {weekly_reports} weekly summary reports")

        # Add final report date
        end_date = datetime.now() + timedelta(days=duration_days)
        next_steps.append(f"Final performance summary on {end_date.strftime('%Y-%m-%d')}")

        # Add alert information
        next_steps.append("Alerts will be sent if significant citation changes are detected")

        return next_steps

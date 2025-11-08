"""
Report Generator Agent

Generates AEO reports and deliverables using AEO Skill report_generator module.
"""

import asyncio
from typing import Any, Dict, Optional
from datetime import datetime

from .base_agent import BaseAgent
from ..communication.protocol import AgentType, TaskMessage
from ..aeo_skill.report_generator import ReportGenerator


class ReporterAgent(BaseAgent):
    """
    Report Generator Agent for AEO reporting.

    Input Requirements:
        - report_type: str (required) - 'audit', 'optimization', 'citation'
        - data: dict (required) - Report data from other agents
        - format: str (optional) - 'markdown', 'html' (default: 'markdown')

    Output Format:
        {
            "report": "...",  # Formatted report string
            "format": "markdown",
            "generated_at": "2025-01-08T...",
            "report_type": "audit"
        }
    """

    def __init__(self):
        """Initialize Reporter Agent."""
        super().__init__(AgentType.REPORTER)
        self.generator = ReportGenerator()
        self.logger.info("Reporter agent initialized")

    async def execute_task(self, task: TaskMessage) -> Dict[str, Any]:
        """Execute report generation task."""
        self.logger.info(f"Executing report task: {task.task_id}")

        if "report_type" not in task.input_data:
            raise ValueError("Missing required input: 'report_type'")
        if "data" not in task.input_data:
            raise ValueError("Missing required input: 'data'")

        report_type = task.input_data.get("report_type")
        data = task.input_data.get("data")
        format_type = task.input_data.get("format", "markdown")

        valid_types = ['audit', 'optimization', 'citation']
        if report_type not in valid_types:
            raise ValueError(f"Invalid report_type. Must be one of: {valid_types}")

        try:
            loop = asyncio.get_event_loop()

            if report_type == 'audit':
                report = await loop.run_in_executor(
                    None,
                    self.generator.generate_audit_report,
                    data,
                    format_type
                )
            elif report_type == 'optimization':
                report = await loop.run_in_executor(
                    None,
                    self.generator.generate_optimization_report,
                    data,
                    format_type
                )
            else:  # citation
                report = await loop.run_in_executor(
                    None,
                    self.generator.generate_citation_report,
                    data,
                    format_type
                )

            result = {
                "report": report,
                "format": format_type,
                "generated_at": datetime.now().isoformat(),
                "report_type": report_type
            }

            self.logger.info(f"Report generated: {len(report)} characters")
            return result

        except Exception as e:
            self.logger.error(f"Report generation failed: {str(e)}", exc_info=True)
            raise RuntimeError(f"Report generation failed: {str(e)}") from e

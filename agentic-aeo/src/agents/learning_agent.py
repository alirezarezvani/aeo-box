"""
Learning Optimizer Agent

Analyzes success patterns and provides adaptive learning recommendations.
"""

import asyncio
from typing import Any, Dict, Optional, List
from datetime import datetime

from .base_agent import BaseAgent
from ..communication.protocol import AgentType, TaskMessage
from ..aeo_skill.success_patterns import SuccessPatternAnalyzer


class LearningAgent(BaseAgent):
    """
    Learning Optimizer Agent for pattern analysis.

    Input Requirements:
        - campaign_data: dict (required) - Campaign results data
        - industry: str (optional) - Industry vertical

    Output Format:
        {
            "patterns": [...],
            "recommendations": [...],
            "confidence_scores": {...}
        }
    """

    def __init__(self):
        """Initialize Learning Agent."""
        super().__init__(AgentType.LEARNING)
        self.analyzer = SuccessPatternAnalyzer()
        self.logger.info("Learning agent initialized")

    async def execute_task(self, task: TaskMessage) -> Dict[str, Any]:
        """Execute pattern analysis task."""
        self.logger.info(f"Executing learning task: {task.task_id}")

        if "campaign_data" not in task.input_data:
            raise ValueError("Missing required input: 'campaign_data'")

        campaign_data = task.input_data.get("campaign_data")
        industry = task.input_data.get("industry")

        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self.analyzer.analyze_patterns,
                campaign_data,
                industry
            )

            self.logger.info(
                f"Pattern analysis complete: {len(result.get('patterns', []))} patterns found"
            )
            return result

        except Exception as e:
            self.logger.error(f"Pattern analysis failed: {str(e)}", exc_info=True)
            raise RuntimeError(f"Pattern analysis failed: {str(e)}") from e

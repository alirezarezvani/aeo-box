"""
Content Optimizer Agent

Optimizes content for AEO using the AEO Skill optimizer module.
Improves E-E-A-T signals, structure, citations, and LLM parsing optimization.
"""

import asyncio
from typing import Any, Dict, Optional, List
from datetime import datetime

from .base_agent import BaseAgent
from ..communication.protocol import AgentType, TaskMessage
from ..aeo_skill.optimizer import ContentOptimizer
from ..aeo_skill.content_analyzer import ContentAnalyzer


class OptimizerAgent(BaseAgent):
    """
    Content Optimizer Agent for AEO content enhancement.

    Integrates with AEO Skill ContentOptimizer to provide:
    - E-E-A-T signal enhancement
    - Structure optimization for LLM parsing
    - Citation quality improvement
    - Data point additions
    - Heading optimization

    Input Requirements:
        - content: str (required) - Content to optimize
        - level: str (optional) - Optimization level: 'conservative', 'balanced' (default), 'aggressive'
        - focus_areas: List[str] (optional) - Specific areas: ['citations', 'structure', 'eeat', 'data_points']
        - context: dict (optional) - Brand voice, industry, etc.

    Output Format:
        {
            "original": "...",
            "optimized": "...",
            "changes": [{type, description, location}],
            "before_score": 75,
            "after_score": 85,
            "improvement": 10,
            "strategies_applied": ["add_structure", "enhance_eeat"],
            "timestamp": "2025-01-08T..."
        }
    """

    def __init__(self, content_analyzer: Optional[ContentAnalyzer] = None):
        """
        Initialize Optimizer Agent.

        Args:
            content_analyzer: Optional ContentAnalyzer for audits
        """
        super().__init__(AgentType.OPTIMIZER)

        # Initialize optimizer with optional analyzer
        self.optimizer = ContentOptimizer(analyzer=content_analyzer)

        self.logger.info("Optimizer agent initialized", extra={
            "has_analyzer": content_analyzer is not None
        })

    async def execute_task(self, task: TaskMessage) -> Dict[str, Any]:
        """
        Execute content optimization task.

        Args:
            task: Task message containing:
                - input_data.content: Content to optimize
                - input_data.level: Optimization level (optional)
                - input_data.focus_areas: Specific areas to focus on (optional)
                - input_data.context: Additional context (optional)

        Returns:
            Optimization results with before/after scores and changes

        Raises:
            ValueError: If content is missing or invalid
            RuntimeError: If optimization fails
        """
        self.logger.info(
            f"Executing optimization task: {task.task_id}",
            extra={
                "task_id": task.task_id,
                "campaign_id": task.campaign_id,
            }
        )

        # Validate required inputs
        if "content" not in task.input_data:
            raise ValueError("Missing required input: 'content'")

        content = task.input_data.get("content")
        if not content or not isinstance(content, str):
            raise ValueError("Invalid content: must be non-empty string")

        # Extract optional parameters
        level = task.input_data.get("level", "balanced")
        focus_areas = task.input_data.get("focus_areas")
        context = task.input_data.get("context", {})

        # Validate optimization level
        valid_levels = ['conservative', 'balanced', 'aggressive']
        if level not in valid_levels:
            raise ValueError(f"Invalid level '{level}'. Must be one of: {valid_levels}")

        self.logger.info(
            f"Starting content optimization",
            extra={
                "content_length": len(content),
                "level": level,
                "focus_areas": focus_areas,
                "has_context": bool(context),
            }
        )

        try:
            # Run optimization (CPU-bound)
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,  # Use default executor
                self.optimizer.optimize,
                content,
                level,
                focus_areas,
                context
            )

            # Add timestamp
            result['timestamp'] = datetime.now().isoformat()

            self.logger.info(
                f"Optimization complete",
                extra={
                    "task_id": task.task_id,
                    "before_score": result["before_score"],
                    "after_score": result["after_score"],
                    "improvement": result["improvement"],
                    "strategies_count": len(result["strategies_applied"]),
                }
            )

            # Return optimization result
            return result

        except Exception as e:
            self.logger.error(
                f"Content optimization failed: {str(e)}",
                extra={
                    "task_id": task.task_id,
                    "error": str(e),
                },
                exc_info=True
            )
            raise RuntimeError(f"Content optimization failed: {str(e)}") from e

    def _validate_quality(self, result: Dict[str, Any]) -> bool:
        """
        Validate quality of optimization result.

        Args:
            result: Optimization result from ContentOptimizer

        Returns:
            True if result meets quality criteria
        """
        required_keys = [
            "original", "optimized", "changes",
            "before_score", "after_score", "improvement", "strategies_applied"
        ]

        # Check all required keys present
        if not all(key in result for key in required_keys):
            return False

        # Check scores are valid numbers
        for score_key in ["before_score", "after_score", "improvement"]:
            if not isinstance(result[score_key], (int, float)):
                return False

        # Check score ranges (0-100)
        if not (0 <= result["before_score"] <= 100):
            return False
        if not (0 <= result["after_score"] <= 100):
            return False

        # Check improvement calculation is correct
        expected_improvement = result["after_score"] - result["before_score"]
        if abs(result["improvement"] - expected_improvement) > 0.1:
            return False

        # Check strategies applied is a list
        if not isinstance(result["strategies_applied"], list):
            return False

        # Check changes is a list
        if not isinstance(result["changes"], list):
            return False

        return True


# Convenience function for quick testing
async def optimize_content(
    content: str,
    level: str = "balanced",
    focus_areas: Optional[List[str]] = None,
    context: Optional[Dict] = None,
    content_analyzer: Optional[ContentAnalyzer] = None
) -> Dict[str, Any]:
    """
    Quick helper to optimize content without creating full task message.

    Args:
        content: Content to optimize
        level: Optimization level ('conservative', 'balanced', 'aggressive')
        focus_areas: Specific areas to focus on
        context: Additional context dict
        content_analyzer: Optional ContentAnalyzer

    Returns:
        Optimization results

    Example:
        >>> result = await optimize_content("My article", level="aggressive")
        >>> print(f"Improvement: +{result['improvement']} points")
    """
    agent = OptimizerAgent(content_analyzer=content_analyzer)

    task = TaskMessage(
        task_id="quick_optimize",
        task_type="optimize_content",
        agent_type=AgentType.OPTIMIZER,
        campaign_id="quick_test",
        input_data={
            "content": content,
            "level": level,
            "focus_areas": focus_areas,
            "context": context or {},
        }
    )

    return await agent.execute_task(task)

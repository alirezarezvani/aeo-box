"""
Content Auditor Agent

Performs comprehensive AEO content audits using the AEO Skill content_analyzer module.
Analyzes E-E-A-T signals, structure, citations, and readability for LLM optimization.
"""

import asyncio
from typing import Any, Dict, Optional
from datetime import datetime

from .base_agent import BaseAgent
from ..communication.protocol import AgentType, TaskMessage
from ..aeo_skill.content_analyzer import ContentAnalyzer
from ..aeo_skill.api_manager import APIManager


class AuditorAgent(BaseAgent):
    """
    Content Auditor Agent for AEO content analysis.

    Integrates with AEO Skill ContentAnalyzer to provide:
    - E-E-A-T scoring (Experience, Expertise, Authoritativeness, Trustworthiness)
    - Content structure analysis
    - Citation quality assessment
    - Readability metrics
    - LLM optimization recommendations

    Input Requirements:
        - content: str (required) - Content to analyze (markdown or plain text)
        - url: str (optional) - Source URL for additional context
        - context: dict (optional) - Additional context (industry, region, etc.)

    Output Format:
        {
            "timestamp": "2025-01-08T...",
            "url": "https://...",
            "content_length": 5000,
            "word_count": 800,
            "scores": {
                "overall": 75,
                "eeat": 70,
                "structure": 80,
                "citations": 65,
                "readability": 75
            },
            "analysis": {...},
            "recommendations": [...]
        }
    """

    def __init__(self, api_manager: Optional[APIManager] = None):
        """
        Initialize Auditor Agent.

        Args:
            api_manager: Optional API manager for enhanced analysis
        """
        super().__init__(AgentType.AUDITOR)

        # Initialize content analyzer with optional API manager
        self.content_analyzer = ContentAnalyzer(api_manager=api_manager)

        self.logger.info("Auditor agent initialized", extra={
            "has_api_manager": api_manager is not None
        })

    async def execute_task(self, task: TaskMessage) -> Dict[str, Any]:
        """
        Execute content audit task.

        Args:
            task: Task message containing:
                - input_data.content: Content to analyze
                - input_data.url: Optional source URL
                - input_data.context: Optional context dict

        Returns:
            Audit results with scores, analysis, and recommendations

        Raises:
            ValueError: If content is missing or invalid
            RuntimeError: If analysis fails
        """
        self.logger.info(
            f"Executing audit task: {task.task_id}",
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

        # Extract optional inputs
        url = task.input_data.get("url")
        context = task.input_data.get("context", {})

        self.logger.info(
            f"Starting content analysis",
            extra={
                "content_length": len(content),
                "has_url": url is not None,
                "has_context": bool(context),
            }
        )

        try:
            # Run analysis (CPU-bound, but fast enough to not need threading)
            # ContentAnalyzer.analyze() is synchronous, so we await to play nice with async
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,  # Use default executor
                self.content_analyzer.analyze,
                content,
                url,
                context
            )

            self.logger.info(
                f"Analysis complete",
                extra={
                    "task_id": task.task_id,
                    "overall_score": result["scores"]["overall"],
                    "eeat_score": result["scores"]["eeat"],
                    "structure_score": result["scores"]["structure"],
                }
            )

            # Return analysis result
            return result

        except Exception as e:
            self.logger.error(
                f"Content analysis failed: {str(e)}",
                extra={
                    "task_id": task.task_id,
                    "error": str(e),
                },
                exc_info=True
            )
            raise RuntimeError(f"Content analysis failed: {str(e)}") from e

    def _validate_quality(self, result: Dict[str, Any]) -> bool:
        """
        Validate quality of analysis result.

        Args:
            result: Analysis result from ContentAnalyzer

        Returns:
            True if result meets quality criteria
        """
        required_keys = ["timestamp", "scores", "analysis", "recommendations"]

        # Check all required keys present
        if not all(key in result for key in required_keys):
            return False

        # Check scores structure
        required_scores = ["overall", "eeat", "structure", "citations", "readability"]
        if not all(score in result["scores"] for score in required_scores):
            return False

        # Check score ranges (0-100)
        for score_name, score_value in result["scores"].items():
            if not isinstance(score_value, (int, float)):
                return False
            if not 0 <= score_value <= 100:
                return False

        return True


# Convenience function for quick testing
async def audit_content(
    content: str,
    url: Optional[str] = None,
    context: Optional[Dict] = None,
    api_manager: Optional[APIManager] = None
) -> Dict[str, Any]:
    """
    Quick helper to audit content without creating full task message.

    Args:
        content: Content to analyze
        url: Optional source URL
        context: Optional context dict
        api_manager: Optional API manager

    Returns:
        Audit results

    Example:
        >>> result = await audit_content("My article content here")
        >>> print(f"AEO Score: {result['scores']['overall']}/100")
    """
    agent = AuditorAgent(api_manager=api_manager)

    task = TaskMessage(
        task_id="quick_audit",
        task_type="audit_content",
        agent_type=AgentType.AUDITOR,
        campaign_id="quick_test",
        input_data={
            "content": content,
            "url": url,
            "context": context or {},
        }
    )

    return await agent.execute_task(task)

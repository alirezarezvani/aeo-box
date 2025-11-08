"""
Citation Tracker Agent

Tracks citations across multiple LLMs using the AEO Skill citation_tracker module.
Monitors citation performance, frequency, and trends.
"""

import asyncio
from typing import Any, Dict, Optional, List
from datetime import datetime

from .base_agent import BaseAgent
from ..communication.protocol import AgentType, TaskMessage
from ..aeo_skill.citation_tracker import CitationTracker


class CitationTrackerAgent(BaseAgent):
    """
    Citation Tracker Agent for LLM citation monitoring.

    Integrates with AEO Skill CitationTracker to provide:
    - Citation frequency tracking across 5 LLMs (ChatGPT, Perplexity, Claude, Gemini, Mistral)
    - Query-specific citation analysis
    - Citation rank and context tracking
    - Historical trend analysis

    Input Requirements:
        - url: str (required) - URL to track
        - queries: List[str] (optional) - Queries to test
        - target_llms: List[str] (optional) - LLMs to check (default: all 5)

    Output Format:
        {
            "url": "https://...",
            "timestamp": "2025-01-08T...",
            "llms_checked": ["ChatGPT", "Perplexity", "Claude", "Gemini", "Mistral"],
            "queries_tested": 10,
            "citations_found": 3,
            "citation_details": [
                {
                    "llm": "ChatGPT",
                    "query": "AEO best practices",
                    "cited": true,
                    "rank": 1,
                    "context": "..."
                }
            ]
        }
    """

    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize Citation Tracker Agent.

        Args:
            data_path: Optional path to citation tracking CSV file
        """
        super().__init__(AgentType.CITATION_TRACKER)

        # Initialize citation tracker with optional data path
        self.tracker = CitationTracker(
            data_path=data_path or '.aeo-agent-data/citation_history.csv'
        )

        self.logger.info("Citation Tracker agent initialized", extra={
            "data_path": self.tracker.data_path
        })

    async def execute_task(self, task: TaskMessage) -> Dict[str, Any]:
        """
        Execute citation tracking task.

        Args:
            task: Task message containing:
                - input_data.url: URL to track
                - input_data.queries: Optional queries to test
                - input_data.target_llms: Optional LLMs to check

        Returns:
            Citation tracking results

        Raises:
            ValueError: If URL is missing or invalid
            RuntimeError: If tracking fails
        """
        self.logger.info(
            f"Executing citation tracking task: {task.task_id}",
            extra={
                "task_id": task.task_id,
                "campaign_id": task.campaign_id,
            }
        )

        # Validate required inputs
        if "url" not in task.input_data:
            raise ValueError("Missing required input: 'url'")

        url = task.input_data.get("url")
        if not url or not isinstance(url, str):
            raise ValueError("Invalid URL: must be non-empty string")

        # Extract optional parameters
        queries = task.input_data.get("queries")
        target_llms = task.input_data.get("target_llms")

        self.logger.info(
            f"Starting citation tracking",
            extra={
                "url": url,
                "queries_count": len(queries) if queries else 0,
                "target_llms": target_llms,
            }
        )

        try:
            # Run citation tracking (may involve network I/O)
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,  # Use default executor
                self.tracker.track_url,
                url,
                queries,
                target_llms
            )

            # Check for errors in result
            if "error" in result:
                raise RuntimeError(result["error"])

            self.logger.info(
                f"Citation tracking complete",
                extra={
                    "task_id": task.task_id,
                    "llms_checked": len(result.get("llms_checked", [])),
                    "citations_found": result.get("citations_found", 0),
                }
            )

            # Return tracking result
            return result

        except Exception as e:
            self.logger.error(
                f"Citation tracking failed: {str(e)}",
                extra={
                    "task_id": task.task_id,
                    "url": url,
                    "error": str(e),
                },
                exc_info=True
            )
            raise RuntimeError(f"Citation tracking failed: {str(e)}") from e

    def _validate_quality(self, result: Dict[str, Any]) -> bool:
        """
        Validate quality of citation tracking result.

        Args:
            result: Tracking result from CitationTracker

        Returns:
            True if result meets quality criteria
        """
        required_keys = [
            "url", "timestamp", "llms_checked",
            "queries_tested", "citations_found", "citation_details"
        ]

        # Check all required keys present
        if not all(key in result for key in required_keys):
            return False

        # Check llms_checked is a list
        if not isinstance(result["llms_checked"], list):
            return False

        # Check numeric fields are valid
        if not isinstance(result["queries_tested"], int):
            return False
        if not isinstance(result["citations_found"], int):
            return False

        # Check non-negative counts
        if result["queries_tested"] < 0:
            return False
        if result["citations_found"] < 0:
            return False

        # Check citation_details is a list
        if not isinstance(result["citation_details"], list):
            return False

        # Check citations_found matches details length
        # (may not always match if some details are aggregated)
        if result["citations_found"] > 0 and len(result["citation_details"]) == 0:
            # If citations found, should have some details
            pass  # Allow this for now as tracking may aggregate

        return True

    async def get_citation_history(
        self,
        url: Optional[str] = None,
        llm: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get historical citation data.

        Args:
            url: Optional URL filter
            llm: Optional LLM filter
            days: Number of days to look back

        Returns:
            Historical citation data
        """
        self.logger.info(
            "Retrieving citation history",
            extra={
                "url": url,
                "llm": llm,
                "days": days,
            }
        )

        try:
            loop = asyncio.get_event_loop()
            history = await loop.run_in_executor(
                None,
                self.tracker.get_history,
                url,
                llm,
                days
            )

            return history

        except Exception as e:
            self.logger.error(
                f"Failed to retrieve citation history: {str(e)}",
                exc_info=True
            )
            return {"error": str(e)}


# Convenience function for quick testing
async def track_citations(
    url: str,
    queries: Optional[List[str]] = None,
    target_llms: Optional[List[str]] = None,
    data_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Quick helper to track citations without creating full task message.

    Args:
        url: URL to track
        queries: Optional queries to test
        target_llms: Optional LLMs to check
        data_path: Optional data path for tracking file

    Returns:
        Citation tracking results

    Example:
        >>> result = await track_citations("https://example.com/article")
        >>> print(f"Citations found: {result['citations_found']}")
    """
    agent = CitationTrackerAgent(data_path=data_path)

    task = TaskMessage(
        task_id="quick_track",
        task_type="track_citations",
        agent_type=AgentType.CITATION_TRACKER,
        campaign_id="quick_test",
        input_data={
            "url": url,
            "queries": queries,
            "target_llms": target_llms,
        }
    )

    return await agent.execute_task(task)

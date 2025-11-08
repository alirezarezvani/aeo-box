"""
Query Researcher Agent

Researches query opportunities and competitor strategies using AEO Skill query_researcher module.
"""

import asyncio
from typing import Any, Dict, Optional, List
from datetime import datetime

from .base_agent import BaseAgent
from ..communication.protocol import AgentType, TaskMessage
from ..aeo_skill.query_researcher import QueryResearcher
from ..aeo_skill.api_manager import APIManager


class ResearcherAgent(BaseAgent):
    """
    Query Researcher Agent for AEO opportunity research.

    Input Requirements:
        - topic: str (required) - Topic/keyword to research
        - region: str (optional) - Geographic region (default: 'US')
        - include_competitors: bool (optional) - Analyze competitors
        - competitor_urls: List[str] (optional) - Competitor URLs

    Output Format:
        {
            "topic": "...",
            "region": "US",
            "target_queries": [{query, priority}],
            "citation_potential": "high",
            "competitor_analysis": {...},
            "content_gaps": [...],
            "recommended_angles": [...]
        }
    """

    def __init__(self, api_manager: Optional[APIManager] = None):
        """Initialize Researcher Agent."""
        super().__init__(AgentType.RESEARCHER)
        self.researcher = QueryResearcher(api_manager=api_manager)
        self.logger.info("Researcher agent initialized")

    async def execute_task(self, task: TaskMessage) -> Dict[str, Any]:
        """Execute query research task."""
        self.logger.info(f"Executing research task: {task.task_id}")

        if "topic" not in task.input_data:
            raise ValueError("Missing required input: 'topic'")

        topic = task.input_data.get("topic")
        if not topic or not isinstance(topic, str):
            raise ValueError("Invalid topic: must be non-empty string")

        region = task.input_data.get("region", "US")
        include_competitors = task.input_data.get("include_competitors", False)
        competitor_urls = task.input_data.get("competitor_urls")

        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self.researcher.research_topic,
                topic,
                region,
                include_competitors,
                competitor_urls
            )

            self.logger.info(f"Research complete: {len(result.get('target_queries', []))} queries found")
            return result

        except Exception as e:
            self.logger.error(f"Research failed: {str(e)}", exc_info=True)
            raise RuntimeError(f"Query research failed: {str(e)}") from e

"""
Structured Logging Infrastructure for Agentic AEO System

Provides JSON and text logging with context fields for agent orchestration.
Supports file and stdout output with configurable levels.
"""

import logging
import json
import sys
from datetime import datetime
from typing import Optional, Any, Dict
from pathlib import Path


class JSONFormatter(logging.Formatter):
    """Format log records as JSON objects"""

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON string.

        Args:
            record: Log record to format

        Returns:
            JSON-formatted log string
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add context fields if present
        if hasattr(record, "agent_type"):
            log_data["agent_type"] = record.agent_type
        if hasattr(record, "task_id"):
            log_data["task_id"] = record.task_id
        if hasattr(record, "campaign_id"):
            log_data["campaign_id"] = record.campaign_id

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add any extra fields
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        return json.dumps(log_data)


class TextFormatter(logging.Formatter):
    """Format log records as human-readable text"""

    def __init__(self):
        super().__init__(
            fmt="%(asctime)s [%(levelname)8s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )


class StructuredLogger:
    """
    Structured logger with context fields for agent operations.

    Provides both JSON and text formatting with support for:
    - Agent-specific context (agent_type, task_id, campaign_id)
    - File and stdout output
    - Configurable log levels
    - Extra fields for custom metadata

    Example:
        >>> logger = StructuredLogger("orchestrator")
        >>> logger.info("Starting campaign", campaign_id="camp_123")
        >>> logger.error("Agent failed", agent_type="auditor", task_id="task_456")
    """

    def __init__(
        self,
        name: str,
        log_level: Optional[str] = None,
        log_format: Optional[str] = None,
        log_file: Optional[str] = None,
        agent_type: Optional[str] = None,
        task_id: Optional[str] = None,
        campaign_id: Optional[str] = None,
    ):
        """
        Initialize structured logger.

        Args:
            name: Logger name (typically module or agent name)
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_format: Output format ("json" or "text")
            log_file: Optional file path for log output
            agent_type: Default agent type for context
            task_id: Default task ID for context
            campaign_id: Default campaign ID for context
        """
        # Load config defaults if not provided
        from .config import get_config
        config = get_config()

        self.name = name
        self.log_level = log_level or config.logging.log_level
        self.log_format = log_format or config.logging.log_format
        self.log_file = log_file or config.logging.log_file

        # Default context fields
        self.default_context = {
            "agent_type": agent_type,
            "task_id": task_id,
            "campaign_id": campaign_id,
        }

        # Create logger instance
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, self.log_level))

        # Clear existing handlers
        self.logger.handlers.clear()

        # Add stdout handler
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(getattr(logging, self.log_level))

        # Set formatter based on format type
        if self.log_format == "json":
            formatter = JSONFormatter()
        else:
            formatter = TextFormatter()

        stdout_handler.setFormatter(formatter)
        self.logger.addHandler(stdout_handler)

        # Add file handler if specified
        if self.log_file:
            log_path = Path(self.log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(log_path)
            file_handler.setLevel(getattr(logging, self.log_level))
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def _log(
        self,
        level: int,
        message: str,
        agent_type: Optional[str] = None,
        task_id: Optional[str] = None,
        campaign_id: Optional[str] = None,
        exc_info: bool = False,
        **extra_fields: Any,
    ) -> None:
        """
        Internal logging method with context fields.

        Args:
            level: Logging level (from logging module)
            message: Log message
            agent_type: Agent type override
            task_id: Task ID override
            campaign_id: Campaign ID override
            exc_info: Include exception traceback
            **extra_fields: Additional fields to include in log
        """
        # Use provided context or defaults
        context = {
            "agent_type": agent_type or self.default_context["agent_type"],
            "task_id": task_id or self.default_context["task_id"],
            "campaign_id": campaign_id or self.default_context["campaign_id"],
        }

        # Create extra dict for log record
        extra = {"extra_fields": extra_fields} if extra_fields else {}

        # Add context fields to record
        for key, value in context.items():
            if value is not None:
                extra[key] = value

        self.logger.log(level, message, exc_info=exc_info, extra=extra)

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message"""
        self._log(logging.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message"""
        self._log(logging.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message"""
        self._log(logging.WARNING, message, **kwargs)

    def error(self, message: str, exc_info: bool = False, **kwargs: Any) -> None:
        """Log error message with optional exception traceback"""
        self._log(logging.ERROR, message, exc_info=exc_info, **kwargs)

    def critical(self, message: str, exc_info: bool = False, **kwargs: Any) -> None:
        """Log critical message with optional exception traceback"""
        self._log(logging.CRITICAL, message, exc_info=exc_info, **kwargs)

    def set_context(
        self,
        agent_type: Optional[str] = None,
        task_id: Optional[str] = None,
        campaign_id: Optional[str] = None,
    ) -> None:
        """
        Update default context fields.

        Args:
            agent_type: Agent type for subsequent logs
            task_id: Task ID for subsequent logs
            campaign_id: Campaign ID for subsequent logs

        Example:
            >>> logger = StructuredLogger("orchestrator")
            >>> logger.set_context(campaign_id="camp_123")
            >>> logger.info("Campaign started")  # Includes campaign_id
        """
        if agent_type is not None:
            self.default_context["agent_type"] = agent_type
        if task_id is not None:
            self.default_context["task_id"] = task_id
        if campaign_id is not None:
            self.default_context["campaign_id"] = campaign_id

    def agent_start(self, agent_type: str, task: Dict[str, Any]) -> None:
        """
        Log agent start with task details.

        Args:
            agent_type: Type of agent starting
            task: Task dictionary

        Example:
            >>> logger.agent_start("auditor", {"task_id": "task_123", "url": "..."})
        """
        self.info(
            f"Agent starting",
            agent_type=agent_type,
            task_id=task.get("task_id"),
            campaign_id=task.get("campaign_id"),
            task_type=task.get("task_type"),
        )

    def agent_complete(
        self,
        agent_type: str,
        task_id: str,
        duration_seconds: float,
        success: bool = True,
    ) -> None:
        """
        Log agent completion with timing.

        Args:
            agent_type: Type of agent that completed
            task_id: Task ID
            duration_seconds: Execution duration
            success: Whether task succeeded

        Example:
            >>> logger.agent_complete("auditor", "task_123", 45.2, success=True)
        """
        status = "completed" if success else "failed"
        self.info(
            f"Agent {status}",
            agent_type=agent_type,
            task_id=task_id,
            duration_seconds=round(duration_seconds, 2),
            success=success,
        )

    def workflow_start(self, workflow_name: str, campaign_id: str, **params: Any) -> None:
        """
        Log workflow start.

        Args:
            workflow_name: Name of workflow (/aeo-campaign, /aeo-compete, etc.)
            campaign_id: Campaign identifier
            **params: Workflow parameters

        Example:
            >>> logger.workflow_start("aeo-campaign", "camp_123", url="...", queries=[...])
        """
        self.info(
            f"Workflow starting: {workflow_name}",
            campaign_id=campaign_id,
            workflow=workflow_name,
            **params,
        )

    def workflow_complete(
        self,
        workflow_name: str,
        campaign_id: str,
        duration_seconds: float,
        success: bool = True,
    ) -> None:
        """
        Log workflow completion.

        Args:
            workflow_name: Name of workflow
            campaign_id: Campaign identifier
            duration_seconds: Total execution duration
            success: Whether workflow succeeded

        Example:
            >>> logger.workflow_complete("aeo-campaign", "camp_123", 120.5, success=True)
        """
        status = "completed" if success else "failed"
        self.info(
            f"Workflow {status}: {workflow_name}",
            campaign_id=campaign_id,
            workflow=workflow_name,
            duration_seconds=round(duration_seconds, 2),
            success=success,
        )


def get_logger(
    name: str,
    agent_type: Optional[str] = None,
    task_id: Optional[str] = None,
    campaign_id: Optional[str] = None,
) -> StructuredLogger:
    """
    Get a structured logger instance.

    Args:
        name: Logger name
        agent_type: Default agent type
        task_id: Default task ID
        campaign_id: Default campaign ID

    Returns:
        StructuredLogger instance

    Example:
        >>> from agentic_aeo.utils.logging import get_logger
        >>> logger = get_logger("orchestrator", campaign_id="camp_123")
        >>> logger.info("Starting orchestration")
    """
    return StructuredLogger(
        name=name,
        agent_type=agent_type,
        task_id=task_id,
        campaign_id=campaign_id,
    )


# Example usage
if __name__ == "__main__":
    # Create logger
    logger = StructuredLogger("test_agent", agent_type="auditor")

    # Basic logging
    logger.info("Testing structured logging")
    logger.debug("Debug message", extra_field="value")

    # Agent lifecycle logging
    task = {
        "task_id": "task_123",
        "task_type": "audit_content",
        "campaign_id": "camp_456",
    }
    logger.agent_start("auditor", task)
    logger.agent_complete("auditor", "task_123", 45.2, success=True)

    # Workflow logging
    logger.workflow_start("aeo-campaign", "camp_456", url="https://example.com")
    logger.workflow_complete("aeo-campaign", "camp_456", 120.5, success=True)

    # Error logging
    try:
        raise ValueError("Test error")
    except Exception:
        logger.error("Error occurred", exc_info=True)

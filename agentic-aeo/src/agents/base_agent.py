"""
Base Agent Class for Multi-Agent AEO System

Provides abstract base class with common functionality for all specialized agents.
Includes retry logic, timeout handling, input validation, and logging integration.
"""

import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional
from ..communication.protocol import (
    TaskMessage,
    TaskResult,
    TaskStatus,
    AgentType,
)
from ..utils.logging import StructuredLogger
from ..utils.config import get_config


class BaseAgent(ABC):
    """
    Abstract base class for all AEO agents.

    Provides:
    - Input validation
    - Retry logic with exponential backoff
    - Timeout handling
    - Structured logging
    - Task result creation helpers

    Subclasses must implement:
    - execute_task(): Core task execution logic

    Example:
        >>> class AuditorAgent(BaseAgent):
        ...     def __init__(self):
        ...         super().__init__(AgentType.AUDITOR)
        ...
        ...     async def execute_task(self, task: TaskMessage) -> Dict[str, Any]:
        ...         # Implementation here
        ...         return {"score": 85, "issues": [...]}
    """

    def __init__(self, agent_type: AgentType):
        """
        Initialize base agent.

        Args:
            agent_type: Type of agent (from AgentType enum)
        """
        self.agent_type = agent_type
        self.config = get_config()
        self.logger = StructuredLogger(
            name=f"agent.{agent_type.value}",
            agent_type=agent_type.value,
        )

        # Configuration from settings
        self.max_retries = self.config.agent.max_retries
        self.retry_delay = self.config.agent.retry_delay_seconds
        self.timeout_seconds = self.config.agent.timeout_seconds

    @abstractmethod
    async def execute_task(self, task: TaskMessage) -> Dict[str, Any]:
        """
        Execute assigned task - must be implemented by subclass.

        Args:
            task: Task message with input data and parameters

        Returns:
            Dictionary with task output data

        Raises:
            ValueError: If input validation fails
            RuntimeError: If task execution fails
        """
        pass

    def validate_input(self, task: TaskMessage) -> bool:
        """
        Validate task input has required fields.

        Args:
            task: Task message to validate

        Returns:
            True if valid

        Raises:
            ValueError: If validation fails
        """
        # Check task message has required fields
        if not task.task_id:
            raise ValueError("Task must have task_id")

        if not task.campaign_id:
            raise ValueError("Task must have campaign_id")

        if not task.input_data:
            raise ValueError("Task must have input_data")

        # Check agent type matches
        if task.agent_type != self.agent_type:
            raise ValueError(
                f"Task agent_type ({task.agent_type}) does not match "
                f"agent ({self.agent_type})"
            )

        self.logger.debug(
            "Task input validation passed",
            task_id=task.task_id,
            campaign_id=task.campaign_id,
        )

        return True

    async def execute_with_retry(
        self,
        task: TaskMessage,
        max_retries: Optional[int] = None,
    ) -> TaskResult:
        """
        Execute task with retry logic and exponential backoff.

        Args:
            task: Task to execute
            max_retries: Override default max retries

        Returns:
            TaskResult with execution outcome

        Example:
            >>> agent = AuditorAgent()
            >>> task = TaskMessage(...)
            >>> result = await agent.execute_with_retry(task)
            >>> print(result.status)  # COMPLETED or FAILED
        """
        retries = max_retries if max_retries is not None else self.max_retries
        started_at = datetime.utcnow()

        # Set logger context
        self.logger.set_context(
            task_id=task.task_id,
            campaign_id=task.campaign_id,
        )

        # Log task start
        self.logger.agent_start(self.agent_type.value, task.model_dump())

        for attempt in range(retries + 1):
            try:
                # Validate input
                self.validate_input(task)

                # Execute with timeout
                timeout = task.timeout_seconds or self.timeout_seconds
                output_data = await asyncio.wait_for(
                    self.execute_task(task),
                    timeout=timeout,
                )

                # Calculate execution time
                completed_at = datetime.utcnow()
                execution_time = (completed_at - started_at).total_seconds()

                # Create successful result
                result = TaskResult(
                    task_id=task.task_id,
                    status=TaskStatus.COMPLETED,
                    agent_type=self.agent_type,
                    output_data=output_data,
                    metadata={
                        "execution_time": round(execution_time, 2),
                        "retry_count": attempt,
                        "agent_version": "1.5.0-dev",
                    },
                    started_at=started_at,
                    completed_at=completed_at,
                )

                # Log success
                self.logger.agent_complete(
                    self.agent_type.value,
                    task.task_id,
                    execution_time,
                    success=True,
                )

                return result

            except asyncio.TimeoutError as e:
                error_msg = f"Task timed out after {timeout}s"
                self.logger.error(
                    error_msg,
                    task_id=task.task_id,
                    attempt=attempt + 1,
                    max_retries=retries,
                )

                # Don't retry on timeout - return failure immediately
                return self._create_error_result(
                    task=task,
                    error_message=error_msg,
                    error_details={"timeout_seconds": timeout},
                    started_at=started_at,
                    retry_count=attempt,
                )

            except ValueError as e:
                # Input validation error - don't retry
                error_msg = f"Input validation failed: {str(e)}"
                self.logger.error(
                    error_msg,
                    task_id=task.task_id,
                    exc_info=True,
                )

                return self._create_error_result(
                    task=task,
                    error_message=error_msg,
                    error_details={"validation_error": str(e)},
                    started_at=started_at,
                    retry_count=attempt,
                )

            except Exception as e:
                error_msg = f"Task execution failed: {str(e)}"
                self.logger.error(
                    error_msg,
                    task_id=task.task_id,
                    attempt=attempt + 1,
                    max_retries=retries,
                    exc_info=True,
                )

                # If this was the last retry, return failure
                if attempt >= retries:
                    return self._create_error_result(
                        task=task,
                        error_message=error_msg,
                        error_details={
                            "exception_type": type(e).__name__,
                            "exception_message": str(e),
                            "retry_count": attempt,
                        },
                        started_at=started_at,
                        retry_count=attempt,
                    )

                # Calculate backoff delay (exponential)
                delay = self.retry_delay * (2 ** attempt)
                self.logger.info(
                    f"Retrying after {delay}s",
                    task_id=task.task_id,
                    attempt=attempt + 1,
                    delay_seconds=delay,
                )
                await asyncio.sleep(delay)

        # Should never reach here, but just in case
        return self._create_error_result(
            task=task,
            error_message="Max retries exceeded",
            error_details={"max_retries": retries},
            started_at=started_at,
            retry_count=retries,
        )

    def _create_error_result(
        self,
        task: TaskMessage,
        error_message: str,
        error_details: Dict[str, Any],
        started_at: datetime,
        retry_count: int,
    ) -> TaskResult:
        """
        Create TaskResult for failed execution.

        Args:
            task: Original task
            error_message: Error message
            error_details: Detailed error information
            started_at: Task start time
            retry_count: Number of retry attempts

        Returns:
            TaskResult with FAILED status
        """
        completed_at = datetime.utcnow()
        execution_time = (completed_at - started_at).total_seconds()

        # Log failure
        self.logger.agent_complete(
            self.agent_type.value,
            task.task_id,
            execution_time,
            success=False,
        )

        return TaskResult(
            task_id=task.task_id,
            status=TaskStatus.FAILED,
            agent_type=self.agent_type,
            output_data={},
            error_message=error_message,
            error_details=error_details,
            metadata={
                "execution_time": round(execution_time, 2),
                "retry_count": retry_count,
                "agent_version": "1.5.0-dev",
            },
            started_at=started_at,
            completed_at=completed_at,
        )

    async def handle_revision(
        self,
        task: TaskMessage,
        revision_notes: list[str],
    ) -> TaskResult:
        """
        Handle revision request from orchestrator.

        Default implementation re-executes task with updated parameters.
        Subclasses can override for custom revision logic.

        Args:
            task: Original task with updated parameters
            revision_notes: Specific issues to address

        Returns:
            TaskResult with revised output
        """
        self.logger.info(
            "Handling revision request",
            task_id=task.task_id,
            revision_notes=revision_notes,
        )

        # Update task parameters with revision context
        task.parameters["revision_notes"] = revision_notes
        task.retry_count += 1

        # Re-execute task
        return await self.execute_with_retry(task)

    def create_markdown_output(
        self,
        title: str,
        sections: Dict[str, str],
    ) -> str:
        """
        Create Markdown-formatted output for human readability.

        Args:
            title: Report title
            sections: Dictionary of section_name -> content

        Returns:
            Formatted Markdown string

        Example:
            >>> markdown = agent.create_markdown_output(
            ...     "Content Audit Report",
            ...     {
            ...         "Summary": "Overall score: 85/100",
            ...         "Issues": "- Low E-E-A-T signals\\n- Missing citations",
            ...     }
            ... )
        """
        lines = [f"# {title}", ""]

        for section_name, content in sections.items():
            lines.append(f"## {section_name}")
            lines.append("")
            lines.append(content)
            lines.append("")

        return "\n".join(lines)

    def __str__(self) -> str:
        """String representation of agent"""
        return f"{self.agent_type.value.title()}Agent"

    def __repr__(self) -> str:
        """Detailed representation of agent"""
        return (
            f"{self.__class__.__name__}("
            f"agent_type={self.agent_type.value}, "
            f"max_retries={self.max_retries}, "
            f"timeout={self.timeout_seconds}s)"
        )


# Example usage
if __name__ == "__main__":
    # Example concrete implementation
    class ExampleAgent(BaseAgent):
        """Example agent implementation"""

        def __init__(self):
            super().__init__(AgentType.AUDITOR)

        async def execute_task(self, task: TaskMessage) -> Dict[str, Any]:
            """Execute example task"""
            self.logger.info("Executing example task", task_id=task.task_id)

            # Simulate work
            await asyncio.sleep(1)

            # Return output
            return {
                "score": 85,
                "analysis": "Content analyzed successfully",
                "timestamp": datetime.utcnow().isoformat(),
            }

    # Test the agent
    async def test_agent():
        agent = ExampleAgent()
        print(f"Created agent: {agent}")
        print(repr(agent))

        # Create test task
        task = TaskMessage(
            task_id="test_123",
            task_type="audit_content",
            agent_type=AgentType.AUDITOR,
            campaign_id="camp_456",
            input_data={"url": "https://example.com"},
        )

        # Execute task
        result = await agent.execute_with_retry(task)
        print(f"\nTask completed: {result.status}")
        print(f"Execution time: {result.execution_time_seconds}s")
        print(f"Output: {result.output_data}")

    # Run test
    asyncio.run(test_agent())

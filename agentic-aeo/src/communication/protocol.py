"""
Communication Protocol for Multi-Agent AEO System

Defines message formats for orchestrator-agent communication using Pydantic.
Implements JSON + Markdown hybrid format for structured data and human-readable content.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, field_validator


class TaskType(str, Enum):
    """Types of tasks that can be assigned to agents"""

    # Auditor agent tasks
    AUDIT_CONTENT = "audit_content"
    ANALYZE_EEAT = "analyze_eeat"

    # Optimizer agent tasks
    OPTIMIZE_CONTENT = "optimize_content"
    IMPROVE_STRUCTURE = "improve_structure"

    # Tracker agent tasks
    TRACK_CITATIONS = "track_citations"
    MONITOR_CHANGES = "monitor_changes"

    # Researcher agent tasks
    RESEARCH_QUERIES = "research_queries"
    ANALYZE_COMPETITORS = "analyze_competitors"

    # Reporter agent tasks
    GENERATE_REPORT = "generate_report"
    CREATE_SUMMARY = "create_summary"

    # Learning agent tasks
    LEARN_PATTERNS = "learn_patterns"
    RECOMMEND_STRATEGIES = "recommend_strategies"


class TaskStatus(str, Enum):
    """Status of task execution"""

    PENDING = "pending"              # Task assigned, not started
    IN_PROGRESS = "in_progress"      # Agent working on task
    COMPLETED = "completed"          # Task completed successfully
    FAILED = "failed"                # Task failed with errors
    REVISION_REQUESTED = "revision_requested"  # Orchestrator requests revision
    CANCELED = "canceled"            # Task canceled


class ValidationStatus(str, Enum):
    """Validation result from orchestrator"""

    VALID = "valid"                  # Output meets all criteria
    NEEDS_REVISION = "needs_revision"  # Output needs improvement
    INVALID = "invalid"              # Output rejected completely


class AgentType(str, Enum):
    """Types of specialized agents"""

    ORCHESTRATOR = "orchestrator"
    AUDITOR = "auditor"
    OPTIMIZER = "optimizer"
    TRACKER = "tracker"
    RESEARCHER = "researcher"
    REPORTER = "reporter"
    LEARNING = "learning"


class TaskMessage(BaseModel):
    """
    Message sent from orchestrator to agent with task assignment.

    Example:
        >>> task = TaskMessage(
        ...     task_id="task_123",
        ...     task_type=TaskType.AUDIT_CONTENT,
        ...     agent_type=AgentType.AUDITOR,
        ...     campaign_id="camp_456",
        ...     input_data={"url": "https://example.com", "content": "..."},
        ...     parameters={"mode": "comprehensive"},
        ... )
    """

    # Task identification
    task_id: str = Field(..., description="Unique task identifier")
    task_type: TaskType = Field(..., description="Type of task to execute")
    agent_type: AgentType = Field(..., description="Target agent type")
    campaign_id: str = Field(..., description="Parent campaign identifier")

    # Task data
    input_data: Dict[str, Any] = Field(..., description="Input data for task")
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Optional task parameters"
    )

    # Dependencies and context
    dependencies: List[str] = Field(
        default_factory=list,
        description="Task IDs that must complete before this task"
    )
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context from previous tasks"
    )

    # Metadata
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Task creation timestamp"
    )
    timeout_seconds: Optional[int] = Field(
        default=300,
        description="Task timeout in seconds"
    )
    retry_count: int = Field(
        default=0,
        description="Number of retry attempts"
    )


class TaskResult(BaseModel):
    """
    Result returned from agent to orchestrator after task execution.

    Example:
        >>> result = TaskResult(
        ...     task_id="task_123",
        ...     status=TaskStatus.COMPLETED,
        ...     agent_type=AgentType.AUDITOR,
        ...     output_data={"score": 85, "issues": [...]},
        ...     metadata={"execution_time": 45.2},
        ... )
    """

    # Task identification
    task_id: str = Field(..., description="Task identifier (matches TaskMessage)")
    status: TaskStatus = Field(..., description="Execution status")
    agent_type: AgentType = Field(..., description="Agent that executed task")

    # Output data
    output_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Task output data"
    )
    output_markdown: Optional[str] = Field(
        default=None,
        description="Human-readable output in Markdown format"
    )

    # Execution metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Execution metadata (timing, tokens, etc.)"
    )

    # Error handling
    error_message: Optional[str] = Field(
        default=None,
        description="Error message if status=FAILED"
    )
    error_details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Detailed error information"
    )

    # Timestamps
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Task start timestamp"
    )
    completed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Task completion timestamp"
    )

    @property
    def execution_time_seconds(self) -> float:
        """Calculate execution time in seconds"""
        return (self.completed_at - self.started_at).total_seconds()


class RevisionRequest(BaseModel):
    """
    Request from orchestrator to agent for output revision.

    Example:
        >>> revision = RevisionRequest(
        ...     task_id="task_123",
        ...     original_result=result,
        ...     revision_notes=["Improve E-E-A-T score", "Add more citations"],
        ...     parameters={"min_score": 90},
        ... )
    """

    # Task identification
    task_id: str = Field(..., description="Task to revise")
    original_result: TaskResult = Field(..., description="Original task result")

    # Revision instructions
    revision_notes: List[str] = Field(
        ...,
        description="Specific issues to address"
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Updated parameters for revision"
    )

    # Metadata
    revision_number: int = Field(
        default=1,
        description="Revision attempt number"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Revision request timestamp"
    )


class ValidationResult(BaseModel):
    """
    Validation result from orchestrator after checking agent output.

    Example:
        >>> validation = ValidationResult(
        ...     task_id="task_123",
        ...     status=ValidationStatus.VALID,
        ...     checks_passed=["completeness", "quality"],
        ...     checks_failed=[],
        ...     score=95,
        ... )
    """

    # Task identification
    task_id: str = Field(..., description="Task being validated")

    # Validation status
    status: ValidationStatus = Field(..., description="Overall validation status")
    checks_passed: List[str] = Field(
        default_factory=list,
        description="List of validation checks that passed"
    )
    checks_failed: List[str] = Field(
        default_factory=list,
        description="List of validation checks that failed"
    )

    # Quality metrics
    score: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
        description="Overall quality score (0-100)"
    )

    # Feedback
    feedback: List[str] = Field(
        default_factory=list,
        description="Specific feedback for improvement"
    )
    suggestions: List[str] = Field(
        default_factory=list,
        description="Suggested improvements"
    )

    # Metadata
    validated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Validation timestamp"
    )


class WorkflowState(BaseModel):
    """
    Current state of a multi-task workflow.

    Example:
        >>> state = WorkflowState(
        ...     workflow_name="aeo-campaign",
        ...     campaign_id="camp_123",
        ...     total_tasks=5,
        ...     completed_tasks=2,
        ...     status="in_progress",
        ... )
    """

    # Workflow identification
    workflow_name: str = Field(..., description="Name of workflow")
    campaign_id: str = Field(..., description="Campaign identifier")

    # Progress tracking
    total_tasks: int = Field(..., ge=1, description="Total number of tasks")
    completed_tasks: int = Field(default=0, ge=0, description="Number of completed tasks")
    failed_tasks: int = Field(default=0, ge=0, description="Number of failed tasks")

    # Current status
    status: str = Field(
        default="pending",
        description="Workflow status (pending, in_progress, completed, failed)"
    )
    current_task_id: Optional[str] = Field(
        default=None,
        description="Currently executing task ID"
    )

    # Task tracking
    task_ids: List[str] = Field(
        default_factory=list,
        description="All task IDs in workflow"
    )
    task_results: Dict[str, TaskResult] = Field(
        default_factory=dict,
        description="Results indexed by task_id"
    )

    # Timestamps
    started_at: Optional[datetime] = Field(
        default=None,
        description="Workflow start timestamp"
    )
    completed_at: Optional[datetime] = Field(
        default=None,
        description="Workflow completion timestamp"
    )

    @property
    def progress_percentage(self) -> float:
        """Calculate workflow progress as percentage"""
        if self.total_tasks == 0:
            return 0.0
        return (self.completed_tasks / self.total_tasks) * 100

    @property
    def is_complete(self) -> bool:
        """Check if workflow is complete"""
        return self.completed_tasks == self.total_tasks

    @property
    def has_failures(self) -> bool:
        """Check if workflow has any failures"""
        return self.failed_tasks > 0


class AgentCapability(BaseModel):
    """
    Description of agent capabilities for orchestrator routing.

    Example:
        >>> capability = AgentCapability(
        ...     agent_type=AgentType.AUDITOR,
        ...     supported_tasks=[TaskType.AUDIT_CONTENT, TaskType.ANALYZE_EEAT],
        ...     max_parallel=3,
        ... )
    """

    agent_type: AgentType = Field(..., description="Agent type")
    supported_tasks: List[TaskType] = Field(
        ...,
        description="Task types this agent can handle"
    )
    max_parallel: int = Field(
        default=1,
        ge=1,
        description="Maximum parallel tasks this agent can handle"
    )
    requires_dependencies: bool = Field(
        default=False,
        description="Whether agent requires completed dependencies"
    )
    average_execution_time: Optional[float] = Field(
        default=None,
        description="Average execution time in seconds"
    )


class CampaignManifest(BaseModel):
    """
    Complete manifest for a campaign with all tasks and results.

    Example:
        >>> manifest = CampaignManifest(
        ...     campaign_id="camp_123",
        ...     workflow_name="aeo-campaign",
        ...     parameters={"url": "...", "queries": [...]},
        ...     tasks=[task1, task2, ...],
        ... )
    """

    # Campaign identification
    campaign_id: str = Field(..., description="Unique campaign identifier")
    workflow_name: str = Field(..., description="Workflow type")

    # Campaign parameters
    parameters: Dict[str, Any] = Field(
        ...,
        description="Campaign input parameters"
    )

    # Tasks and results
    tasks: List[TaskMessage] = Field(
        default_factory=list,
        description="All tasks in campaign"
    )
    results: Dict[str, TaskResult] = Field(
        default_factory=dict,
        description="Results indexed by task_id"
    )

    # State tracking
    workflow_state: WorkflowState = Field(
        ...,
        description="Current workflow state"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Campaign creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Last update timestamp"
    )

    def to_json_file(self) -> Dict[str, Any]:
        """Export campaign manifest as JSON-serializable dict"""
        return self.model_dump(mode="json")

    @classmethod
    def from_json_file(cls, data: Dict[str, Any]) -> "CampaignManifest":
        """Load campaign manifest from JSON dict"""
        return cls(**data)


# Example usage and validation
if __name__ == "__main__":
    # Create a task message
    task = TaskMessage(
        task_id="task_123",
        task_type=TaskType.AUDIT_CONTENT,
        agent_type=AgentType.AUDITOR,
        campaign_id="camp_456",
        input_data={
            "url": "https://example.com/article",
            "content": "Article content here...",
        },
        parameters={"mode": "comprehensive"},
    )
    print("TaskMessage created:")
    print(task.model_dump_json(indent=2))
    print()

    # Create a task result
    result = TaskResult(
        task_id="task_123",
        status=TaskStatus.COMPLETED,
        agent_type=AgentType.AUDITOR,
        output_data={
            "overall_score": 85,
            "eeat_score": 78,
            "structure_score": 92,
            "issues": ["Low expertise signals", "Missing author bio"],
        },
        output_markdown="# Content Audit Report\n\n...",
        metadata={
            "execution_time": 45.2,
            "tokens_used": 12500,
        },
    )
    print("TaskResult created:")
    print(result.model_dump_json(indent=2))
    print(f"Execution time: {result.execution_time_seconds}s")
    print()

    # Create a workflow state
    workflow = WorkflowState(
        workflow_name="aeo-campaign",
        campaign_id="camp_456",
        total_tasks=5,
        completed_tasks=2,
        status="in_progress",
        task_ids=["task_1", "task_2", "task_3", "task_4", "task_5"],
    )
    print("WorkflowState created:")
    print(f"Progress: {workflow.progress_percentage:.1f}%")
    print(f"Complete: {workflow.is_complete}")
    print()

    # Create a validation result
    validation = ValidationResult(
        task_id="task_123",
        status=ValidationStatus.VALID,
        checks_passed=["completeness", "quality", "format"],
        checks_failed=[],
        score=95,
        feedback=["Excellent content analysis", "Well-structured output"],
    )
    print("ValidationResult created:")
    print(validation.model_dump_json(indent=2))

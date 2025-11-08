"""
Communication protocol for multi-agent orchestration
"""

from .protocol import (
    # Enums
    TaskType,
    TaskStatus,
    ValidationStatus,
    AgentType,

    # Core message types
    TaskMessage,
    TaskResult,
    RevisionRequest,
    ValidationResult,

    # Workflow state
    WorkflowState,
    AgentCapability,
    CampaignManifest,
)

__all__ = [
    # Enums
    "TaskType",
    "TaskStatus",
    "ValidationStatus",
    "AgentType",

    # Core message types
    "TaskMessage",
    "TaskResult",
    "RevisionRequest",
    "ValidationResult",

    # Workflow state
    "WorkflowState",
    "AgentCapability",
    "CampaignManifest",
]

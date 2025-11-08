"""
Agentic AEO - Multi-Agent Answer Engine Optimization System

v1.5.0-dev
"""

__version__ = "1.5.0-dev"
__author__ = "Alireza Rezvani"

from .utils import get_config, get_logger
from .communication import (
    TaskType,
    TaskStatus,
    AgentType,
    TaskMessage,
    TaskResult,
)
from .agents import BaseAgent

__all__ = [
    # Version
    "__version__",
    "__author__",

    # Utils
    "get_config",
    "get_logger",

    # Communication
    "TaskType",
    "TaskStatus",
    "AgentType",
    "TaskMessage",
    "TaskResult",

    # Agents
    "BaseAgent",
]

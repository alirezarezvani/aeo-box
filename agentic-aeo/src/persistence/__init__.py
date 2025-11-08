"""
Data persistence for campaign, workflow, and task storage
"""

from .campaign_store import CampaignStore, get_campaign_store
from .workflow_store import WorkflowStore, get_workflow_store
from .file_ops import (
    AtomicFileWriter,
    write_json,
    read_json,
    append_to_jsonl,
    read_jsonl,
)

__all__ = [
    # Campaign store
    "CampaignStore",
    "get_campaign_store",

    # Workflow store
    "WorkflowStore",
    "get_workflow_store",

    # File operations
    "AtomicFileWriter",
    "write_json",
    "read_json",
    "append_to_jsonl",
    "read_jsonl",
]

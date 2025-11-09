# v1.5.0 Remediation Plan

**Created**: 2025-11-09
**Target Completion**: 2025-11-10 EOD
**Target Release**: 2025-11-11

---

## Overview

This document provides a detailed, task-by-task remediation plan for the 10 critical issues identified in the code review. Each task includes:
- Specific files to modify
- Exact code changes required
- Testing requirements
- Success criteria

**Total Estimated Effort**: 12-16 hours (1.5-2 days)

---

## Phase 1: Critical Fixes (MUST COMPLETE BEFORE RELEASE)

### Task 1: Fix Workflow Protocol Violations ⚠️ BLOCKER

**Priority**: P0 - CRITICAL
**Effort**: 4 hours
**Assignee**: TBD
**Status**: 🔴 Not Started

#### Description
All 3 workflows create TaskMessage objects without required `campaign_id` and `task_type` fields. This violates the protocol and will cause validation errors.

#### Files to Modify
1. `src/workflows/campaign_workflow.py`
2. `src/workflows/competitive_workflow.py`
3. `src/workflows/monitoring_workflow.py`
4. `tests/unit/workflows/test_campaign_workflow.py`
5. `tests/unit/workflows/test_competitive_workflow.py`
6. `tests/unit/workflows/test_monitoring_workflow.py`

#### Detailed Changes

**Step 1: Update campaign_workflow.py**

```python
# Line 58: Add campaign_id parameter
def decompose(
    self,
    campaign_id: str,  # ADD THIS
    url: str,
    queries: Optional[List[str]] = None,
    competitors: Optional[List[str]] = None,
    mode: ExecutionMode = ExecutionMode.balanced,
) -> List[TaskMessage]:

# Lines 62-75: Add campaign_id and task_type
tasks.append(TaskMessage(
    task_id=f"audit_{timestamp}",
    campaign_id=campaign_id,  # ADD THIS
    task_type=TaskType.AUDIT_CONTENT,  # ADD THIS
    agent_type=AgentType.AUDITOR,
    input_data={...},
    priority=1,
    depends_on=[],
    deadline=datetime.now() + timedelta(minutes=5)
))
```

**Apply same pattern to**:
- Line 93-100: Optimizer task → `task_type=TaskType.OPTIMIZE_CONTENT`
- Line 118-125: Citation tracker → `task_type=TaskType.TRACK_CITATIONS`
- Line 143-150: Auditor (balanced) → `task_type=TaskType.AUDIT_CONTENT`
- Line 168-175: Optimizer (balanced) → `task_type=TaskType.OPTIMIZE_CONTENT`
- Line 193-200: Auditor (minimal) → `task_type=TaskType.AUDIT_CONTENT`

**Step 2: Update competitive_workflow.py**

Same pattern for 4 locations:
- Line 71-84: Analysis → `task_type=TaskType.ANALYZE_COMPETITORS`
- Line 102-115: Comparison → `task_type=TaskType.COMPARE_CONTENT`
- Line 133-146: Report → `task_type=TaskType.GENERATE_REPORT`
- Line 164-177: Minimal → `task_type=TaskType.ANALYZE_COMPETITORS`

**Step 3: Update monitoring_workflow.py**

Same pattern for 4 locations:
- Line 68-81: Tracking → `task_type=TaskType.TRACK_CITATIONS`
- Line 99-112: Alerts → `task_type=TaskType.CHECK_ALERTS`
- Line 130-143: Reports → `task_type=TaskType.GENERATE_REPORT`
- Line 161-174: Check → `task_type=TaskType.TRACK_CITATIONS`

**Step 4: Update Orchestrator Calls**

Update all workflow invocations to pass campaign_id:

`src/agents/orchestrator_agent.py`:
```python
# Line 240
tasks = workflow.decompose(
    campaign_id=campaign_id,  # ADD THIS
    url=workflow_params.get("url"),
    queries=workflow_params.get("queries"),
    competitors=workflow_params.get("competitors"),
    mode=execution_mode,
)
```

**Step 5: Update Tests**

Update all workflow tests to pass campaign_id:

```python
def test_campaign_workflow_decompose():
    workflow = CampaignWorkflow()
    tasks = workflow.decompose(
        campaign_id="test_campaign_123",  # ADD THIS
        url="https://example.com",
        mode=ExecutionMode.comprehensive
    )

    # Verify protocol compliance
    for task in tasks:
        assert task.campaign_id == "test_campaign_123"
        assert task.task_type is not None
        assert task.agent_type is not None
```

#### Testing Requirements
- [ ] All unit tests pass
- [ ] Integration tests verify protocol compliance
- [ ] E2E workflow execution succeeds
- [ ] No validation errors in logs

#### Success Criteria
- ✅ All 14 TaskMessage constructions include campaign_id
- ✅ All 14 TaskMessage constructions include task_type
- ✅ All tests updated and passing
- ✅ No protocol validation errors

#### Dependencies
- None

---

### Task 2: Fix Deprecated datetime.utcnow() ⚠️ BLOCKER

**Priority**: P0 - CRITICAL
**Effort**: 2 hours
**Assignee**: TBD
**Status**: 🔴 Not Started

#### Description
Using deprecated `datetime.utcnow()` in 23 locations across 5 files. Must replace with `datetime.now(timezone.utc)` for Python 3.12+ compatibility.

#### Files to Modify
1. `src/agents/base_agent.py` (4 occurrences)
2. `src/agents/orchestrator_agent.py` (3 occurrences)
3. `src/communication/protocol.py` (8 occurrences)
4. `src/persistence/campaign_store.py` (3 occurrences)
5. `src/utils/logging.py` (1 occurrence)

#### Detailed Changes

**Step 1: Add timezone import to all files**

```python
from datetime import datetime, timezone
```

**Step 2: Replace datetime.utcnow() calls**

**base_agent.py**:
```python
# Line 142
started_at = datetime.now(timezone.utc)

# Line 167
completed_at = datetime.now(timezone.utc)

# Line 294
timestamp = datetime.now(timezone.utc)

# Line 419
current_time = datetime.now(timezone.utc)
```

**orchestrator_agent.py**:
```python
# Line 226
campaign_id = f"temp_{datetime.now(timezone.utc).timestamp()}"
# Note: Will be replaced by UUID in Task 8

# Line 322
timestamp = datetime.now(timezone.utc).timestamp()

# Line 378
end_time = datetime.now(timezone.utc)
```

**protocol.py** (Pydantic default_factory):
```python
# Line 113
created_at: datetime = Field(
    default_factory=lambda: datetime.now(timezone.utc),
    description="Task creation timestamp"
)

# Lines 173, 174, 195, 219, 275, 424, 425 - same pattern
default_factory=lambda: datetime.now(timezone.utc)
```

**campaign_store.py**:
```python
# Line 84
timestamp=datetime.now(timezone.utc)

# Line 195
manifest.workflow_state.updated_at = datetime.now(timezone.utc)

# Line 257
updated_at=datetime.now(timezone.utc)
```

**logging.py**:
```python
# Line 30
"timestamp": datetime.now(timezone.utc).isoformat()
```

#### Testing Requirements
- [ ] All tests pass with new datetime objects
- [ ] No deprecation warnings in Python 3.12
- [ ] Timezone-aware datetimes work correctly
- [ ] Date comparisons still work correctly

#### Success Criteria
- ✅ All 23 occurrences replaced
- ✅ No `datetime.utcnow()` in codebase
- ✅ All tests passing
- ✅ No DeprecationWarnings

#### Dependencies
- None (can be done in parallel with Task 1)

---

### Task 3: Fix CORS Security Vulnerability ⚠️ BLOCKER

**Priority**: P0 - SECURITY
**Effort**: 1 hour
**Assignee**: TBD
**Status**: 🔴 Not Started

#### Description
API allows requests from ANY origin with wildcard CORS configuration. Must restrict to specific origins.

#### Files to Modify
1. `src/api/main.py`
2. `src/utils/config.py` (add CORS config)
3. `.env.example` (document CORS settings)
4. `agentic-aeo/README.md` (update deployment docs)

#### Detailed Changes

**Step 1: Add CORS configuration to config.py**

```python
# src/utils/config.py - Add to Config model

class APIConfig(BaseModel):
    """API server configuration"""
    host: str = Field(default="0.0.0.0", description="API host")
    port: int = Field(default=8000, ge=1024, le=65535, description="API port")

    # ADD THESE FIELDS
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins"
    )
    allowed_methods: List[str] = Field(
        default=["GET", "POST", "DELETE"],
        description="Allowed HTTP methods"
    )
    allowed_headers: List[str] = Field(
        default=["Content-Type", "Authorization"],
        description="Allowed HTTP headers"
    )
```

**Step 2: Update main.py to use config**

```python
# src/api/main.py

from ..utils.config import get_config

config = get_config()

# Line 83-89: Replace with
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.api.allowed_origins,
    allow_credentials=True,
    allow_methods=config.api.allowed_methods,
    allow_headers=config.api.allowed_headers,
)
```

**Step 3: Add environment variable support**

Create `.env.example`:
```bash
# CORS Configuration
# Comma-separated list of allowed origins
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# For production, specify your domains:
# ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

**Step 4: Update config loading**

```python
# src/utils/config.py - Update from_env() method

@classmethod
def from_env(cls) -> "Config":
    load_dotenv()

    # Parse CORS origins from environment
    allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000")
    allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]

    return cls(
        api=APIConfig(
            host=os.getenv("API_HOST", "0.0.0.0"),
            port=int(os.getenv("API_PORT", "8000")),
            allowed_origins=allowed_origins,  # ADD THIS
        ),
        # ... rest of config
    )
```

#### Testing Requirements
- [ ] Create test with allowed origin - should succeed
- [ ] Create test with disallowed origin - should fail
- [ ] Verify preflight OPTIONS requests work
- [ ] Test with credentials

```python
# tests/integration/test_cors.py
def test_cors_allowed_origin(client):
    response = client.get("/api/campaigns", headers={"Origin": "http://localhost:3000"})
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"

def test_cors_disallowed_origin(client):
    response = client.get("/api/campaigns", headers={"Origin": "https://evil.com"})
    # Should not have CORS headers
    assert "access-control-allow-origin" not in response.headers
```

#### Success Criteria
- ✅ CORS restricted to configured origins only
- ✅ Methods restricted to GET, POST, DELETE
- ✅ Headers restricted to Content-Type, Authorization
- ✅ Environment-based configuration working
- ✅ Documentation updated

#### Dependencies
- None

---

### Task 4: Fix Exception Detail Leakage ⚠️ BLOCKER

**Priority**: P0 - SECURITY
**Effort**: 1 hour
**Assignee**: TBD
**Status**: 🔴 Not Started

#### Description
API returns full exception details to clients, exposing internal implementation and potential vulnerabilities.

#### Files to Modify
1. `src/api/main.py`
2. `src/api/routes/campaigns.py`
3. `src/api/routes/reports.py`

#### Detailed Changes

**Step 1: Update global exception handler**

```python
# src/api/main.py

import logging
import uuid

logger = logging.getLogger(__name__)

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions with proper logging and generic responses"""

    # Generate unique error ID for correlation
    error_id = str(uuid.uuid4())

    # Log full error internally with context
    logger.error(
        f"Unhandled exception [error_id={error_id}]: {exc}",
        exc_info=True,
        extra={
            "error_id": error_id,
            "path": request.url.path,
            "method": request.method,
            "client_ip": request.client.host,
        }
    )

    # Return generic error to client
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail=f"An unexpected error occurred. Error ID: {error_id}",  # Generic + tracking ID
            timestamp=datetime.now()
        ).dict()
    )
```

**Step 2: Update campaign routes exception handling**

```python
# src/api/routes/campaigns.py

# Line 87-90
except Exception as e:
    error_id = str(uuid.uuid4())
    logger.error(
        f"Campaign execution failed [error_id={error_id}]",
        exc_info=True,
        extra={
            "error_id": error_id,
            "campaign_id": campaign_id,
            "workflow_name": workflow_name,
            "error": str(e)
        }
    )
    campaigns_store[campaign_id]["status"] = WorkflowStatus.failed
    campaigns_store[campaign_id]["errors"] = [f"Error ID: {error_id}"]
    raise HTTPException(
        status_code=500,
        detail=f"Campaign execution failed. Error ID: {error_id}"
    )
```

**Step 3: Apply same pattern to all exception handlers**

Update similar exception handlers in:
- `campaigns.py` lines 171-174
- `reports.py` (all exception handlers)

#### Testing Requirements
- [ ] Verify error logging includes full stack trace
- [ ] Verify client receives generic message only
- [ ] Verify error ID allows log correlation
- [ ] Test various exception types

```python
# tests/integration/test_error_handling.py
def test_internal_error_no_detail_leakage(client, mocker):
    """Verify exception details not exposed to client"""
    # Mock to raise exception with sensitive info
    mocker.patch("orchestrator.execute_workflow", side_effect=Exception("Secret DB password: abc123"))

    response = client.post("/api/campaigns", json={...})

    assert response.status_code == 500
    assert "Secret DB password" not in response.text
    assert "Error ID:" in response.json()["detail"]
```

#### Success Criteria
- ✅ No exception details in API responses
- ✅ All errors logged with full context
- ✅ Error IDs enable support correlation
- ✅ Tests verify no information leakage

#### Dependencies
- None

---

### Task 5: Fix Platform Compatibility (Windows) ⚠️ BLOCKER

**Priority**: P0 - CRITICAL
**Effort**: 3 hours
**Assignee**: TBD
**Status**: 🔴 Not Started

#### Description
Code uses `fcntl` module which is UNIX-only. Application crashes immediately on Windows.

#### Files to Modify
1. `src/persistence/file_ops.py`
2. `tests/integration/test_file_ops.py` (add platform-specific tests)

#### Detailed Changes

**Step 1: Implement cross-platform file locking**

```python
# src/persistence/file_ops.py

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from contextlib import contextmanager

# Platform-specific imports
if sys.platform == "win32":
    import msvcrt
else:
    import fcntl


class AtomicFileWriter:
    """
    Atomic file writer with cross-platform file locking.

    Supports both Windows (msvcrt) and UNIX (fcntl) file locking.
    """

    def _lock_file(self, file_handle, exclusive: bool = True) -> None:
        """
        Lock file in a cross-platform way.

        Args:
            file_handle: Open file handle
            exclusive: If True, acquire exclusive lock; otherwise shared lock
        """
        if sys.platform == "win32":
            # Windows file locking using msvcrt
            try:
                # Lock first byte of file
                # LK_NBLCK = non-blocking exclusive lock
                # LK_LOCK = blocking exclusive lock
                msvcrt.locking(
                    file_handle.fileno(),
                    msvcrt.LK_LOCK,
                    1
                )
            except OSError as e:
                raise OSError(f"Failed to acquire file lock (Windows): {e}") from e
        else:
            # UNIX file locking using fcntl
            try:
                lock_type = fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH
                fcntl.flock(file_handle.fileno(), lock_type)
            except OSError as e:
                raise OSError(f"Failed to acquire file lock (UNIX): {e}") from e

    def _unlock_file(self, file_handle) -> None:
        """
        Unlock file in a cross-platform way.

        Args:
            file_handle: Open file handle
        """
        if sys.platform == "win32":
            # Windows unlock
            try:
                msvcrt.locking(
                    file_handle.fileno(),
                    msvcrt.LK_UNLCK,
                    1
                )
            except OSError:
                # Ignore unlock errors (file may already be unlocked)
                pass
        else:
            # UNIX unlock
            try:
                fcntl.flock(file_handle.fileno(), fcntl.LOCK_UN)
            except OSError:
                # Ignore unlock errors
                pass

    @contextmanager
    def atomic_write(self, file_path: Path, mode: str = "w", encoding: str = "utf-8"):
        """
        Context manager for atomic file writes with locking.

        Example:
            with writer.atomic_write(Path("data.json")) as f:
                json.dump(data, f)
        """
        temp_path = file_path.with_suffix(file_path.suffix + ".tmp")

        try:
            # Open temp file and acquire lock
            with open(temp_path, mode, encoding=encoding) as f:
                self._lock_file(f, exclusive=True)
                try:
                    yield f
                    f.flush()
                    import os
                    os.fsync(f.fileno())  # Ensure written to disk
                finally:
                    self._unlock_file(f)

            # Atomic rename (works on both Windows and UNIX)
            temp_path.replace(file_path)

        except Exception as e:
            # Cleanup temp file on error
            if temp_path.exists():
                temp_path.unlink()
            raise

    # Update other methods similarly...
```

**Step 2: Update all file operations to use new methods**

Lines 80, 134, 181 - Replace direct fcntl calls with `self._lock_file()` and `self._unlock_file()`.

**Step 3: Add platform-specific tests**

```python
# tests/integration/test_file_ops.py

import sys
import pytest
from pathlib import Path
from persistence.file_ops import AtomicFileWriter

@pytest.mark.skipif(sys.platform != "win32", reason="Windows only")
def test_file_locking_windows(tmp_path):
    """Verify file locking works on Windows"""
    writer = AtomicFileWriter()
    test_file = tmp_path / "test.txt"

    with writer.atomic_write(test_file) as f:
        f.write("test content")

    assert test_file.exists()
    assert test_file.read_text() == "test content"


@pytest.mark.skipif(sys.platform == "win32", reason="UNIX only")
def test_file_locking_unix(tmp_path):
    """Verify file locking works on UNIX"""
    writer = AtomicFileWriter()
    test_file = tmp_path / "test.txt"

    with writer.atomic_write(test_file) as f:
        f.write("test content")

    assert test_file.exists()
    assert test_file.read_text() == "test content"


def test_file_locking_cross_platform(tmp_path):
    """Verify file locking works on current platform"""
    writer = AtomicFileWriter()
    test_file = tmp_path / "test.txt"

    with writer.atomic_write(test_file) as f:
        f.write("platform-agnostic test")

    assert test_file.exists()
```

#### Testing Requirements
- [ ] Test on Windows (if available)
- [ ] Test on UNIX/Linux
- [ ] Test on macOS
- [ ] Verify no crashes on any platform
- [ ] Test concurrent file access

#### Success Criteria
- ✅ No fcntl imports in Windows
- ✅ File operations work on all platforms
- ✅ Platform-specific tests passing
- ✅ No crashes on Windows

#### Dependencies
- Requires Windows test environment (optional - can use CI/CD)

---

### Task 6: Add Missing Error Logging ⚠️ HIGH

**Priority**: P1 - HIGH
**Effort**: 2 hours
**Assignee**: TBD
**Status**: 🔴 Not Started

#### Description
Exception handlers in API routes don't log errors, making debugging impossible.

#### Files to Modify
1. `src/api/routes/campaigns.py`
2. `src/api/routes/reports.py`

#### Detailed Changes

**Step 1: Add logging to all exception handlers**

```python
# src/api/routes/campaigns.py

import logging

logger = logging.getLogger(__name__)

# Line 87-90
except Exception as e:
    logger.error(
        f"Campaign execution failed",
        exc_info=True,
        extra={
            "campaign_id": campaign_id,
            "workflow_name": workflow_name,
            "error_type": type(e).__name__,
            "error_message": str(e)
        }
    )
    campaigns_store[campaign_id]["status"] = WorkflowStatus.failed
    campaigns_store[campaign_id]["errors"] = [str(e)]
    raise HTTPException(status_code=500, detail=str(e))
```

Apply to all exception handlers in both files.

#### Testing Requirements
- [ ] Verify logs captured for all error scenarios
- [ ] Verify exc_info=True includes stack traces
- [ ] Verify structured logging fields present

#### Success Criteria
- ✅ All exception handlers log errors
- ✅ Logs include full context
- ✅ Stack traces captured

#### Dependencies
- None

---

### Task 7: Fix Campaign ID Collisions ⚠️ HIGH

**Priority**: P1 - HIGH
**Effort**: 1 hour
**Assignee**: TBD
**Status**: 🔴 Not Started

#### Description
Temporary campaign IDs use timestamp which can collide if workflows start concurrently.

#### Files to Modify
1. `src/agents/orchestrator_agent.py`

#### Detailed Changes

```python
# src/agents/orchestrator_agent.py

import uuid  # ADD THIS

# Line 226, 322, 378 - Replace timestamp with UUID
campaign_id = f"temp_{uuid.uuid4().hex[:12]}"
```

#### Testing Requirements
- [ ] Test concurrent workflow creation
- [ ] Verify no ID collisions
- [ ] Test with 100+ concurrent workflows

```python
def test_concurrent_campaign_ids():
    """Verify no campaign ID collisions"""
    orchestrator = OrchestratorAgent()

    # Create 100 campaigns concurrently
    tasks = [
        orchestrator.execute_workflow("aeo-campaign", {...})
        for _ in range(100)
    ]

    results = await asyncio.gather(*tasks)
    campaign_ids = [r.campaign_id for r in results]

    # All IDs should be unique
    assert len(campaign_ids) == len(set(campaign_ids))
```

#### Success Criteria
- ✅ UUID-based campaign IDs
- ✅ No collisions in stress tests
- ✅ Tests passing

#### Dependencies
- None

---

## Phase 2: Important Fixes (Recommended)

### Task 8: Add Path Traversal Protection

**Priority**: P2 - MEDIUM
**Effort**: 1 hour

See CODE_REVIEW_REPORT.md section for full details.

---

### Task 9: Refactor CLI Duplication

**Priority**: P2 - MEDIUM
**Effort**: 2 hours

Extract shared orchestrator creation logic to utility function.

---

### Task 10: Add Delete Campaign Protection

**Priority**: P2 - MEDIUM
**Effort**: 2 hours

Add force flag, status checks, and optional backup before deletion.

---

## Testing Strategy

### Unit Tests
- [ ] All workflow protocol tests updated
- [ ] Platform-specific file locking tests
- [ ] CORS configuration tests
- [ ] Error handling tests

### Integration Tests
- [ ] E2E workflow execution with fixes
- [ ] API security tests (CORS, error leakage)
- [ ] Cross-platform file operations
- [ ] Concurrent workflow execution

### Manual Testing
- [ ] Run on Windows (if available)
- [ ] Run on Linux
- [ ] Run on macOS
- [ ] Test API with real HTTP client
- [ ] Test CLI with all commands

---

## Release Checklist

### Before Starting Fixes
- [ ] Create feature branch `fix/v1.5.0-critical-issues`
- [ ] Review this entire plan
- [ ] Set up test environments

### After Each Task
- [ ] Run unit tests
- [ ] Run integration tests
- [ ] Update task status in this document
- [ ] Commit changes with descriptive message

### After All Critical Fixes
- [ ] Run full test suite
- [ ] Run mypy in strict mode
- [ ] Check for deprecation warnings
- [ ] Update CHANGELOG.md
- [ ] Update version to 1.5.0
- [ ] Create pull request
- [ ] Code review
- [ ] Merge to main
- [ ] Create GitHub release
- [ ] Tag v1.5.0

---

## Tracking Progress

### Task Status Legend
- 🔴 Not Started
- 🟡 In Progress
- 🟢 Completed
- ⏸️ Blocked

### Current Status (2025-11-09)

| Task | Priority | Status | Assignee | ETA |
|------|----------|--------|----------|-----|
| 1. Workflow Protocol | P0 | 🔴 | TBD | 4h |
| 2. datetime Deprecation | P0 | 🔴 | TBD | 2h |
| 3. CORS Security | P0 | 🔴 | TBD | 1h |
| 4. Exception Leakage | P0 | 🔴 | TBD | 1h |
| 5. Platform Compat | P0 | 🔴 | TBD | 3h |
| 6. Error Logging | P1 | 🔴 | TBD | 2h |
| 7. Campaign ID | P1 | 🔴 | TBD | 1h |

**Total Time**: 14 hours estimated

---

## Contact & Support

**Questions**: See GitHub issues
**Blockers**: Escalate immediately
**Updates**: Update this document as tasks complete

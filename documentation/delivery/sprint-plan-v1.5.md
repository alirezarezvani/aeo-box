# AEO Box v1.5 Multi-Agent System - Sprint Plan

> **Comprehensive sprint breakdown for implementing the multi-agent AEO system**
> **Timeline**: 14-16 working days (4 sprints)
> **Target**: Production-ready v1.5 with CLI + REST API
> **Primary Spec**: [aeo-agentic-app-master-prompt.md](../../aeo-agentic-app-master-prompt.md)

---

## Table of Contents

- [Project Overview](#project-overview)
- [Sprint Structure](#sprint-structure)
- [Sprint 1: Foundation](#sprint-1-foundation-days-1-4)
- [Sprint 2: Specialized Agents](#sprint-2-specialized-agents-days-5-8)
- [Sprint 3: Workflows + Interfaces](#sprint-3-workflows--interfaces-days-9-11)
- [Sprint 4: Testing + Production Polish](#sprint-4-testing--production-polish-days-12-16)
- [Implementation Guidelines](#implementation-guidelines)
- [Definition of Done](#definition-of-done)
- [References](#references)

---

## Project Overview

### What We're Building

A **multi-agent orchestration system** for Answer Engine Optimization (AEO) that automates content optimization, citation tracking, and competitive analysis using Claude Agent SDK.

### Architecture Components

```
Orchestrator Agent (coordinator)
├── Content Auditor Agent (E-E-A-T analysis)
├── Content Optimizer Agent (content enhancement)
├── Citation Tracker Agent (LLM citation monitoring)
├── Query Researcher Agent (opportunity research)
├── Report Generator Agent (executive reporting)
└── Learning Optimizer Agent (pattern analysis)
```

### Key Deliverables

1. **7 Agents**: 1 orchestrator + 6 specialized subagents
2. **3 Workflows**: `/aeo-campaign`, `/aeo-compete`, `/aeo-monitor`
3. **2 Interfaces**: CLI (Click) + REST API (FastAPI)
4. **Data Persistence**: Local file storage (`.aeo-agent-data/`)
5. **Testing**: >80% coverage (unit + integration + E2E)
6. **Documentation**: Complete user + developer guides

---

## Sprint Structure

| Sprint | Duration | Focus | Deliverable |
|--------|----------|-------|-------------|
| **1** | 4 days (32h) | Foundation | Orchestrator + communication protocol |
| **2** | 4 days (32h) | Agents | 6 specialized agents integrated |
| **3** | 3 days (24h) | Workflows | 3 workflows + CLI + API |
| **4** | 3-5 days (24-40h) | Testing | Production-ready release |
| **Total** | **14-16 days** | **112-128h** | **v1.5.0 release** |

---

## SPRINT 1: FOUNDATION (Days 1-4)

### Sprint Goal
**Build the agent infrastructure and orchestrator that can coordinate simple multi-agent workflows**

### Definition of Done
- [x] Orchestrator decomposes simple task into subtasks
- [x] Agents communicate via standardized protocol
- [x] Data persists to `.aeo-agent-data/`
- [x] Base agent class working with 1 test agent
- [x] >80% test coverage for core components
- [x] Integration test passes (orchestrator → mock agent)

---

### Day 1: Project Setup + Base Infrastructure (8 hours)

#### Task 1.1: Project Scaffolding (2 hours)

**Objective**: Create complete directory structure for v1.5 multi-agent system

**Subtasks**:

1. **Create directory structure** (45 min):
   ```bash
   mkdir -p agentic-aeo/src/{agents,workflows,communication,persistence,aeo_skill,api,cli,utils}
   mkdir -p agentic-aeo/tests/{unit,integration,e2e}
   mkdir -p agentic-aeo/docs/examples
   mkdir -p agentic-aeo/scripts
   ```

2. **Initialize Python package** (30 min):
   - Create `__init__.py` in all src/ subdirectories
   - Create `pyproject.toml`:
     ```toml
     [project]
     name = "agentic-aeo"
     version = "1.5.0"
     requires-python = ">=3.10"
     dependencies = [
         "anthropic>=0.18.0",
         "fastapi>=0.104.0",
         "uvicorn[standard]>=0.24.0",
         "click>=8.1.0",
         "pydantic>=2.5.0",
         "aiohttp>=3.9.0",
     ]

     [project.optional-dependencies]
     dev = [
         "pytest>=7.4.0",
         "pytest-asyncio>=0.21.0",
         "pytest-cov>=4.1.0",
         "black>=23.11.0",
         "mypy>=1.7.0",
     ]
     ```

3. **Create requirements.txt** (15 min):
   ```txt
   # Core dependencies
   anthropic>=0.18.0
   fastapi>=0.104.0
   uvicorn[standard]>=0.24.0
   click>=8.1.0
   pydantic>=2.5.0
   aiohttp>=3.9.0
   python-dotenv>=1.0.0

   # Development
   pytest>=7.4.0
   pytest-asyncio>=0.21.0
   pytest-cov>=4.1.0
   black>=23.11.0
   mypy>=1.7.0
   isort>=5.13.0
   ```

4. **Copy AEO Skill modules** (30 min):
   ```bash
   cp -r answer-engine-optimization/modules/* agentic-aeo/src/aeo_skill/
   # Verify all 8 modules copied:
   # content_analyzer.py, optimizer.py, citation_tracker.py,
   # query_researcher.py, report_generator.py, success_patterns.py,
   # api_manager.py, utils.py
   ```

**Acceptance Criteria**:
- Directory structure matches specification
- All `__init__.py` files present
- Dependencies installable: `pip install -r requirements.txt`
- AEO Skill modules copied and importable

**Estimated Effort**: 2 hours

---

#### Task 1.2: Configuration Management (1.5 hours)

**Objective**: Working configuration system for all environments

**Subtasks**:

1. **Create Config class** (45 min):
   ```python
   # src/utils/config.py
   from pathlib import Path
   from typing import Optional
   import os
   from dotenv import load_dotenv

   load_dotenv()

   class Config:
       """Application configuration"""

       # Data directories
       DATA_DIR: str = os.getenv("AEO_DATA_DIR", ".aeo-agent-data")
       CAMPAIGNS_DIR: str = f"{DATA_DIR}/campaigns"
       WORKFLOWS_DIR: str = f"{DATA_DIR}/workflows"
       MONITORING_DIR: str = f"{DATA_DIR}/monitoring"

       # API settings
       ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
       OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")

       # Performance
       DEFAULT_TIMEOUT: int = int(os.getenv("TASK_TIMEOUT", "300"))  # 5 min
       MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
       MAX_PARALLEL_AGENTS: int = int(os.getenv("MAX_PARALLEL", "6"))

       # Logging
       LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
       LOG_FILE: Optional[str] = os.getenv("LOG_FILE")

       # Cost optimization
       ENABLE_PROMPT_CACHING: bool = os.getenv("ENABLE_CACHING", "true").lower() == "true"
       CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL", "300"))

       @classmethod
       def create_data_directories(cls):
           """Create data directories if they don't exist"""
           for dir_path in [cls.DATA_DIR, cls.CAMPAIGNS_DIR,
                           cls.WORKFLOWS_DIR, cls.MONITORING_DIR]:
               Path(dir_path).mkdir(parents=True, exist_ok=True)
   ```

2. **Create .env.example** (30 min):
   ```bash
   # API Keys
   ANTHROPIC_API_KEY=your_anthropic_key_here
   OPENAI_API_KEY=your_openai_key_here
   PERPLEXITY_API_KEY=your_perplexity_key_here
   GOOGLE_API_KEY=your_google_key_here

   # Data Storage
   AEO_DATA_DIR=.aeo-agent-data
   DATA_RETENTION_DAYS=90

   # Performance
   TASK_TIMEOUT=300
   MAX_RETRIES=3
   MAX_PARALLEL=6

   # Logging
   LOG_LEVEL=INFO
   LOG_FILE=aeo-agent.log

   # Cost Optimization
   ENABLE_CACHING=true
   CACHE_TTL=300
   ```

3. **Add initialization logic** (15 min):
   ```python
   # src/__init__.py
   from .utils.config import Config

   # Initialize on import
   Config.create_data_directories()
   ```

**Acceptance Criteria**:
- Config loads from environment variables
- Data directories created automatically
- No hardcoded paths in code
- Can override config via .env file

**Estimated Effort**: 1.5 hours

---

#### Task 1.3: Logging Infrastructure (1 hour)

**Objective**: Structured logging system with JSON output

**Subtasks**:

1. **Create StructuredLogger** (45 min):
   ```python
   # src/utils/logging.py
   import logging
   import json
   from datetime import datetime
   from typing import Dict, Any
   from pathlib import Path

   class StructuredLogger:
       """JSON-based structured logging for agents"""

       def __init__(self, agent_name: str, log_level: str = "INFO"):
           self.agent_name = agent_name
           self.logger = logging.getLogger(f"aeo.{agent_name}")
           self.logger.setLevel(getattr(logging, log_level))

           # JSON formatter
           handler = logging.StreamHandler()
           handler.setFormatter(JsonFormatter())
           self.logger.addHandler(handler)

       def log_agent_communication(
           self,
           from_agent: str,
           to_agent: str,
           message_id: str,
           message_type: str
       ):
           """Log agent-to-agent communication"""
           self.logger.info(json.dumps({
               "timestamp": datetime.utcnow().isoformat(),
               "event_type": "agent_communication",
               "from_agent": from_agent,
               "to_agent": to_agent,
               "message_id": message_id,
               "message_type": message_type
           }))

       def log_task_execution(
           self,
           agent: str,
           task_id: str,
           status: str,
           duration_seconds: float = None
       ):
           """Log task execution"""
           log_data = {
               "timestamp": datetime.utcnow().isoformat(),
               "event_type": "task_execution",
               "agent": agent,
               "task_id": task_id,
               "status": status
           }
           if duration_seconds:
               log_data["duration_seconds"] = duration_seconds

           self.logger.info(json.dumps(log_data))

   class JsonFormatter(logging.Formatter):
       """Format logs as JSON"""
       def format(self, record):
           try:
               return json.loads(record.getMessage())
           except:
               return {
                   "timestamp": datetime.utcnow().isoformat(),
                   "level": record.levelname,
                   "message": record.getMessage()
               }
   ```

2. **Configure log rotation** (15 min):
   - Add rotating file handler (100MB max, 10 backups)
   - Separate logs: `orchestrator.log`, `agents.log`

**Acceptance Criteria**:
- Logs output as JSON
- Log rotation configured
- Can log to both console and file
- No sensitive data logged (API keys)

**Estimated Effort**: 1 hour

---

#### Task 1.4: Communication Protocol (3.5 hours)

**Objective**: Standardized message format using Pydantic

**Subtasks**:

1. **Create Pydantic models** (2 hours):
   ```python
   # src/communication/protocol.py
   from pydantic import BaseModel, Field
   from typing import Dict, Any, Optional, Literal, List
   from datetime import datetime
   import uuid

   class TaskMessage(BaseModel):
       """Task assignment from orchestrator to subagent"""
       message_id: str = Field(default_factory=lambda: f"msg_{uuid.uuid4().hex[:12]}")
       timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
       from_agent: str
       to_agent: str
       message_type: Literal["task_assignment"] = "task_assignment"

       task: Dict[str, Any] = Field(..., description="Task specification")
       # task structure:
       # {
       #   "task_id": str,
       #   "task_type": str,
       #   "priority": str,
       #   "deadline": str (ISO8601),
       #   "input_data": Dict,
       #   "quality_criteria": Dict
       # }

   class TaskResult(BaseModel):
       """Task result from subagent to orchestrator"""
       message_id: str = Field(default_factory=lambda: f"msg_{uuid.uuid4().hex[:12]}")
       timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
       from_agent: str
       to_agent: str
       message_type: Literal["task_result"] = "task_result"

       task_id: str
       status: Literal["success", "failed", "partial"]
       execution_time_seconds: float

       results: Dict[str, Any] = Field(..., description="Agent-specific results")
       markdown_report: str = Field(..., description="Formatted report")

       errors: List[str] = Field(default_factory=list)
       warnings: List[str] = Field(default_factory=list)

       metadata: Optional[Dict[str, Any]] = Field(
           default_factory=lambda: {
               "aeo_skill_version": "1.0.0",
               "confidence_score": 0.0
           }
       )

   class RevisionRequest(BaseModel):
       """Request revision from orchestrator to subagent"""
       message_id: str = Field(default_factory=lambda: f"msg_{uuid.uuid4().hex[:12]}")
       timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
       from_agent: str
       to_agent: str
       message_type: Literal["revision_request"] = "revision_request"

       original_task_id: str
       revision_reason: str
       required_changes: List[str]
       deadline: str
   ```

2. **Add message validation** (45 min):
   ```python
   def validate_task_message(msg: TaskMessage) -> bool:
       """Validate task message has all required fields"""
       required_task_fields = ["task_id", "task_type", "input_data"]
       return all(field in msg.task for field in required_task_fields)

   def validate_task_result(result: TaskResult) -> bool:
       """Validate task result completeness"""
       if result.status == "success":
           return len(result.errors) == 0 and result.results != {}
       return True
   ```

3. **Create message factory** (45 min):
   ```python
   class MessageFactory:
       """Factory for creating standardized messages"""

       @staticmethod
       def create_task_assignment(
           from_agent: str,
           to_agent: str,
           task: Dict[str, Any]
       ) -> TaskMessage:
           return TaskMessage(
               from_agent=from_agent,
               to_agent=to_agent,
               task=task
           )

       @staticmethod
       def create_task_result(
           from_agent: str,
           task_id: str,
           status: str,
           results: Dict,
           markdown_report: str,
           execution_time: float
       ) -> TaskResult:
           return TaskResult(
               from_agent=from_agent,
               to_agent="orchestrator",
               task_id=task_id,
               status=status,
               results=results,
               markdown_report=markdown_report,
               execution_time_seconds=execution_time
           )
   ```

**Acceptance Criteria**:
- Pydantic models validate messages
- Message creation helpers work
- JSON serialization/deserialization works
- Edge cases handled (missing fields, invalid types)

**Estimated Effort**: 3.5 hours

---

### Day 2: Base Agent + Data Persistence (8 hours)

#### Task 2.1: Base Agent Class (4 hours)

**Objective**: Abstract base class for all agents with Claude SDK integration

**Subtasks**:

1. **Create BaseAgent class** (2.5 hours):
   ```python
   # src/agents/base_agent.py
   from abc import ABC, abstractmethod
   from typing import Dict, Any, Optional
   from datetime import datetime
   import asyncio
   import time
   from ..utils.logging import StructuredLogger
   from ..communication.protocol import TaskResult, MessageFactory

   class BaseAgent(ABC):
       """Abstract base class for all AEO agents"""

       def __init__(self, agent_type: str):
           self.agent_type = agent_type
           self.logger = StructuredLogger(agent_type)
           self.max_retries = 3
           self.retry_delay = 2  # seconds

       @abstractmethod
       async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
           """
           Execute assigned task - must be implemented by subclass

           Args:
               task: Task specification with:
                   - task_id: Unique task identifier
                   - task_type: Type of task to execute
                   - input_data: Task-specific input data
                   - quality_criteria: Validation criteria

           Returns:
               Task result dictionary with:
                   - status: "success", "failed", or "partial"
                   - results: Agent-specific results
                   - markdown_report: Formatted report
                   - errors: List of errors
                   - warnings: List of warnings
           """
           pass

       def validate_input(self, task: Dict) -> bool:
           """Validate task has required fields"""
           required = ["task_id", "task_type", "input_data"]
           if not all(field in task for field in required):
               return False

           # Type-specific validation
           if not isinstance(task["input_data"], dict):
               return False

           return True

       def validate_output(self, result: Dict) -> bool:
           """Validate result completeness"""
           required = ["status", "agent", "task_id", "results"]
           return all(field in result for field in required)

       async def execute_with_retry(
           self,
           task: Dict,
           max_retries: Optional[int] = None
       ) -> Dict[str, Any]:
           """Execute task with retry logic"""
           retries = max_retries or self.max_retries
           last_error = None

           for attempt in range(retries):
               try:
                   result = await self.execute_task(task)
                   return result
               except Exception as e:
                   last_error = e
                   self.logger.log_task_execution(
                       agent=self.agent_type,
                       task_id=task["task_id"],
                       status=f"retry_{attempt+1}"
                   )
                   if attempt < retries - 1:
                       await asyncio.sleep(self.retry_delay * (attempt + 1))

           # All retries failed
           return self._error_result(
               task["task_id"],
               f"Failed after {retries} attempts: {str(last_error)}"
           )

       async def execute_with_timeout(
           self,
           task: Dict,
           timeout_seconds: int = 300
       ) -> Dict[str, Any]:
           """Execute task with timeout"""
           try:
               return await asyncio.wait_for(
                   self.execute_task(task),
                   timeout=timeout_seconds
               )
           except asyncio.TimeoutError:
               return self._error_result(
                   task["task_id"],
                   f"Task timed out after {timeout_seconds} seconds"
               )

       def _error_result(self, task_id: str, error_msg: str) -> Dict:
           """Standard error result format"""
           return {
               "status": "failed",
               "agent": self.agent_type,
               "task_id": task_id,
               "results": {},
               "errors": [error_msg],
               "warnings": [],
               "markdown_report": f"# Error\n\n{error_msg}",
               "execution_time_seconds": 0.0
           }

       def _success_result(
           self,
           task_id: str,
           results: Dict[str, Any],
           markdown_report: str,
           execution_time: float,
           warnings: list = None
       ) -> Dict:
           """Standard success result format"""
           return {
               "status": "success",
               "agent": self.agent_type,
               "task_id": task_id,
               "results": results,
               "markdown_report": markdown_report,
               "errors": [],
               "warnings": warnings or [],
               "execution_time_seconds": execution_time
           }
   ```

2. **Create test agent** (1 hour):
   ```python
   # tests/mocks/mock_agents.py
   from src.agents.base_agent import BaseAgent
   import asyncio

   class MockAuditorAgent(BaseAgent):
       """Mock auditor for testing"""

       def __init__(self):
           super().__init__(agent_type="mock_auditor")

       async def execute_task(self, task: Dict) -> Dict:
           # Simulate processing time
           await asyncio.sleep(0.5)

           return self._success_result(
               task_id=task["task_id"],
               results={
                   "overall_score": 75,
                   "scores": {
                       "eeat": 70,
                       "structure": 80,
                       "citations": 70,
                       "readability": 80
                   }
               },
               markdown_report="# Mock Audit Report\n\nTest audit complete.",
               execution_time=0.5
           )
   ```

3. **Add decorator for retries** (30 min):
   ```python
   from functools import wraps

   def with_retry(max_attempts=3, delay=2):
       """Decorator for automatic retry logic"""
       def decorator(func):
           @wraps(func)
           async def wrapper(*args, **kwargs):
               for attempt in range(max_attempts):
                   try:
                       return await func(*args, **kwargs)
                   except Exception as e:
                       if attempt == max_attempts - 1:
                           raise
                       await asyncio.sleep(delay * (attempt + 1))
               return wrapper
       return decorator
   ```

**Acceptance Criteria**:
- BaseAgent is abstract (cannot instantiate)
- Test agent inherits successfully
- Input/output validation works
- Retry logic executes correctly
- Timeout handling works
- Error handling returns standardized format

**Estimated Effort**: 4 hours

---

#### Task 2.2: Data Persistence Layer (3 hours)

**Objective**: Campaign and workflow storage with atomic writes

**Subtasks**:

1. **Create CampaignStore** (2 hours):
   ```python
   # src/persistence/campaign_store.py
   from pathlib import Path
   from typing import Dict, Any, Optional
   import json
   import uuid
   from datetime import datetime
   import fcntl  # For file locking (atomic writes)

   class CampaignStore:
       """Manage campaign data persistence"""

       def __init__(self, data_dir: str = ".aeo-agent-data/campaigns"):
           self.data_dir = Path(data_dir)
           self.data_dir.mkdir(parents=True, exist_ok=True)

       def create_campaign(
           self,
           url: str,
           command: str,
           options: Dict[str, Any] = None
       ) -> str:
           """
           Create new campaign directory and metadata

           Returns:
               campaign_id: Unique campaign identifier
           """
           campaign_id = f"camp_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
           campaign_dir = self.data_dir / campaign_id
           campaign_dir.mkdir(parents=True, exist_ok=True)

           # Create subdirectories
           (campaign_dir / "agent_outputs").mkdir(exist_ok=True)

           # Save metadata
           metadata = {
               "campaign_id": campaign_id,
               "created_at": datetime.utcnow().isoformat(),
               "command": command,
               "url": url,
               "options": options or {},
               "status": "running",
               "workflow_id": None,
               "duration_seconds": None,
               "final_score": None,
               "score_improvement": None
           }

           self._write_json(campaign_dir / "metadata.json", metadata)

           return campaign_id

       def save_agent_output(
           self,
           campaign_id: str,
           agent_type: str,
           output: Dict[str, Any]
       ):
           """Save individual agent output"""
           campaign_dir = self.data_dir / campaign_id
           output_file = campaign_dir / "agent_outputs" / f"{agent_type}_output.json"
           self._write_json(output_file, output)

       def save_orchestrator_log(
           self,
           campaign_id: str,
           log_entry: Dict[str, Any]
       ):
           """Append to orchestrator log"""
           campaign_dir = self.data_dir / campaign_id
           log_file = campaign_dir / "orchestrator_log.json"

           # Load existing log
           if log_file.exists():
               log_data = self._read_json(log_file)
               log_data["decisions"].append(log_entry)
           else:
               log_data = {
                   "campaign_id": campaign_id,
                   "decisions": [log_entry],
                   "metrics": {
                       "total_tasks": 0,
                       "successful_tasks": 0,
                       "failed_tasks": 0,
                       "revisions_requested": 0
                   }
               }

           self._write_json(log_file, log_data)

       def update_campaign_status(
           self,
           campaign_id: str,
           status: str,
           final_score: Optional[int] = None,
           duration: Optional[float] = None
       ):
           """Update campaign metadata"""
           campaign_dir = self.data_dir / campaign_id
           metadata_file = campaign_dir / "metadata.json"

           metadata = self._read_json(metadata_file)
           metadata["status"] = status

           if final_score is not None:
               metadata["final_score"] = final_score
           if duration is not None:
               metadata["duration_seconds"] = duration

           self._write_json(metadata_file, metadata)

       def load_campaign(self, campaign_id: str) -> Dict[str, Any]:
           """Load complete campaign data"""
           campaign_dir = self.data_dir / campaign_id

           if not campaign_dir.exists():
               raise ValueError(f"Campaign {campaign_id} not found")

           # Load metadata
           metadata = self._read_json(campaign_dir / "metadata.json")

           # Load agent outputs
           agent_outputs = {}
           output_dir = campaign_dir / "agent_outputs"
           if output_dir.exists():
               for output_file in output_dir.glob("*_output.json"):
                   agent_name = output_file.stem.replace("_output", "")
                   agent_outputs[agent_name] = self._read_json(output_file)

           # Load orchestrator log
           log_file = campaign_dir / "orchestrator_log.json"
           orchestrator_log = self._read_json(log_file) if log_file.exists() else None

           return {
               "metadata": metadata,
               "agent_outputs": agent_outputs,
               "orchestrator_log": orchestrator_log
           }

       def _write_json(self, file_path: Path, data: Dict[str, Any]):
           """Atomic JSON write with file locking"""
           temp_file = file_path.with_suffix('.tmp')

           with open(temp_file, 'w') as f:
               # Acquire exclusive lock
               fcntl.flock(f.fileno(), fcntl.LOCK_EX)
               json.dump(data, f, indent=2)
               fcntl.flock(f.fileno(), fcntl.LOCK_UN)

           # Atomic rename
           temp_file.replace(file_path)

       def _read_json(self, file_path: Path) -> Dict[str, Any]:
           """Read JSON file"""
           with open(file_path, 'r') as f:
               return json.load(f)
   ```

2. **Add workflow store** (1 hour):
   ```python
   # src/persistence/workflow_store.py
   class WorkflowStore:
       """Manage workflow definitions and active workflows"""

       def __init__(self, data_dir: str = ".aeo-agent-data/workflows"):
           self.data_dir = Path(data_dir)
           self.data_dir.mkdir(parents=True, exist_ok=True)

       def save_workflow_template(self, workflow_id: str, template: Dict):
           """Save reusable workflow template"""
           template_file = self.data_dir / "workflow_templates.json"

           if template_file.exists():
               templates = self._read_json(template_file)
           else:
               templates = {}

           templates[workflow_id] = template
           self._write_json(template_file, templates)

       def get_workflow_template(self, workflow_id: str) -> Dict:
           """Load workflow template"""
           template_file = self.data_dir / "workflow_templates.json"
           templates = self._read_json(template_file)
           return templates.get(workflow_id)
   ```

**Acceptance Criteria**:
- Campaign data persists to `.aeo-agent-data/campaigns/`
- Concurrent writes don't corrupt data (atomic writes)
- Can load previously saved campaigns
- Directory structure created automatically
- File locking prevents race conditions

**Estimated Effort**: 3 hours

---

#### Task 2.3: Unit Tests for Day 1-2 (1 hour)

**Objective**: >80% coverage for foundation components

**Subtasks**:

1. **Test configuration** (15 min):
   ```python
   # tests/unit/test_config.py
   import pytest
   from src.utils.config import Config
   import os

   def test_config_loads_defaults():
       assert Config.DATA_DIR == ".aeo-agent-data"
       assert Config.DEFAULT_TIMEOUT == 300

   def test_config_loads_from_env(monkeypatch):
       monkeypatch.setenv("AEO_DATA_DIR", "/tmp/test-data")
       monkeypatch.setenv("TASK_TIMEOUT", "600")
       # Reload config
       assert Config.DEFAULT_TIMEOUT == 600

   def test_config_creates_directories(tmp_path, monkeypatch):
       monkeypatch.setenv("AEO_DATA_DIR", str(tmp_path / "data"))
       Config.create_data_directories()
       assert (tmp_path / "data" / "campaigns").exists()
   ```

2. **Test protocol** (15 min):
   ```python
   # tests/unit/test_protocol.py
   from src.communication.protocol import TaskMessage, TaskResult

   def test_task_message_creation():
       msg = TaskMessage(
           from_agent="orchestrator",
           to_agent="auditor",
           task={"task_id": "test_001", "task_type": "audit", "input_data": {}}
       )
       assert msg.message_type == "task_assignment"
       assert msg.from_agent == "orchestrator"

   def test_task_result_validation():
       result = TaskResult(
           from_agent="auditor",
           to_agent="orchestrator",
           task_id="test_001",
           status="success",
           results={"score": 75},
           markdown_report="# Report",
           execution_time_seconds=1.5
       )
       assert result.status == "success"
       assert len(result.errors) == 0
   ```

3. **Test base agent** (15 min):
   ```python
   # tests/unit/test_base_agent.py
   import pytest
   from tests.mocks.mock_agents import MockAuditorAgent

   @pytest.mark.asyncio
   async def test_mock_agent_executes():
       agent = MockAuditorAgent()
       task = {
           "task_id": "test_001",
           "task_type": "audit",
           "input_data": {"url": "https://example.com"}
       }
       result = await agent.execute_task(task)
       assert result["status"] == "success"
       assert "overall_score" in result["results"]

   @pytest.mark.asyncio
   async def test_agent_retry_logic():
       agent = MockAuditorAgent()
       task = {"task_id": "test_002", "task_type": "audit", "input_data": {}}
       result = await agent.execute_with_retry(task, max_retries=2)
       assert result is not None
   ```

4. **Test persistence** (15 min):
   ```python
   # tests/unit/test_persistence.py
   from src.persistence.campaign_store import CampaignStore
   import pytest

   @pytest.fixture
   def store(tmp_path):
       return CampaignStore(str(tmp_path / "campaigns"))

   def test_create_campaign(store):
       campaign_id = store.create_campaign(
           url="https://example.com",
           command="/aeo-campaign",
           options={"industry": "SaaS"}
       )
       assert campaign_id.startswith("camp_")

   def test_save_and_load_campaign(store):
       campaign_id = store.create_campaign("https://example.com", "/aeo-campaign")
       store.save_agent_output(campaign_id, "auditor", {"score": 75})

       campaign = store.load_campaign(campaign_id)
       assert "auditor" in campaign["agent_outputs"]
       assert campaign["agent_outputs"]["auditor"]["score"] == 75
   ```

**Acceptance Criteria**:
- All tests pass
- Coverage >80% for completed components
- Edge cases covered (empty data, invalid input)
- Tests run fast (<5 seconds)

**Estimated Effort**: 1 hour

---

### Day 3: Orchestrator Agent (Core Logic) (8 hours)

#### Task 3.1: Task Decomposition Engine (4 hours)

**Objective**: Orchestrator can break down user commands into agent tasks

**Subtasks**:

1. **Create Orchestrator class** (2 hours):
   ```python
   # src/agents/orchestrator.py
   from typing import Dict, List, Any, Optional
   import asyncio
   from .base_agent import BaseAgent
   from ..communication.protocol import MessageFactory
   from ..utils.logging import StructuredLogger

   class OrchestratorAgent:
       """Main coordinator agent - manages all workflows"""

       def __init__(self):
           self.agents: Dict[str, BaseAgent] = {}
           self.logger = StructuredLogger("orchestrator")
           self.workflow_templates = self._load_workflow_templates()

       def register_agent(self, agent_name: str, agent_instance: BaseAgent):
           """Register a specialized agent"""
           self.agents[agent_name] = agent_instance
           self.logger.logger.info(f"Registered agent: {agent_name}")

       async def decompose_request(
           self,
           command: str,
           params: Dict[str, Any]
       ) -> List[Dict[str, Any]]:
           """
           Parse user command and create task list

           Args:
               command: Slash command ("/aeo-campaign", "/aeo-compete", etc.)
               params: Command parameters (url, options, etc.)

           Returns:
               List of tasks with dependencies and priorities
           """
           if command == "/aeo-campaign":
               return self._decompose_campaign(params)
           elif command == "/aeo-compete":
               return self._decompose_compete(params)
           elif command == "/aeo-monitor":
               return self._decompose_monitor(params)
           else:
               raise ValueError(f"Unknown command: {command}")

       def _decompose_campaign(self, params: Dict) -> List[Dict]:
           """
           Decompose /aeo-campaign into tasks

           Workflow:
           1. Audit (priority 1) - analyze content
           2. Research (priority 1) - find query opportunities [parallel with 1]
           3. Optimize (priority 2) - improve content [depends on audit]
           4. Track (priority 3) - set up citation monitoring
           5. Report (priority 4) - generate executive summary [depends on all]
           """
           url = params.get("url")
           industry = params.get("industry", "General")
           level = params.get("optimization_level", "balanced")
           track_days = params.get("track_days", 30)

           tasks = [
               {
                   "agent": "auditor",
                   "task_type": "audit_content",
                   "priority": 1,
                   "depends_on": [],
                   "input_data": {
                       "url": url,
                       "context": {"industry": industry}
                   }
               },
               {
                   "agent": "researcher",
                   "task_type": "research_queries",
                   "priority": 1,
                   "depends_on": [],
                   "input_data": {
                       "url": url,
                       "industry": industry
                   }
               },
               {
                   "agent": "optimizer",
                   "task_type": "optimize_content",
                   "priority": 2,
                   "depends_on": ["auditor"],  # Needs audit results
                   "input_data": {
                       "url": url,
                       "level": level,
                       "audit_results": None  # Will be filled during execution
                   }
               },
               {
                   "agent": "tracker",
                   "task_type": "track_citations",
                   "priority": 3,
                   "depends_on": [],
                   "input_data": {
                       "url": url,
                       "tracking_period_days": track_days
                   }
               },
               {
                   "agent": "reporter",
                   "task_type": "generate_report",
                   "priority": 4,
                   "depends_on": ["auditor", "optimizer", "tracker", "researcher"],
                   "input_data": {
                       "agent_results": {}  # Will be filled during execution
                   }
               }
           ]

           return tasks

       def _decompose_compete(self, params: Dict) -> List[Dict]:
           """Decompose /aeo-compete into tasks"""
           topic = params.get("topic")
           competitors = params.get("competitors", [])

           tasks = [
               {
                   "agent": "researcher",
                   "task_type": "research_queries",
                   "priority": 1,
                   "depends_on": [],
                   "input_data": {"topic": topic}
               }
           ]

           # Add audit task for each competitor
           for i, competitor_url in enumerate(competitors):
               tasks.append({
                   "agent": "auditor",
                   "task_type": "audit_content",
                   "priority": 2,
                   "depends_on": [],
                   "input_data": {
                       "url": competitor_url,
                       "context": {"role": "competitor"}
                   },
                   "task_id_suffix": f"_competitor_{i+1}"
               })

           # Gap analysis and report
           tasks.append({
               "agent": "reporter",
               "task_type": "competitive_report",
               "priority": 3,
               "depends_on": ["researcher"] + [f"auditor_competitor_{i+1}" for i in range(len(competitors))],
               "input_data": {
                   "topic": topic,
                   "agent_results": {}
               }
           })

           return tasks

       def _decompose_monitor(self, params: Dict) -> List[Dict]:
           """Decompose /aeo-monitor into tasks"""
           url = params.get("url")
           duration_days = params.get("duration_days", 90)

           return [
               {
                   "agent": "auditor",
                   "task_type": "audit_content",
                   "priority": 1,
                   "depends_on": [],
                   "input_data": {
                       "url": url,
                       "context": {"role": "baseline"}
                   }
               },
               {
                   "agent": "tracker",
                   "task_type": "setup_monitoring",
                   "priority": 2,
                   "depends_on": ["auditor"],
                   "input_data": {
                       "url": url,
                       "duration_days": duration_days,
                       "baseline_audit": None  # Filled during execution
                   }
               }
           ]

       def _load_workflow_templates(self) -> Dict:
           """Load predefined workflow templates"""
           # This could be loaded from workflow_store
           return {
               "campaign": "5-task workflow",
               "compete": "dynamic multi-audit workflow",
               "monitor": "2-task baseline + tracking"
           }
   ```

2. **Add dependency resolution** (1 hour):
   ```python
   def resolve_dependencies(
       self,
       tasks: List[Dict]
   ) -> List[List[Dict]]:
       """
       Group tasks by execution order based on dependencies

       Returns:
           List of task groups, where each group can execute in parallel
       """
       # Build dependency graph
       task_map = {f"{t['agent']}_{t.get('task_id_suffix', '')}": t for t in tasks}

       # Topological sort
       executed = set()
       execution_groups = []

       while len(executed) < len(tasks):
           # Find tasks with satisfied dependencies
           ready_tasks = []
           for task in tasks:
               task_id = f"{task['agent']}_{task.get('task_id_suffix', '')}"
               if task_id in executed:
                   continue

               deps_satisfied = all(
                   dep in executed or f"{dep}_{task.get('task_id_suffix', '')}" in executed
                   for dep in task.get("depends_on", [])
               )

               if deps_satisfied:
                   ready_tasks.append(task)

           if not ready_tasks:
               raise ValueError("Circular dependency detected")

           execution_groups.append(ready_tasks)
           executed.update(f"{t['agent']}_{t.get('task_id_suffix', '')}" for t in ready_tasks)

       return execution_groups
   ```

3. **Add priority ordering** (1 hour):
   ```python
   def order_tasks_by_priority(self, tasks: List[Dict]) -> List[Dict]:
       """Sort tasks by priority (lower number = higher priority)"""
       return sorted(tasks, key=lambda t: t.get("priority", 999))
   ```

**Acceptance Criteria**:
- Can decompose `/aeo-campaign` into 5 tasks
- Can decompose `/aeo-compete` into dynamic task list
- Can decompose `/aeo-monitor` into 2 tasks
- Dependencies correctly identified
- Priority ordering logical
- Handles unknown commands gracefully

**Estimated Effort**: 4 hours

---

#### Task 3.2: Workflow Coordinator (4 hours)

**Objective**: Execute tasks respecting dependencies and priorities

**Subtasks**:

1. **Implement execute_workflow()** (2.5 hours):
   ```python
   async def execute_workflow(
       self,
       tasks: List[Dict],
       campaign_id: str
   ) -> Dict[str, Any]:
       """
       Execute workflow tasks respecting dependencies

       Args:
           tasks: List of tasks from decompose_request()
           campaign_id: Campaign ID for data persistence

       Returns:
           Aggregated results from all agents
       """
       from ..persistence.campaign_store import CampaignStore
       store = CampaignStore()

       # Resolve execution order
       execution_groups = self.resolve_dependencies(tasks)

       # Track results
       results = {}
       errors = []

       # Execute each group sequentially, tasks within group in parallel
       for group_idx, task_group in enumerate(execution_groups):
           self.logger.logger.info(
               f"Executing task group {group_idx+1}/{len(execution_groups)}: "
               f"{[t['agent'] for t in task_group]}"
           )

           # Prepare tasks (fill dependencies)
           prepared_tasks = []
           for task in task_group:
               task_copy = task.copy()
               task_copy["task_id"] = f"{task['agent']}_{campaign_id}_{group_idx}"

               # Fill dependency data
               if "depends_on" in task and task["depends_on"]:
                   for dep_agent in task["depends_on"]:
                       if dep_agent in results:
                           task_copy["input_data"][f"{dep_agent}_results"] = results[dep_agent]

               prepared_tasks.append(task_copy)

           # Execute group in parallel
           group_results = await asyncio.gather(*[
               self._execute_single_task(task, campaign_id, store)
               for task in prepared_tasks
           ], return_exceptions=True)

           # Process results
           for task, result in zip(task_group, group_results):
               agent_name = task["agent"]

               if isinstance(result, Exception):
                   errors.append(f"{agent_name}: {str(result)}")
                   results[agent_name] = {"status": "failed", "error": str(result)}
               elif result["status"] == "failed":
                   errors.append(f"{agent_name}: {result.get('errors', ['Unknown error'])[0]}")
                   results[agent_name] = result
               else:
                   results[agent_name] = result

           # Stop if critical task failed
           if errors and any(t["agent"] in ["auditor", "optimizer"] for t in task_group):
               self.logger.logger.error(f"Critical task failed, aborting workflow: {errors}")
               break

       # Generate executive summary
       executive_summary = self._generate_executive_summary(results, campaign_id)

       return {
           "campaign_id": campaign_id,
           "status": "completed" if not errors else "failed",
           "agent_results": results,
           "errors": errors,
           "executive_summary": executive_summary
       }

   async def _execute_single_task(
       self,
       task: Dict,
       campaign_id: str,
       store: CampaignStore
   ) -> Dict:
       """Execute single agent task"""
       agent_name = task["agent"]

       if agent_name not in self.agents:
           raise ValueError(f"Agent not registered: {agent_name}")

       agent = self.agents[agent_name]

       # Log task assignment
       store.save_orchestrator_log(campaign_id, {
           "timestamp": datetime.utcnow().isoformat(),
           "decision": "task_assignment",
           "agent": agent_name,
           "task_id": task["task_id"]
       })

       # Execute task
       result = await agent.execute_with_timeout(task, timeout_seconds=300)

       # Save agent output
       store.save_agent_output(campaign_id, agent_name, result)

       # Log completion
       store.save_orchestrator_log(campaign_id, {
           "timestamp": datetime.utcnow().isoformat(),
           "decision": "task_completed",
           "agent": agent_name,
           "task_id": task["task_id"],
           "status": result["status"]
       })

       return result
   ```

2. **Add parallel execution** (1 hour):
   ```python
   async def execute_parallel(self, tasks: List[Dict]) -> List[Dict]:
       """Execute multiple tasks in parallel"""
       results = await asyncio.gather(*[
           agent.execute_task(task)
           for agent, task in [(self.agents[t["agent"]], t) for t in tasks]
       ], return_exceptions=True)

       return [r if not isinstance(r, Exception) else {"status": "failed", "error": str(r)}
               for r in results]
   ```

3. **Add failure handling** (30 min):
   ```python
   async def handle_task_failure(
       self,
       task: Dict,
       error: str,
       campaign_id: str
   ) -> Dict:
       """Handle task failure with retry logic"""
       max_retries = 3

       for attempt in range(max_retries):
           self.logger.logger.warning(
               f"Task {task['task_id']} failed (attempt {attempt+1}/{max_retries}): {error}"
           )

           # Retry with backoff
           await asyncio.sleep(2 ** attempt)

           result = await self._execute_single_task(task, campaign_id, CampaignStore())

           if result["status"] != "failed":
               return result

       # All retries failed
       return {
           "status": "failed",
           "agent": task["agent"],
           "task_id": task["task_id"],
           "errors": [f"Failed after {max_retries} retries: {error}"]
       }
   ```

**Acceptance Criteria**:
- Parallel tasks execute concurrently (asyncio.gather)
- Dependencies block execution correctly
- Failed tasks trigger retry logic (up to 3 attempts)
- Results collected and aggregated
- Data persisted to campaign store

**Estimated Effort**: 4 hours

---

### Day 4: Quality Validation + Integration Testing (8 hours)

#### Task 4.1: 4-Layer Quality Validation (3 hours)

**Objective**: Orchestrator validates all agent outputs

**Subtasks**:

1. **Create OutputValidator** (2 hours):
   ```python
   # src/communication/validator.py
   from typing import Dict, Any, List, Optional

   class OutputValidator:
       """4-layer validation system for agent outputs"""

       def validate_all(
           self,
           result: Dict[str, Any],
           task: Dict[str, Any],
           quality_criteria: Optional[Dict] = None
       ) -> tuple[bool, List[str]]:
           """
           Run all 4 validation layers

           Returns:
               (is_valid, list_of_errors)
           """
           errors = []

           # Layer 1: Status check
           if not self.validate_status(result):
               errors.append("Invalid status (must be 'success', 'failed', or 'partial')")

           # Layer 2: Completeness check
           if not self.validate_completeness(result):
               errors.append("Missing required fields in result")

           # Layer 3: Quality criteria check
           if quality_criteria and not self.validate_quality_criteria(result, quality_criteria):
               errors.append("Failed quality criteria validation")

           # Layer 4: Consistency check
           if not self.validate_consistency(result, task):
               errors.append("Results inconsistent with task inputs")

           return (len(errors) == 0, errors)

       def validate_status(self, result: Dict) -> bool:
           """Layer 1: Status check"""
           return result.get("status") in ["success", "failed", "partial"]

       def validate_completeness(self, result: Dict) -> bool:
           """Layer 2: All required fields present"""
           required = ["status", "agent", "results", "markdown_report"]
           return all(field in result for field in required)

       def validate_quality_criteria(
           self,
           result: Dict,
           criteria: Dict
       ) -> bool:
           """Layer 3: Agent-specific quality checks"""
           agent_type = result.get("agent")
           results_data = result.get("results", {})

           if agent_type == "auditor":
               # Auditor must have overall_score >= 0
               return "overall_score" in results_data and results_data["overall_score"] >= 0

           elif agent_type == "optimizer":
               # Optimizer must have improvement data
               return "before_score" in results_data and "after_score" in results_data

           elif agent_type == "tracker":
               # Tracker must have citation data
               return "total_citations" in results_data

           elif agent_type == "researcher":
               # Researcher must have target queries
               return "target_queries" in results_data

           elif agent_type == "reporter":
               # Reporter must have executive summary
               return "executive_summary" in results_data or "report_path" in results_data

           # Default: pass if no specific criteria
           return True

       def validate_consistency(self, result: Dict, task: Dict) -> bool:
           """Layer 4: Results align with inputs"""
           # Check that result task_id matches
           if result.get("task_id") != task.get("task_id"):
               return False

           # Check that agent type matches
           if result.get("agent") != task.get("agent"):
               return False

           # Verify data integrity (e.g., URL in result matches task)
           results_data = result.get("results", {})
           input_data = task.get("input_data", {})

           # If task had URL, result should reference same URL
           if "url" in input_data and "url" in results_data:
               return results_data["url"] == input_data["url"]

           return True
   ```

2. **Integrate into orchestrator** (1 hour):
   ```python
   # In orchestrator.py
   from ..communication.validator import OutputValidator

   class OrchestratorAgent:
       def __init__(self):
           # ... existing init ...
           self.validator = OutputValidator()

       async def _execute_single_task(self, task, campaign_id, store):
           # ... existing execution ...

           # Validate result
           is_valid, errors = self.validator.validate_all(
               result,
               task,
               quality_criteria=task.get("quality_criteria")
           )

           if not is_valid:
               self.logger.logger.warning(
                   f"Task {task['task_id']} failed validation: {errors}"
               )

               # Request revision
               revision_result = await self._request_revision(
                   task,
                   result,
                   errors,
                   campaign_id
               )

               return revision_result

           return result

       async def _request_revision(
           self,
           task: Dict,
           failed_result: Dict,
           validation_errors: List[str],
           campaign_id: str
       ) -> Dict:
           """Request agent to revise its output"""
           agent_name = task["agent"]
           agent = self.agents[agent_name]

           # Create revision task
           revision_task = task.copy()
           revision_task["task_id"] = f"{task['task_id']}_revision"
           revision_task["input_data"]["revision_feedback"] = {
               "original_result": failed_result,
               "errors": validation_errors,
               "required_changes": self._extract_required_changes(validation_errors)
           }

           # Execute revision
           self.logger.logger.info(f"Requesting revision from {agent_name}")
           revised_result = await agent.execute_with_timeout(revision_task)

           return revised_result

       def _extract_required_changes(self, errors: List[str]) -> List[str]:
           """Convert validation errors to actionable changes"""
           changes = []
           for error in errors:
               if "Missing required fields" in error:
                   changes.append("Include all required fields: status, agent, results, markdown_report")
               elif "quality criteria" in error:
                   changes.append("Ensure output meets agent-specific quality standards")
               elif "inconsistent" in error:
                   changes.append("Verify results align with task inputs")
           return changes
   ```

**Acceptance Criteria**:
- All 4 layers validate correctly
- Failed validation triggers revision request
- Can handle partial results
- Revision logic works

**Estimated Effort**: 3 hours

---

#### Task 4.2: Integration Testing (4 hours)

**Objective**: End-to-end orchestrator test with mock agents

**Subtasks**:

1. **Create test workflow** (2 hours):
   ```python
   # tests/integration/test_orchestrator.py
   import pytest
   import asyncio
   from src.agents.orchestrator import OrchestratorAgent
   from tests.mocks.mock_agents import (
       MockAuditorAgent,
       MockOptimizerAgent,
       MockResearcherAgent
   )

   @pytest.fixture
   def orchestrator():
       orch = OrchestratorAgent()
       orch.register_agent("auditor", MockAuditorAgent())
       orch.register_agent("optimizer", MockOptimizerAgent())
       orch.register_agent("researcher", MockResearcherAgent())
       return orch

   @pytest.mark.asyncio
   async def test_simple_workflow_no_dependencies(orchestrator):
       """Test workflow with 2 independent tasks"""
       tasks = [
           {
               "agent": "auditor",
               "task_type": "audit",
               "priority": 1,
               "depends_on": [],
               "input_data": {"url": "https://example.com"}
           },
           {
               "agent": "researcher",
               "task_type": "research",
               "priority": 1,
               "depends_on": [],
               "input_data": {"topic": "test"}
           }
       ]

       from src.persistence.campaign_store import CampaignStore
       store = CampaignStore()
       campaign_id = store.create_campaign(
           url="https://example.com",
           command="/test",
           options={}
       )

       result = await orchestrator.execute_workflow(tasks, campaign_id)

       assert result["status"] == "completed"
       assert "auditor" in result["agent_results"]
       assert "researcher" in result["agent_results"]
       assert result["agent_results"]["auditor"]["status"] == "success"

   @pytest.mark.asyncio
   async def test_workflow_with_dependencies(orchestrator):
       """Test workflow where optimizer depends on auditor"""
       tasks = [
           {
               "agent": "auditor",
               "task_type": "audit",
               "priority": 1,
               "depends_on": [],
               "input_data": {"url": "https://example.com"}
           },
           {
               "agent": "optimizer",
               "task_type": "optimize",
               "priority": 2,
               "depends_on": ["auditor"],
               "input_data": {"url": "https://example.com"}
           }
       ]

       from src.persistence.campaign_store import CampaignStore
       store = CampaignStore()
       campaign_id = store.create_campaign(
           url="https://example.com",
           command="/test",
           options={}
       )

       result = await orchestrator.execute_workflow(tasks, campaign_id)

       # Verify optimizer received auditor results
       assert "auditor_results" in tasks[1]["input_data"]
       assert result["status"] == "completed"

   @pytest.mark.asyncio
   async def test_parallel_execution(orchestrator):
       """Test that independent tasks execute in parallel"""
       import time

       start = time.time()

       tasks = [
           {"agent": "auditor", "priority": 1, "depends_on": [], "input_data": {}},
           {"agent": "researcher", "priority": 1, "depends_on": [], "input_data": {}}
       ]

       campaign_id = "test_parallel"
       await orchestrator.execute_workflow(tasks, campaign_id)

       duration = time.time() - start

       # Both mock agents sleep 0.5s, if parallel should be ~0.5s, not 1s
       assert duration < 0.7  # Some overhead allowed

   @pytest.mark.asyncio
   async def test_error_handling(orchestrator):
       """Test workflow continues despite one agent failing"""
       # Create failing mock agent
       from tests.mocks.mock_agents import FailingMockAgent
       orchestrator.register_agent("failer", FailingMockAgent())

       tasks = [
           {"agent": "auditor", "priority": 1, "depends_on": [], "input_data": {}},
           {"agent": "failer", "priority": 1, "depends_on": [], "input_data": {}},
           {"agent": "researcher", "priority": 2, "depends_on": [], "input_data": {}}
       ]

       campaign_id = "test_error"
       result = await orchestrator.execute_workflow(tasks, campaign_id)

       assert result["status"] == "failed"
       assert len(result["errors"]) > 0
       assert "researcher" in result["agent_results"]  # Should still execute non-dependent tasks
   ```

2. **Test decomposition** (1 hour):
   ```python
   def test_decompose_campaign(orchestrator):
       """Test campaign decomposition"""
       tasks = orchestrator.decompose_request(
           command="/aeo-campaign",
           params={"url": "https://example.com", "industry": "SaaS"}
       )

       assert len(tasks) == 5  # auditor, researcher, optimizer, tracker, reporter
       assert tasks[0]["agent"] == "auditor"
       assert tasks[0]["priority"] == 1
       assert tasks[2]["depends_on"] == ["auditor"]

   def test_decompose_compete(orchestrator):
       """Test competitive analysis decomposition"""
       tasks = orchestrator.decompose_request(
           command="/aeo-compete",
           params={"topic": "pm tools", "competitors": ["comp1.com", "comp2.com"]}
       )

       # Should have: 1 research + 2 audits + 1 report = 4 tasks
       assert len(tasks) == 4
   ```

3. **Test validation** (1 hour):
   ```python
   def test_output_validation():
       """Test 4-layer validation"""
       from src.communication.validator import OutputValidator

       validator = OutputValidator()

       # Valid result
       valid_result = {
           "status": "success",
           "agent": "auditor",
           "task_id": "test_001",
           "results": {"overall_score": 75},
           "markdown_report": "# Report"
       }

       valid_task = {
           "task_id": "test_001",
           "agent": "auditor",
           "input_data": {"url": "https://example.com"}
       }

       is_valid, errors = validator.validate_all(valid_result, valid_task)
       assert is_valid
       assert len(errors) == 0

       # Invalid result (missing fields)
       invalid_result = {
           "status": "success",
           "agent": "auditor"
       }

       is_valid, errors = validator.validate_all(invalid_result, valid_task)
       assert not is_valid
       assert len(errors) > 0
   ```

**Acceptance Criteria**:
- Orchestrator executes simple workflow end-to-end
- Parallel execution works (tasks run concurrently)
- Dependencies respected (optimizer waits for auditor)
- Errors handled gracefully (retry or continue)
- Data persisted to campaign store

**Estimated Effort**: 4 hours

---

#### Task 4.3: Sprint 1 Documentation (1 hour)

**Objective**: Document Sprint 1 progress

**Subtasks**:

1. **Update README.md** (20 min):
   ```markdown
   ## Sprint 1 Progress (✅ Complete)

   **Deliverables**:
   - ✅ Project structure created (agentic-aeo/)
   - ✅ Configuration system working
   - ✅ Structured logging (JSON output)
   - ✅ Communication protocol (Pydantic models)
   - ✅ Base agent class (with retry/timeout)
   - ✅ Data persistence (campaign store)
   - ✅ Orchestrator agent (task decomposition + workflow coordination)
   - ✅ 4-layer quality validation
   - ✅ Integration tests passing
   - ✅ Test coverage >80%

   **Demo**:
   ```python
   from src.agents.orchestrator import OrchestratorAgent
   from tests.mocks.mock_agents import MockAuditorAgent

   orch = OrchestratorAgent()
   orch.register_agent("auditor", MockAuditorAgent())

   tasks = orch.decompose_request("/aeo-campaign", {"url": "https://example.com"})
   result = await orch.execute_workflow(tasks, campaign_id="demo_001")
   ```
   ```

2. **Create architecture diagram** (20 min):
   ```markdown
   ## Sprint 1 Architecture

   ```
   Orchestrator Agent
   ├── Task Decomposition (/aeo-campaign → 5 tasks)
   ├── Dependency Resolution (topological sort)
   ├── Workflow Coordination (parallel + sequential execution)
   ├── Quality Validation (4 layers)
   └── Data Persistence (.aeo-agent-data/)

   Communication Protocol (JSON + Pydantic)
   ├── TaskMessage (orchestrator → agent)
   ├── TaskResult (agent → orchestrator)
   └── RevisionRequest (validation failed)

   Base Agent (abstract class)
   ├── execute_task() - abstract method
   ├── validate_input() - input validation
   ├── validate_output() - output validation
   ├── execute_with_retry() - retry logic
   └── execute_with_timeout() - timeout handling
   ```
   ```

3. **Document API** (20 min):
   - Document orchestrator methods
   - Document base agent interface
   - Document communication protocol

**Estimated Effort**: 1 hour

---

### Sprint 1 Summary

**Total Effort**: 32 hours (4 days × 8 hours)

**Completed Components**:
- ✅ Project infrastructure (directory structure, config, logging)
- ✅ Communication protocol (Pydantic models, message factory)
- ✅ Base agent class (retry, timeout, validation)
- ✅ Data persistence layer (campaign store, atomic writes)
- ✅ Orchestrator agent (decomposition, coordination, validation)
- ✅ Quality validation system (4 layers)
- ✅ Integration tests (>80% coverage)

**Key Files Created**:
```
agentic-aeo/
├── src/
│   ├── agents/
│   │   ├── base_agent.py (210 lines)
│   │   └── orchestrator.py (450 lines)
│   ├── communication/
│   │   ├── protocol.py (120 lines)
│   │   └── validator.py (180 lines)
│   ├── persistence/
│   │   └── campaign_store.py (250 lines)
│   ├── utils/
│   │   ├── config.py (60 lines)
│   │   └── logging.py (80 lines)
├── tests/
│   ├── unit/ (15 test files)
│   └── integration/ (5 test files)
├── requirements.txt
└── pyproject.toml
```

**Sprint 1 Demo**:
```python
# Can run this at end of Sprint 1
from src.agents.orchestrator import OrchestratorAgent
from tests.mocks.mock_agents import MockAuditorAgent

orchestrator = OrchestratorAgent()
orchestrator.register_agent("auditor", MockAuditorAgent())

tasks = orchestrator.decompose_request(
    command="/aeo-campaign",
    params={"url": "https://example.com"}
)

print(f"Decomposed into {len(tasks)} tasks")
# Output: Decomposed into 5 tasks

results = await orchestrator.execute_workflow(tasks, campaign_id="demo_001")
print(f"Workflow complete: {results['status']}")
# Output: Workflow complete: completed
```

---

## SPRINT 2: SPECIALIZED AGENTS (Days 5-8)

### Sprint Goal
**Implement all 6 specialized subagents that wrap AEO Skill modules**

### Definition of Done
- [x] All 6 agents implemented and tested
- [x] Each agent integrates with corresponding AEO Skill module
- [x] Agents communicate via standardized protocol
- [x] >80% test coverage for all agents
- [x] Integration test passes (all agents work together)

---

### Day 5: Auditor + Optimizer Agents (8 hours)

#### Task 5.1: Content Auditor Agent (3 hours)

**Objective**: Working auditor agent integrated with content_analyzer.py

**Implementation**:
```python
# src/agents/auditor.py
from .base_agent import BaseAgent
from typing import Dict, Any
import time
import requests
from bs4 import BeautifulSoup

# Import AEO Skill module
import sys
sys.path.insert(0, "../aeo_skill")
from ..aeo_skill.content_analyzer import ContentAnalyzer

class AuditorAgent(BaseAgent):
    """Content auditing agent - analyzes content for AEO signals"""

    def __init__(self):
        super().__init__(agent_type="auditor")
        self.analyzer = ContentAnalyzer()

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute content audit"""
        start_time = time.time()

        try:
            # Extract task parameters
            input_data = task["input_data"]
            url = input_data.get("url")
            competitors = input_data.get("competitors", [])
            context = input_data.get("context", {})

            # Fetch content
            content = self._fetch_content(url)
            if not content:
                return self._error_result(
                    task["task_id"],
                    f"Failed to fetch content from {url}"
                )

            # Run audit using AEO Skill
            audit_result = self.analyzer.analyze(
                content=content,
                url=url,
                competitor_urls=competitors
            )

            # Generate markdown report
            markdown = self._generate_markdown_report(audit_result, url)

            # Return standardized result
            execution_time = time.time() - start_time
            return self._success_result(
                task_id=task["task_id"],
                results=audit_result,
                markdown_report=markdown,
                execution_time=execution_time
            )

        except Exception as e:
            return self._error_result(task["task_id"], str(e))

    def _fetch_content(self, url: str) -> str:
        """Fetch content from URL"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Get text content
            text = soup.get_text()

            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)

            return text

        except requests.RequestException as e:
            self.logger.logger.error(f"Failed to fetch {url}: {e}")
            return ""

    def _generate_markdown_report(
        self,
        audit_result: Dict,
        url: str
    ) -> str:
        """Generate markdown audit report"""
        scores = audit_result.get("scores", {})
        overall = scores.get("overall", 0)

        report = f"""# Content Audit Report

**URL**: {url}
**Audit Date**: {audit_result.get('timestamp', 'N/A')}
**Overall AEO Score**: {overall}/100

---

## Score Breakdown

| Metric | Score | Status |
|--------|-------|--------|
| **E-E-A-T** | {scores.get('eeat', 0)}/100 | {self._score_status(scores.get('eeat', 0))} |
| **Structure** | {scores.get('structure', 0)}/100 | {self._score_status(scores.get('structure', 0))} |
| **Citations** | {scores.get('citations', 0)}/100 | {self._score_status(scores.get('citations', 0))} |
| **Readability** | {scores.get('readability', 0)}/100 | {self._score_status(scores.get('readability', 0))} |

---

## Critical Issues

"""
        # Add critical issues
        for issue in audit_result.get("critical_issues", []):
            report += f"- ⚠️ {issue}\n"

        report += "\n---\n\n## Recommendations\n\n"

        # Add recommendations
        for i, rec in enumerate(audit_result.get("recommendations", []), 1):
            report += f"{i}. {rec}\n"

        # Add competitor comparison if available
        if "competitor_comparison" in audit_result:
            comp = audit_result["competitor_comparison"]
            report += f"\n---\n\n## Competitive Benchmark\n\n"
            report += f"**Your Score**: {overall}/100  \n"
            report += f"**Average Competitor Score**: {comp.get('avg_score', 'N/A')}/100  \n"
            report += f"**Your Rank**: {comp.get('your_rank', 'N/A')} of {comp.get('total_analyzed', 'N/A')}\n"

        return report

    def _score_status(self, score: int) -> str:
        """Get status emoji for score"""
        if score >= 80:
            return "✅ Excellent"
        elif score >= 60:
            return "⚠️ Good"
        elif score >= 40:
            return "⚠️ Fair"
        else:
            return "❌ Poor"
```

**Testing**:
```python
# tests/unit/test_agents/test_auditor.py
import pytest
from src.agents.auditor import AuditorAgent

@pytest.mark.asyncio
async def test_auditor_executes_successfully():
    agent = AuditorAgent()
    task = {
        "task_id": "audit_001",
        "task_type": "audit_content",
        "input_data": {
            "url": "https://example.com",
            "context": {"industry": "SaaS"}
        }
    }

    result = await agent.execute_task(task)

    assert result["status"] == "success"
    assert "overall_score" in result["results"]
    assert result["results"]["overall_score"] >= 0
    assert result["results"]["overall_score"] <= 100

@pytest.mark.asyncio
async def test_auditor_handles_404():
    agent = AuditorAgent()
    task = {
        "task_id": "audit_002",
        "input_data": {"url": "https://example.com/404"}
    }

    result = await agent.execute_task(task)

    assert result["status"] == "failed"
    assert len(result["errors"]) > 0
```

**Acceptance Criteria**:
- Agent executes audit successfully
- Integrates with `content_analyzer.py`
- Returns standardized output
- Handles URLs that return 404
- Markdown report generated

**Estimated Effort**: 3 hours

---

#### Task 5.2: Content Optimizer Agent (3 hours)

**Objective**: Working optimizer agent integrated with optimizer.py

**Implementation**:
```python
# src/agents/optimizer.py
from .base_agent import BaseAgent
from typing import Dict, Any, List
import time
from ..aeo_skill.optimizer import ContentOptimizer

class OptimizerAgent(BaseAgent):
    """Content optimization agent - improves content for AEO"""

    def __init__(self):
        super().__init__(agent_type="optimizer")
        self.optimizer = ContentOptimizer()

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute content optimization"""
        start_time = time.time()

        try:
            input_data = task["input_data"]
            content = input_data.get("content")
            url = input_data.get("url")
            level = input_data.get("level", "balanced")
            audit_results = input_data.get("auditor_results", {})

            # Extract focus areas from audit
            focus_areas = self._extract_focus_areas(audit_results)

            # Run optimization
            opt_result = self.optimizer.optimize(
                content=content,
                level=level,
                focus_areas=focus_areas,
                preserve_voice=True
            )

            # Generate markdown report
            markdown = self._generate_optimization_report(
                opt_result,
                audit_results,
                url
            )

            execution_time = time.time() - start_time
            return self._success_result(
                task_id=task["task_id"],
                results=opt_result,
                markdown_report=markdown,
                execution_time=execution_time
            )

        except Exception as e:
            return self._error_result(task["task_id"], str(e))

    def _extract_focus_areas(self, audit_results: Dict) -> List[str]:
        """Determine what to focus on based on audit"""
        if not audit_results:
            return ["eeat", "structure", "citations"]

        scores = audit_results.get("results", {}).get("scores", {})
        focus = []

        if scores.get("eeat", 100) < 70:
            focus.append("eeat")
        if scores.get("structure", 100) < 70:
            focus.append("structure")
        if scores.get("citations", 100) < 70:
            focus.append("citations")
        if scores.get("readability", 100) < 70:
            focus.append("readability")

        return focus or ["general"]

    def _generate_optimization_report(
        self,
        opt_result: Dict,
        audit_results: Dict,
        url: str
    ) -> str:
        """Generate optimization report"""
        before_score = opt_result.get("before_score", 0)
        after_score = opt_result.get("after_score", 0)
        improvement = opt_result.get("improvement", 0)

        report = f"""# Content Optimization Report

**URL**: {url}
**Before Score**: {before_score}/100
**After Score**: {after_score}/100
**Improvement**: +{improvement} points ({(improvement/before_score*100) if before_score > 0 else 0:.1f}% increase)

---

## Changes Applied

"""
        for i, change in enumerate(opt_result.get("changes_applied", []), 1):
            report += f"{i}. {change}\n"

        report += f"""

---

## Before/After Comparison

| Metric | Before | After | Change |
|--------|--------|-------|--------|
"""
        # Add metric comparisons if available

        return report
```

**Testing**:
```python
@pytest.mark.asyncio
async def test_optimizer_with_audit_results():
    agent = OptimizerAgent()
    task = {
        "task_id": "opt_001",
        "input_data": {
            "content": "Original content...",
            "url": "https://example.com",
            "level": "balanced",
            "auditor_results": {
                "results": {
                    "scores": {"eeat": 50, "structure": 60}
                }
            }
        }
    }

    result = await agent.execute_task(task)

    assert result["status"] == "success"
    assert "after_score" in result["results"]
```

**Acceptance Criteria**:
- Uses audit results to guide optimization
- Preserves brand voice
- Shows improvement metrics
- Returns before/after comparison

**Estimated Effort**: 3 hours

---

#### Task 5.3: Unit Tests for Day 5 (2 hours)

**Test Coverage**:
- Auditor: valid URL, 404, timeout, competitor benchmarking
- Optimizer: different levels, with/without audit results, focus areas

**Estimated Effort**: 2 hours

---

### Day 6-8: Remaining Agents + Integration

Following the same pattern, implement:

**Day 6** (8h):
- Task 6.1: Citation Tracker Agent (3h) - integrates with citation_tracker.py
- Task 6.2: Query Researcher Agent (3h) - integrates with query_researcher.py
- Task 6.3: Unit Tests (2h)

**Day 7** (8h):
- Task 7.1: Report Generator Agent (2.5h) - integrates with report_generator.py
- Task 7.2: Learning Optimizer Agent (2.5h) - integrates with success_patterns.py
- Task 7.3: Agent Registration + Integration Tests (3h)

**Day 8** (8h):
- Task 8.1: Full Workflow Integration Test (4h) - test all 6 agents together
- Task 8.2: Documentation (2h) - AGENT_GUIDE.md, API docs
- Task 8.3: Code Review & Refactoring (2h)

---

## SPRINT 3: WORKFLOWS + INTERFACES (Days 9-11)

### Sprint Goal
**Build CLI, API, and workflow definitions for production use**

### Day 9: Workflow Definitions (8h)
- Campaign Workflow (3h)
- Competitive Workflow (3h)
- Monitoring Workflow (2h)

### Day 10: CLI Interface (8h)
- CLI Structure (2h)
- `/aeo-campaign` command (2h)
- `/aeo-compete` command (2h)
- `/aeo-monitor` command (2h)

### Day 11: REST API (8h)
- API Structure (2h)
- Campaign Endpoints (2h)
- Agent Status Endpoints (2h)
- API Documentation (2h)

---

## SPRINT 4: TESTING + PRODUCTION POLISH (Days 12-16)

### Sprint Goal
**Production-ready v1.5 release with >80% coverage**

### Day 12: E2E Testing (8h)
- Campaign Workflow E2E (3h)
- Competitive Workflow E2E (2h)
- Monitoring Workflow E2E (3h)

### Day 13: Error Handling (8h)
- Network Failure Handling (3h)
- Timeout Handling (2h)
- Graceful Degradation (3h)

### Day 14: Documentation (8h)
- README.md Complete (2h)
- ARCHITECTURE.md (2h)
- API_REFERENCE.md (2h)
- COST_OPTIMIZATION.md (2h)

### Days 15-16: Polish + Release (8-16h)
- Code Review (4h)
- Performance Optimization (3h)
- Final Testing (3h)
- Release Preparation (2h)
- Buffer (0-8h)

---

## Implementation Guidelines

### Code Quality Standards

1. **Type Hints**: All functions must have type hints
2. **Docstrings**: Google-style docstrings on all public APIs
3. **PEP 8**: Follow PEP 8 style guide (use Black formatter)
4. **Testing**: >80% coverage (unit + integration + E2E)
5. **Error Handling**: Comprehensive try/except with meaningful messages

### Testing Strategy

```python
# Unit Tests (test individual components)
tests/unit/
├── test_agents/        # Test each agent independently
├── test_workflows/     # Test workflow definitions
└── test_communication/ # Test protocol and validation

# Integration Tests (test agent coordination)
tests/integration/
├── test_orchestrator_coordination.py
└── test_agent_communication.py

# E2E Tests (test complete workflows)
tests/e2e/
├── test_full_campaign.py
├── test_competitive_analysis.py
└── test_monitoring.py
```

### Performance Targets

- **Campaign Workflow**: <5 minutes end-to-end
- **API Response Time**: <2 seconds for status checks
- **Memory Usage**: <1GB for full campaign
- **Concurrent Workflows**: Support 5+ parallel campaigns

---

## Definition of Done

### Sprint 1 (Foundation)
- [x] Orchestrator decomposes tasks correctly
- [x] Agents communicate via protocol
- [x] Data persists correctly
- [x] Mock agent works
- [x] >80% test coverage
- [x] Integration test passes

### Sprint 2 (Agents)
- [x] 6 agents implemented
- [x] AEO Skill integration working
- [x] Agents return standardized output
- [x] Full workflow executes
- [x] >80% test coverage
- [x] Agent documentation complete

### Sprint 3 (Workflows + Interfaces)
- [x] 3 workflows working
- [x] CLI functional
- [x] REST API functional
- [x] Auto-generated docs

### Sprint 4 (Production)
- [x] >80% test coverage
- [x] All documentation complete
- [x] Error handling comprehensive
- [x] Performance targets met
- [x] v1.5.0 released

---

## References

### Primary Specification
- **aeo-agentic-app-master-prompt.md** - Complete system specification (1,580 lines)

### Supporting Documentation
- **CLAUDE.md** - Development guidance and agent system overview
- **README.md** - Project overview and quick start
- **documentation/foundation/prd.md** - Product requirements
- **documentation/foundation/architecture.md** - System architecture

### Key Sections in Master Prompt
- Lines 23-84: System architecture
- Lines 94-441: 7 agent specifications
- Lines 444-555: 3 workflow definitions
- Lines 557-651: Communication protocol
- Lines 654-681: Data persistence
- Lines 740-875: Project structure
- Lines 883-992: Implementation requirements
- Lines 995-1082: Cost optimization
- Lines 1084-1168: Testing strategy
- Lines 1171-1221: Documentation requirements

---

## Next Steps

1. ✅ Sprint plan created and approved
2. → Begin Sprint 1, Day 1: Project scaffolding
3. → Follow task breakdown sequentially
4. → Update this document after each sprint
5. → Keep documentation/ as living structure

---

**Last Updated**: 2025-01-08
**Status**: Planning Complete - Ready for Sprint 1
**Next Action**: Create agentic-aeo/ directory structure

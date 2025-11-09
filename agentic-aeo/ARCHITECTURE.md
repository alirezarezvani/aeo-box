# AEO Multi-Agent System Architecture v1.5

**Last Updated**: 2025-11-09
**Version**: 1.5.0-dev
**Status**: Production-Ready Architecture

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Agent Architecture](#2-agent-architecture)
3. [Workflow Orchestration](#3-workflow-orchestration)
4. [Communication Protocol](#4-communication-protocol)
5. [Data Layer](#5-data-layer)
6. [API Architecture](#6-api-architecture)
7. [CLI Architecture](#7-cli-architecture)
8. [Quality & Testing](#8-quality--testing)
9. [Deployment Architecture](#9-deployment-architecture)
10. [Extension Points](#10-extension-points)

---

## 1. System Overview

### High-Level Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE LAYER                       │
├─────────────────────┬────────────────────┬───────────────────────┤
│  CLI (Click)        │  REST API (FastAPI)│  Future: Web UI       │
│  src/cli/           │  src/api/          │                       │
└─────────────────────┴────────────────────┴───────────────────────┘
                                │
                    ┌───────────▼────────────┐
                    │  ORCHESTRATOR AGENT    │
                    │  Coordination Layer    │
                    │  src/agents/           │
                    │  orchestrator_agent.py │
                    └───────────┬────────────┘
                                │
                ┌───────────────▼────────────────┐
                │  COMMUNICATION PROTOCOL       │
                │  JSON + Markdown Messages     │
                │  src/communication/protocol.py│
                └───────────────┬────────────────┘
                                │
    ┌───────────┬───────┬───────┼───────┬────────┬────────┐
    ▼           ▼       ▼       ▼       ▼        ▼        ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│Auditor │ │Optimizer│ │Tracker │ │Research│ │Reporter│ │Learning│
│ Agent  │ │  Agent  │ │ Agent  │ │ Agent  │ │ Agent  │ │ Agent  │
└────┬───┘ └───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘
     │         │          │          │          │          │
     └─────────┴──────────┼──────────┴──────────┴──────────┘
                          │
                 ┌────────▼──────────┐
                 │  AEO SKILL LAYER  │
                 │  Core Business     │
                 │  src/aeo_skill/    │
                 └────────┬──────────┘
                          │
                 ┌────────▼──────────┐
                 │  PERSISTENCE LAYER │
                 │  Local File System │
                 │  src/persistence/  │
                 └───────────────────┘
```

### Design Principles

1. **Local-First Architecture**: All data stored locally in `.aeo-agent-data/`
2. **Agent Autonomy**: Each agent is self-contained with specific responsibilities
3. **Graceful Degradation**: System works without external APIs using Claude built-ins
4. **Async-First**: All I/O operations are asynchronous for performance
5. **Type Safety**: Pydantic models ensure data integrity throughout

### Technology Stack

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Language** | Python | >=3.9 | Core implementation |
| **LLM SDK** | Anthropic | >=0.18.0 | Claude integration |
| **Web Framework** | FastAPI | >=0.109.0 | REST API server |
| **CLI Framework** | Click | >=8.1.0 | Command-line interface |
| **Validation** | Pydantic | >=2.0.0 | Data validation & serialization |
| **Async Server** | Uvicorn | >=0.27.0 | ASGI server |
| **Testing** | Pytest | >=7.4.0 | Test framework |
| **Code Quality** | Black/Ruff | Latest | Formatting & linting |

### Key Architectural Decisions

| Decision | Rationale | Impact |
|----------|-----------|--------|
| **Multi-agent over monolithic** | Separation of concerns, parallel execution | Higher complexity, better scalability |
| **Local storage over database** | Privacy, simplicity, no dependencies | Limited querying, file I/O overhead |
| **JSON/Markdown hybrid protocol** | Machine-readable + human-readable | Slightly larger messages, better debugging |
| **Async everywhere** | Non-blocking I/O, parallel agent execution | More complex code, better performance |
| **Pydantic for all data models** | Type safety, automatic validation | Slight overhead, fewer runtime errors |

---

## 2. Agent Architecture

### Orchestrator Agent

**File**: `src/agents/orchestrator_agent.py`
**Purpose**: Central coordinator for all workflow execution

```python
class OrchestratorAgent(BaseAgent):
    """
    Responsibilities:
    - Task decomposition
    - Agent routing
    - Parallel execution (up to 6 agents)
    - Dependency management
    - Quality validation
    - Revision handling
    """
```

**Key Methods**:
- `execute_workflow()`: Main entry point for workflow execution
- `_decompose_workflow()`: Breaks workflows into agent tasks
- `_execute_tasks_with_dependencies()`: Manages task execution order
- `_validate_output()`: 4-layer quality validation
- `_request_revision()`: Handles output improvement requests

### Base Agent Pattern

**File**: `src/agents/base_agent.py`
**Purpose**: Abstract base class providing common functionality

```python
class BaseAgent(ABC):
    """
    Provides:
    - Input validation
    - Retry logic with exponential backoff
    - Timeout handling (default: 300s)
    - Structured logging
    - Task result creation
    """

    @abstractmethod
    async def execute_task(self, task: TaskMessage) -> Dict[str, Any]:
        """Must be implemented by each specialized agent"""
```

### Specialized Agents

#### 1. Auditor Agent (`auditor_agent.py`)
- **Purpose**: Content analysis and E-E-A-T scoring
- **Integrates**: `aeo_skill.content_analyzer`
- **Key Features**:
  - Experience, Expertise, Authoritativeness, Trustworthiness scoring
  - Content structure analysis
  - Citation quality assessment
  - LLM optimization recommendations
- **Output**: Scores (0-100), analysis details, improvement recommendations

#### 2. Optimizer Agent (`optimizer_agent.py`)
- **Purpose**: AI-powered content improvements
- **Integrates**: `aeo_skill.optimizer`
- **Optimization Levels**:
  - **Conservative**: Minor improvements, preserve voice
  - **Balanced**: Moderate changes, enhance clarity
  - **Aggressive**: Major restructuring for maximum impact
- **Output**: Optimized content, change summary, improvement metrics

#### 3. Citation Tracker Agent (`citation_tracker_agent.py`)
- **Purpose**: Multi-LLM citation monitoring
- **Integrates**: `aeo_skill.citation_tracker`
- **Platforms Tracked**:
  - ChatGPT (GPT-4)
  - Claude (Anthropic)
  - Perplexity AI
  - Google Gemini
  - Mistral
  - Llama
- **Output**: Citation frequency, platform breakdown, trending analysis

#### 4. Researcher Agent (`researcher_agent.py`)
- **Purpose**: Query opportunity discovery
- **Integrates**: `aeo_skill.query_researcher`
- **Key Features**:
  - SERP analysis
  - Competitor identification
  - Query volume estimation
  - Content gap analysis
- **Output**: Target queries, competition metrics, opportunity scores

#### 5. Reporter Agent (`reporter_agent.py`)
- **Purpose**: Client-ready report generation
- **Integrates**: `aeo_skill.report_generator`
- **Report Types**:
  - Campaign reports (comprehensive analysis)
  - Competitive analysis reports
  - Monitoring reports (citation tracking)
- **Output**: Markdown reports, executive summaries, action items

#### 6. Learning Agent (`learning_agent.py`)
- **Purpose**: Adaptive pattern recognition
- **Integrates**: `aeo_skill.success_patterns`
- **Key Features**:
  - Success pattern identification
  - Strategy recommendations
  - Performance prediction
  - Optimization learning
- **Output**: Patterns identified, strategy recommendations, confidence scores

### Agent Lifecycle

```
1. Initialization
   └─> Load configuration
   └─> Initialize AEO Skill module
   └─> Setup logging

2. Task Reception
   └─> Receive TaskMessage from Orchestrator
   └─> Validate input data
   └─> Check dependencies

3. Execution
   └─> Execute core logic (with retries)
   └─> Handle timeouts (default: 300s)
   └─> Log progress

4. Result Return
   └─> Create TaskResult
   └─> Include metadata (timing, tokens)
   └─> Return to Orchestrator

5. Revision Handling (if requested)
   └─> Receive RevisionRequest
   └─> Re-execute with modifications
   └─> Return improved result
```

### Agent State Management

Each agent maintains:
- **Configuration**: From `utils.config`
- **Logger**: Structured logging with agent context
- **Retry State**: Current attempt count, backoff delay
- **Task Context**: Current task being executed

---

## 3. Workflow Orchestration

### Available Workflows

#### 1. Campaign Workflow (`campaign_workflow.py`)
**Command**: `/aeo-campaign`
**Purpose**: Complete end-to-end AEO optimization

**Task Decomposition**:
```
Priority 1 (Parallel):
├── Content Audit (Auditor Agent)
└── Query Research (Researcher Agent)

Priority 2 (Depends on Priority 1):
└── Content Optimization (Optimizer Agent)

Priority 3:
└── Citation Tracking Setup (Tracker Agent)

Priority 4:
└── Report Generation (Reporter Agent)

Priority 5:
└── Pattern Learning (Learning Agent)
```

#### 2. Competitive Analysis Workflow (`competitive_workflow.py`)
**Command**: `/aeo-compete`
**Purpose**: Analyze competitor AEO performance

**Task Decomposition**:
```
Priority 1 (Parallel for each competitor):
├── Competitor 1 Audit (Auditor Agent)
├── Competitor 2 Audit (Auditor Agent)
└── Competitor N Audit (Auditor Agent)

Priority 2:
└── Competitive Analysis (Researcher Agent)

Priority 3:
└── Opportunity Report (Reporter Agent)

Priority 4:
└── Strategy Learning (Learning Agent)
```

#### 3. Monitoring Workflow (`monitoring_workflow.py`)
**Command**: `/aeo-monitor`
**Purpose**: Track citation performance over time

**Task Decomposition**:
```
Priority 1:
└── Baseline Citation Check (Tracker Agent)

Priority 2 (Scheduled):
└── Periodic Citation Updates (Tracker Agent)

Priority 3:
└── Trend Analysis (Learning Agent)

Priority 4:
└── Performance Report (Reporter Agent)
```

### Task Decomposition Logic

```python
def _decompose_workflow(workflow_name: str, parameters: Dict) -> List[TaskMessage]:
    """
    Decomposition Strategy:
    1. Identify workflow type
    2. Create task list based on parameters
    3. Assign priorities (1-5)
    4. Define dependencies
    5. Set timeouts and deadlines
    6. Return ordered task list
    """
```

### Parallel vs Sequential Execution

**Parallel Execution Rules**:
- Maximum 6 agents simultaneously (configurable)
- Only tasks with same priority and no dependencies
- Resource-intensive agents (Auditor, Optimizer) limited to 3 parallel

**Sequential Requirements**:
- Tasks with explicit dependencies
- Tasks requiring previous task output
- Final reporting tasks

### Workflow State Machine

```
States:
┌──────────┐
│ PENDING  │ ──> Workflow created, not started
└────┬─────┘
     │
┌────▼─────────────┐
│ IN_PROGRESS      │ ──> Tasks executing
└────┬─────────────┘
     │
     ├──────────────┬────────────┬──────────────┐
     ▼              ▼            ▼              ▼
┌────────────┐ ┌────────────┐ ┌────────┐ ┌──────────┐
│ COMPLETED  │ │   FAILED   │ │CANCELED│ │REVISION  │
└────────────┘ └────────────┘ └────────┘ └──────────┘
```

---

## 4. Communication Protocol

### Message Format Specifications

**File**: `src/communication/protocol.py`

#### TaskMessage (Orchestrator → Agent)

```python
class TaskMessage(BaseModel):
    # Identification
    task_id: str              # Unique task identifier
    task_type: TaskType       # AUDIT_CONTENT, OPTIMIZE_CONTENT, etc.
    agent_type: AgentType     # Target agent
    campaign_id: str          # Parent campaign

    # Data
    input_data: Dict[str, Any]    # Task-specific input
    parameters: Dict[str, Any]    # Optional parameters

    # Dependencies
    dependencies: List[str]        # Task IDs that must complete first
    context: Dict[str, Any]        # Context from previous tasks

    # Metadata
    created_at: datetime
    timeout_seconds: Optional[int] = 300
    retry_count: int = 0
```

#### TaskResult (Agent → Orchestrator)

```python
class TaskResult(BaseModel):
    # Identification
    task_id: str
    status: TaskStatus        # COMPLETED, FAILED, etc.
    agent_type: AgentType

    # Output
    output_data: Dict[str, Any]      # Structured output
    output_markdown: Optional[str]    # Human-readable output

    # Metadata
    metadata: Dict[str, Any]          # Timing, tokens, etc.
    started_at: datetime
    completed_at: datetime

    # Error handling
    error_message: Optional[str]
    error_details: Optional[Dict]
```

### Task Assignment Protocol

```
1. Orchestrator creates TaskMessage
2. Validates agent availability
3. Sends message to agent queue
4. Agent acknowledges receipt
5. Agent processes task
6. Agent returns TaskResult
7. Orchestrator validates result
8. (Optional) Orchestrator requests revision
```

### Result Reporting Protocol

```
1. Agent completes task execution
2. Creates TaskResult with output
3. Includes execution metadata
4. Sends to Orchestrator
5. Orchestrator logs result
6. Orchestrator updates campaign state
7. Orchestrator checks for dependent tasks
8. Orchestrator triggers next tasks
```

### Error Handling and Retry Logic

**Retry Strategy**:
```python
retry_delay = base_delay * (2 ** attempt)  # Exponential backoff
max_retries = 3  # Configurable
max_delay = 60    # Cap at 60 seconds
```

**Error Propagation**:
1. Agent catches exception
2. Logs error with context
3. Creates TaskResult with FAILED status
4. Includes error details
5. Orchestrator decides retry/fail/continue

---

## 5. Data Layer

### Data Persistence Architecture

**Directory Structure**:
```
.aeo-agent-data/
├── campaigns/
│   └── campaign_20250109_123456_abc123/
│       ├── manifest.json           # Campaign metadata
│       ├── tasks.jsonl            # Task execution log
│       ├── results/               # Individual task results
│       │   ├── task_1.json
│       │   └── task_2.json
│       └── outputs/               # Generated outputs
│           ├── report.md
│           └── optimized_content.md
├── monitoring/
│   └── site_domain_com/
│       ├── baseline.json
│       └── updates/
│           └── 2025-01-09.json
└── cache/
    └── api_responses/
```

### Storage Formats

#### Campaign Manifest (`manifest.json`)
```json
{
  "campaign_id": "campaign_20250109_123456_abc123",
  "workflow_name": "aeo-campaign",
  "parameters": {...},
  "state": "completed",
  "created_at": "2025-01-09T12:34:56Z",
  "completed_at": "2025-01-09T13:04:56Z",
  "total_tasks": 6,
  "completed_tasks": 6,
  "failed_tasks": 0,
  "task_ids": [...],
  "summary": {...}
}
```

#### Task Result (`results/task_1.json`)
```json
{
  "task_id": "audit_20250109_123456",
  "agent_type": "auditor",
  "status": "completed",
  "output_data": {
    "scores": {...},
    "analysis": {...},
    "recommendations": [...]
  },
  "metadata": {
    "execution_time_seconds": 45.2,
    "tokens_used": 1500
  }
}
```

### Data Flow Through System

```
1. User Input
   └─> CLI/API parameters

2. Campaign Creation
   └─> Generate campaign_id
   └─> Create campaign directory
   └─> Save manifest.json

3. Task Execution
   └─> Read input data
   └─> Process with agent
   └─> Write to results/
   └─> Append to tasks.jsonl

4. Report Generation
   └─> Read all results
   └─> Generate report
   └─> Save to outputs/

5. User Access
   └─> Read from outputs/
   └─> Return to CLI/API
```

### State Management

**Campaign States**:
- `pending`: Created but not started
- `in_progress`: Tasks executing
- `completed`: All tasks successful
- `failed`: Critical failure occurred
- `canceled`: User canceled workflow

**Task States**:
- `pending`: Assigned to agent
- `in_progress`: Agent processing
- `completed`: Successfully finished
- `failed`: Error occurred
- `revision_requested`: Needs improvement
- `canceled`: Skipped or stopped

---

## 6. API Architecture

### FastAPI Implementation

**Main File**: `src/api/main.py`

```python
app = FastAPI(
    title="AEO Multi-Agent API",
    version="1.5.0",
    docs_url="/docs",      # Swagger UI
    redoc_url="/redoc"     # ReDoc UI
)
```

### Endpoint Organization

#### Root Endpoints
- `GET /` - API information
- `GET /health` - Health check

#### Campaign Endpoints (`src/api/routes/campaigns.py`)
- `POST /api/campaigns` - Create new campaign
- `POST /api/campaigns/compete` - Competitive analysis
- `POST /api/campaigns/monitor` - Start monitoring

#### Status Endpoints (`src/api/routes/status.py`)
- `GET /api/status/{campaign_id}` - Get campaign status
- `GET /api/status/{campaign_id}/results` - Get results
- `DELETE /api/campaigns/{campaign_id}` - Cancel campaign

### Request/Response Pipeline

```
1. Request Reception
   └─> FastAPI route handler
   └─> Pydantic model validation

2. Parameter Processing
   └─> Extract from request body
   └─> Apply defaults
   └─> Validate business rules

3. Workflow Execution
   └─> Create async task
   └─> Return workflow_id immediately

4. Background Processing
   └─> Orchestrator executes workflow
   └─> Updates stored in persistence

5. Status Polling
   └─> Client polls /status endpoint
   └─> Returns current state

6. Result Retrieval
   └─> Client gets final results
   └─> Cleanup if requested
```

### Error Handling Strategy

```python
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url)
        }
    )
```

**HTTP Status Codes**:
- `200`: Success
- `201`: Campaign created
- `400`: Invalid parameters
- `404`: Campaign not found
- `409`: Conflict (duplicate)
- `500`: Internal error
- `503`: Service unavailable

### CORS and Security

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # Configure for production
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"]
)
```

**Security Considerations**:
- API key authentication (planned)
- Rate limiting (planned)
- Input sanitization via Pydantic
- No direct file system access

---

## 7. CLI Architecture

### Click Framework Implementation

**Main File**: `src/cli/main.py`

```python
@click.group()
@click.version_option(version="1.5.0")
@click.option('--verbose', '-v', is_flag=True)
@click.option('--data-dir', default=".aeo-agent-data")
def cli(ctx, verbose, data_dir):
    """AEO Multi-Agent System"""
```

### Command Structure

```
aeo-agent
├── campaign      # Run AEO campaign
│   ├── --url     # Target URL
│   ├── --queries # Target queries
│   └── --mode    # minimal|balanced|comprehensive
├── compete       # Competitive analysis
│   ├── --query   # Target query
│   └── --urls    # Competitor URLs
└── monitor       # Citation monitoring
    ├── --url     # Target URL
    └── --duration # Days to monitor
```

### Parameter Validation

```python
@click.command()
@click.option('--url', required=True,
              help='URL to optimize')
@click.option('--mode',
              type=click.Choice(['minimal', 'balanced', 'comprehensive']),
              default='balanced')
def campaign(url, mode):
    # Validation logic
    if not url.startswith(('http://', 'https://')):
        raise click.BadParameter('URL must start with http:// or https://')
```

### Output Formatting

**Progress Display**:
```python
with click.progressbar(tasks, label='Processing') as bar:
    for task in bar:
        process_task(task)
```

**Result Display**:
```python
click.echo(click.style('✓ Campaign completed', fg='green'))
click.echo(f'Results saved to: {output_path}')
```

**Error Display**:
```python
click.echo(click.style('✗ Error occurred', fg='red'), err=True)
click.echo(f'Details: {error_message}', err=True)
```

---

## 8. Quality & Testing

### Testing Strategy

**Test Pyramid**:
```
        E2E Tests
         (5%)
      ╱         ╲
    Integration Tests
        (25%)
   ╱             ╲
    Unit Tests
      (70%)
```

### Test Organization

```
tests/
├── unit/                     # Component tests
│   ├── test_auditor_agent.py
│   ├── test_optimizer_agent.py
│   ├── test_workflows.py
│   └── test_api.py
├── integration/              # Multi-component tests
│   ├── test_orchestrator_integration.py
│   ├── test_workflow_integration.py
│   └── test_error_handling.py
├── e2e/                      # Full workflow tests
│   ├── test_full_campaign.py
│   ├── test_competitive_analysis.py
│   └── test_monitoring.py
└── mocks/                    # Test fixtures
    └── mock_agents.py
```

### Quality Validation Layers

#### Layer 1: Input Validation
- Pydantic models validate all inputs
- Type checking at boundaries
- Business rule validation

#### Layer 2: Unit Testing
- Each agent tested independently
- Mock external dependencies
- Test coverage >80%

#### Layer 3: Integration Testing
- Agent communication tested
- Workflow orchestration validated
- Error scenarios covered

#### Layer 4: E2E Testing
- Complete workflows tested
- Real data processing
- Performance benchmarks

### Coverage Approach

**Current Coverage**: >80%

```bash
# Run with coverage
pytest --cov=src --cov-report=html

# Coverage by module
src/agents/: 85%
src/workflows/: 82%
src/communication/: 90%
src/persistence/: 78%
src/api/: 75%
src/cli/: 70%
```

### Performance Considerations

**Benchmarks**:
- Campaign workflow: 15-30 minutes (comprehensive)
- Competitive analysis: 10-20 minutes (5 competitors)
- Monitoring update: 2-5 minutes

**Optimization Strategies**:
- Prompt caching (90% cost reduction)
- Request batching
- Parallel agent execution
- Async I/O throughout

---

## 9. Deployment Architecture

### Local-First Design

**Installation**:
```bash
pip install -r requirements.txt
cp .env.example .env
# Add ANTHROPIC_API_KEY to .env
```

**Execution Modes**:
1. **CLI Mode**: Direct command execution
2. **API Mode**: REST server (uvicorn)
3. **Scheduled Mode**: Cron-based monitoring (planned)

### Data Directory Structure

```
.aeo-agent-data/
├── config.json           # User configuration
├── campaigns/            # Campaign data
├── monitoring/          # Monitoring data
├── cache/               # API response cache
└── logs/                # Application logs
```

### Dependencies and Requirements

**Python Dependencies** (`requirements.txt`):
```
anthropic>=0.18.0      # Claude SDK
pydantic>=2.0.0        # Data validation
python-dotenv>=1.0.0   # Environment variables
fastapi>=0.109.0       # REST API
uvicorn>=0.27.0        # ASGI server
click>=8.1.0           # CLI framework
aiofiles>=23.2.0       # Async file I/O
httpx>=0.26.0          # HTTP client
```

**System Requirements**:
- Python 3.9+
- 4GB RAM minimum
- 1GB disk space
- Internet connection (for API calls)

### Scalability Considerations

**Horizontal Scaling** (Future):
- Multiple orchestrator instances
- Task queue (Redis/RabbitMQ)
- Distributed agents

**Vertical Scaling** (Current):
- Increase parallel agents (max 6)
- Increase timeout limits
- Optimize prompt caching

**Performance Limits**:
- Max 6 parallel agents
- Max 200K token context
- Max 1 hour workflow timeout

---

## 10. Extension Points

### How to Add New Agents

1. **Create Agent Class** (`src/agents/new_agent.py`):
```python
from .base_agent import BaseAgent
from ..communication.protocol import AgentType

class NewAgent(BaseAgent):
    def __init__(self):
        super().__init__(AgentType.NEW_TYPE)

    async def execute_task(self, task: TaskMessage) -> Dict[str, Any]:
        # Implementation
        return {"result": "data"}
```

2. **Register Agent Type** (`src/communication/protocol.py`):
```python
class AgentType(str, Enum):
    # ... existing types ...
    NEW_TYPE = "new_type"
```

3. **Add to Orchestrator** (`src/agents/orchestrator_agent.py`):
```python
# In __init__ or register_agent method
self.agent_registry[AgentType.NEW_TYPE] = NewAgent()
```

### How to Create New Workflows

1. **Create Workflow Class** (`src/workflows/new_workflow.py`):
```python
class NewWorkflow:
    def decompose(self, **params) -> List[TaskMessage]:
        tasks = []
        # Create task messages
        return tasks
```

2. **Register in Orchestrator**:
```python
WORKFLOW_REGISTRY = {
    "new-workflow": NewWorkflow
}
```

3. **Add CLI Command** (`src/cli/commands/new_command.py`):
```python
@click.command()
def new_command():
    # Implementation
```

### How to Extend the API

1. **Create Route Module** (`src/api/routes/new_route.py`):
```python
from fastapi import APIRouter

router = APIRouter(prefix="/api/new", tags=["new"])

@router.post("/endpoint")
async def new_endpoint(params: RequestModel):
    # Implementation
    return ResponseModel()
```

2. **Register Route** (`src/api/main.py`):
```python
from .routes import new_route
app.include_router(new_route.router)
```

### Plugin Architecture (Future)

**Planned Extension System**:
```python
# plugins/my_plugin/
├── __init__.py
├── agent.py         # Custom agent
├── workflow.py      # Custom workflow
└── config.yaml      # Plugin metadata
```

**Plugin Loading**:
```python
def load_plugins(plugin_dir: Path):
    for plugin_path in plugin_dir.glob("*/config.yaml"):
        config = load_yaml(plugin_path)
        module = import_module(config["module"])
        register_plugin(module)
```

---

## Configuration Reference

### Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...

# Optional - Claude Configuration
ENABLE_PROMPT_CACHING=true      # 90% cost savings
ENABLE_EXTENDED_CONTEXT=true    # 200K tokens
ENABLE_REQUEST_BATCHING=true    # Batch API calls

# Optional - Agent Configuration
MAX_PARALLEL_AGENTS=6            # 1-6 agents
AGENT_TIMEOUT_SECONDS=300        # 30-3600 seconds
AGENT_MAX_RETRIES=3              # 0-10 retries
AGENT_RETRY_DELAY_SECONDS=2      # 1-60 seconds

# Optional - Data Configuration
DATA_DIR=.aeo-agent-data         # Storage location
ENABLE_DATA_COMPRESSION=false    # Compress JSON
CAMPAIGN_RETENTION_DAYS=90       # Auto-cleanup

# Optional - API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=1
API_RELOAD=false
```

### Configuration Objects

**Config Loading** (`src/utils/config.py`):
```python
config = get_config()
config.claude.api_key
config.agent.max_parallel_agents
config.data.data_dir
```

---

## Performance Metrics

### System Benchmarks

| Workflow | Minimal Mode | Balanced Mode | Comprehensive Mode |
|----------|-------------|---------------|-------------------|
| **Campaign** | 5-10 min | 15-30 min | 45-90 min |
| **Competitive** (5 URLs) | 10 min | 20 min | 40 min |
| **Monitoring** (Update) | 2 min | 5 min | 10 min |

### Resource Usage

| Component | CPU Usage | Memory Usage | Network I/O |
|-----------|-----------|--------------|-------------|
| **Orchestrator** | Low | 50-100 MB | Minimal |
| **Auditor Agent** | Medium | 100-200 MB | API calls |
| **Optimizer Agent** | High | 200-500 MB | API calls |
| **Tracker Agent** | Low | 50-100 MB | API calls |
| **Full System** | Medium | 500MB-1GB | Variable |

### Cost Optimization

**Strategies Implemented**:
1. **Prompt Caching**: 90% reduction in API costs
2. **Request Batching**: Combine multiple calls
3. **Local Processing**: Use Claude built-ins when possible
4. **Smart Retries**: Exponential backoff prevents waste

**Estimated Costs** (per workflow):
- Campaign: $0.10-$0.50
- Competitive: $0.20-$0.80
- Monitoring: $0.05-$0.20

---

## Monitoring & Observability

### Logging Architecture

**Structured Logging** (`src/utils/logging.py`):
```python
logger = StructuredLogger(
    name="agent.auditor",
    agent_type="auditor"
)
logger.info("Task started",
    task_id=task_id,
    campaign_id=campaign_id
)
```

**Log Levels**:
- `DEBUG`: Detailed execution flow
- `INFO`: Normal operations
- `WARNING`: Recoverable issues
- `ERROR`: Failures requiring attention

### Metrics Collection (Future)

**Planned Metrics**:
- Task execution times
- Agent success rates
- API token usage
- Error frequencies
- Workflow completion rates

---

## Security Considerations

### Current Security Measures

1. **Input Validation**: Pydantic models validate all inputs
2. **Local Storage**: No external data transmission by default
3. **API Key Protection**: Environment variables, never logged
4. **Error Sanitization**: Sensitive data removed from errors

### Future Security Enhancements

1. **API Authentication**: JWT tokens for API access
2. **Rate Limiting**: Prevent abuse
3. **Encryption**: Encrypt sensitive stored data
4. **Audit Logging**: Track all operations
5. **Sandboxing**: Isolate agent execution

---

## Troubleshooting Guide

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| **Agent timeout** | Long-running task | Increase `AGENT_TIMEOUT_SECONDS` |
| **Rate limit errors** | Too many API calls | Enable batching, add delays |
| **Memory issues** | Large content processing | Process in chunks |
| **File not found** | Missing data directory | Run with `--data-dir` option |
| **API key invalid** | Missing/wrong key | Check `.env` file |

### Debug Mode

```bash
# Enable verbose logging
export LOG_LEVEL=DEBUG
aeo-agent campaign --url https://example.com --verbose

# Check logs
tail -f .aeo-agent-data/logs/aeo-agent.log
```

---

## Version History

| Version | Date | Major Changes |
|---------|------|---------------|
| **1.5.0-dev** | 2025-01-09 | Current development version |
| **1.0.0** | (Planned) | Production release |

---

## License

MIT License - See LICENSE file for details.

---

**End of Document**

*This architecture document represents the complete technical design of the AEO Multi-Agent System v1.5. For implementation details, refer to the source code in the respective modules.*
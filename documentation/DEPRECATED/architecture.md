# AEO Box System Architecture

**Version**: 1.0
**Date**: 2025-11-08
**Status**: Active Development

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture Principles](#architecture-principles)
3. [System Components](#system-components)
4. [Component Details](#component-details)
5. [Data Architecture](#data-architecture)
6. [Communication Protocol](#communication-protocol)
7. [API Design](#api-design)
8. [CLI Design](#cli-design)
9. [Deployment Architecture](#deployment-architecture)
10. [Scalability](#scalability)
11. [Security Architecture](#security-architecture)
12. [Error Handling](#error-handling)
13. [Monitoring & Logging](#monitoring--logging)
14. [Cost Optimization](#cost-optimization)
15. [Technology Stack](#technology-stack)

---

## Overview

###

 Architecture Type

**Multi-Agent Orchestration System** with hybrid deployment (CLI + Web API)

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                      │
├──────────────┬─────────────────────────────────┬─────────────┤
│  CLI Client  │       Web API (FastAPI)         │  Slash Cmds │
│   (Click)    │     REST + WebSocket            │  (.claude/) │
└──────────────┴──────────────┬──────────────────┴─────────────┘
                               │
                               ▼
         ┌────────────────────────────────────────────┐
         │      ORCHESTRATOR AGENT (Main Agent)       │
         │  - Task Decomposition                      │
         │  - Workflow Coordination                   │
         │  - Quality Validation (4-layer)            │
         │  - Executive Reporting                     │
         └────────────────────────────────────────────┘
                               │
         ┌─────────────────────┴─────────────────────┐
         │        AGENT COMMUNICATION LAYER          │
         │      (JSON + Markdown Hybrid Protocol)    │
         └─────────────────────┬─────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
┌───────────────┐      ┌───────────────┐     ┌──────────────┐
│   Auditor     │      │   Optimizer   │     │   Tracker    │
│    Agent      │      │     Agent     │     │    Agent     │
└───────────────┘      └───────────────┘     └──────────────┘
        │                      │                      │
        ▼                      ▼                      ▼
┌───────────────┐      ┌───────────────┐     ┌──────────────┐
│  Researcher   │      │   Reporter    │     │   Learning   │
│    Agent      │      │     Agent     │     │    Agent     │
└───────────────┘      └───────────────┘     └──────────────┘
        │                      │                      │
        └──────────────────────┼──────────────────────┘
                               │
                               ▼
              ┌───────────────────────────────────┐
              │    AEO SKILL (Python Modules)    │
              │  - content_analyzer.py           │
              │  - optimizer.py                  │
              │  - citation_tracker.py           │
              │  - query_researcher.py           │
              │  - report_generator.py           │
              │  - success_patterns.py           │
              │  - api_manager.py                │
              │  - utils.py                      │
              └───────────────────────────────────┘
                               │
                               ▼
              ┌────────────────────────────────┐
              │    DATA PERSISTENCE LAYER      │
              │  - .aeo-data/ (Skill data)     │
              │  - .aeo-agent-data/ (Agents)   │
              └────────────────────────────────┘
```

### Architecture Patterns

- **Multi-Agent Pattern**: Orchestrator coordinates specialized agents
- **Command Pattern**: CLI commands trigger workflow execution
- **Repository Pattern**: Data persistence abstracted from business logic
- **Strategy Pattern**: Multiple optimization strategies (conservative/balanced/aggressive)
- **Observer Pattern**: Citation monitoring with notification system (future)

---

## Architecture Principles

### 1. Local-First

**Principle**: All user data stays on the user's machine by default.

**Rationale**:
- Privacy guarantee (no external data transmission)
- Works offline
- No vendor lock-in
- User owns their data

**Implementation**:
- Data stored in `.aeo-data/` and `.aeo-agent-data/`
- API calls opt-in only
- Telemetry disabled by default

---

### 2. Graceful Degradation

**Principle**: Core features work without paid external APIs.

**Rationale**:
- Cost-effective for budget-conscious users
- Resilient to API outages
- No hard dependencies on third-party services

**Implementation**:
```python
# Example: Citation tracker
if api_key_exists:
    use_external_api()
else:
    use_claude_builtin_capabilities()  # Fallback
```

---

### 3. Modularity

**Principle**: Each component is independently replaceable.

**Rationale**:
- Easy to test
- Easy to extend
- Technology agnostic (can swap out LLMs, storage, etc.)

**Implementation**:
- AEO Skill modules are self-contained
- Agents are wrappers (decoupled from core logic)
- Data layer abstracted via repository pattern

---

### 4. Fail-Safe Defaults

**Principle**: Default configuration minimizes risk of errors.

**Rationale**:
- Beginner-friendly
- Production-safe out of the box
- Prevents accidental data loss or API overspending

**Implementation**:
- Conservative optimization level by default
- Rate limiting enabled by default
- Auto-retry with exponential backoff
- Data retention configurable (default: 90 days)

---

### 5. Observable

**Principle**: System behavior is transparent and debuggable.

**Rationale**:
- Easy troubleshooting
- Performance monitoring
- User trust (know what's happening)

**Implementation**:
- Structured logging (DEBUG, INFO, WARNING, ERROR)
- Progress indicators during long operations
- Detailed error messages with suggestions

---

## System Components

### Component Overview

| Component | Type | Status | Description |
|-----------|------|--------|-------------|
| **AEO Skill** | Core Library | ✅ Implemented | Python modules for AEO analysis |
| **Orchestrator Agent** | Coordinator | 🚧 Planned | Main agent coordinating workflows |
| **6 Specialized Agents** | Workers | 🚧 Planned | Auditor, Optimizer, Tracker, Researcher, Reporter, Learning |
| **CLI Interface** | User Interface | 🚧 Planned | Click-based terminal application |
| **REST API** | User Interface | 🚧 Planned | FastAPI web API |
| **Data Persistence** | Storage | ✅ Implemented | Local file system (JSON, CSV) |
| **Communication Layer** | Messaging | 🚧 Planned | JSON + Markdown hybrid protocol |

---

## Component Details

### 1. AEO Skill (Python Modules)

**Location**: `answer-engine-optimization/modules/`

**Architecture**: Modular, self-contained Python modules

#### 1.1 content_analyzer.py

**Purpose**: Comprehensive content auditing for AEO signals

**Public Interface**:
```python
class ContentAnalyzer:
    def analyze(
        self,
        content: str,
        url: Optional[str] = None,
        competitor_urls: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Returns:
        {
            "timestamp": "2025-01-07T10:30:00Z",
            "url": "https://example.com",
            "scores": {
                "overall": 75,      # 0-100
                "eeat": 68,         # Experience, Expertise, Authoritativeness, Trust
                "structure": 82,    # Headings, lists, tables
                "citations": 70,    # Authoritative source linking
                "readability": 75   # Flesch-Kincaid, etc.
            },
            "recommendations": [
                {
                    "type": "add_structure",
                    "priority": "high",
                    "description": "Add H2 subheadings for better content chunking"
                },
                ...
            ],
            "competitor_comparison": {...}
        }
        """
```

**Dependencies**:
- Python stdlib (no required external deps)
- Optional: `anthropic` (for enhanced analysis via Claude API)
- Optional: `ahrefs`, `semrush` APIs (for competitor benchmarking)

**Performance**:
- Target: <2 min for 5000-word article
- Actual: ~1-1.5 min (measured)

**Data Storage**:
- `.aeo-data/projects/{PROJECT_NAME}/audit_history.csv`

---

#### 1.2 optimizer.py

**Purpose**: AI-powered content optimization

**Public Interface**:
```python
class ContentOptimizer:
    def optimize(
        self,
        content: str,
        level: Literal["conservative", "balanced", "aggressive"] = "balanced",
        focus_areas: Optional[List[str]] = None,
        preserve_sections: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Returns:
        {
            "optimized_content": "...",
            "change_log": [
                {
                    "type": "add_structure",
                    "line": 15,
                    "before": "...",
                    "after": "...",
                    "rationale": "Improved LLM parsing"
                },
                ...
            ],
            "metrics": {
                "before_score": 65,
                "after_score": 78,
                "improvement": 13
            }
        }
        """
```

**Optimization Strategies**:
- `add_structure`: Add headings, lists, tables
- `add_citations`: Link to authoritative sources
- `enhance_eeat`: Add author credentials, data points
- `add_data_points`: Statistics, research findings
- `improve_chunking`: Break into paragraph-per-idea

**Optimization Levels**:
- **Conservative** (60-70 score): Minimal changes, preserve voice heavily
- **Balanced** (70-80 score): Moderate improvements (default)
- **Aggressive** (80-90+ score): Maximum optimization, may alter voice

**Dependencies**:
- `anthropic` (Claude API for content generation)

**Performance**:
- Target: <3 min for 5000-word article
- Actual: ~2-2.5 min (measured)

**Data Storage**:
- `.aeo-data/projects/{PROJECT_NAME}/optimization_log.json`

---

#### 1.3 citation_tracker.py

**Purpose**: Monitor citations across multiple LLMs

**Public Interface**:
```python
class CitationTracker:
    def track(
        self,
        url: str,
        queries: List[str],
        llms: List[str] = ["chatgpt", "perplexity", "claude", "gemini", "mistral"]
    ) -> Dict[str, Any]:
        """
        Returns:
        {
            "url": "https://example.com",
            "timestamp": "2025-01-07T10:30:00Z",
            "citations": [
                {
                    "llm": "chatgpt",
                    "query": "What is AEO?",
                    "cited": true,
                    "position": 2,  # Position in response
                    "context": "According to [source], AEO is..."
                },
                ...
            ],
            "summary": {
                "total_queries": 10,
                "total_citations": 7,
                "citation_rate": 0.7
            }
        }
        """
```

**Tracking Frequency**:
- Daily checks (configurable)
- On-demand via API/CLI

**Supported LLMs**:
1. ChatGPT (OpenAI)
2. Perplexity
3. Claude (Anthropic)
4. Gemini (Google)
5. Mistral

**Dependencies**:
- `anthropic` (for Claude integration)
- `openai` (for ChatGPT access - optional)
- HTTP libraries for Perplexity, Gemini, Mistral APIs

**Performance**:
- Target: <30 sec per LLM
- Actual: ~20-25 sec (network latency)

**Data Storage**:
- `.aeo-data/projects/{PROJECT_NAME}/citation_tracking.csv`

---

#### 1.4 query_researcher.py

**Purpose**: Discover high-value query opportunities

**Public Interface**:
```python
class QueryResearcher:
    def research(
        self,
        topic: str,
        competitor_urls: Optional[List[str]] = None,
        industry: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Returns:
        {
            "topic": "Answer Engine Optimization",
            "target_queries": [
                {
                    "query": "What is AEO?",
                    "citation_potential": 0.85,  # 0-1
                    "competition": "medium",
                    "current_citations": 12,  # Competitors being cited
                    "content_gap": true  # Opportunity for you
                },
                ...
            ],
            "competitor_analysis": [...]
        }
        """
```

**Research Methods**:
1. LLM query generation (Claude-powered)
2. Competitor URL analysis (Ahrefs/SEMrush optional)
3. Content gap identification

**Dependencies**:
- `anthropic` (Claude API)
- Optional: `ahrefs`, `semrush` (for competitor data)

**Performance**:
- Target: <2 min for 10 competitor URLs
- Actual: ~1.5 min

**Data Storage**:
- `.aeo-data/projects/{PROJECT_NAME}/query_research.json`

---

#### 1.5 report_generator.py

**Purpose**: Generate client-ready reports

**Public Interface**:
```python
class ReportGenerator:
    def generate(
        self,
        audit_results: Dict,
        optimization_results: Optional[Dict] = None,
        citation_data: Optional[Dict] = None,
        template: str = "default"
    ) -> str:
        """
        Returns: Markdown report
        """
```

**Report Types**:
1. **Executive Summary** - High-level overview for stakeholders
2. **Full Audit Report** - Detailed analysis and recommendations
3. **Optimization Report** - Before/after comparison
4. **Citation Performance** - Trend analysis
5. **Competitive Analysis** - Benchmark against competitors

**Output Formats**:
- Markdown (current)
- PDF (future via pandoc or weasyprint)

**Dependencies**:
- Python stdlib
- Future: `pandoc` or `weasyprint` for PDF generation

**Performance**:
- Target: <1 min
- Actual: <30 sec

---

#### 1.6 success_patterns.py

**Purpose**: Adaptive learning from successful optimizations

**Public Interface**:
```python
class SuccessPatternLearner:
    def learn(
        self,
        optimization_result: Dict,
        citation_performance: Dict,
        industry: Optional[str] = None
    ) -> None:
        """
        Updates success pattern library
        """

    def get_recommendations(
        self,
        content_type: str,
        industry: Optional[str] = None
    ) -> List[Dict]:
        """
        Returns learned patterns for similar content
        """
```

**Learning Approach**:
1. Track optimization → citation correlation
2. Build industry-specific pattern library
3. Identify high-performing strategies
4. Recommend based on historical success

**Privacy**:
- Local storage by default (`.aeo-data/success_patterns.json`)
- Opt-in anonymized sharing for community patterns

**Dependencies**:
- Python stdlib

**Data Storage**:
- `.aeo-data/success_patterns.json` (~1MB max)

---

#### 1.7 api_manager.py

**Purpose**: Manage external API integrations

**Public Interface**:
```python
class APIManager:
    def call_api(
        self,
        api_name: str,  # "ahrefs", "semrush", "openai"
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Handles rate limiting, retries, graceful degradation
        """
```

**Supported APIs**:
- Ahrefs (SEO data)
- SEMrush (competitor analysis)
- OpenAI (ChatGPT access)
- Anthropic (Claude API)
- Google (Gemini access)

**Features**:
- Auto rate limiting
- Exponential backoff retry (3x)
- Graceful degradation (fallback to local capabilities)
- API key management (encrypted storage)

**Dependencies**:
- `requests`
- Platform keychain integration (macOS Keychain, Windows Credential Manager, Linux Secret Service)

---

#### 1.8 utils.py

**Purpose**: Shared utilities

**Functions**:
```python
def parse_markdown(content: str) -> Dict[str, Any]:
    """Parse markdown into structured data"""

def calculate_readability(text: str) -> Dict[str, float]:
    """Flesch-Kincaid, Gunning Fog, etc."""

def extract_entities(text: str) -> List[str]:
    """Extract named entities (people, places, organizations)"""

def chunk_content(text: str, max_tokens: int = 1000) -> List[str]:
    """Split content into LLM-friendly chunks"""
```

**Dependencies**:
- Python stdlib
- Optional: `nltk` (for advanced readability metrics)

---

### 2. Multi-Agent System (Planned)

**Architecture**: Orchestrator + 6 Specialized Subagents

#### 2.1 Orchestrator Agent

**Responsibilities**:

1. **Task Decomposition**
   - Parse user requests (CLI/API)
   - Break into discrete subtasks
   - Determine optimal agent assignment

2. **Workflow Coordination**
   - Execute agents in correct order
   - Pass results between agents
   - Handle dependencies

3. **Quality Validation**
   - 4-layer validation:
     1. Status check (success/failed/partial)
     2. Completeness check (all required fields present)
     3. Quality criteria (agent-specific validation)
     4. Consistency check (results align with inputs)

4. **Executive Reporting**
   - Synthesize subagent outputs
   - Generate human-readable summaries
   - Provide actionable next steps

**Technology**:
- Claude Agent SDK (Python)
- asyncio for concurrent agent execution

**Message Flow**:
```
User → Orchestrator → [Parallel: Auditor, Researcher]
                    → Optimizer (depends on Auditor)
                    → Reporter (depends on all)
                    → Learning (background)
     ← Orchestrator ← Final Report
```

---

#### 2.2 Specialized Subagents

**Agent Architecture** (Wrapper Pattern):

Each agent wraps a specific AEO Skill module:

```python
class AuditorAgent(BaseAgent):
    def execute(self, task: Dict) -> Dict:
        # 1. Validate input
        # 2. Call content_analyzer.py
        analyzer = ContentAnalyzer()
        result = analyzer.analyze(...)
        # 3. Format output (JSON + Markdown)
        # 4. Validate output
        return {
            "status": "success",
            "data": result,
            "markdown_summary": "# Audit Complete\n\n..."
        }
```

**6 Specialized Agents**:

1. **Auditor Agent** → `content_analyzer.py`
2. **Optimizer Agent** → `optimizer.py`
3. **Tracker Agent** → `citation_tracker.py`
4. **Researcher Agent** → `query_researcher.py`
5. **Reporter Agent** → `report_generator.py`
6. **Learning Agent** → `success_patterns.py`

**Shared Base Class**:
```python
class BaseAgent:
    def execute(self, task: Dict) -> Dict:
        raise NotImplementedError

    def validate_input(self, task: Dict) -> bool:
        """Ensure task has required fields"""

    def validate_output(self, result: Dict) -> bool:
        """Check result completeness and quality"""
```

---

## Data Architecture

### Data Storage Structure

```
.aeo-data/                              # AEO Skill data
├── projects/
│   ├── example-com/
│   │   ├── config.json                 # Project settings
│   │   ├── audit_history.csv           # Historical audits
│   │   ├── optimization_log.json       # Optimization changes
│   │   └── citation_tracking.csv       # Citation data
│   └── another-project/
│       └── ...
├── success_patterns.json               # Adaptive learning
└── config.json                         # Global settings

.aeo-agent-data/                        # Multi-agent data
├── campaigns/
│   ├── camp_20250107_001/
│   │   ├── metadata.json               # Campaign info
│   │   ├── orchestrator_log.json       # Orchestrator decisions
│   │   ├── agent_outputs/
│   │   │   ├── auditor.json
│   │   │   ├── optimizer.json
│   │   │   └── ...
│   │   └── final_report.md
│   └── ...
├── workflows/
│   └── workflow_definitions.json       # Custom workflow templates
└── monitoring/
    └── citation_schedules.json         # Scheduled checks
```

### Data Models

#### Audit Report Schema
```json
{
  "timestamp": "2025-01-07T10:30:00Z",
  "url": "https://example.com/article",
  "scores": {
    "overall": 75,
    "eeat": 68,
    "structure": 82,
    "citations": 70,
    "readability": 75
  },
  "recommendations": [
    {
      "type": "add_structure",
      "priority": "high",
      "description": "Add H2 subheadings",
      "expected_impact": "+5 points"
    }
  ],
  "competitor_comparison": {
    "avg_score": 72,
    "your_rank": 3,
    "top_performers": [...]
  }
}
```

#### Optimization Result Schema
```json
{
  "timestamp": "2025-01-07T10:35:00Z",
  "url": "https://example.com/article",
  "level": "balanced",
  "optimized_content": "...",
  "change_log": [
    {
      "type": "add_structure",
      "line": 15,
      "before": "Original text...",
      "after": "Optimized text...",
      "rationale": "Improved LLM parsing"
    }
  ],
  "metrics": {
    "before_score": 65,
    "after_score": 78,
    "improvement": 13
  }
}
```

#### Citation Tracking Schema
```csv
timestamp,url,query,llm,cited,position,context
2025-01-07T10:00:00Z,https://example.com,What is AEO?,chatgpt,true,2,"According to [source]..."
2025-01-07T10:00:10Z,https://example.com,What is AEO?,perplexity,false,N/A,""
...
```

### Data Retention Policy

**Configurable** via `DATA_RETENTION_DAYS` environment variable:

- **Audit history**: Last 10 audits per project (or 90 days, whichever is larger)
- **Citation tracking**: Configurable (default: 365 days)
- **Success patterns**: Indefinite (~1MB total)
- **Campaign logs**: Last 50 campaigns (or 180 days)

**Cleanup**:
- Automated cleanup on startup (if configured)
- Manual cleanup via `aeo cleanup --older-than 90d`

---

## Communication Protocol

### Agent-to-Agent Message Format

**JSON + Markdown Hybrid**:

```json
{
  "message_id": "msg_20250107_001",
  "timestamp": "2025-01-07T10:30:00Z",
  "from": "orchestrator",
  "to": "auditor",
  "message_type": "task_assignment",
  "task": {
    "task_id": "task_001",
    "type": "audit",
    "input": {
      "content": "...",
      "url": "https://example.com"
    },
    "requirements": {
      "min_score": 70,
      "include_competitors": true
    }
  },
  "results": null,
  "markdown_report": null
}
```

**Response**:
```json
{
  "message_id": "msg_20250107_002",
  "timestamp": "2025-01-07T10:32:00Z",
  "from": "auditor",
  "to": "orchestrator",
  "message_type": "task_result",
  "task": null,
  "results": {
    "status": "success",
    "data": {...},
    "metadata": {
      "execution_time": "1.5 minutes",
      "tokens_used": 15000
    }
  },
  "markdown_report": "# Audit Complete\n\n**Score**: 75/100\n\n..."
}
```

### Message Types

1. **task_assignment** - Orchestrator → Subagent
2. **task_result** - Subagent → Orchestrator
3. **revision_request** - Orchestrator → Subagent (if validation fails)
4. **status_update** - Subagent → Orchestrator (progress)

### Quality Validation Rules

**4-Layer Validation**:

1. **Status Check**:
   ```python
   assert result["status"] in ["success", "failed", "partial"]
   ```

2. **Completeness Check**:
   ```python
   required_fields = ["data", "metadata", "markdown_report"]
   assert all(field in result for field in required_fields)
   ```

3. **Quality Criteria** (agent-specific):
   ```python
   # Auditor example:
   assert result["data"]["scores"]["overall"] >= 0
   assert result["data"]["scores"]["overall"] <= 100
   assert len(result["data"]["recommendations"]) > 0
   ```

4. **Consistency Check**:
   ```python
   # Results align with inputs
   assert result["data"]["url"] == task["input"]["url"]
   ```

---

## API Design

### REST API (FastAPI - Planned)

**Base URL**: `http://localhost:8000/api/v1`

#### Endpoints

##### POST /campaigns
Start a new AEO campaign

**Request**:
```json
{
  "url": "https://example.com/article",
  "options": {
    "industry": "SaaS",
    "optimization_level": "balanced",
    "tracking_days": 30,
    "include_competitors": true,
    "competitor_urls": ["https://competitor.com/article"]
  }
}
```

**Response** (202 Accepted):
```json
{
  "campaign_id": "camp_20250107_001",
  "status": "running",
  "estimated_completion": "2025-01-07T11:00:00Z",
  "progress_url": "/api/v1/campaigns/camp_20250107_001"
}
```

---

##### GET /campaigns/{campaign_id}
Get campaign status and results

**Response** (200 OK):
```json
{
  "campaign_id": "camp_20250107_001",
  "status": "completed",
  "created_at": "2025-01-07T10:30:00Z",
  "completed_at": "2025-01-07T10:35:00Z",
  "results": {
    "audit_score": 78,
    "optimization_improvement": 13,
    "citations_found": 7,
    "report_url": "/api/v1/campaigns/camp_20250107_001/report"
  }
}
```

---

##### POST /compete
Run competitive analysis

**Request**:
```json
{
  "url": "https://example.com/article",
  "competitor_urls": [
    "https://competitor1.com/article",
    "https://competitor2.com/article"
  ]
}
```

**Response** (200 OK):
```json
{
  "your_score": 75,
  "avg_competitor_score": 72,
  "your_rank": 2,
  "gaps": [
    "Competitors have more authoritative citations",
    "Your structure is better, but E-E-A-T is weaker"
  ]
}
```

---

##### POST /monitor
Start citation monitoring

**Request**:
```json
{
  "url": "https://example.com/article",
  "queries": [
    "What is AEO?",
    "How to optimize for ChatGPT?"
  ],
  "frequency": "daily",
  "llms": ["chatgpt", "perplexity", "claude"]
}
```

**Response** (201 Created):
```json
{
  "monitor_id": "mon_20250107_001",
  "status": "active",
  "next_check": "2025-01-08T10:00:00Z"
}
```

---

##### GET /agents/status
Get status of all agents

**Response** (200 OK):
```json
{
  "agents": [
    {
      "name": "auditor",
      "status": "idle",
      "last_execution": "2025-01-07T10:32:00Z",
      "success_rate": 0.98
    },
    ...
  ]
}
```

---

##### GET /patterns
Get success patterns

**Response** (200 OK):
```json
{
  "patterns": [
    {
      "content_type": "listicle",
      "industry": "SaaS",
      "success_rate": 0.85,
      "recommended_strategies": [
        "add_structure",
        "add_data_points"
      ]
    },
    ...
  ]
}
```

---

### Authentication

**Phase 1**: None (local CLI only)

**Phase 2**: API key-based
```bash
curl -H "X-API-Key: your_api_key_here" \
  http://localhost:8000/api/v1/campaigns
```

**Future**: OAuth 2.0 for hosted SaaS version

---

### Rate Limiting

| Tier | Requests/Hour | Burst |
|------|---------------|-------|
| **Free** | 100 | 10 |
| **Pro** | 1000 | 50 |
| **Enterprise** | Unlimited | Unlimited |

**Headers**:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 85
X-RateLimit-Reset: 1704628800
```

---

## CLI Design

### CLI Framework: Click

**Command Structure**:
```bash
aeo <command> [options]
```

### Commands

#### aeo campaign
Run end-to-end AEO campaign

```bash
aeo campaign <url> [options]

Options:
  --level TEXT             Optimization level (conservative/balanced/aggressive)
  --industry TEXT          Industry for pattern matching (SaaS/ecommerce/publishing)
  --tracking-days INTEGER  Days to monitor citations (default: 30)
  --competitors TEXT       Comma-separated competitor URLs
  --output PATH            Output path for report (default: ./aeo-report.md)

Example:
  aeo campaign https://example.com/article \
    --level balanced \
    --industry SaaS \
    --tracking-days 30 \
    --competitors https://competitor.com/article
```

---

#### aeo audit
Audit content for AEO signals

```bash
aeo audit <url|file> [options]

Options:
  --output PATH       Output path for audit report
  --format TEXT       Output format (md/json, default: md)
  --strict-citations  Enable strict citation checking

Example:
  aeo audit https://example.com/article --output audit.md
  aeo audit ./article.md --format json
```

---

#### aeo optimize
Optimize content for citations

```bash
aeo optimize <url|file> [options]

Options:
  --level TEXT         Optimization level (conservative/balanced/aggressive)
  --preserve TEXT      Comma-separated sections to preserve
  --output PATH        Output path for optimized content

Example:
  aeo optimize ./article.md --level balanced --output optimized.md
```

---

#### aeo track
Track citations across LLMs

```bash
aeo track <url> [options]

Options:
  --queries TEXT  Comma-separated queries to track
  --llms TEXT     Comma-separated LLMs (chatgpt,perplexity,claude,gemini,mistral)
  --frequency TEXT Tracking frequency (daily/weekly, default: daily)

Example:
  aeo track https://example.com/article \
    --queries "What is AEO?,How to optimize for LLMs?" \
    --llms chatgpt,perplexity
```

---

#### aeo compete
Competitive citation analysis

```bash
aeo compete <url> [options]

Options:
  --competitors TEXT  Comma-separated competitor URLs (required)
  --output PATH       Output path for analysis report

Example:
  aeo compete https://example.com/article \
    --competitors https://c1.com/article,https://c2.com/article
```

---

#### aeo report
Generate AEO report

```bash
aeo report <project> [options]

Options:
  --format TEXT   Report format (md/pdf, default: md)
  --template TEXT Report template (default/executive/full)
  --output PATH   Output path

Example:
  aeo report example-com --format pdf --template executive
```

---

#### aeo research
Query opportunity research

```bash
aeo research <topic> [options]

Options:
  --competitors TEXT  Competitor URLs for analysis
  --industry TEXT     Industry for pattern matching

Example:
  aeo research "Answer Engine Optimization" \
    --industry SaaS \
    --competitors https://competitor.com
```

---

#### aeo configure
Configure AEO settings

```bash
aeo configure [options]

Options:
  --set TEXT  Set configuration (KEY=VALUE)
  --list      List all configuration
  --reset     Reset to defaults

Example:
  aeo configure --set DATA_RETENTION_DAYS=365
  aeo configure --list
```

---

### Progress Indicators

**Spinner** for short tasks (<1 min):
```
⠋ Auditing content... (15s)
```

**Progress bar** for long tasks (>1 min):
```
Optimizing content [████████████--------] 60% (1.2/2.0 min)
```

**Real-time updates** for campaigns:
```
✓ Auditor Agent complete (75/100)
⠋ Optimizer Agent running...
⏸ Tracker Agent queued
```

---

## Deployment Architecture

### Local Deployment

**Architecture**: Single-machine Python application

```
User Machine
├── Python 3.10+ virtual environment
├── AEO Box installation (pip package)
├── Data storage (.aeo-data/, .aeo-agent-data/)
└── Claude Code CLI integration (optional)
```

**Installation**:
```bash
# Option 1: pip install (future)
pip install aeo-box

# Option 2: Copy to Claude Code skills
cp -r answer-engine-optimization ~/.claude/skills/aeo

# Option 3: Run from source
git clone https://github.com/alirezarezvani/aeo-box.git
cd aeo-suite
python -m venv venv
source venv/bin/activate
pip install -r answer-engine-optimization/requirements.txt
```

**Runtime**:
```bash
# CLI usage
aeo campaign https://example.com/article

# Or via Python
python -c "from aeo_box import ContentAnalyzer; ..."

# Or via Claude Code
claude "analyze this article for AEO: path/to/article.md"
```

---

### Multi-Agent Deployment (Planned)

**Architecture**: Orchestrator + Subagents via Claude Agent SDK

```
User Machine
├── Orchestrator Agent (main process)
│   ├── FastAPI web server (port 8000)
│   ├── CLI interface (Click)
│   └── Agent coordination logic
├── 6 Specialized Subagents (spawned processes)
│   ├── Auditor Agent
│   ├── Optimizer Agent
│   ├── Tracker Agent
│   ├── Researcher Agent
│   ├── Reporter Agent
│   └── Learning Agent
├── AEO Skill modules (Python libraries)
└── Data storage (.aeo-agent-data/)
```

**Process Model**:
- **Orchestrator**: Main process, always running
- **Subagents**: Spawned on-demand, terminated after completion
- **Background Workers**: Citation tracking (cron-like)

**Concurrency**:
- **Async I/O**: asyncio for non-blocking operations
- **Process Pool**: Multi-processing for CPU-bound tasks (future optimization)
- **Queue System**: asyncio.Queue for agent coordination

---

### Docker Deployment (Future)

**Dockerfile** (planned):
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "aeo_box.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Docker Compose** (planned):
```yaml
version: '3.8'
services:
  aeo-box:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/.aeo-agent-data
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
```

---

## Scalability

### Current Bottlenecks

| Component | Bottleneck | Impact |
|-----------|------------|--------|
| **Content Audit** | Sequential processing | 1 article at a time |
| **External APIs** | Rate limits (Ahrefs: 1 req/sec) | Slow competitor analysis |
| **Citation Checks** | Network latency | 30 sec per LLM |
| **Data Storage** | File I/O | Slow large-scale queries |

---

### Scaling Strategies

#### 1. Batch Processing

**Problem**: Process 100+ articles one at a time

**Solution**: Parallel execution with asyncio

```python
async def batch_audit(urls: List[str]) -> List[Dict]:
    tasks = [audit_async(url) for url in urls]
    return await asyncio.gather(*tasks)
```

**Expected Improvement**: 10x faster for 10+ articles

---

#### 2. Queue System for Citation Checks

**Problem**: Citation checks block user workflow

**Solution**: Background worker pattern

```python
# User starts monitoring
aeo track https://example.com --frequency daily

# Background worker checks daily
@cron("0 10 * * *")  # 10am daily
async def run_citation_checks():
    schedules = load_monitoring_schedules()
    for schedule in schedules:
        await check_citations_async(schedule)
```

**Expected Improvement**: Non-blocking user experience

---

#### 3. Prompt Caching

**Problem**: Repeated API calls for similar content

**Solution**: Cache Claude API prompts (90% cost savings)

```python
# System prompt (cached)
SYSTEM_PROMPT = """
You are an AEO specialist...
"""

# User prompt (not cached)
user_prompt = f"Audit this content: {content}"

# Claude API caches system prompt
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    system=[
        {"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}
    ],
    messages=[{"role": "user", "content": user_prompt}]
)
```

**Expected Improvement**: 90% cost reduction, 2x faster

---

#### 4. Distributed Agents (Future)

**Problem**: Single machine bottleneck for large agencies

**Solution**: Distribute agents across multiple machines

```python
# Master machine (orchestrator)
orchestrator = OrchestratorAgent()

# Worker machines (subagents)
worker_1 = [AuditorAgent, OptimizerAgent]
worker_2 = [TrackerAgent, ResearcherAgent]
worker_3 = [ReporterAgent, LearningAgent]

# Task distribution
orchestrator.distribute_tasks(workers=[worker_1, worker_2, worker_3])
```

**Expected Improvement**: 3x throughput for agencies

---

### Performance Targets

| Metric | Current | Target (v1.5) | Target (v2.0) |
|--------|---------|---------------|---------------|
| **Audit Time** (5000-word article) | 1.5 min | <2 min | <1 min |
| **Optimization Time** | 2.5 min | <3 min | <2 min |
| **Campaign Workflow** | N/A | <5 min | <3 min |
| **Concurrent Users** | 1 | 100 | 1000 |
| **URLs Monitored** | N/A | 1000 | 10000 |
| **Batch Processing** (100 articles) | N/A | <30 min | <15 min |

---

## Security Architecture

### Data Security

#### 1. API Key Encryption

**Storage**: Platform keychain (OS-level)

```python
import keyring

# Store API key
keyring.set_password("aeo-box", "anthropic_api_key", api_key)

# Retrieve API key
api_key = keyring.get_password("aeo-box", "anthropic_api_key")
```

**Supported Platforms**:
- macOS: Keychain
- Windows: Credential Manager
- Linux: Secret Service (freedesktop.org)

---

#### 2. Content Privacy

**Principle**: No external transmission by default

**Implementation**:
```python
# User must opt-in for external API calls
if user_config.get("allow_external_apis", False):
    use_external_api()
else:
    use_local_capabilities()  # Fallback
```

**Data Flow**:
- **Local-only**: Content never leaves machine
- **Opt-in external**: User explicitly enables (Ahrefs, SEMrush)
- **Claude API**: Only if user provides API key

---

### API Security

#### 1. Input Validation

**Pydantic Models** for all API inputs:

```python
from pydantic import BaseModel, HttpUrl, constr

class CampaignRequest(BaseModel):
    url: HttpUrl  # Validates URL format
    optimization_level: Literal["conservative", "balanced", "aggressive"]
    tracking_days: int = Field(ge=1, le=365)  # 1-365 days
    competitor_urls: Optional[List[HttpUrl]] = None
```

**Benefits**:
- Prevents injection attacks
- Type safety
- Automatic validation errors

---

#### 2. Rate Limiting

**Implementation** (FastAPI Middleware):

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/campaigns")
@limiter.limit("100/hour")  # 100 requests per hour
async def create_campaign(request: CampaignRequest):
    ...
```

---

#### 3. CORS Policy

**Development**: Allow all origins

**Production**: Whitelist only

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.aeo-box.com"],  # Production only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
```

---

### Privacy Compliance

#### GDPR Compliance

**Requirements**:
1. ✅ **Data minimization**: Only collect necessary data
2. ✅ **User consent**: Opt-in for external API usage
3. ✅ **Right to deletion**: `aeo cleanup --all`
4. ✅ **Data portability**: Export to CSV/JSON
5. ✅ **Transparency**: Clear documentation on data usage

**Implementation**:
```bash
# User can delete all data
aeo cleanup --all

# Export data
aeo export --format json --output my-data.json
```

---

## Error Handling

### Retry Logic

**Strategy**: Exponential backoff with jitter

```python
import time
import random

def retry_with_backoff(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except TransientError as e:
            if attempt == max_retries - 1:
                raise
            delay = (2 ** attempt) + random.uniform(0, 1)  # Exponential + jitter
            time.sleep(delay)
```

**Transient Errors**:
- Network timeouts
- API rate limits (429)
- Temporary service unavailability (503)

---

### Graceful Degradation

**Example**: Citation tracker without external APIs

```python
def track_citations(url: str, queries: List[str]):
    if has_api_access():
        return track_with_external_api(url, queries)
    else:
        # Fallback: Use Claude's built-in web search
        return track_with_claude_builtin(url, queries)
```

**User Experience**:
```
⚠ External API unavailable, using built-in capabilities
✓ Citation check complete (limited to Claude search)
```

---

### Error Classification

| Error Type | User Action | System Action |
|------------|-------------|---------------|
| **Transient** (network timeout) | None | Auto-retry 3x |
| **Configuration** (missing API key) | Fix config | Show clear instructions |
| **Invalid Input** (malformed URL) | Fix input | Validation error with example |
| **System** (disk full) | Free space | Graceful shutdown with warning |

---

## Monitoring & Logging

### Logging Levels

#### DEBUG
**Usage**: Development, troubleshooting

```
[DEBUG] Agent communication: orchestrator -> auditor
[DEBUG] API call: POST https://api.anthropic.com/v1/messages
[DEBUG] Prompt caching: cache_hit=true, tokens_saved=15000
```

#### INFO
**Usage**: Normal operation, major milestones

```
[INFO] Campaign started: camp_20250107_001
[INFO] Auditor Agent complete: score=75/100
[INFO] Optimization complete: improvement=+13 points
```

#### WARNING
**Usage**: Degraded performance, fallbacks

```
[WARNING] External API unavailable, using built-in capabilities
[WARNING] Rate limit approaching: 95/100 requests used
[WARNING] Data retention: 120 days old data will be cleaned
```

#### ERROR
**Usage**: Failures, exceptions

```
[ERROR] Agent execution failed: auditor (timeout after 5 min)
[ERROR] API call failed: 429 Too Many Requests
[ERROR] Data storage failed: disk full
```

---

### Structured Logging

**Format**: JSON for easy parsing

```json
{
  "timestamp": "2025-01-07T10:30:00.123Z",
  "level": "INFO",
  "component": "orchestrator",
  "message": "Campaign started",
  "metadata": {
    "campaign_id": "camp_20250107_001",
    "url": "https://example.com",
    "user": "user_123"
  }
}
```

**Benefits**:
- Easy to parse and analyze
- Supports log aggregation (ELK, Splunk)
- Machine-readable

---

### Metrics (Future)

**Key Metrics**:

| Metric | Type | Description |
|--------|------|-------------|
| **audit_completion_time** | Histogram | Time to complete audit |
| **optimization_success_rate** | Counter | % of successful optimizations |
| **citation_tracking_uptime** | Gauge | % uptime for tracking service |
| **api_latency** | Histogram | API response time (p50, p95, p99) |
| **error_rate** | Counter | Errors per minute |
| **active_users** | Gauge | Currently active users |

**Export**: Prometheus format (future integration)

---

## Cost Optimization

### Claude Max Pro Optimization Strategies

#### 1. Prompt Caching (90% Savings)

**How it works**: Cache system prompts that don't change

**Implementation**:
```python
SYSTEM_PROMPT = """
You are an AEO specialist. Your role is to...
[5000 tokens of context]
"""

# Cache this prompt (billed at $0.30/MTok write, $0.03/MTok read)
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    system=[
        {"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}
    ],
    messages=[{"role": "user", "content": user_content}]
)
```

**Savings**:
- Without caching: $3.00/MTok write
- With caching: $0.30/MTok write + $0.03/MTok read (subsequent calls)
- **Result**: 90% cost reduction

---

#### 2. Extended Context (200K Tokens)

**How it works**: Batch multiple articles in one request

**Implementation**:
```python
# Instead of 100 separate audits:
for article in articles:
    audit(article)  # 100 API calls

# Batch into one audit:
batch_audit(articles)  # 1 API call with 100 articles
```

**Savings**:
- 100 separate calls: $30 (100 × $0.30)
- 1 batched call: $0.60 (200K tokens × $3.00/MTok)
- **Result**: 98% cost reduction

---

#### 3. Request Batching (6 Agents → 1 Call)

**How it works**: Coordinate all agents in one Claude request

**Implementation**:
```python
# Instead of 6 separate agent calls:
auditor_result = call_auditor()    # 1 API call
optimizer_result = call_optimizer()  # 1 API call
... # 4 more API calls
# Total: 6 API calls

# Batch coordination in orchestrator:
orchestrator_result = orchestrate_all_agents()  # 1 API call
# Total: 1 API call
```

**Savings**:
- 6 separate calls: $18 (6 × $3.00)
- 1 orchestrated call: $3.00
- **Result**: 83% cost reduction

---

### Cost Projections

**Without Optimization** (100 campaigns/day):

| Operation | Cost | Frequency | Monthly Cost |
|-----------|------|-----------|--------------|
| Audit | $0.50 | 100/day | $1,500 |
| Optimize | $1.00 | 100/day | $3,000 |
| 6 Agents | $3.00 | 100/day | $9,000 |
| **Total** | | | **$13,500** |

**With Optimization** (100 campaigns/day):

| Operation | Cost | Optimization | Monthly Cost |
|-----------|------|--------------|--------------|
| Audit | $0.50 | 90% caching | $150 |
| Optimize | $1.00 | 90% caching | $300 |
| 6 Agents | $3.00 | 83% batching + 90% caching | $162 |
| **Total** | | | **$612** |

**Savings**: $12,888/month (95.5% reduction)

---

## Technology Stack

### Core Technologies

| Layer | Technology | Version | Rationale |
|-------|-----------|---------|-----------|
| **Language** | Python | 3.10+ | Mature, AI/ML ecosystem |
| **Multi-Agent** | Claude Agent SDK | Latest | First-class Claude integration |
| **REST API** | FastAPI | 0.104+ | Fast, modern, type-safe |
| **CLI** | Click | 8.1+ | Industry standard, easy to use |
| **Async** | asyncio | stdlib | Built-in, performant |
| **HTTP Client** | httpx | 0.25+ | Async HTTP support |

### Testing

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Unit Tests** | pytest | Test individual functions |
| **Integration Tests** | pytest + pytest-asyncio | Test agent workflows |
| **Coverage** | pytest-cov | >80% coverage target |
| **Mocking** | pytest-mock | Mock external APIs |
| **Fixtures** | pytest fixtures | Test data management |

### Data & Storage

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Primary Storage** | Local file system | Simple, portable |
| **Audit Data** | JSON | Structured, easy to parse |
| **Citation Data** | CSV | Spreadsheet compatibility |
| **Success Patterns** | JSON | Flexible schema |
| **Future Database** | SQLite (optional) | If relational queries needed |

### Deployment

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Package Manager** | pip | Standard Python distribution |
| **Virtual Env** | venv | Dependency isolation |
| **CI/CD** | GitHub Actions | Automated testing, deployment |
| **Containerization** | Docker (future) | Reproducible environments |
| **Process Manager** | systemd (future) | Background service management |

### Development Tools

| Tool | Purpose |
|------|---------|
| **Linter** | ruff (replaces flake8, black, isort) |
| **Type Checker** | mypy |
| **Formatter** | ruff format |
| **Pre-commit** | pre-commit hooks |
| **Documentation** | Sphinx (future) |

---

## Appendices

### A. Agent Specifications

See: [Multi-Agent System Specification](../../aeo-agentic-app-master-prompt.md)

### B. API Reference

See: [API_REFERENCE.md](../api-reference.md)

### C. Data Models

**Pydantic Schemas** (planned):

```python
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Literal

class AuditRequest(BaseModel):
    content: str
    url: Optional[HttpUrl] = None
    competitor_urls: Optional[List[HttpUrl]] = None

class AuditResult(BaseModel):
    timestamp: str
    url: Optional[HttpUrl]
    scores: Dict[str, float]
    recommendations: List[Dict]
    competitor_comparison: Optional[Dict] = None

class CampaignRequest(BaseModel):
    url: HttpUrl
    optimization_level: Literal["conservative", "balanced", "aggressive"] = "balanced"
    tracking_days: int = 30
    industry: Optional[str] = None

class CampaignResult(BaseModel):
    campaign_id: str
    status: Literal["running", "completed", "failed"]
    results: Optional[Dict] = None
```

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-08 | AEO Box Team | Initial architecture documentation |

---

**Next Review Date**: 2025-12-08 (monthly review)

---

<p align="center">
  <strong>Questions or feedback? Open a GitHub Discussion!</strong>
</p>

# AEO Box API Reference

**Version**: 1.0
**Last Updated**: 2025-11-08

Complete API reference for AEO Box Python SDK and REST API (planned).

---

## Table of Contents

1. [Python SDK](#python-sdk)
2. [REST API](#rest-api-planned)
3. [CLI Commands](#cli-commands-planned)
4. [Data Models](#data-models)
5. [Error Codes](#error-codes)

---

## Python SDK

### Installation

```bash
# Current (v1.0): Manual import
git clone https://github.com/alirezarezvani/aeo-box.git
cd aeo-suite/answer-engine-optimization

# Future (v1.5): PyPI package
pip install aeo-box
```

---

### ContentAnalyzer

**Module**: `answer_engine_optimization.modules.content_analyzer`

#### Class: `ContentAnalyzer`

Analyzes content for AEO signals (E-E-A-T, structure, citations, readability).

##### `analyze()`

```python
def analyze(
    self,
    content: str,
    url: Optional[str] = None,
    competitor_urls: Optional[List[str]] = None
) -> Dict[str, Any]
```

**Parameters**:
- `content` (str, required): Article content (markdown or plain text)
- `url` (str, optional): URL of the article for reference
- `competitor_urls` (List[str], optional): Competitor URLs for benchmarking

**Returns**: `Dict[str, Any]`
```python
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
            "priority": "high",  # high, medium, low
            "description": "Add H2 subheadings for better content chunking",
            "expected_impact": "+5 points"
        }
    ],
    "competitor_comparison": {
        "avg_score": 72,
        "your_rank": 2,
        "top_performers": [...]
    }
}
```

**Example**:
```python
from answer_engine_optimization.modules.content_analyzer import ContentAnalyzer

analyzer = ContentAnalyzer()
audit = analyzer.analyze(
    content=open("article.md").read(),
    url="https://yoursite.com/article",
    competitor_urls=["https://competitor.com/article"]
)

print(f"AEO Score: {audit['scores']['overall']}/100")
```

**Raises**:
- `ValueError`: If content is empty or invalid
- `APIError`: If external API calls fail (with API keys)

---

### ContentOptimizer

**Module**: `answer_engine_optimization.modules.optimizer`

#### Class: `ContentOptimizer`

Optimizes content for better AEO scores using AI.

##### `optimize()`

```python
def optimize(
    self,
    content: str,
    level: Literal["conservative", "balanced", "aggressive"] = "balanced",
    focus_areas: Optional[List[str]] = None,
    preserve_sections: Optional[List[str]] = None
) -> Dict[str, Any]
```

**Parameters**:
- `content` (str, required): Article content to optimize
- `level` (str, optional): Optimization level
  - `"conservative"`: Minimal changes (60-70 score target)
  - `"balanced"`: Moderate improvements (70-80, default)
  - `"aggressive"`: Maximum optimization (80-90+)
- `focus_areas` (List[str], optional): Areas to focus on
  - Options: `["structure", "eeat", "citations", "readability"]`
- `preserve_sections` (List[str], optional): Section headers to preserve unchanged

**Returns**: `Dict[str, Any]`
```python
{
    "optimized_content": "...",  # Full optimized content
    "change_log": [
        {
            "type": "add_structure",
            "line": 15,
            "before": "Original text...",
            "after": "Optimized text...",
            "rationale": "Improved LLM parsing with H2 subheading"
        }
    ],
    "metrics": {
        "before_score": 65,
        "after_score": 78,
        "improvement": 13
    }
}
```

**Example**:
```python
from answer_engine_optimization.modules.optimizer import ContentOptimizer

optimizer = ContentOptimizer()
result = optimizer.optimize(
    content=content,
    level="balanced",
    focus_areas=["structure", "citations"],
    preserve_sections=["Introduction"]
)

with open("optimized.md", "w") as f:
    f.write(result['optimized_content'])
```

**Requires**: `ANTHROPIC_API_KEY` environment variable

**Raises**:
- `MissingAPIKeyError`: If API key not set
- `OptimizationError`: If optimization fails

---

### CitationTracker

**Module**: `answer_engine_optimization.modules.citation_tracker`

#### Class: `CitationTracker`

Tracks citations across multiple LLMs.

##### `track()`

```python
def track(
    self,
    url: str,
    queries: List[str],
    llms: List[str] = ["chatgpt", "perplexity", "claude", "gemini", "mistral"]
) -> Dict[str, Any]
```

**Parameters**:
- `url` (str, required): URL to track
- `queries` (List[str], required): Queries to check for citations
- `llms` (List[str], optional): LLMs to check (default: all 5)

**Returns**: `Dict[str, Any]`
```python
{
    "url": "https://example.com",
    "timestamp": "2025-01-07T10:30:00Z",
    "citations": [
        {
            "llm": "chatgpt",
            "query": "What is AEO?",
            "cited": true,
            "position": 2,  # Position in response (1-based)
            "context": "According to [source], AEO is..."
        }
    ],
    "summary": {
        "total_queries": 3,
        "total_citations": 7,  # Out of 15 total (3 queries × 5 LLMs)
        "citation_rate": 0.467  # 46.7%
    }
}
```

**Example**:
```python
from answer_engine_optimization.modules.citation_tracker import CitationTracker

tracker = CitationTracker()
result = tracker.track(
    url="https://yoursite.com/article",
    queries=["What is AEO?", "How to optimize for LLMs?"],
    llms=["chatgpt", "perplexity", "claude"]
)

print(f"Citation Rate: {result['summary']['citation_rate']:.1%}")
```

**Requires**: API keys for target LLMs (or `ANTHROPIC_API_KEY` for fallback)

**Raises**:
- `URLError`: If URL is invalid or unreachable
- `APIError`: If LLM API calls fail

---

### QueryResearcher

**Module**: `answer_engine_optimization.modules.query_researcher`

#### Class: `QueryResearcher`

Discovers high-value query opportunities.

##### `research()`

```python
def research(
    self,
    topic: str,
    competitor_urls: Optional[List[str]] = None,
    industry: Optional[str] = None
) -> Dict[str, Any]
```

**Parameters**:
- `topic` (str, required): Topic to research
- `competitor_urls` (List[str], optional): Competitor URLs for analysis
- `industry` (str, optional): Industry for pattern matching (e.g., "SaaS", "ecommerce")

**Returns**: `Dict[str, Any]`
```python
{
    "topic": "Answer Engine Optimization",
    "target_queries": [
        {
            "query": "What is AEO?",
            "citation_potential": 0.85,  # 0-1 scale
            "competition": "medium",  # low, medium, high
            "current_citations": 12,  # Competitors being cited
            "content_gap": true  # Opportunity for you
        }
    ],
    "competitor_analysis": [...]
}
```

**Example**:
```python
from answer_engine_optimization.modules.query_researcher import QueryResearcher

researcher = QueryResearcher()
result = researcher.research(
    topic="Answer Engine Optimization",
    competitor_urls=["https://competitor.com/aeo-guide"],
    industry="SaaS"
)

# Top opportunities
for query in result['target_queries'][:5]:
    if query['content_gap']:
        print(f"{query['query']} - Potential: {query['citation_potential']:.0%}")
```

---

### ReportGenerator

**Module**: `answer_engine_optimization.modules.report_generator`

#### Class: `ReportGenerator`

Generates client-ready reports.

##### `generate()`

```python
def generate(
    self,
    audit_results: Dict,
    optimization_results: Optional[Dict] = None,
    citation_data: Optional[Dict] = None,
    template: str = "default"
) -> str
```

**Parameters**:
- `audit_results` (Dict, required): Output from `ContentAnalyzer.analyze()`
- `optimization_results` (Dict, optional): Output from `ContentOptimizer.optimize()`
- `citation_data` (Dict, optional): Output from `CitationTracker.track()`
- `template` (str, optional): Report template
  - Options: `"default"`, `"executive"`, `"full"`, `"optimization"`

**Returns**: `str` - Markdown report

**Example**:
```python
from answer_engine_optimization.modules.report_generator import ReportGenerator

generator = ReportGenerator()
report = generator.generate(
    audit_results=audit,
    optimization_results=optimization_result,
    citation_data=citation_result,
    template="executive"
)

with open("report.md", "w") as f:
    f.write(report)
```

---

### SuccessPatternLearner

**Module**: `answer_engine_optimization.modules.success_patterns`

#### Class: `SuccessPatternLearner`

Adaptive learning system for success patterns.

##### `learn()`

```python
def learn(
    self,
    optimization_result: Dict,
    citation_performance: Dict,
    industry: Optional[str] = None
) -> None
```

**Parameters**:
- `optimization_result` (Dict, required): Optimization data
- `citation_performance` (Dict, required): Citation tracking results
- `industry` (str, optional): Industry classification

**Returns**: `None` (updates pattern library)

**Example**:
```python
from answer_engine_optimization.modules.success_patterns import SuccessPatternLearner

learner = SuccessPatternLearner()
learner.learn(
    optimization_result=optimization_result,
    citation_performance=citation_result,
    industry="SaaS"
)
```

##### `get_recommendations()`

```python
def get_recommendations(
    self,
    content_type: str,
    industry: Optional[str] = None
) -> List[Dict]
```

**Parameters**:
- `content_type` (str, required): Content type (e.g., "listicle", "guide", "tutorial")
- `industry` (str, optional): Industry filter

**Returns**: `List[Dict]` - Learned patterns
```python
[
    {
        "strategy": "add_structure",
        "success_rate": 0.85,
        "avg_improvement": 12,
        "sample_size": 45
    }
]
```

**Example**:
```python
recommendations = learner.get_recommendations(
    content_type="listicle",
    industry="SaaS"
)

for rec in recommendations:
    print(f"{rec['strategy']}: {rec['success_rate']:.0%} success rate")
```

---

## REST API (Planned)

**Status**: Coming in v1.5

**Base URL**: `http://localhost:8000/api/v1`

### Authentication

**Current (v1.5)**: None (local CLI only)

**Future (v2.0)**: API key-based

```bash
curl -H "X-API-Key: your_api_key" \
  http://localhost:8000/api/v1/campaigns
```

---

### Endpoints

#### POST /campaigns

Start a new AEO campaign (orchestrator workflow).

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

#### GET /campaigns/{campaign_id}

Get campaign status and results.

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

#### POST /compete

Run competitive analysis.

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

#### POST /monitor

Start citation monitoring.

**Request**:
```json
{
  "url": "https://example.com/article",
  "queries": ["What is AEO?", "How to optimize for ChatGPT?"],
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

#### GET /agents/status

Get status of all agents.

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
    {
      "name": "optimizer",
      "status": "running",
      "current_task": "camp_20250107_002",
      "success_rate": 0.95
    }
  ]
}
```

---

#### GET /patterns

Get success patterns.

**Response** (200 OK):
```json
{
  "patterns": [
    {
      "content_type": "listicle",
      "industry": "SaaS",
      "success_rate": 0.85,
      "recommended_strategies": ["add_structure", "add_data_points"]
    }
  ]
}
```

---

### Rate Limiting

| Tier | Requests/Hour | Burst | Monthly Cost |
|------|---------------|-------|--------------|
| **Free** | 100 | 10 | $0 |
| **Pro** | 1000 | 50 | $49 |
| **Enterprise** | Unlimited | Unlimited | $199 |

**Headers**:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 85
X-RateLimit-Reset: 1704628800
```

---

## CLI Commands (Planned)

**Status**: Coming in v1.5

### aeo campaign

Run complete AEO campaign.

```bash
aeo campaign <url> [options]

Options:
  --level TEXT             Optimization level (conservative/balanced/aggressive)
  --industry TEXT          Industry for pattern matching
  --tracking-days INTEGER  Days to monitor citations (default: 30)
  --competitors TEXT       Comma-separated competitor URLs
  --output PATH            Output path for report

Example:
  aeo campaign https://example.com/article \
    --level balanced \
    --industry SaaS \
    --competitors https://competitor.com/article
```

---

### aeo audit

Audit content for AEO signals.

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

### aeo optimize

Optimize content.

```bash
aeo optimize <url|file> [options]

Options:
  --level TEXT         Optimization level
  --preserve TEXT      Comma-separated sections to preserve
  --output PATH        Output path for optimized content

Example:
  aeo optimize ./article.md --level balanced --output optimized.md
```

---

### aeo track

Track citations.

```bash
aeo track <url> [options]

Options:
  --queries TEXT   Comma-separated queries
  --llms TEXT      Comma-separated LLMs
  --frequency TEXT Tracking frequency (daily/weekly)

Example:
  aeo track https://example.com/article \
    --queries "What is AEO?,How to optimize for LLMs?"
```

---

## Data Models

### AuditResult

```python
from typing import Dict, List, Optional
from pydantic import BaseModel, HttpUrl

class AuditResult(BaseModel):
    timestamp: str
    url: Optional[HttpUrl]
    scores: Dict[str, float]  # {"overall": 75, "eeat": 68, ...}
    recommendations: List[Dict]
    competitor_comparison: Optional[Dict] = None
```

---

### OptimizationResult

```python
class OptimizationResult(BaseModel):
    optimized_content: str
    change_log: List[Dict]
    metrics: Dict[str, float]  # {"before_score": 65, "after_score": 78, ...}
```

---

### CitationResult

```python
class CitationResult(BaseModel):
    url: HttpUrl
    timestamp: str
    citations: List[Dict]  # Per-LLM citation data
    summary: Dict[str, Any]  # Aggregate stats
```

---

## Error Codes

### HTTP Status Codes (REST API)

| Code | Meaning | Description |
|------|---------|-------------|
| **200** | OK | Request successful |
| **201** | Created | Resource created (e.g., monitoring started) |
| **202** | Accepted | Request accepted, processing asynchronously |
| **400** | Bad Request | Invalid input (check error message) |
| **401** | Unauthorized | Missing or invalid API key |
| **404** | Not Found | Resource not found (campaign_id, etc.) |
| **429** | Too Many Requests | Rate limit exceeded |
| **500** | Internal Server Error | Server error (check logs) |

---

### Python Exception Classes

```python
# Base exception
class AEOError(Exception):
    pass

# API-related errors
class APIError(AEOError):
    """External API call failed"""
    pass

class MissingAPIKeyError(AEOError):
    """Required API key not set"""
    pass

class RateLimitError(AEOError):
    """API rate limit exceeded"""
    pass

# Input validation errors
class InvalidURLError(AEOError):
    """Invalid URL format"""
    pass

class InvalidContentError(AEOError):
    """Content is empty or malformed"""
    pass

# Processing errors
class OptimizationError(AEOError):
    """Optimization failed"""
    pass

class CitationTrackingError(AEOError):
    """Citation tracking failed"""
    pass
```

**Example Usage**:
```python
from answer_engine_optimization.modules.content_analyzer import ContentAnalyzer
from answer_engine_optimization.exceptions import InvalidContentError

try:
    analyzer = ContentAnalyzer()
    audit = analyzer.analyze(content="")
except InvalidContentError as e:
    print(f"Error: {e}")
```

---

### Error Response Format (REST API)

```json
{
  "error": {
    "code": "invalid_url",
    "message": "URL must include protocol (https://)",
    "details": {
      "provided_url": "example.com",
      "expected_format": "https://example.com"
    }
  }
}
```

---

## Versioning

**API Version**: v1

**Backward Compatibility**: Guaranteed within major version

**Deprecation Policy**:
- Deprecated features maintained for 6 months
- Warning in response headers: `X-API-Deprecated: true`
- Migration guide provided

---

## Examples

### Complete Workflow (Python)

```python
from answer_engine_optimization.modules.content_analyzer import ContentAnalyzer
from answer_engine_optimization.modules.optimizer import ContentOptimizer
from answer_engine_optimization.modules.citation_tracker import CitationTracker
from answer_engine_optimization.modules.report_generator import ReportGenerator

# 1. Audit
analyzer = ContentAnalyzer()
audit = analyzer.analyze(content=content, url=url)

if audit['scores']['overall'] < 75:
    # 2. Optimize
    optimizer = ContentOptimizer()
    result = optimizer.optimize(content=content, level="balanced")

    # Save optimized content
    with open("optimized.md", "w") as f:
        f.write(result['optimized_content'])

# 3. Track citations
tracker = CitationTracker()
citations = tracker.track(url=url, queries=queries)

# 4. Generate report
generator = ReportGenerator()
report = generator.generate(
    audit_results=audit,
    optimization_results=result,
    citation_data=citations,
    template="executive"
)

print(report)
```

---

### Complete Workflow (REST API - Planned)

```bash
# 1. Start campaign
CAMPAIGN_ID=$(curl -X POST http://localhost:8000/api/v1/campaigns \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/article",
    "options": {"optimization_level": "balanced"}
  }' | jq -r '.campaign_id')

# 2. Check status
curl http://localhost:8000/api/v1/campaigns/$CAMPAIGN_ID

# 3. Get report
curl http://localhost:8000/api/v1/campaigns/$CAMPAIGN_ID/report \
  -o report.md
```

---

## SDK Roadmap

### v1.0 (Current)
- ✅ Python modules (content_analyzer, optimizer, etc.)
- ✅ Manual import
- ✅ Basic error handling

### v1.5 (Q1 2025)
- [ ] PyPI package (`pip install aeo-box`)
- [ ] Multi-agent orchestration
- [ ] REST API (FastAPI)
- [ ] CLI commands (Click)
- [ ] Async/await support

### v2.0 (Q2-Q4 2025)
- [ ] TypeScript SDK
- [ ] GraphQL API
- [ ] WebSocket support (real-time updates)
- [ ] Webhook notifications

---

## Support

- **Documentation**: [docs/](.)
- **GitHub Issues**: [github.com/alirezarezvani/aeo-box/issues](https://github.com/alirezarezvani/aeo-box/issues)
- **Discussions**: [github.com/alirezarezvani/aeo-box/discussions](https://github.com/alirezarezvani/aeo-box/discussions)

---

<p align="center">
  <strong>Happy coding! 🚀</strong>
</p>

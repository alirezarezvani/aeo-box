# API Reference - AEO Multi-Agent System v1.5

**Last Updated**: 2025-11-09
**API Version**: 1.5.0
**Status**: Production-Ready

---

## Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Authentication](#authentication)
4. [Base URL & Versioning](#base-url--versioning)
5. [Endpoints](#endpoints)
6. [Data Models](#data-models)
7. [Workflow Status](#workflow-status)
8. [Error Handling](#error-handling)
9. [Rate Limiting](#rate-limiting)
10. [Best Practices](#best-practices)
11. [Code Examples](#code-examples)

---

## Overview

The AEO Multi-Agent API provides programmatic access to comprehensive Answer Engine Optimization workflows powered by a multi-agent system. Optimize your content for AI-powered answer engines like ChatGPT, Claude, Perplexity, and Gemini.

### Key Features

- **Async Execution**: Non-blocking workflow execution with real-time status tracking
- **Multi-Agent Orchestration**: Coordinated execution by 6 specialized agents
- **Flexible Modes**: Minimal (15-30 min), Balanced (45-90 min), Comprehensive (2-4 hours)
- **Complete Workflows**: E-E-A-T audit, query research, optimization, citation tracking
- **Cost Optimized**: 95%+ savings with prompt caching and request batching

### API Conventions

- **RESTful Design**: Standard HTTP methods (GET, POST, DELETE)
- **JSON Format**: All requests and responses use `application/json`
- **Async by Default**: POST requests return immediately with workflow ID
- **Status Polling**: Use status endpoints to track workflow progress
- **ISO 8601 Timestamps**: All timestamps in UTC format (`2025-11-09T10:30:00Z`)

---

## Getting Started

### Quick Start

```bash
# 1. Start the API server
uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# 2. Check API health
curl http://localhost:8000/health

# 3. Create a campaign
curl -X POST http://localhost:8000/api/campaigns \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/article",
    "mode": "balanced",
    "industry": "SaaS"
  }'

# 4. Check campaign status
curl http://localhost:8000/api/status/{campaign_id}
```

### Interactive Documentation

- **Swagger UI**: `http://localhost:8000/docs` - Interactive API exploration
- **ReDoc**: `http://localhost:8000/redoc` - Alternative documentation interface

---

## Authentication

**Current Version**: No authentication required (development mode)

**Production Recommendations**:
- API key authentication via `X-API-Key` header
- JWT token-based authentication
- OAuth 2.0 for third-party integrations

**Example (Future)**:
```bash
curl -X POST http://localhost:8000/api/campaigns \
  -H "X-API-Key: your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

---

## Base URL & Versioning

### Base URL

```
http://localhost:8000
```

For production deployments, replace with your domain:
```
https://api.yourdomain.com
```

### API Versioning

Current version: **v1.5.0**

Version information available at:
- Root endpoint: `GET /`
- Health endpoint: `GET /health`

**Future Versioning Strategy**:
- URL-based: `/v2/api/campaigns`
- Header-based: `Accept: application/vnd.aeo.v2+json`

---

## Endpoints

### Root Endpoints

#### GET / - API Root Information

Get API metadata and available endpoints.

**Response**: `200 OK`

```json
{
  "message": "AEO Multi-Agent API",
  "version": "1.5.0",
  "docs": "/docs",
  "redoc": "/redoc",
  "health": "/health",
  "endpoints": {
    "campaigns": "/api/campaigns",
    "status": "/api/status/{campaign_id}",
    "competitive": "/api/competitive",
    "monitoring": "/api/monitoring"
  }
}
```

**cURL Example**:
```bash
curl http://localhost:8000/
```

**Python Example**:
```python
import requests

response = requests.get("http://localhost:8000/")
data = response.json()
print(f"API Version: {data['version']}")
print(f"Documentation: {data['docs']}")
```

---

#### GET /health - Health Check

Monitor API health and system status.

**Response**: `200 OK`

```json
{
  "status": "healthy",
  "version": "1.5.0",
  "timestamp": "2025-11-09T10:30:00Z",
  "agents_registered": 6
}
```

**Response Fields**:
- `status` (string): API health status
  - `healthy`: All systems operational
  - `degraded`: Partial functionality
  - `unhealthy`: Critical issues
- `version` (string): Current API version
- `timestamp` (datetime): Current server time (UTC)
- `agents_registered` (integer): Number of registered agents in orchestrator

**cURL Example**:
```bash
curl http://localhost:8000/health
```

**Python Example**:
```python
import requests

response = requests.get("http://localhost:8000/health")
health = response.json()

if health["status"] == "healthy":
    print(f"✓ API is healthy with {health['agents_registered']} agents")
else:
    print(f"✗ API status: {health['status']}")
```

**Use Cases**:
- Load balancer health checks
- Monitoring and alerting systems
- Pre-deployment verification
- System status dashboards

---

### Campaign Endpoints

#### POST /api/campaigns - Create AEO Campaign

Launch a complete AEO optimization workflow including content audit, query research, optimization, citation tracking, and report generation.

**Request Body**:

```json
{
  "url": "https://example.com/article",
  "mode": "balanced",
  "industry": "SaaS",
  "optimization_level": "balanced",
  "tracking_duration_days": 30,
  "queries": ["AEO best practices", "content optimization"]
}
```

**Request Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `url` | string (URL) | **Yes** | - | URL of content to optimize (must start with http:// or https://) |
| `mode` | enum | No | `balanced` | Campaign execution mode (`minimal`, `balanced`, `comprehensive`) |
| `industry` | string | No | `null` | Industry vertical for context (e.g., "SaaS", "E-commerce", "Healthcare") |
| `optimization_level` | enum | No | `balanced` | Content optimization aggressiveness (`conservative`, `balanced`, `aggressive`) |
| `tracking_duration_days` | integer | No | `30` | Citation tracking duration (1-365 days) |
| `queries` | array[string] | No | `null` | Target queries to optimize for (optional, auto-discovered if not provided) |

**Response**: `202 Accepted`

```json
{
  "campaign_id": "campaign_20251109_103000",
  "status": "running",
  "created_at": "2025-11-09T10:30:00Z",
  "message": "Campaign workflow started successfully. Check status at /api/status/{campaign_id}"
}
```

**Response Fields**:
- `campaign_id` (string): Unique campaign identifier - use for status tracking
- `status` (enum): Current workflow status (`running`)
- `created_at` (datetime): Campaign creation timestamp (UTC)
- `message` (string): Human-readable status message

**Status Codes**:
- `202 Accepted`: Campaign started successfully
- `400 Bad Request`: Invalid URL or workflow validation failed
- `422 Unprocessable Entity`: Request validation failed (invalid parameters)
- `500 Internal Server Error`: Unexpected server error

**Error Response Example** (`400 Bad Request`):
```json
{
  "error": "Invalid URL format",
  "detail": "URL must start with http:// or https://",
  "timestamp": "2025-11-09T10:30:00Z"
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:8000/api/campaigns \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/article",
    "mode": "balanced",
    "industry": "SaaS",
    "optimization_level": "balanced",
    "tracking_duration_days": 30,
    "queries": ["AEO best practices", "content optimization"]
  }'
```

**Python Example**:
```python
import requests

payload = {
    "url": "https://example.com/article",
    "mode": "balanced",
    "industry": "SaaS",
    "optimization_level": "balanced",
    "tracking_duration_days": 30,
    "queries": ["AEO best practices", "content optimization"]
}

response = requests.post(
    "http://localhost:8000/api/campaigns",
    json=payload
)

if response.status_code == 202:
    campaign = response.json()
    print(f"✓ Campaign started: {campaign['campaign_id']}")
    print(f"Status: {campaign['status']}")
else:
    error = response.json()
    print(f"✗ Error: {error['error']}")
```

**Campaign Execution Modes**:

| Mode | Duration | Tasks | Use Case |
|------|----------|-------|----------|
| `minimal` | 15-30 min | Basic audit + quick recommendations | Quick content check |
| `balanced` | 45-90 min | Full audit, optimization, basic tracking | Standard optimization |
| `comprehensive` | 2-4 hours | Complete analysis, extended tracking, learning | Enterprise-grade optimization |

**Optimization Levels**:

| Level | Impact | Approach |
|-------|--------|----------|
| `conservative` | Low | Minor improvements, preserve original voice |
| `balanced` | Medium | Moderate changes, enhance clarity |
| `aggressive` | High | Major restructuring for maximum AEO impact |

---

#### POST /api/competitive - Create Competitive Analysis

Analyze competitor content for AEO performance and identify optimization opportunities.

**Request Body**:

```json
{
  "topic": "project management",
  "competitor_urls": [
    "https://competitor1.com/article",
    "https://competitor2.com/article",
    "https://competitor3.com/article"
  ],
  "region": "US",
  "include_citations": true
}
```

**Request Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `topic` | string | **Yes** | - | Topic or industry to analyze (min 3 characters) |
| `competitor_urls` | array[string] | **Yes** | - | Competitor URLs to analyze (1-10 URLs, must be valid HTTP/HTTPS) |
| `region` | string | No | `US` | Geographic region for analysis (e.g., "US", "UK", "EU") |
| `include_citations` | boolean | No | `true` | Include citation frequency analysis |

**Response**: `202 Accepted`

```json
{
  "analysis_id": "analysis_20251109_110000",
  "status": "running",
  "created_at": "2025-11-09T11:00:00Z",
  "message": "Competitive analysis started. Check status at /api/status/{analysis_id}"
}
```

**Status Codes**:
- `202 Accepted`: Analysis started successfully
- `400 Bad Request`: Invalid topic or URLs
- `422 Unprocessable Entity`: Too many URLs (max 10) or validation failed
- `500 Internal Server Error`: Unexpected server error

**cURL Example**:
```bash
curl -X POST http://localhost:8000/api/competitive \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "project management",
    "competitor_urls": [
      "https://competitor1.com/article",
      "https://competitor2.com/article"
    ],
    "region": "US",
    "include_citations": true
  }'
```

**Python Example**:
```python
import requests

payload = {
    "topic": "project management",
    "competitor_urls": [
        "https://competitor1.com/article",
        "https://competitor2.com/article",
        "https://competitor3.com/article"
    ],
    "region": "US",
    "include_citations": True
}

response = requests.post(
    "http://localhost:8000/api/competitive",
    json=payload
)

if response.status_code == 202:
    analysis = response.json()
    print(f"✓ Analysis started: {analysis['analysis_id']}")
else:
    print(f"✗ Error: {response.json()['error']}")
```

---

#### POST /api/monitoring - Setup Citation Monitoring

Configure continuous monitoring to track how often your content is cited by AI models.

**Request Body**:

```json
{
  "url": "https://example.com/article",
  "duration_days": 90,
  "queries": ["topic 1", "topic 2"],
  "alert_on_changes": true,
  "weekly_reports": true
}
```

**Request Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `url` | string (URL) | **Yes** | - | URL to monitor for citations |
| `duration_days` | integer | No | `90` | Monitoring duration (1-365 days) |
| `queries` | array[string] | No | `null` | Specific queries to track (optional) |
| `alert_on_changes` | boolean | No | `true` | Send alerts when citation metrics change |
| `weekly_reports` | boolean | No | `true` | Generate weekly summary reports |

**Response**: `202 Accepted`

```json
{
  "monitor_id": "monitor_20251109_113000",
  "status": "running",
  "created_at": "2025-11-09T11:30:00Z",
  "message": "Monitoring setup started. Check status at /api/status/{monitor_id}"
}
```

**Status Codes**:
- `202 Accepted`: Monitoring setup started successfully
- `400 Bad Request`: Invalid URL or duration
- `422 Unprocessable Entity`: Duration out of range (1-365 days)
- `500 Internal Server Error`: Unexpected server error

**cURL Example**:
```bash
curl -X POST http://localhost:8000/api/monitoring \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/article",
    "duration_days": 90,
    "queries": ["AEO optimization", "content strategy"],
    "alert_on_changes": true,
    "weekly_reports": true
  }'
```

**Python Example**:
```python
import requests

payload = {
    "url": "https://example.com/article",
    "duration_days": 90,
    "queries": ["AEO optimization", "content strategy"],
    "alert_on_changes": True,
    "weekly_reports": True
}

response = requests.post(
    "http://localhost:8000/api/monitoring",
    json=payload
)

if response.status_code == 202:
    monitor = response.json()
    print(f"✓ Monitoring started: {monitor['monitor_id']}")
    print(f"Duration: {payload['duration_days']} days")
else:
    print(f"✗ Error: {response.json()['error']}")
```

---

### Status Endpoints

#### GET /api/status/{workflow_id} - Get Workflow Status

Retrieve current status and results of any workflow (campaign, competitive analysis, or monitoring setup).

**Path Parameters**:
- `workflow_id` (string, required): Campaign ID, analysis ID, or monitor ID

**Response**: `200 OK`

```json
{
  "campaign_id": "campaign_20251109_103000",
  "status": "completed",
  "created_at": "2025-11-09T10:30:00Z",
  "completed_at": "2025-11-09T12:15:00Z",
  "progress": {
    "total_tasks": 8,
    "completed_tasks": 8,
    "completion_percentage": 100,
    "tasks": {
      "audit": "completed",
      "research": "completed",
      "optimize": "completed",
      "tracking": "completed",
      "report": "completed"
    }
  },
  "results": {
    "workflow_state": {
      "status": "completed",
      "total_tasks": 8,
      "completed_tasks": 8
    },
    "task_results": [
      {
        "task_type": "audit",
        "status": "completed",
        "summary": "E-E-A-T audit completed with 7/10 score",
        "output_data": {
          "scores": {
            "experience": 7.5,
            "expertise": 8.0,
            "authoritativeness": 6.5,
            "trustworthiness": 7.0
          },
          "recommendations": [
            "Add author bio with credentials",
            "Include more data-backed citations",
            "Improve content structure"
          ]
        }
      },
      {
        "task_type": "optimize",
        "status": "completed",
        "summary": "Content optimized with 23% improvement",
        "output_data": {
          "improvement_score": 23.4,
          "changes_made": 15,
          "optimized_sections": ["introduction", "methodology", "conclusion"]
        }
      }
    ]
  },
  "errors": []
}
```

**Response Fields**:
- `campaign_id` (string): Unique workflow identifier
- `status` (enum): Current workflow status (see [Workflow Status](#workflow-status))
- `created_at` (datetime): Workflow creation timestamp (UTC)
- `completed_at` (datetime, nullable): Completion timestamp if finished
- `progress` (object): Task completion progress tracking
  - `total_tasks` (integer): Total number of tasks
  - `completed_tasks` (integer): Number of completed tasks
  - `completion_percentage` (integer): Completion percentage (0-100)
  - `tasks` (object): Individual task statuses
- `results` (object, nullable): Workflow results if completed
- `errors` (array[string]): Error messages if any failures occurred

**Status Codes**:
- `200 OK`: Status retrieved successfully
- `404 Not Found`: Workflow ID does not exist
- `500 Internal Server Error`: Unexpected server error

**Error Response Example** (`404 Not Found`):
```json
{
  "error": "Workflow not found",
  "detail": "Workflow campaign_20251109_999 not found",
  "timestamp": "2025-11-09T10:30:00Z"
}
```

**cURL Example**:
```bash
curl http://localhost:8000/api/status/campaign_20251109_103000
```

**Python Example with Polling**:
```python
import requests
import time

def poll_workflow_status(workflow_id, max_attempts=60, delay=30):
    """Poll workflow status until completion or timeout"""
    url = f"http://localhost:8000/api/status/{workflow_id}"

    for attempt in range(max_attempts):
        response = requests.get(url)

        if response.status_code == 404:
            print(f"✗ Workflow {workflow_id} not found")
            return None

        data = response.json()
        status = data["status"]

        print(f"Attempt {attempt+1}: Status = {status}", end="")

        if "progress" in data:
            progress = data["progress"]
            pct = progress.get("completion_percentage", 0)
            print(f" ({pct}% complete)")
        else:
            print()

        if status in ["completed", "failed"]:
            return data

        time.sleep(delay)

    print("✗ Timeout waiting for workflow completion")
    return None

# Usage
workflow_id = "campaign_20251109_103000"
result = poll_workflow_status(workflow_id)

if result and result["status"] == "completed":
    print(f"✓ Workflow completed successfully")
    print(f"Tasks completed: {result['progress']['completed_tasks']}")
else:
    print(f"✗ Workflow did not complete successfully")
```

---

#### GET /api/campaigns - List All Campaigns

Retrieve a list of all workflow IDs with their current status.

**Response**: `200 OK`

```json
[
  {
    "id": "campaign_20251109_103000",
    "status": "completed",
    "created_at": "2025-11-09T10:30:00Z",
    "completed_at": "2025-11-09T12:15:00Z",
    "type": "campaign"
  },
  {
    "id": "analysis_20251109_110000",
    "status": "running",
    "created_at": "2025-11-09T11:00:00Z",
    "completed_at": null,
    "type": "analysis"
  },
  {
    "id": "monitor_20251109_113000",
    "status": "completed",
    "created_at": "2025-11-09T11:30:00Z",
    "completed_at": "2025-11-09T11:35:00Z",
    "type": "monitor"
  }
]
```

**Response Fields** (array of objects):
- `id` (string): Workflow identifier
- `status` (enum): Current status
- `created_at` (datetime): Creation timestamp
- `completed_at` (datetime, nullable): Completion timestamp
- `type` (enum): Workflow type (`campaign`, `analysis`, `monitor`)

**Status Codes**:
- `200 OK`: List retrieved successfully
- `500 Internal Server Error`: Unexpected server error

**cURL Example**:
```bash
curl http://localhost:8000/api/campaigns
```

**Python Example**:
```python
import requests

response = requests.get("http://localhost:8000/api/campaigns")
workflows = response.json()

print(f"Total workflows: {len(workflows)}")
for workflow in workflows:
    print(f"- {workflow['id']}: {workflow['status']} ({workflow['type']})")
```

---

#### DELETE /api/campaigns/{workflow_id} - Delete Campaign

Remove campaign data from storage.

**Path Parameters**:
- `workflow_id` (string, required): Workflow identifier to delete

**Response**: `200 OK`

```json
{
  "message": "Workflow campaign_20251109_103000 deleted successfully",
  "timestamp": "2025-11-09T15:00:00Z"
}
```

**Status Codes**:
- `200 OK`: Workflow deleted successfully
- `404 Not Found`: Workflow ID does not exist
- `500 Internal Server Error`: Unexpected server error

**cURL Example**:
```bash
curl -X DELETE http://localhost:8000/api/campaigns/campaign_20251109_103000
```

**Python Example**:
```python
import requests

workflow_id = "campaign_20251109_103000"
response = requests.delete(f"http://localhost:8000/api/campaigns/{workflow_id}")

if response.status_code == 200:
    print(f"✓ Workflow {workflow_id} deleted")
else:
    print(f"✗ Error: {response.json()['error']}")
```

---

## Data Models

### Campaign Modes

```python
class CampaignMode(str, Enum):
    minimal = "minimal"           # Quick audit (15-30 min)
    balanced = "balanced"         # Full optimization (45-90 min)
    comprehensive = "comprehensive"  # Enterprise-grade (2-4 hours)
```

### Optimization Levels

```python
class OptimizationLevel(str, Enum):
    conservative = "conservative"  # Preserve voice, minor improvements
    balanced = "balanced"          # Moderate changes, better clarity
    aggressive = "aggressive"      # Major restructuring, max impact
```

### Workflow Status

```python
class WorkflowStatus(str, Enum):
    pending = "pending"        # Created, not started
    running = "running"        # Currently executing
    completed = "completed"    # Successfully finished
    partial = "partial"        # Partially completed (some failures)
    failed = "failed"          # Critical failure
```

---

## Workflow Status

### Status Values

| Status | Description | Typical Duration | Next Steps |
|--------|-------------|------------------|------------|
| `pending` | Workflow accepted but not started | < 5 seconds | Wait for `running` status |
| `running` | Workflow currently executing | 15 min - 4 hours (mode-dependent) | Poll status endpoint periodically |
| `completed` | Workflow finished successfully | - | Retrieve results from `results` field |
| `partial` | Some tasks succeeded, some failed | - | Check `results` and `errors` fields |
| `failed` | Workflow failed completely | - | Check `errors` field, fix issues, retry |

### Progress Tracking

The `progress` object provides detailed task completion information:

```json
{
  "total_tasks": 8,
  "completed_tasks": 6,
  "completion_percentage": 75,
  "tasks": {
    "audit": "completed",
    "research": "completed",
    "optimize": "running",
    "tracking": "pending",
    "report": "pending"
  }
}
```

**Polling Recommendations**:
- Poll interval: 30-60 seconds
- Use exponential backoff: Start at 10s, increase to max 60s
- Implement timeout: Max 6 hours for comprehensive workflows
- Check `completion_percentage` for progress bars

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Common Causes | Resolution |
|------|---------|---------------|------------|
| `200` | OK | Request successful | Process response data |
| `202` | Accepted | Workflow started | Poll status endpoint |
| `400` | Bad Request | Invalid parameters | Check error details, fix request |
| `404` | Not Found | Workflow doesn't exist | Verify workflow ID |
| `422` | Unprocessable Entity | Validation failed | Check field constraints |
| `500` | Internal Server Error | Server error | Retry after delay, report if persists |

### Error Response Format

All errors return a consistent format:

```json
{
  "error": "Short error message",
  "detail": "Detailed error information",
  "timestamp": "2025-11-09T10:30:00Z"
}
```

### Common Error Scenarios

#### Invalid URL Format (422)

```json
{
  "detail": [
    {
      "loc": ["body", "url"],
      "msg": "invalid or missing URL scheme",
      "type": "value_error.url.scheme"
    }
  ]
}
```

**Fix**: Ensure URL starts with `http://` or `https://`

#### Invalid Mode (422)

```json
{
  "detail": [
    {
      "loc": ["body", "mode"],
      "msg": "value is not a valid enumeration member; permitted: 'minimal', 'balanced', 'comprehensive'",
      "type": "type_error.enum"
    }
  ]
}
```

**Fix**: Use valid mode: `minimal`, `balanced`, or `comprehensive`

#### Workflow Not Found (404)

```json
{
  "error": "Workflow not found",
  "detail": "Workflow campaign_20251109_999 not found",
  "timestamp": "2025-11-09T10:30:00Z"
}
```

**Fix**: Verify workflow ID, check `/api/campaigns` for available workflows

---

## Rate Limiting

**Current Implementation**: No rate limiting (development version)

**Production Recommendations**:

```
Rate Limit: 100 requests/minute per IP
Burst Limit: 20 requests/second
Rate Limit Response: 429 Too Many Requests
```

**Rate Limit Headers** (planned):
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1699450800
```

**Best Practices**:
- Implement exponential backoff on 429 responses
- Cache workflow results to reduce API calls
- Use webhooks (future) instead of polling when possible

---

## Best Practices

### 1. Async Workflow Pattern

Always treat POST requests as async operations:

```python
# ✓ Good - Async pattern
response = requests.post("/api/campaigns", json=payload)
campaign_id = response.json()["campaign_id"]

# Poll for completion
while True:
    status = requests.get(f"/api/status/{campaign_id}").json()
    if status["status"] in ["completed", "failed"]:
        break
    time.sleep(30)
```

```python
# ✗ Bad - Expecting immediate results
response = requests.post("/api/campaigns", json=payload)
results = response.json()["results"]  # This will fail!
```

### 2. Exponential Backoff

Implement intelligent polling with exponential backoff:

```python
def poll_with_backoff(workflow_id, initial_delay=10, max_delay=60):
    delay = initial_delay
    while True:
        status = get_status(workflow_id)
        if status["status"] in ["completed", "failed"]:
            return status

        time.sleep(delay)
        delay = min(delay * 1.5, max_delay)  # Exponential increase
```

### 3. Error Handling

Always handle errors gracefully:

```python
try:
    response = requests.post("/api/campaigns", json=payload)
    response.raise_for_status()  # Raise exception for 4xx/5xx

    campaign = response.json()
    # Process successful response

except requests.exceptions.HTTPError as e:
    if e.response.status_code == 422:
        # Handle validation errors
        errors = e.response.json()["detail"]
        for error in errors:
            print(f"Field {error['loc']}: {error['msg']}")
    elif e.response.status_code == 400:
        # Handle business logic errors
        print(f"Error: {e.response.json()['error']}")
    else:
        # Handle other errors
        print(f"HTTP error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### 4. Validation Before Submission

Validate parameters before making API calls:

```python
def validate_campaign_request(url, mode, duration_days):
    """Validate request before API call"""
    if not url.startswith(('http://', 'https://')):
        raise ValueError("URL must start with http:// or https://")

    if mode not in ['minimal', 'balanced', 'comprehensive']:
        raise ValueError("Mode must be minimal, balanced, or comprehensive")

    if not (1 <= duration_days <= 365):
        raise ValueError("Duration must be between 1 and 365 days")

    return True
```

### 5. Timeout Configuration

Set appropriate timeouts for requests:

```python
import requests

# Short timeout for health checks
response = requests.get("/health", timeout=5)

# Longer timeout for workflow creation
response = requests.post("/api/campaigns", json=payload, timeout=30)

# No timeout for status polling (use max_attempts instead)
response = requests.get(f"/api/status/{id}", timeout=None)
```

---

## Code Examples

### Complete Workflow Example (Python)

```python
import requests
import time
from typing import Optional, Dict

class AEOClient:
    """Production-ready AEO API client"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def check_health(self) -> bool:
        """Check API health"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.json()["status"] == "healthy"
        except Exception:
            return False

    def create_campaign(
        self,
        url: str,
        mode: str = "balanced",
        industry: Optional[str] = None,
        queries: Optional[list] = None
    ) -> str:
        """Create AEO campaign and return campaign ID"""
        payload = {
            "url": url,
            "mode": mode,
            "industry": industry,
            "queries": queries
        }

        response = self.session.post(
            f"{self.base_url}/api/campaigns",
            json=payload,
            timeout=30
        )
        response.raise_for_status()

        return response.json()["campaign_id"]

    def get_status(self, workflow_id: str) -> Dict:
        """Get workflow status"""
        response = self.session.get(
            f"{self.base_url}/api/status/{workflow_id}",
            timeout=10
        )
        response.raise_for_status()
        return response.json()

    def wait_for_completion(
        self,
        workflow_id: str,
        max_attempts: int = 120,
        initial_delay: int = 10,
        max_delay: int = 60
    ) -> Dict:
        """Poll workflow until completion with exponential backoff"""
        delay = initial_delay

        for attempt in range(max_attempts):
            status_data = self.get_status(workflow_id)
            status = status_data["status"]

            print(f"Attempt {attempt+1}: {status}", end="")
            if "progress" in status_data:
                pct = status_data["progress"].get("completion_percentage", 0)
                print(f" ({pct}%)")
            else:
                print()

            if status in ["completed", "failed", "partial"]:
                return status_data

            time.sleep(delay)
            delay = min(delay * 1.5, max_delay)

        raise TimeoutError(f"Workflow {workflow_id} did not complete in time")

    def run_campaign(self, url: str, **kwargs) -> Dict:
        """Complete workflow: create, poll, return results"""
        # Check API health
        if not self.check_health():
            raise ConnectionError("API is not healthy")

        # Create campaign
        campaign_id = self.create_campaign(url, **kwargs)
        print(f"✓ Campaign created: {campaign_id}")

        # Wait for completion
        result = self.wait_for_completion(campaign_id)

        if result["status"] == "completed":
            print(f"✓ Campaign completed successfully")
            return result["results"]
        else:
            print(f"✗ Campaign failed: {result.get('errors', [])}")
            raise RuntimeError(f"Campaign failed: {result['status']}")


# Usage
if __name__ == "__main__":
    client = AEOClient()

    try:
        results = client.run_campaign(
            url="https://example.com/article",
            mode="balanced",
            industry="SaaS",
            queries=["AEO optimization", "content strategy"]
        )

        print("\nResults:")
        print(f"Total tasks: {results['workflow_state']['total_tasks']}")
        print(f"Completed: {results['workflow_state']['completed_tasks']}")

        for task_result in results["task_results"]:
            print(f"- {task_result['task_type']}: {task_result['summary']}")

    except Exception as e:
        print(f"Error: {e}")
```

### Competitive Analysis Example

```python
def analyze_competitors(client: AEOClient, topic: str, urls: list):
    """Run competitive analysis"""
    payload = {
        "topic": topic,
        "competitor_urls": urls,
        "region": "US",
        "include_citations": True
    }

    response = client.session.post(
        f"{client.base_url}/api/competitive",
        json=payload,
        timeout=30
    )
    response.raise_for_status()

    analysis_id = response.json()["analysis_id"]
    print(f"✓ Analysis started: {analysis_id}")

    # Wait for completion
    result = client.wait_for_completion(analysis_id)
    return result["results"]


# Usage
competitors = [
    "https://competitor1.com/article",
    "https://competitor2.com/article",
    "https://competitor3.com/article"
]

analysis = analyze_competitors(client, "project management", competitors)
print(f"Competitors analyzed: {len(competitors)}")
```

### Citation Monitoring Example

```python
def setup_monitoring(client: AEOClient, url: str, duration_days: int = 90):
    """Setup citation monitoring"""
    payload = {
        "url": url,
        "duration_days": duration_days,
        "queries": ["main topic", "related topic"],
        "alert_on_changes": True,
        "weekly_reports": True
    }

    response = client.session.post(
        f"{client.base_url}/api/monitoring",
        json=payload,
        timeout=30
    )
    response.raise_for_status()

    monitor_id = response.json()["monitor_id"]
    print(f"✓ Monitoring started: {monitor_id}")

    # Wait for initial setup
    result = client.wait_for_completion(monitor_id, max_attempts=20)
    return result["results"]


# Usage
monitoring = setup_monitoring(client, "https://example.com/article", 90)
print(f"Monitoring configured for 90 days")
```

---

## Webhooks (Future)

**Planned Feature**: Webhook support for async notifications

```json
{
  "webhook_url": "https://yourapp.com/webhooks/aeo",
  "events": ["workflow.completed", "workflow.failed", "citation.changed"]
}
```

**Webhook Payload Example**:
```json
{
  "event": "workflow.completed",
  "workflow_id": "campaign_20251109_103000",
  "status": "completed",
  "timestamp": "2025-11-09T12:15:00Z",
  "results_url": "/api/status/campaign_20251109_103000"
}
```

---

## Support & Resources

- **Interactive API Docs**: `http://localhost:8000/docs`
- **Alternative Docs**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/health`
- **Error Reference**: See [ERROR_CODES.md](./src/api/ERROR_CODES.md)
- **Architecture**: See [ARCHITECTURE.md](./ARCHITECTURE.md)
- **GitHub Issues**: Report bugs and feature requests

---

## Changelog

### v1.5.0 (2025-11-09)
- Initial API release
- 7 REST endpoints
- Async workflow execution
- Comprehensive error handling
- Production-ready documentation

---

**End of API Reference**

*For cost optimization strategies, see [COST_OPTIMIZATION.md](./COST_OPTIMIZATION.md)*

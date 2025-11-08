# API Error Codes and Status Responses

## HTTP Status Codes

The AEO Multi-Agent API uses standard HTTP status codes to indicate the success or failure of requests.

### Success Codes (2xx)

#### 200 OK
**Endpoints**: GET /health, GET /, GET /api/campaigns, GET /api/status/{workflow_id}

**Description**: Request successful, data returned in response body.

**Example Response**:
```json
{
  "status": "healthy",
  "version": "1.5.0",
  "timestamp": "2025-01-08T12:00:00Z",
  "agents_registered": 6
}
```

#### 202 Accepted
**Endpoints**: POST /api/campaigns, POST /api/competitive, POST /api/monitoring

**Description**: Request accepted for processing. Workflow started in background. Use workflow ID to check status.

**Example Response**:
```json
{
  "campaign_id": "campaign_20250108_001",
  "status": "running",
  "created_at": "2025-01-08T10:30:00Z",
  "message": "Campaign workflow started successfully. Check status at /api/status/{campaign_id}"
}
```

**Follow-up**: Poll GET /api/status/{workflow_id} to track progress.

---

### Client Error Codes (4xx)

#### 400 Bad Request
**Endpoints**: All POST endpoints

**Cause**: Invalid request data that passed validation but failed business logic checks.

**Common Scenarios**:
- Invalid URL format (must start with http:// or https://)
- Workflow validation failed
- Invalid parameter combination

**Example Response**:
```json
{
  "error": "Invalid URL format",
  "detail": "URL must start with http:// or https://",
  "timestamp": "2025-01-08T10:30:00Z"
}
```

**Resolution**: Check request parameters against API documentation. Verify URL format, mode values, and parameter ranges.

#### 404 Not Found
**Endpoints**: GET /api/status/{workflow_id}, DELETE /api/campaigns/{workflow_id}

**Cause**: Requested workflow ID does not exist.

**Example Response**:
```json
{
  "error": "Workflow not found",
  "detail": "Workflow campaign_20250108_999 not found",
  "timestamp": "2025-01-08T10:30:00Z"
}
```

**Resolution**: Verify workflow ID is correct. Check GET /api/campaigns to list all available workflows.

#### 422 Unprocessable Entity
**Endpoints**: All POST endpoints

**Cause**: Request validation failed (Pydantic validation error).

**Common Scenarios**:

1. **Invalid URL**:
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

2. **Invalid Mode**:
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

3. **Invalid Duration** (out of range):
```json
{
  "detail": [
    {
      "loc": ["body", "tracking_duration_days"],
      "msg": "ensure this value is less than or equal to 365",
      "type": "value_error.number.not_le"
    }
  ]
}
```

4. **Too Many Competitors**:
```json
{
  "detail": [
    {
      "loc": ["body", "competitor_urls"],
      "msg": "ensure this value has at most 10 items",
      "type": "value_error.list.max_items"
    }
  ]
}
```

5. **Missing Required Field**:
```json
{
  "detail": [
    {
      "loc": ["body", "url"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Resolution**: Check validation error details. Fix request payload according to field constraints:
- **url**: Must be valid HTTP/HTTPS URL
- **mode**: Must be "minimal", "balanced", or "comprehensive"
- **optimization_level**: Must be "conservative", "balanced", or "aggressive"
- **tracking_duration_days**: Must be between 1 and 365
- **competitor_urls**: Must have 1-10 items
- **duration_days**: Must be between 1 and 365

---

### Server Error Codes (5xx)

#### 500 Internal Server Error
**Endpoints**: All endpoints

**Cause**: Unexpected server error during request processing.

**Example Response**:
```json
{
  "error": "Internal server error",
  "detail": "Unexpected error occurred during workflow execution",
  "timestamp": "2025-01-08T10:30:00Z"
}
```

**Resolution**:
1. Check API health: GET /health
2. Retry request after a delay
3. If error persists, report to system administrator

---

## Workflow Status Values

When checking workflow status (GET /api/status/{workflow_id}), the `status` field indicates current state:

### pending
**Description**: Workflow accepted but not yet started.

**Typical Duration**: < 5 seconds

**Next Steps**: Wait for status to change to "running".

### running
**Description**: Workflow currently executing.

**Typical Duration**:
- Minimal mode: 15-30 minutes
- Balanced mode: 45-90 minutes
- Comprehensive mode: 2-4 hours

**Progress Tracking**: Use `progress.completion_percentage` to track execution.

### completed
**Description**: Workflow finished successfully. Results available.

**Next Steps**: Retrieve results from `results` field.

### partial
**Description**: Workflow partially completed. Some tasks succeeded, some failed.

**Next Steps**:
1. Check `results` field for completed task results
2. Check `errors` field for failure details
3. Consider re-running failed tasks

### failed
**Description**: Workflow failed completely.

**Next Steps**:
1. Check `errors` field for failure reason
2. Fix issues and retry workflow
3. If error persists, report to system administrator

---

## Common Error Scenarios and Solutions

### Scenario 1: Invalid URL Format
**Error**: 422 Unprocessable Entity
```json
{"loc": ["body", "url"], "msg": "invalid or missing URL scheme"}
```

**Solution**:
```json
// ❌ Wrong
{"url": "example.com"}

// ✅ Correct
{"url": "https://example.com"}
```

### Scenario 2: Campaign Mode Typo
**Error**: 422 Unprocessable Entity
```json
{"loc": ["body", "mode"], "msg": "value is not a valid enumeration member"}
```

**Solution**:
```json
// ❌ Wrong
{"mode": "medium"}

// ✅ Correct
{"mode": "balanced"}
```

### Scenario 3: Tracking Duration Out of Range
**Error**: 422 Unprocessable Entity
```json
{"loc": ["body", "tracking_duration_days"], "msg": "ensure this value is less than or equal to 365"}
```

**Solution**:
```json
// ❌ Wrong
{"tracking_duration_days": 500}

// ✅ Correct (max 365 days)
{"tracking_duration_days": 365}
```

### Scenario 4: Too Many Competitors
**Error**: 422 Unprocessable Entity
```json
{"loc": ["body", "competitor_urls"], "msg": "ensure this value has at most 10 items"}
```

**Solution**:
```json
// ❌ Wrong (15 URLs)
{"competitor_urls": ["url1", "url2", ..., "url15"]}

// ✅ Correct (max 10 URLs)
{"competitor_urls": ["url1", "url2", ..., "url10"]}
```

### Scenario 5: Workflow Not Found
**Error**: 404 Not Found
```json
{"error": "Workflow campaign_20250108_999 not found"}
```

**Solution**:
1. Verify workflow ID matches the one returned from creation endpoint
2. List all workflows: GET /api/campaigns
3. Workflow may have been deleted

---

## Rate Limiting

**Current Implementation**: No rate limiting (development version)

**Production Recommendation**:
- Rate limit: 100 requests/minute per IP
- Burst limit: 20 requests/second
- Exceeded limit response: 429 Too Many Requests

---

## Best Practices

1. **Always check HTTP status code** before processing response
2. **Handle 202 Accepted properly** - poll status endpoint, don't expect immediate results
3. **Implement exponential backoff** when polling status endpoint
4. **Parse validation errors** - they provide specific field-level guidance
5. **Monitor health endpoint** - check /health before critical operations
6. **Log error details** - timestamp and detail fields help debugging

---

## Support

For additional help:
- **API Documentation**: /docs (Swagger UI)
- **Alternative Docs**: /redoc (ReDoc)
- **Health Check**: /health
- **List Workflows**: GET /api/campaigns

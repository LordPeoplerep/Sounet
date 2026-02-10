# Souent API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication

Some endpoints require authorization via API key in the `X-API-Key` header:

```bash
curl -H "X-API-Key: your-api-key-here" http://localhost:8000/api/v1/endpoint
```

**Authorization Tiers:**
- **basic**: Default tier, standard interaction
- **advisory**: Enhanced context access (requires ADVISORY_API_KEY)
- **admin_ready**: System administration (requires ADMIN_API_KEY)

---

## Endpoints

### Chat Endpoints

#### POST /api/v1/chat/message
Send a message to Souent AI.

**Request:**
```json
{
  "message": "What is the purpose of Souent?",
  "session_id": "session_abc123",
  "user_id": "user_456",
  "authorization_tier": "basic"
}
```

**Response:**
```json
{
  "response": "Souent is a logic-first AI chatbot...",
  "session_id": "session_abc123",
  "model": "SLM-A1 (Anthroi-1)",
  "timestamp": "2024-01-15T10:30:00",
  "metadata": {
    "authorization_tier": "basic",
    "user_id": "user_456"
  }
}
```

#### GET /api/v1/chat/history/{session_id}
Retrieve conversation history for a session.

**Response:**
```json
{
  "session_id": "session_abc123",
  "messages": [
    {
      "role": "user",
      "content": "Hello",
      "timestamp": "2024-01-15T10:29:00"
    },
    {
      "role": "assistant",
      "content": "Hello. How can I assist you?",
      "timestamp": "2024-01-15T10:29:05"
    }
  ],
  "created_at": "2024-01-15T10:29:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

#### DELETE /api/v1/chat/session/{session_id}
Clear a conversation session.

**Response:**
```json
{
  "status": "success",
  "message": "Session session_abc123 cleared",
  "timestamp": "2024-01-15T10:31:00"
}
```

#### POST /api/v1/chat/session/new
Create a new conversation session.

**Response:**
```json
{
  "session_id": "session_xyz789",
  "created_at": "2024-01-15T10:32:00",
  "status": "active"
}
```

---

### Memory Endpoints

#### GET /api/v1/memory/preferences/{user_id}
Retrieve user preferences.

**Response:**
```json
{
  "user_id": "user_456",
  "tone_preference": "balanced",
  "max_response_length": 500,
  "enable_clarification_questions": true,
  "custom_settings": {},
  "updated_at": "2024-01-15T10:00:00"
}
```

#### PUT /api/v1/memory/preferences
Update user preferences.

**Request:**
```json
{
  "user_id": "user_456",
  "tone_preference": "concise",
  "max_response_length": 300,
  "enable_clarification_questions": false
}
```

**Response:**
```json
{
  "user_id": "user_456",
  "tone_preference": "concise",
  "max_response_length": 300,
  "enable_clarification_questions": false,
  "updated_at": "2024-01-15T10:35:00"
}
```

#### GET /api/v1/memory/canon
Retrieve canon memory (read-only system knowledge).

**Response:**
```json
{
  "system_knowledge": {
    "developer": "VelaPlex Systems",
    "application": "Souent"
  },
  "model_info": {
    "current_model": "SLM-A1",
    "model_name": "Anthroi-1",
    "version": "1.0.0",
    "characteristics": [
      "Logic-first reasoning",
      "Conservative inference"
    ]
  },
  "locked": true,
  "version": "1.0.0"
}
```

#### PUT /api/v1/memory/canon
Update canon memory (ADMIN ONLY).

**Headers:**
```
X-API-Key: admin-your-secure-key-here
```

**Request:**
```json
{
  "system_knowledge": {
    "new_key": "new_value"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Canon memory updated successfully",
  "timestamp": "2024-01-15T10:40:00",
  "updated_fields": ["system_knowledge"]
}
```

#### GET /api/v1/memory/canon/info
Get canon memory metadata.

**Response:**
```json
{
  "locked": true,
  "version": "1.0.0",
  "last_updated": "2024-01-15T10:40:00",
  "model_name": "Anthroi-1",
  "model_version": "1.0.0"
}
```

---

### System Endpoints

#### GET /api/v1/system/health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "app_name": "Souent",
  "version": "1.0.0",
  "model": "SLM-A1 (Anthroi-1)",
  "memory_storage": "file",
  "uptime_seconds": 3600.0,
  "timestamp": "2024-01-15T11:00:00"
}
```

#### GET /api/v1/system/models
Get available AI models.

**Response:**
```json
{
  "current_model": {
    "model_designation": "SLM-A1",
    "model_name": "Anthroi-1",
    "version": "1.0.0",
    "provider": "openai",
    "underlying_model": "gpt-4",
    "characteristics": [
      "Logic-first reasoning",
      "Conservative inference",
      "Explicit uncertainty handling",
      "No emotional simulation",
      "No immersive roleplay"
    ]
  },
  "available_models": [
    {
      "id": "SLM-A1",
      "name": "Anthroi-1",
      "version": "1.0.0",
      "status": "active"
    }
  ],
  "future_models": [
    {
      "id": "SLM-A2",
      "name": "Anthroi-2",
      "status": "planned"
    }
  ]
}
```

#### GET /api/v1/system/status
Detailed system status.

**Response:**
```json
{
  "application": {
    "name": "Souent",
    "version": "1.0.0",
    "environment": "development",
    "debug_mode": true
  },
  "model": {
    "designation": "SLM-A1",
    "name": "Anthroi-1",
    "provider": "openai",
    "underlying_model": "gpt-4"
  },
  "memory": {
    "storage_type": "file",
    "layers": [
      "Ephemeral Session Memory",
      "Persistent User Preferences",
      "Locked Canon Memory"
    ]
  },
  "features": {
    "tone_harmonization": true,
    "context_weave": true,
    "authorization_tiers": ["basic", "advisory", "admin_ready"],
    "rate_limiting": true
  },
  "uptime_seconds": 3600.0,
  "status": "operational"
}
```

#### GET /api/v1/system/capabilities
Get Souent's capabilities and limitations.

**Response:**
```json
{
  "capabilities": [
    "Logic-first reasoning and analysis",
    "Code review and debugging assistance",
    "Technical documentation analysis"
  ],
  "characteristics": [
    "Conservative inference",
    "Explicit uncertainty handling",
    "No emotional simulation"
  ],
  "limitations": [
    "Cannot access real-time information",
    "Cannot execute code",
    "Cannot claim emotions"
  ],
  "authorization_tiers": {
    "basic": "Standard user interaction",
    "advisory": "Enhanced context access",
    "admin_ready": "System administration"
  }
}
```

---

## Error Responses

All endpoints may return error responses in the following format:

**400 Bad Request:**
```json
{
  "error": "Validation error",
  "detail": "Message cannot be empty",
  "timestamp": "2024-01-15T11:00:00"
}
```

**403 Forbidden:**
```json
{
  "error": "Forbidden",
  "detail": "Admin authorization required",
  "timestamp": "2024-01-15T11:00:00"
}
```

**404 Not Found:**
```json
{
  "error": "Not found",
  "detail": "Session not found",
  "timestamp": "2024-01-15T11:00:00"
}
```

**429 Too Many Requests:**
```json
{
  "error": "Rate limit exceeded",
  "detail": "Maximum 60 requests per 60 seconds",
  "retry_after": 60
}
```

**500 Internal Server Error:**
```json
{
  "error": "Internal server error",
  "detail": "An error occurred processing your request",
  "timestamp": "2024-01-15T11:00:00"
}
```

---

## Rate Limiting

Default rate limits:
- **60 requests per 60 seconds** per IP address

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1705318860
```

---

## Examples

### cURL Examples

**Send a message:**
```bash
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain logic-first reasoning",
    "session_id": "session_123"
  }'
```

**Get conversation history:**
```bash
curl http://localhost:8000/api/v1/chat/history/session_123
```

**Update user preferences:**
```bash
curl -X PUT http://localhost:8000/api/v1/memory/preferences \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_456",
    "tone_preference": "detailed"
  }'
```

### Python Examples

```python
import requests

# Send a message
response = requests.post(
    'http://localhost:8000/api/v1/chat/message',
    json={
        'message': 'Hello, Souent!',
        'session_id': 'session_123'
    }
)
print(response.json())

# Get system status
status = requests.get('http://localhost:8000/api/v1/system/status')
print(status.json())
```

### JavaScript Examples

```javascript
// Send a message
const response = await fetch('http://localhost:8000/api/v1/chat/message', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    message: 'Hello, Souent!',
    session_id: 'session_123'
  })
});
const data = await response.json();
console.log(data);
```

---

## Interactive Documentation

FastAPI provides interactive API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

These interfaces allow you to:
- Browse all endpoints
- View request/response schemas
- Test endpoints directly in the browser

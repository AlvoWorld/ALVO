# ALVO Platform API Documentation

## Overview

The ALVO Platform provides a RESTful API for managing AI agents, conversations, knowledge bases, and system monitoring. The API is built with FastAPI and follows OpenAPI 3.0 standards.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

Currently, the API does not require authentication. In production, JWT tokens should be implemented.

## API Endpoints

### Agents API

#### Create Agent
```http
POST /api/v1/agents/
```

**Request Body:**
```json
{
  "name": "string",
  "description": "string",
  "model": "string",
  "system_prompt": "string",
  "is_active": true
}
```

**Response:**
```json
{
  "id": 1,
  "name": "string",
  "description": "string",
  "model": "string",
  "system_prompt": "string",
  "is_active": true,
  "created_at": "2026-03-29T19:05:47Z",
  "updated_at": "2026-03-29T19:05:47Z"
}
```

#### List Agents
```http
GET /api/v1/agents/
```

**Query Parameters:**
- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum number of records to return (default: 20)
- `active_only` (bool, optional): Filter active agents only (default: false)

**Response:**
```json
{
  "agents": [
    {
      "id": 1,
      "name": "string",
      "description": "string",
      "model": "string",
      "is_active": true,
      "created_at": "2026-03-29T19:05:47Z"
    }
  ],
  "total": 1
}
```

#### Get Agent
```http
GET /api/v1/agents/{agent_id}
```

**Path Parameters:**
- `agent_id` (int): Agent ID

**Response:** Agent object

#### Update Agent
```http
PUT /api/v1/agents/{agent_id}
```

**Request Body:**
```json
{
  "name": "string",
  "description": "string",
  "model": "string",
  "system_prompt": "string",
  "is_active": false
}
```

**Response:** Updated agent object

#### Delete Agent
```http
DELETE /api/v1/agents/{agent_id}
```

**Response:**
```json
{
  "message": "Agent deleted",
  "id": 1
}
```

#### Get Agent Statistics
```http
GET /api/v1/agents/{agent_id}/stats
```

**Response:**
```json
{
  "agent_id": 1,
  "agent_name": "string",
  "conversation_count": 42,
  "knowledge_entries": 10,
  "is_active": true
}
```

### Conversations API

#### Create Conversation
```http
POST /api/v1/conversations/
```

**Request Body:**
```json
{
  "agent_id": 1,
  "session_id": "string",
  "role": "user",
  "content": "string"
}
```

**Response:**
```json
{
  "id": 1,
  "agent_id": 1,
  "session_id": "string",
  "role": "user",
  "content": "string",
  "created_at": "2026-03-29T19:05:47Z"
}
```

#### List Conversations
```http
GET /api/v1/conversations/
```

**Query Parameters:**
- `agent_id` (int, optional): Filter by agent ID
- `session_id` (string, optional): Filter by session ID
- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum number of records to return (default: 20)

**Response:**
```json
{
  "results": [
    {
      "id": 1,
      "agent_id": 1,
      "session_id": "string",
      "role": "user",
      "content": "string",
      "created_at": "2026-03-29T19:05:47Z"
    }
  ],
  "total": 1,
  "query": ""
}
```

#### Search Conversations
```http
POST /api/v1/conversations/search
```

**Request Body:**
```json
{
  "query": "string",
  "agent_id": 1,
  "session_id": "string",
  "limit": 20
}
```

**Response:** ConversationSearchResponse object

#### Get Conversation
```http
GET /api/v1/conversations/{conversation_id}
```

**Response:** Conversation object

### Documents API

#### Upload Document
```http
POST /api/v1/documents/upload
```

**Request Body:** `multipart/form-data`
- `file`: Document file (PDF, TXT, MD)
- `agent_id`: Target agent ID

**Response:**
```json
{
  "id": 1,
  "filename": "string",
  "file_type": "string",
  "file_size": 1024,
  "agent_id": 1,
  "created_at": "2026-03-29T19:05:47Z"
}
```

#### List Documents
```http
GET /api/v1/documents/
```

**Query Parameters:**
- `agent_id` (int, optional): Filter by agent ID

**Response:** Array of document objects

#### Delete Document
```http
DELETE /api/v1/documents/{document_id}
```

**Response:**
```json
{
  "message": "Document deleted",
  "id": 1
}
```

### Knowledge Base API

#### Add Knowledge Entry
```http
POST /api/v1/knowledge-base/
```

**Request Body:**
```json
{
  "agent_id": 1,
  "content": "string",
  "metadata": {}
}
```

**Response:**
```json
{
  "id": 1,
  "agent_id": 1,
  "content": "string",
  "metadata": {},
  "created_at": "2026-03-29T19:05:47Z"
}
```

#### Search Knowledge Base
```http
POST /api/v1/knowledge-base/search
```

**Request Body:**
```json
{
  "query": "string",
  "agent_id": 1,
  "limit": 10
}
```

**Response:** Array of matching knowledge entries

### LLM API

#### Chat Completion
```http
POST /api/v1/llm/chat
```

**Request Body:**
```json
{
  "agent_id": 1,
  "messages": [
    {
      "role": "user",
      "content": "string"
    }
  ],
  "model": "string",
  "temperature": 0.7,
  "max_tokens": 1000
}
```

**Response:**
```json
{
  "id": "string",
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "string"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 100,
    "completion_tokens": 50,
    "total_tokens": 150
  }
}
```

## WebSocket API

### Connection
```
ws://localhost:8000/ws
```

### Message Types

#### Agent Status Update
```json
{
  "type": "agent_status",
  "data": {
    "agent_id": 1,
    "status": "active",
    "timestamp": "2026-03-29T19:05:47Z"
  }
}
```

#### Token Usage Update
```json
{
  "type": "token_usage",
  "data": {
    "agent_id": 1,
    "tokens_used": 150,
    "cost": 0.00225,
    "timestamp": "2026-03-29T19:05:47Z"
  }
}
```

#### System Metrics
```json
{
  "type": "system_metrics",
  "data": {
    "cpu_usage": 45.2,
    "memory_usage": 68.5,
    "disk_usage": 32.1,
    "active_agents": 5,
    "timestamp": "2026-03-29T19:05:47Z"
  }
}
```

#### Heartbeat
```json
{
  "type": "heartbeat",
  "data": {
    "timestamp": "2026-03-29T19:05:47Z",
    "status": "alive"
  }
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 409 Conflict
```json
{
  "detail": "Resource already exists"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

Currently, no rate limiting is implemented. In production, implement rate limiting per IP or API key.

## Data Models

### Agent
```typescript
interface Agent {
  id: number;
  name: string;
  description: string;
  model: string;
  system_prompt: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}
```

### Conversation
```typescript
interface Conversation {
  id: number;
  agent_id: number;
  session_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  created_at: string;
}
```

### Document
```typescript
interface Document {
  id: number;
  filename: string;
  file_type: string;
  file_size: number;
  agent_id: number;
  created_at: string;
}
```

### KnowledgeEntry
```typescript
interface KnowledgeEntry {
  id: number;
  agent_id: number;
  content: string;
  metadata: Record<string, any>;
  created_at: string;
}
```

## SDK Examples

### Python
```python
import requests

# Create agent
response = requests.post("http://localhost:8000/api/v1/agents/", json={
    "name": "My Agent",
    "description": "A helpful assistant",
    "model": "gpt-4",
    "system_prompt": "You are a helpful assistant."
})
agent = response.json()

# Chat completion
response = requests.post("http://localhost:8000/api/v1/llm/chat", json={
    "agent_id": agent["id"],
    "messages": [{"role": "user", "content": "Hello!"}]
})
print(response.json()["choices"][0]["message"]["content"])
```

### JavaScript
```javascript
// Create agent
const response = await fetch('http://localhost:8000/api/v1/agents/', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    name: 'My Agent',
    description: 'A helpful assistant',
    model: 'gpt-4',
    system_prompt: 'You are a helpful assistant.'
  })
});
const agent = await response.json();

// Chat completion
const chatResponse = await fetch('http://localhost:8000/api/v1/llm/chat', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    agent_id: agent.id,
    messages: [{role: 'user', content: 'Hello!'}]
  })
});
const result = await chatResponse.json();
console.log(result.choices[0].message.content);
```

## Interactive Documentation

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Changelog

### v1.0.0 (2026-03-29)
- Initial API release
- Agent management endpoints
- Conversation logging and search
- Document upload and management
- Knowledge base operations
- LLM integration with OpenRouter
- WebSocket real-time updates
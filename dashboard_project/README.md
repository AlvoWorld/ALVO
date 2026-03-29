# OSYA Web Dashboard

A comprehensive web dashboard for managing AI agents, knowledge bases, and conversations.

## Features

### Dashboard (NEW!)
- **Token Usage Charts** - Real-time visualization of token consumption
  - Area and bar chart views
  - Time range filtering (1H, 6H, 24H, 7D, 30D)
  - Usage breakdown by agent and AI model
  - Cost tracking

- **Agent Status Monitoring** - Real-time agent health dashboard
  - Live status indicators (Active, Idle, Busy, Error, Offline)
  - Token usage progress bars per agent
  - Task completion tracking
  - Click-to-expand agent details

- **System Metrics** - Infrastructure monitoring
  - CPU, Memory, Disk usage gauges
  - Active agent count
  - Task statistics

- **Model Distribution** - AI model usage analytics
  - Pie charts for usage by agent
  - Token distribution across models

### Backend Features
1. **File Upload for Agent Knowledge Base**
   - Upload PDF, TXT, MD documents
   - Drag-and-drop interface
   - Progress tracking

2. **Document Management**
   - View uploaded documents
   - Search across documents
   - Delete documents
   - Document preview

3. **Agent Memory/Persistent Context**
   - View agent conversations
   - Manage agent memory
   - Context persistence settings

4. **Search Across All Agent Conversations**
   - Full-text search
   - Filter by agent, date, content
   - Search results highlighting

5. **LLM Integration**
   - OpenRouter API integration with rate-limit retry
   - Batch concurrent chat completions
   - Multiple model support

## Tech Stack

### Frontend
- React 18
- TypeScript
- Tailwind CSS
- Recharts (data visualization)
- WebSocket (real-time updates)

### Backend
- FastAPI
- SQLAlchemy
- SQLite/PostgreSQL
- File Storage: Local filesystem

## Installation

### Backend

```bash
cd dashboard_project
pip install -r requirements.txt
```

### Frontend

```bash
cd dashboard_project/frontend
npm install
```

## Running

### Backend

```bash
cd dashboard_project
uvicorn app.main:app --reload
```

Backend will be available at `http://localhost:8000`

### Frontend

```bash
cd dashboard_project/frontend
npm start
```

Frontend will be available at `http://localhost:3000`

## Project Structure

```
dashboard_project/
├── app/                    # Backend (FastAPI)
│   ├── main.py
│   ├── routers/
│   ├── services/
│   └── models/
├── frontend/               # Frontend (React)
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── pages/          # Page components
│   │   ├── hooks/          # React hooks
│   │   ├── services/       # API & WebSocket
│   │   ├── types/          # TypeScript types
│   │   └── utils/          # Utility functions
│   └── package.json
├── tests/                  # Backend tests
├── requirements.txt
└── README.md
```

## API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## WebSocket Endpoints

- `ws://localhost:8000/ws` - Real-time updates

### Message Types
- `agent_status` - Agent status changes
- `token_usage` - New token usage data
- `system_metrics` - System metric updates
- `heartbeat` - Agent heartbeat signals

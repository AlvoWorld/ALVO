# ALVO Platform

A comprehensive AI agent management platform with real-time monitoring, knowledge base management, and conversation tracking.

## Features

### 🤖 Agent Management
- Create and configure AI agents
- Monitor agent status in real-time
- Track token usage and costs
- Manage agent knowledge bases

### 💬 Conversation Tracking
- Log all agent conversations
- Search across conversation history
- Session-based context management
- Real-time WebSocket updates

### 📚 Knowledge Base
- Upload documents (PDF, TXT, MD)
- Search across knowledge entries
- Agent-specific knowledge isolation
- Metadata management

### 📊 Real-time Dashboard
- Token usage charts and analytics
- System metrics monitoring
- Agent status indicators
- Model distribution visualization

### 🔌 LLM Integration
- OpenRouter API integration
- Multiple model support
- Rate limit handling
- Batch processing capabilities

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL (optional)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd alvo-platform
```

2. **Backend Setup**
```bash
cd dashboard_project
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

3. **Frontend Setup**
```bash
cd dashboard_project/frontend
npm install
npm start
```

4. **Access the Application**
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Project Structure

```
alvo-platform/
├── dashboard_project/          # Main application
│   ├── app/                   # Backend (FastAPI)
│   │   ├── routers/          # API endpoints
│   │   ├── services/         # Business logic
│   │   ├── models.py         # Database models
│   │   └── main.py           # FastAPI app
│   ├── frontend/             # Frontend (React)
│   │   ├── src/
│   │   │   ├── components/   # UI components
│   │   │   ├── pages/        # Page components
│   │   │   ├── hooks/        # React hooks
│   │   │   └── services/     # API services
│   │   └── package.json
│   ├── tests/                # Backend tests
│   ├── requirements.txt      # Python dependencies
│   └── README.md            # Project documentation
├── API_DOCUMENTATION.md      # API reference
├── INSTALLATION_GUIDE.md     # Setup instructions
└── README.md                # This file
```

## API Reference

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/agents/` | GET, POST | Agent management |
| `/conversations/` | GET, POST | Conversation tracking |
| `/documents/` | GET, POST, DELETE | Document management |
| `/knowledge-base/` | GET, POST, DELETE | Knowledge management |
| `/llm/chat` | POST | LLM integration |

### WebSocket Events

| Event | Description |
|-------|-------------|
| `agent_status` | Agent status changes |
| `token_usage` | Token consumption updates |
| `system_metrics` | System resource usage |
| `heartbeat` | Agent heartbeat signals |

For detailed API documentation, see [API_DOCUMENTATION.md](API_DOCUMENTATION.md).

## Configuration

### Environment Variables

Create `.env` files in the respective directories:

**Backend (`dashboard_project/.env`)**
```env
DATABASE_URL=sqlite:///./app.db
OPENROUTER_API_KEY=your_api_key
SECRET_KEY=your_secret_key
```

**Frontend (`dashboard_project/frontend/.env`)**
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000/ws
```

## Development

### Running Tests
```bash
# Backend tests
cd dashboard_project
pytest tests/

# Frontend tests
cd dashboard_project/frontend
npm test
```

### Code Quality
```bash
# Python linting
flake8 app/

# JavaScript linting
cd dashboard_project/frontend
npm run lint
```

## Deployment

### Docker Deployment
```bash
docker-compose up -d
```

### Manual Deployment
See [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) for detailed deployment instructions.

## Architecture

### Backend Stack
- **FastAPI** - Web framework
- **SQLAlchemy** - ORM
- **SQLite/PostgreSQL** - Database
- **WebSockets** - Real-time communication

### Frontend Stack
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Recharts** - Data visualization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

[License information]

## Support

For issues and questions:
- Create an issue in the repository
- Check the documentation
- Contact the development team

## Changelog

### v1.0.0 (2026-03-29)
- Initial release
- Agent management system
- Conversation tracking
- Knowledge base management
- Real-time dashboard
- LLM integration
- WebSocket updates

---

**Built with ❤️ by the ALVO Platform Team**
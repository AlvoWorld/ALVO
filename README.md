# OSYA Agents — Open Source AI Agent Platform

A simple, reliable AI agent orchestration platform that works with **any LLM provider** (OpenRouter, Anthropic, Google, etc.) without vendor lock-in.

## Features

- 🤖 **Multi-Agent System** — Create and manage AI agent teams
- 🔌 **Any LLM Provider** — OpenRouter, Anthropic, Google, Groq, local models
- 📋 **Task Management** — Create, assign, and track tasks
- 🛠️ **Tools** — Bash, file operations, web search, API calls
- 💬 **Telegram Integration** — Communicate with agents via Telegram
- 📊 **Web Dashboard** — Manage everything from a browser
- ⏰ **Heartbeat Scheduler** — Automatic periodic agent runs
- 🔗 **Multi-Agent Coordination** — Agents can delegate to each other

## Quick Start

```bash
# Clone
git clone https://github.com/sds333/osya-agents.git
cd osya-agents

# Install
pip install -r requirements.txt

# Configure
cp config.yaml.example config.yaml
# Edit config.yaml with your API keys

# Run
python main.py
```

## Configuration

```yaml
providers:
  openrouter:
    api_key: "sk-or-v1-..."
    base_url: "https://openrouter.ai/api/v1"
  anthropic:
    api_key: "sk-ant-..."
  google:
    api_key: "..."

database:
  path: "osya.db"

server:
  host: "0.0.0.0"
  port: 8000

telegram:
  bot_token: "..."

agents:
  - name: CEO
    provider: openrouter
    model: anthropic/claude-sonnet-4
    instructions: "You are the CEO..."
    heartbeat: 3600
    reports_to: null
```

## Agent Configuration

Each agent has:
- **name** — unique identifier
- **provider** — LLM provider (openrouter, anthropic, google)
- **model** — model ID
- **instructions** — agent prompt/instructions
- **heartbeat** — seconds between automatic runs
- **reports_to** — parent agent name (null for top-level)
- **tools** — list of allowed tools

## Tools

- `bash` — Execute shell commands
- `read` — Read files
- `write` — Write files
- `web_search` — Search the web
- `web_fetch` — Fetch web pages
- `send_telegram` — Send Telegram messages

## API Endpoints

- `GET /api/agents` — List agents
- `POST /api/agents` — Create agent
- `GET /api/tasks` — List tasks
- `POST /api/tasks` — Create task
- `POST /api/agents/{name}/run` — Run agent
- `GET /api/agents/{name}/runs` — Get run history

## License

MIT

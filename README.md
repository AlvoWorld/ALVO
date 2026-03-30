# AXIOM Platform

AI agent orchestration platform with autonomous teams.

## Quick Start

```bash
# Install
pip install -r requirements.txt

# Run
OPENROUTER_API_KEY=sk-or-xxx python3 main.py --config config.yaml

# Dashboard
open http://localhost:8000
```

## Structure

| Directory | Description |
|-----------|-------------|
| `api/` | FastAPI endpoints |
| `core/` | Business logic |
| `static/` | CSS, JS, images |
| `templates/` | HTML templates |
| `tests/` | Unit tests |
| `scripts/` | CLI tools |
| `config/` | Configuration |
| `data/` | Database |
| `docs/` | Documentation |

## API

- `GET /api/health` — System status
- `GET /api/agents` — List agents
- `POST /api/agents/{id}/run` — Run agent
- `GET /api/tasks` — List tasks
- `GET /api/stats` — Statistics
- `GET /api/failover/status` — Key failover

## Agents

24 autonomous agents organized in hierarchy:
- CEO → CTO → Developers
- CEO → Project Manager → Tasks
- CEO → Security → SOC/Pentest

## Models

- NVIDIA Nemotron 3 Super (free)
- StepFun Step 3.5 Flash (free)
- Auto failover on errors

## License

Proprietary — AXIOM Platform

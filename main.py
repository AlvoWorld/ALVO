"""
OSYA Agents — Main Entry Point
Starts the web server, scheduler, and Telegram bot.
"""
import yaml
import logging
import asyncio
import argparse
from pathlib import Path

from core.database import Database
from core.runner import AgentRunner
from core.scheduler import Scheduler
from api.routes import app, setup as setup_api

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
)
logger = logging.getLogger(__name__)


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    path = Path(config_path)
    if not path.exists():
        logger.warning(f"Config file {config_path} not found, using defaults")
        return {
            "database": {"path": "osya.db"},
            "server": {"host": "0.0.0.0", "port": 8000},
            "providers": {},
            "workdir": "/tmp",
            "tool_timeout": 30,
        }
    
    with open(path) as f:
        return yaml.safe_load(f)


def setup_default_agents(db: Database, config: dict):
    """Create default OSYA agents if they don't exist."""
    agents_config = [
        {
            "name": "CEO",
            "provider": "openrouter",
            "model": "anthropic/claude-sonnet-4",
            "instructions": """You are the CEO of OSYA — an Amazon FBA private label brand selling women's leggings.

## Your Role
You coordinate the AI agent team. You make strategic decisions, assign tasks, review results, and report progress.

## Team Structure
- Agent Engineer: Builds and maintains the agent team
- Listing Manager: Optimizes Amazon product listings
- PPC Manager: Manages Amazon PPC campaigns
- Product Manager: Handles product development and returns

## Key Metrics
- Sales: units, revenue, ROAS
- Return rate: target <5%
- PPC: ACoS, ROAS, spend
- Organic ranking: key keywords

## Constraints
- Financial decisions >$100: need Dima approval
- Document all decisions in comments""",
            "heartbeat_sec": 3600,
            "reports_to": None,
            "tools": ["bash", "read", "write", "web_search", "web_fetch"],
            "max_turns": 100,
        },
        {
            "name": "Agent Engineer",
            "provider": "openrouter",
            "model": "anthropic/claude-sonnet-4",
            "instructions": """You are the Agent Engineer for OSYA.

## Your Role
Design, build, and maintain the AI agent team. Create agents, write prompts, configure models.

## Reports to: CEO

## Constraints
- Cannot create agents without CEO approval
- Document all changes in comments""",
            "heartbeat_sec": 3600,
            "reports_to": "CEO",
            "tools": ["bash", "read", "write", "web_search"],
            "max_turns": 100,
        },
        {
            "name": "Listing Manager",
            "provider": "openrouter",
            "model": "anthropic/claude-sonnet-4",
            "instructions": """You are the Listing Manager for OSYA.

## Your Role
Optimize Amazon product listings. Improve titles, bullet points, descriptions, images, keywords.

## Reports to: Agent Engineer

## Constraints
- No price changes without CEO approval
- Document all changes in comments""",
            "heartbeat_sec": 1800,
            "reports_to": "Agent Engineer",
            "tools": ["bash", "read", "write", "web_search", "web_fetch"],
            "max_turns": 100,
        },
        {
            "name": "PPC Manager",
            "provider": "openrouter",
            "model": "anthropic/claude-sonnet-4",
            "instructions": """You are the PPC Manager for OSYA.

## Your Role
Manage Amazon PPC campaigns. Optimize bids, add negative keywords, monitor ROAS/ACoS.

## Reports to: CEO

## Constraints
- Budget changes >$50 need CEO approval
- Document all changes in comments""",
            "heartbeat_sec": 1800,
            "reports_to": "CEO",
            "tools": ["bash", "read", "write", "web_search", "web_fetch"],
            "max_turns": 100,
        },
        {
            "name": "Product Manager",
            "provider": "openrouter",
            "model": "anthropic/claude-sonnet-4",
            "instructions": """You are the Product Manager for OSYA.

## Your Role
Handle product development and returns analysis. Analyze return reasons, quality issues.

## Reports to: Agent Engineer

## Constraints
- No product changes without CEO approval
- Document all changes in comments""",
            "heartbeat_sec": 1800,
            "reports_to": "Agent Engineer",
            "tools": ["bash", "read", "write", "web_search", "web_fetch"],
            "max_turns": 100,
        },
    ]
    
    for ac in agents_config:
        existing = db.get_agent(name=ac["name"])
        if not existing:
            # Resolve reports_to
            reports_to_id = None
            if ac["reports_to"]:
                parent = db.get_agent(name=ac["reports_to"])
                reports_to_id = parent["id"] if parent else None
            
            db.create_agent(
                name=ac["name"],
                provider=ac["provider"],
                model=ac["model"],
                instructions=ac["instructions"],
                heartbeat_sec=ac["heartbeat_sec"],
                reports_to=reports_to_id,
                tools=ac["tools"],
                max_turns=ac["max_turns"],
            )
            logger.info(f"Created agent: {ac['name']}")


def main():
    parser = argparse.ArgumentParser(description="OSYA Agents")
    parser.add_argument("--config", default="config.yaml", help="Config file path")
    parser.add_argument("--port", type=int, default=None, help="Server port")
    parser.add_argument("--host", default=None, help="Server host")
    args = parser.parse_args()
    
    # Load config
    config = load_config(args.config)
    
    # Override from args
    if args.port:
        config.setdefault("server", {})["port"] = args.port
    if args.host:
        config.setdefault("server", {})["host"] = args.host
    
    # Set up database
    db_path = config.get("database", {}).get("path", "osya.db")
    db = Database(db_path)
    logger.info(f"Database: {db_path}")
    
    # Set up default agents
    setup_default_agents(db, config)
    
    # Set up runner
    runner = AgentRunner(db, config)
    
    # Set up scheduler
    scheduler = Scheduler(db, runner)
    scheduler.start()
    logger.info("Scheduler started")
    
    # Set up API
    setup_api(db, runner, scheduler)
    
    # Start server
    import uvicorn
    host = config.get("server", {}).get("host", "0.0.0.0")
    port = config.get("server", {}).get("port", 8000)
    
    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()

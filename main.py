"""
OSYA Agents — Main Entry Point
Starts the web server, scheduler, and Telegram bot.
"""
import yaml
import logging
import asyncio
import argparse
import threading
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
    """Create agents from config.yaml if they don't exist."""
    agents_config = config.get("agents", [])
    
    if not agents_config:
        logger.warning("No agents defined in config.yaml")
        return
    
    # First pass: create all agents (without resolving reports_to)
    for ac in agents_config:
        existing = db.get_agent(name=ac["name"])
        if not existing:
            db.create_agent(
                name=ac["name"],
                provider=ac.get("provider", "openrouter"),
                model=ac.get("model", "anthropic/claude-sonnet-4"),
                instructions=ac.get("instructions", ""),
                heartbeat_sec=ac.get("heartbeat_sec", 0),
                reports_to=None,  # resolved in second pass
                tools=ac.get("tools", ["bash", "read", "write", "web_search"]),
                max_turns=ac.get("max_turns", 100),
            )
            logger.info(f"Created agent: {ac['name']}")
    
    # Second pass: resolve reports_to (name -> id)
    for ac in agents_config:
        reports_to_name = ac.get("reports_to")
        if reports_to_name:
            parent = db.get_agent(name=reports_to_name)
            if parent:
                agent = db.get_agent(name=ac["name"])
                if agent and agent.get("reports_to") != parent["id"]:
                    db.update_agent(agent["id"], reports_to=parent["id"])
                    logger.info(f"Linked {ac['name']} -> {reports_to_name}")
            else:
                logger.warning(f"Parent agent '{reports_to_name}' not found for '{ac['name']}'")


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

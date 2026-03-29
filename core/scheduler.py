"""
OSYA Agents — Scheduler Module
Heartbeat-based agent scheduling.
"""
import time
import threading
import logging
from datetime import datetime
from typing import Dict

from .database import Database
from .runner import AgentRunner

logger = logging.getLogger(__name__)


class Scheduler:
    """Manages scheduled agent runs (heartbeats)."""
    
    def __init__(self, db: Database, runner: AgentRunner, check_interval: int = 30):
        self.db = db
        self.runner = runner
        self.check_interval = check_interval
        self.running = False
        self.thread = None
        self.last_runs: Dict[str, float] = {}
    
    def start(self):
        """Start the scheduler."""
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        logger.info("Scheduler started")
    
    def stop(self):
        """Stop the scheduler."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Scheduler stopped")
    
    def _loop(self):
        """Main scheduler loop."""
        while self.running:
            try:
                self._check_heartbeats()
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
            time.sleep(self.check_interval)
    
    def _check_heartbeats(self):
        """Check and run heartbeat agents."""
        agents = self.db.list_agents()
        now = time.time()
        
        for agent in agents:
            heartbeat = agent.get('heartbeat_sec', 0)
            if heartbeat <= 0:
                continue
            
            if agent.get('status') == 'running':
                continue
            
            agent_id = agent['id']
            last_run = self.last_runs.get(agent_id, 0)
            
            if now - last_run >= heartbeat:
                logger.info(f"Heartbeat: running {agent['name']}")
                self.last_runs[agent_id] = now
                
                # Run in background thread
                thread = threading.Thread(
                    target=self._run_agent,
                    args=(agent['name'],),
                    daemon=True,
                )
                thread.start()
    
    def _run_agent(self, agent_name: str):
        """Run an agent in a background thread."""
        try:
            result = self.runner.run(agent_name)
            logger.info(f"Heartbeat {agent_name}: {result.get('status')}")
        except Exception as e:
            logger.error(f"Heartbeat {agent_name} failed: {e}")

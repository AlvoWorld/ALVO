"""
OSYA Agents — Agent Runner
Core agent execution engine with tool-calling loop.
"""
import json
import os
import yaml
from typing import List, Dict, Any, Optional
from datetime import datetime

from .database import Database
from .llm import LLMProvider
from .tools import ToolExecutor


class AgentRunner:
    """Runs an agent with tool-calling loop."""
    
    def __init__(self, db: Database, config: dict = None):
        self.db = db
        self.config = config or {}
        self.tool_executor = ToolExecutor(
            workdir=self.config.get("workdir", "/tmp"),
            timeout=self.config.get("tool_timeout", 30),
        )
    
    def run(self, agent_name: str, message: str = None, task_id: str = None) -> Dict[str, Any]:
        """Run an agent with a message or task."""
        agent = self.db.get_agent(name=agent_name)
        if not agent:
            return {"error": f"Agent '{agent_name}' not found"}
        
        # Get task if specified
        task = None
        if task_id:
            task = self.db.get_task(task_id)
            if task and not message:
                message = f"Task: {task['title']}\n\n{task['description']}"
        
        if not message:
            # Get first pending task
            tasks = self.db.list_tasks(status='todo', assignee_id=agent['id'])
            if tasks:
                task = tasks[0]
                message = f"Task: {task['title']}\n\n{task['description']}"
            else:
                message = "No pending tasks. Check your heartbeat checklist."
        
        # Create run
        run_id = self.db.create_run(agent['id'], task_id)
        
        # Update agent status
        self.db.update_agent(agent['id'], status='running')
        
        # Build system prompt
        system_prompt = self._build_system_prompt(agent)
        
        # Build messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ]
        
        # Add task context if exists
        if task:
            comments = self.db.get_comments(task_id or task['id'])
            if comments:
                comment_text = "\n".join([
                    f"[{c['author']} at {c['created_at']}]: {c['content']}" 
                    for c in comments[-5:]
                ])
                messages.append({
                    "role": "system", 
                    "content": f"Task comments:\n{comment_text}"
                })
        
        # Save user message
        self.db.add_message(run_id, "user", message)
        
        # Initialize LLM
        provider = agent.get('provider', 'openrouter')
        model = agent.get('model', 'openrouter/auto')
        
        # Get provider config
        provider_config = self.config.get('providers', {}).get(provider, {})
        api_key = provider_config.get('api_key')
        base_url = provider_config.get('base_url')
        
        # Model failover list
        fallback_models = [
            'nvidia/nemotron-3-super-120b-a12b:free',
            'stepfun/step-3.5-flash:free',
        ]
        if model not in fallback_models:
            fallback_models.insert(0, model)
        else:
            fallback_models.remove(model)
            fallback_models.insert(0, model)
        
        last_error = None
        for attempt_model in fallback_models:
            try:
                llm = LLMProvider(provider, attempt_model, api_key=api_key, base_url=base_url)
                if attempt_model != model:
                    print(f"🔄 Model failover: {model} → {attempt_model}")
                
                max_turns = agent.get('max_turns', 100)
                tools = json.loads(agent['tools']) if isinstance(agent['tools'], str) else agent['tools']
                total_input = 0
                total_output = 0
                total_cost = 0.0
                
                for turn in range(max_turns):
                    response = llm.chat(
                        messages=messages,
                        tools=tools,
                        max_tokens=4096,
                        temperature=0.7,
                    )
                    
                    total_input += response.input_tokens
                    total_output += response.output_tokens
                    total_cost += response.cost_usd
                    
                    assistant_content = response.content
                    self.db.add_message(run_id, "assistant", assistant_content)
                    
                    if not response.tool_calls:
                        messages.append({"role": "assistant", "content": assistant_content})
                        break
                    
                    tool_calls_msg = {
                        "role": "assistant",
                        "content": assistant_content or "",
                        "tool_calls": [
                            {
                                "id": tc["id"],
                                "type": "function",
                                "function": {
                                    "name": tc["name"],
                                    "arguments": json.dumps(tc["input"]),
                                }
                            }
                            for tc in response.tool_calls
                        ]
                    }
                    messages.append(tool_calls_msg)
                    
                    for tc in response.tool_calls:
                        tool_output = self.tool_executor.execute(tc["name"], tc["input"])
                        self.db.add_message(
                            run_id, "tool", tool_output,
                            tool_name=tc["name"],
                            tool_input=json.dumps(tc["input"]),
                            tool_output=tool_output,
                        )
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tc["id"],
                            "content": tool_output,
                        })
                
                # Success - update and return
                self.db.update_run(run_id, 
                    status='completed',
                    input_tokens=total_input,
                    output_tokens=total_output,
                    cost_usd=total_cost,
                    finished_at=datetime.now().isoformat(),
                )
                self.db.update_agent(agent['id'], status='idle')
                
                if task:
                    self.db.update_task(task['id'], status='done')
                    self.db.add_comment(task['id'], agent_name, 
                        f"Completed. Cost: ${total_cost:.4f}, Tokens: {total_input}in/{total_output}out")
                
                return {
                    "run_id": run_id,
                    "status": "completed",
                    "response": assistant_content,
                    "input_tokens": total_input,
                    "output_tokens": total_output,
                    "cost_usd": total_cost,
                    "turns": turn + 1,
                }
                    
            except Exception as e:
                last_error = str(e)
                if '429' in last_error or '401' in last_error or '403' in last_error:
                    print(f"⚠️ Model {attempt_model} failed: {last_error[:60]}, trying next...")
                    continue
                else:
                    raise
        
        # All models failed
        error_msg = f"All models failed. Last error: {last_error}"
        self.db.update_run(run_id, 
            status='failed',
            error=error_msg,
            finished_at=datetime.now().isoformat(),
        )
        self.db.update_agent(agent['id'], status='error')
        
        if task:
            self.db.add_comment(task['id'], agent_name, f"Failed: {error_msg}")
        
        return {
            "run_id": run_id,
            "status": "failed",
            "error": error_msg,
        }
    
    def _build_system_prompt(self, agent: dict) -> str:
        """Build the system prompt for an agent."""
        parts = []
        
        # Agent identity
        parts.append(f"You are {agent['name']}, an AI agent.")
        
        # Instructions
        if agent.get('instructions'):
            parts.append(f"\n## Your Instructions\n{agent['instructions']}")
        
        # Reporting structure
        if agent.get('reports_to'):
            parent = self.db.get_agent(agent_id=agent['reports_to'])
            if parent:
                parts.append(f"\nYou report to: {parent['name']}")
        
        # Team info
        agents = self.db.list_agents()
        team = [a for a in agents if a['id'] != agent['id'] and a.get('status') != 'terminated']
        if team:
            parts.append("\n## Your Team")
            for a in team:
                reports = ""
                if a.get('reports_to') == agent['id']:
                    reports = " (reports to you)"
                parts.append(f"- {a['name']}{reports}")
        
        # Tools
        tools = json.loads(agent['tools']) if isinstance(agent['tools'], str) else agent['tools']
        parts.append(f"\n## Available Tools\n{', '.join(tools)}")
        
        # Date/time
        parts.append(f"\nCurrent time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        
        return "\n".join(parts)

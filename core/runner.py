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
    

    def _get_agent_task(self, agent: dict, message: str = None, task_id: str = None):
        """Get task and message for agent run."""
        task = None
        if task_id:
            task = self.db.get_task(task_id)
            if task and not message:
                message = f"Task: {task['title']}\n\n{task['description']}"
        
        if not message:
            tasks = self.db.list_tasks(status='todo', assignee_id=agent['id'])
            if tasks:
                task = tasks[0]
                message = f"Task: {task['title']}\n\n{task['description']}"
            else:
                message = "No pending tasks. Check your heartbeat checklist."
        
        return task, message

    def _build_messages(self, agent: dict, message: str, task: dict, run_id: str) -> list:
        """Build message list for LLM."""
        system_prompt = self._build_system_prompt(agent)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ]
        
        if task:
            comments = self.db.get_comments(task['id'])
            if comments:
                comment_text = "\n".join([
                    f"[{c['author']} at {c['created_at']}]: {c['content']}" 
                    for c in comments[-5:]
                ])
                messages.append({
                    "role": "system", 
                    "content": f"Task comments:\n{comment_text}"
                })
        
        self.db.add_message(run_id, "user", message)
        return messages

    def _get_fallback_models(self, primary_model: str) -> list:
        """Get model failover list."""
        fallbacks = [
            'nvidia/nemotron-3-super-120b-a12b:free',
            'stepfun/step-3.5-flash:free',
        ]
        if primary_model not in fallbacks:
            fallbacks.insert(0, primary_model)
        else:
            fallbacks.remove(primary_model)
            fallbacks.insert(0, primary_model)
        return fallbacks

    def _execute_tool_calls(self, response, messages: list, run_id: str):
        """Execute tool calls and update messages."""
        tool_calls_msg = {
            "role": "assistant",
            "content": response.content or "",
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

    def _complete_run(self, run_id: str, agent: dict, task: dict, 
                      agent_name: str, total_input: int, total_output: int, 
                      total_cost: float, turns: int) -> dict:
        """Mark run as completed and update related records."""
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
            "input_tokens": total_input,
            "output_tokens": total_output,
            "cost_usd": total_cost,
            "turns": turns,
        }

    def _fail_run(self, run_id: str, agent: dict, task: dict, 
                  agent_name: str, error_msg: str) -> dict:
        """Mark run as failed and update related records."""
        self.db.update_run(run_id, 
            status='failed',
            error=error_msg,
            finished_at=datetime.now().isoformat(),
        )
        self.db.update_agent(agent['id'], status='error')
        
        if task:
            self.db.add_comment(task['id'], agent_name, f"Failed: {error_msg}")
        
        return {"run_id": run_id, "status": "failed", "error": error_msg}

    def run(self, agent_name: str, message: str = None, task_id: str = None) -> Dict[str, Any]:
        """Run an agent with a message or task."""
        agent = self.db.get_agent(name=agent_name)
        if not agent:
            return {"error": f"Agent '{agent_name}' not found"}
        
        # Get task and message
        task, message = self._get_agent_task(agent, message, task_id)
        
        # Create run and update status
        run_id = self.db.create_run(agent['id'], task_id)
        self.db.update_agent(agent['id'], status='running')
        
        # Build messages
        messages = self._build_messages(agent, message, task, run_id)
        
        # Get provider config
        provider = agent.get('provider', 'openrouter')
        model = agent.get('model', 'openrouter/auto')
        provider_config = self.config.get('providers', {}).get(provider, {})
        api_key = provider_config.get('api_key')
        base_url = provider_config.get('base_url')
        
        # Model failover
        fallback_models = self._get_fallback_models(model)
        
        last_error = None
        for attempt_model in fallback_models:
            try:
                llm = LLMProvider(provider, attempt_model, api_key=api_key, base_url=base_url)
                if attempt_model != model:
                    print(f"🔄 Model failover: {model} → {attempt_model}")
                
                max_turns = agent.get('max_turns', 100)
                tools = json.loads(agent['tools']) if isinstance(agent['tools'], str) else agent['tools']
                total_input = total_output = 0
                total_cost = 0.0
                
                for turn in range(max_turns):
                    response = llm.chat(messages=messages, tools=tools, max_tokens=4096, temperature=0.7)
                    
                    total_input += response.input_tokens
                    total_output += response.output_tokens
                    total_cost += response.cost_usd
                    
                    self.db.add_message(run_id, "assistant", response.content)
                    
                    if not response.tool_calls:
                        messages.append({"role": "assistant", "content": response.content})
                        break
                    
                    self._execute_tool_calls(response, messages, run_id)
                
                return self._complete_run(run_id, agent, task, agent_name, 
                                         total_input, total_output, total_cost, turn + 1)
                    
            except Exception as e:
                last_error = str(e)
                if any(code in last_error for code in ['429', '401', '403']):
                    print(f"⚠️ Model {attempt_model} failed: {last_error[:60]}, trying next...")
                    continue
                raise
        
        return self._fail_run(run_id, agent, task, agent_name, 
                            f"All models failed. Last error: {last_error}")
    
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

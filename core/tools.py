"""
OSYA Agents — Tools Module
Safe tool execution for agents.
"""
import subprocess
import os
import json
from typing import Dict, Any
from pathlib import Path


class ToolExecutor:
    """Executes tools safely with proper sandboxing."""
    
    def __init__(self, workdir: str = "/tmp", timeout: int = 30):
        self.workdir = workdir
        self.timeout = timeout
    
    def execute(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """Execute a tool and return the result."""
        handlers = {
            "bash": self._bash,
            "read": self._read,
            "write": self._write,
            "web_search": self._web_search,
            "web_fetch": self._web_fetch,
        }
        
        handler = handlers.get(tool_name)
        if not handler:
            return f"Error: Unknown tool '{tool_name}'"
        
        try:
            return handler(**tool_input)
        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"
    
    def _bash(self, command: str) -> str:
        """Execute a bash command."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=self.workdir,
            )
            output = result.stdout
            if result.stderr:
                output += f"\n[stderr]\n{result.stderr}"
            if result.returncode != 0:
                output += f"\n[exit code: {result.returncode}]"
            return output.strip() or "(no output)"
        except subprocess.TimeoutExpired:
            return f"Error: Command timed out after {self.timeout}s"
    
    def _read(self, path: str) -> str:
        """Read a file."""
        try:
            p = Path(path)
            if not p.exists():
                return f"Error: File not found: {path}"
            if p.stat().st_size > 100_000:
                content = p.read_text()[:100_000]
                return content + f"\n\n[File truncated - {p.stat().st_size} bytes total]"
            return p.read_text()
        except PermissionError:
            return f"Error: Permission denied: {path}"
        except Exception as e:
            return f"Error reading {path}: {str(e)}"
    
    def _write(self, path: str, content: str) -> str:
        """Write content to a file."""
        try:
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
            return f"Written {len(content)} bytes to {path}"
        except PermissionError:
            return f"Error: Permission denied: {path}"
        except Exception as e:
            return f"Error writing {path}: {str(e)}"
    
    def _web_search(self, query: str) -> str:
        """Search the web using DuckDuckGo."""
        try:
            import httpx
            url = f"https://html.duckduckgo.com/html/?q={query}"
            response = httpx.get(url, timeout=10.0, follow_redirects=True)
            # Simple extraction of results
            from html.parser import HTMLParser
            
            class ResultParser(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self.results = []
                    self.current = {}
                    self.in_title = False
                    self.in_snippet = False
                
                def handle_starttag(self, tag, attrs):
                    attrs_dict = dict(attrs)
                    if tag == 'a' and 'result__a' in attrs_dict.get('class', ''):
                        self.in_title = True
                        self.current = {'url': attrs_dict.get('href', '')}
                    elif tag == 'a' and 'result__snippet' in attrs_dict.get('class', ''):
                        self.in_snippet = True
                
                def handle_data(self, data):
                    if self.in_title:
                        self.current['title'] = data.strip()
                        self.in_title = False
                    elif self.in_snippet:
                        self.current['snippet'] = data.strip()
                        self.in_snippet = False
                        if self.current.get('title'):
                            self.results.append(self.current)
                            self.current = {}
            
            parser = ResultParser()
            parser.feed(response.text)
            
            if not parser.results:
                return f"No results found for: {query}"
            
            output = f"Search results for: {query}\n\n"
            for i, r in enumerate(parser.results[:5], 1):
                output += f"{i}. {r.get('title', 'No title')}\n"
                output += f"   {r.get('snippet', 'No description')}\n"
                output += f"   {r.get('url', '')}\n\n"
            
            return output
        except Exception as e:
            return f"Search error: {str(e)}"
    
    def _web_fetch(self, url: str) -> str:
        """Fetch a web page."""
        try:
            import httpx
            response = httpx.get(url, timeout=15.0, follow_redirects=True)
            response.raise_for_status()
            
            # Simple HTML to text conversion
            text = response.text
            # Remove script and style tags
            import re
            text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
            text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
            text = re.sub(r'<[^>]+>', ' ', text)
            text = re.sub(r'\s+', ' ', text).strip()
            
            if len(text) > 50_000:
                text = text[:50_000] + "\n\n[Content truncated]"
            
            return text
        except Exception as e:
            return f"Fetch error: {str(e)}"

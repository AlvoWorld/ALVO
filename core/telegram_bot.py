"""
OSYA Agents — Telegram Bot
Communication bridge between humans and agents.
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class TelegramBot:
    """Telegram bot for agent communication."""
    
    def __init__(self, token: str, db, runner):
        self.token = token
        self.db = db
        self.runner = runner
        self.bot = None
    
    async def start(self):
        """Start the Telegram bot."""
        try:
            from telegram import Update
            from telegram.ext import Application, CommandHandler, MessageHandler, filters
            
            app = Application.builder().token(self.token).build()
            
            # Command handlers
            app.add_handler(CommandHandler("start", self._cmd_start))
            app.add_handler(CommandHandler("agents", self._cmd_agents))
            app.add_handler(CommandHandler("tasks", self._cmd_tasks))
            app.add_handler(CommandHandler("run", self._cmd_run))
            app.add_handler(CommandHandler("status", self._cmd_status))
            
            # Message handler
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message))
            
            self.bot = app
            logger.info("Telegram bot starting...")
            await app.run_polling()
        
        except ImportError:
            logger.warning("python-telegram-bot not installed. Telegram bot disabled.")
        except Exception as e:
            logger.error(f"Telegram bot error: {e}")
    
    async def _cmd_start(self, update, context):
        await update.message.reply_text(
            "🤖 OSYA Agents Bot\n\n"
            "Commands:\n"
            "/agents — List agents\n"
            "/tasks — List tasks\n"
            "/run <agent> <message> — Run agent\n"
            "/status — System status\n"
        )
    
    async def _cmd_agents(self, update, context):
        agents = self.db.list_agents()
        if not agents:
            await update.message.reply_text("No agents configured.")
            return
        
        text = "🤖 **Agents:**\n\n"
        for a in agents:
            status_emoji = {"idle": "🟢", "running": "🟡", "error": "🔴"}.get(a['status'], "⚪")
            text += f"{status_emoji} **{a['name']}** — {a.get('model', 'no model')} ({a['status']})\n"
        
        await update.message.reply_text(text, parse_mode='Markdown')
    
    async def _cmd_tasks(self, update, context):
        tasks = self.db.list_tasks(status='todo')
        if not tasks:
            await update.message.reply_text("No pending tasks.")
            return
        
        text = "📋 **Pending Tasks:**\n\n"
        for t in tasks[:10]:
            assignee = t.get('assignee_name', 'unassigned')
            priority_emoji = {"high": "🔴", "normal": "🟡"}.get(t.get('priority', 'normal'), "⚪")
            text += f"{priority_emoji} **{t['title']}**\n   → {assignee}\n"
        
        await update.message.reply_text(text, parse_mode='Markdown')
    
    async def _cmd_run(self, update, context):
        args = context.args
        if not args:
            await update.message.reply_text("Usage: /run <agent_name> [message]")
            return
        
        agent_name = args[0]
        message = ' '.join(args[1:]) if len(args) > 1 else None
        
        await update.message.reply_text(f"Running {agent_name}...")
        
        try:
            result = self.runner.run(agent_name, message=message)
            if result.get('status') == 'completed':
                response = result.get('response', 'No response')
                if len(response) > 4000:
                    response = response[:4000] + "..."
                await update.message.reply_text(f"✅ **{agent_name}** finished:\n\n{response}", parse_mode='Markdown')
            else:
                await update.message.reply_text(f"❌ **{agent_name}** failed: {result.get('error', 'Unknown error')}")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def _cmd_status(self, update, context):
        agents = self.db.list_agents()
        tasks = self.db.list_tasks()
        
        todo_count = len([t for t in tasks if t['status'] == 'todo'])
        running_count = len([a for a in agents if a['status'] == 'running'])
        error_count = len([a for a in agents if a['status'] == 'error'])
        
        text = (
            f"📊 **System Status**\n\n"
            f"Agents: {len(agents)} total, {running_count} running, {error_count} errors\n"
            f"Tasks: {todo_count} pending\n"
        )
        
        await update.message.reply_text(text, parse_mode='Markdown')
    
    async def _handle_message(self, update, context):
        """Handle regular messages - forward to CEO agent."""
        text = update.message.text
        user = update.message.from_user.first_name
        
        # Forward to CEO
        message = f"Message from {user} via Telegram:\n\n{text}"
        
        try:
            result = self.runner.run("CEO", message=message)
            response = result.get('response', 'CEO is not responding.')
            if len(response) > 4000:
                response = response[:4000] + "..."
            await update.message.reply_text(f"🤖 CEO:\n\n{response}")
        except Exception as e:
            await update.message.reply_text(f"Error: {str(e)}")
    
    async def send_message(self, chat_id: str, text: str):
        """Send a message to a Telegram chat."""
        if self.bot:
            await self.bot.bot.send_message(chat_id=chat_id, text=text)

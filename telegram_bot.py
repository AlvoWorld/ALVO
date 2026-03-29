"""
OSYA Agents — Telegram Bot Standalone
Run as a separate process alongside the web server.
"""
import yaml
import logging
from pathlib import Path

# Import necessary classes from telegram.ext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
)
logger = logging.getLogger(__name__)


def load_config(config_path: str = "config.yaml") -> dict:
    path = Path(config_path)
    if not path.exists():
        return {}
    with open(path) as f:
        return yaml.safe_load(f)


def main():
    config = load_config()
    token = config.get("telegram", {}).get("bot_token", "")

    if not token:
        logger.error("No Telegram bot token configured!")
        return

    # Import dependencies
    from core.database import Database
    from core.runner import AgentRunner

    # Set up database and runner
    db_path = config.get("database", {}).get("path", "osya.db")
    db = Database(db_path)
    runner = AgentRunner(db, config)

    # Build bot application
    application = Application.builder().token(token).build()

    # --- Handlers ---

    async def cmd_start(update: Update, context):
        keyboard = [
            [InlineKeyboardButton("📋 Задачи", callback_data='list_tasks')],
            [InlineKeyboardButton("👥 Агенты", callback_data='list_agents')],
            [InlineKeyboardButton("📊 Статус", callback_data='show_status')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "🤖 ALVO Agents Bot\n\n"
            "Добро пожаловать! Выберите действие:",
            reply_markup=reply_markup
        )

    async def cmd_menu(update: Update, context):
        keyboard = [
            [InlineKeyboardButton("📋 Задачи", callback_data='list_tasks')],
            [InlineKeyboardButton("👥 Агенты", callback_data='list_agents')],
            [InlineKeyboardButton("📊 Статус", callback_data='show_status')],
            [InlineKeyboardButton("🚀 Запустить агента", callback_data='run_agent_menu')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "🤖 ALVO Agents Bot\n\n"
            "Выберите действие:",
            reply_markup=reply_markup
        )

    async def list_agents(update: Update, context):
        query = update.callback_query
        await query.answer() 

        agents = db.list_agents()
        text = "👥 Команда ALVO:\n\n"
        if not agents:
            text += "Нет доступных агентов."
        else:
            keyboard = []
            for a in agents:
                status = "🟢" if a.get('status') != 'running' else "🔄"
                agent_name = a['name']
                text += f"{status} {agent_name} ({a['model']})\n"
                # Add buttons for each agent
                keyboard.append([
                    InlineKeyboardButton("🚀 Запустить", callback_data=f'run_agent:{agent_name}'),
                    InlineKeyboardButton("📝 Детали", callback_data=f'agent_details:{agent_name}')
                ])
        
        # Add a back button
        keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data='main_menu')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text=text, reply_markup=reply_markup)


    async def list_tasks(update: Update, context):
        query = update.callback_query
        await query.answer()

        tasks = db.list_tasks()
        text = "📋 Задачи:\n\n"
        if not tasks:
            text += "Нет активных задач."
        else:
            keyboard = []
            for t in tasks[:20]:
                status_emoji = {'todo': '⬜', 'in_progress': '🔄', 'done': '✅'}.get(t['status'], '❓')
                task_title = t['title']
                task_id = t['id']
                text += f"{status_emoji} {task_title}\n"
                # Add buttons for each task
                keyboard.append([
                    InlineKeyboardButton("✅ Выполнить", callback_data=f'complete_task:{task_id}'),
                    InlineKeyboardButton("✍️ Комментарий", callback_data=f'add_comment:{task_id}')
                ])
        
        # Add a back button
        keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data='main_menu')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text=text, reply_markup=reply_markup)

    async def show_status(update: Update, context):
        query = update.callback_query
        await query.answer()

        agents = db.list_agents()
        tasks = db.list_tasks()
        running = sum(1 for a in agents if a.get('status') == 'running')
        todo = sum(1 for t in tasks if t['status'] == 'todo')
        done = sum(1 for t in tasks if t['status'] == 'done')

        text = (
            "📊 Статус ALVO:\n\n"
            f"👥 Агентов: {len(agents)}\n"
            f"🔄 Работают: {running}\n"
            f"📋 Задач: {len(tasks)} (⬜ {todo} / ✅ {done})\n"
        )
        
        # Add a back button
        keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text=text, reply_markup=reply_markup)

    async def cmd_run(update: Update, context):
        await update.message.reply_text("Для запуска агента используйте команду /menu и выберите '🚀 Запустить агента'.")

    async def handle_message(update: Update, context):
        user_msg = update.message.text
        user_name = update.message.from_user.first_name

        task_id = db.create_task(
            title=f"[Telegram] {user_name}: {user_msg[:80]}",
            description=user_msg,
            priority="normal"
        )

        await update.message.reply_text(
            f"📝 Задача создана!\n\n«{user_msg[:100]}»\nCEO получит и распределит её."
        )

        try:
            runner.run("CEO", task_id=task_id)
        except Exception as e:
            logger.error(f"CEO run error: {e}")

    async def handle_callback_query(update: Update, context):
        query = update.callback_query
        data = query.data

        if data == 'list_tasks':
            await list_tasks(update, context)
        elif data == 'list_agents':
            await list_agents(update, context)
        elif data == 'show_status':
            await show_status(update, context)
        elif data == 'run_agent_menu':
            await query.answer("Выберите агента для запуска.")
            await query.edit_message_text("Пожалуйста, введите команду /run <имя агента> для запуска.")
        elif data.startswith('run_agent:'):
            agent_name = data.split(':')[1]
            await query.answer(f"Запуск агента {agent_name}...")
            
            # Here you might want to ask for a message or task details
            # For now, just run the agent with no specific message
            try:
                result = runner.run(agent_name)
                response_text = f"🚀 Агент {agent_name} запущен.\n"
                if result.get('status') == 'completed':
                    response_text += f"Результат: {result.get('response', 'Нет ответа')}"
                elif result.get('status') == 'failed':
                    response_text += f"Ошибка: {result.get('error', 'Неизвестная ошибка')}"
                else:
                    response_text += f"Статус: {result.get('status', 'Неизвестен')}"
                await query.edit_message_text(response_text)
            except Exception as e:
                await query.edit_message_text(f"❌ Ошибка при запуске {agent_name}: {e}")

        elif data.startswith('agent_details:'):
            agent_name = data.split(':')[1]
            await query.answer(f"Детали агента {agent_name}")
            agent = db.get_agent(name=agent_name)
            if agent:
                text = f"**Детали агента: {agent_name}**\n\n"
                text += f"Модель: {agent.get('model', 'N/A')}\n"
                text += f"Провайдер: {agent.get('provider', 'N/A')}\n"
                text += f"Статус: {agent.get('status', 'N/A')}\n"
                text += f"Инструкции: {agent.get('instructions', 'N/A')}\n"
                text += f"Отчитывается перед: {agent.get('reports_to', 'N/A')}\n"
                text += f"Инструменты: {', '.join(agent.get('tools', []))}\n"
                await query.edit_message_text(text, parse_mode='Markdown')
            else:
                await query.edit_message_text(f"Агент '{agent_name}' не найден.")
        
        elif data.startswith('complete_task:'):
            task_id = data.split(':')[1]
            await query.answer("Отметить задачу как выполненную.")
            if db.update_task(task_id, status='done'):
                await query.edit_message_text("✅ Задача помечена как выполненная.")
            else:
                await query.edit_message_text("❌ Не удалось пометить задачу как выполненную.")

        elif data.startswith('add_comment:'):
            task_id = data.split(':')[1]
            await query.answer("Добавить комментарий к задаче.")
            # Prompt user to enter comment
            await query.edit_message_text("Пожалуйста, введите ваш комментарий к задаче:")
            # Store task_id in user_data to retrieve it in the message handler
            context.user_data['commenting_task_id'] = task_id

        elif data == 'main_menu':
            await query.answer("Возврат в главное меню.")
            await cmd_menu(update, context) # Re-use cmd_menu to display the menu
        
        else:
            await query.answer("Неизвестная команда.")


    # Register handlers
    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("menu", cmd_menu))
    application.add_handler(CommandHandler("run", cmd_run)) 
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    
    # Modify message handler to handle comments
    async def custom_handle_message(update: Update, context):
        if context.user_data.get('commenting_task_id'):
            task_id = context.user_data.pop('commenting_task_id')
            comment_text = update.message.text
            user_name = update.message.from_user.first_name
            db.add_comment(task_id, user_name, comment_text)
            await update.message.reply_text("Комментарий добавлен.")
        else:
            # Original handle_message logic for general messages
            user_msg = update.message.text
            user_name = update.message.from_user.first_name
            task_id = db.create_task(
                title=f"[Telegram] {user_name}: {user_msg[:80]}",
                description=user_msg,
                priority="normal"
            )
            await update.message.reply_text(
                f"📝 Задача создана!\n\n«{user_msg[:100]}»\nCEO получит и распределит её."
            )
            try:
                runner.run("CEO", task_id=task_id)
            except Exception as e:
                logger.error(f"CEO run error: {e}")

    # Replace the default message handler with the custom one
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, custom_handle_message))

    logger.info("Telegram bot starting polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

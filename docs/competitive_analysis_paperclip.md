# 📊 Конкурентный анализ: Paperclip — слабые места и жалобы

## Источники: обзоры (vibecoding.app, toolworthy.ai, grokipedia), документация, GitHub

---

## 🔴 Критические недостатки

### 1. Привязка к Claude/Node.js
- Сильнейший adapter только для Claude (claude_local)
- Другие LLM-провайдеры поддерживаются "community-contributed" — качество не гарантировано
- Требует Node.js 20+ и pnpm 9.15+ — узкий стек
- **Наше преимущество:** ALVO работает с любым LLM через OpenRouter

### 2. Одиночная машина
- Designed for local workflows
- Production distributed deployment — не primary use case
- Нет горизонтального масштабирования
- **Наше преимущество:** ALVO — Python, легко масштабируется

### 3. Embedded PostgreSQL
- Тяжёлая зависимость (PostgreSQL встроена)
- Нет гибкости в выборе БД
- Сложная настройка для продакшена
- **Наше преимущество:** SQLite по умолчанию, легко переключиться

---

## 🟡 Средние проблемы (жалобы пользователей)

### 4. Нет Telegram-интеграции из коробки
- Paperclip работает через CLI + React dashboard
- Нет нативного бота для общения с агентами
- Пользователи просят мобильное приложение
- **Наше преимущество:** Нативная Telegram-интеграция в ALVO

### 5. Ограниченное управление агентами
- Нет granular permissions (кто что может делать)
- Нет ролевой модели доступа
- Heartbeat-ы работают, но нет fine-grained контроля
- **Наша возможность:** Система permissions per agent

### 6. Слабый мониторинг затрат
- Budget tracking есть, но basic
- Нет breakdown по токенам, моделям, агентам
- Нет алертов при превышении бюджета
- **Наша возможность:** Детальная аналитика расходов

### 7. Мало документации
- "Fewer tutorials, blog posts, and Stack Overflow answers"
- Сообщество маленькое
- Third-party документации почти нет
- **Наша возможность:** Полная документация на русском + английском

---

## 🟢 Что Paperclip делает хорошо (чему учиться)

- Метафора "компания" (CEO, Engineer, QA) — интуитивно понятно
- React dashboard out of the box
- 16 pre-built company templates
- Heartbeat scheduling с atomic execution
- "Polaroids" — persistent agent memory
- Budget tracking per run
- Multi-company isolation

---

## 📋 Желания пользователей (feature requests)

1. **Managed hosting / cloud version** — не хотят self-hosted
2. **Больше LLM-провайдеров** — OpenRouter, local models
3. **Mobile app** — мониторинг с телефона
4. **Better error handling** — graceful degradation при ошибках API
5. **Agent permissions** — кто может что делать
6. **Visual workflow builder** — drag-and-drop для связей агентов
7. **Multi-language support** — не только английский
8. **Integration marketplace** — плагины/скиллы от сообщества
9. **Better cost controls** — hard limits, alerts, per-agent budgets
10. **Webhook support** — триггеры от внешних событий
11. **Audit logs** — полная история действий агентов
12. **Sandbox isolation** — безопасное выполнение кода

---

## 🎯 Наша стратегия: "Сделать лучше"

| Paperclip | ALVO (наш путь) |
|-----------|-----------------|
| Только Claude | Любой LLM через OpenRouter |
| Node.js + Postgres | Python + SQLite (лёгкий) |
| Local only | Deploy anywhere |
| CLI + Dashboard | Dashboard + Telegram бот |
| Английский | Русский + English |
| 16 шаблонов | Готовые конфигурации для бизнесов |
| Basic budgets | Детальная аналитика расходов |
| Self-hosted only | Self-hosted + managed option |

---

*Документ создан: 2026-03-29*
*Цель: Обосновать competitive advantage ALVO перед Paperclip*

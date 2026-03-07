# Claude Code Configuration

## Структура

```
.claude/
├── agents/          # Документация агентов и субагентов
│   ├── explore.md
│   ├── plan.md
│   ├── general-purpose.md
│   ├── claude-code-guide.md
│   └── README.md
│
├── commands/         # Пользовательские команды (/view, /edit, /test)
│   ├── view.md
│   ├── edit.md
│   ├── test.md
│   └── README.md
│
├── hooks/           # Хуки (pre-command, on-write)
│   ├── pre-command.bash
│   ├── on-write-write.sh
│   └── README.md
│
├── mcp/             # MCP серверы
│   └── README.md
│
├── skills/          # Навыки
│   └── README.md
│
├── settings.json    # Основные настройки
├── settings.local.json
├── mcp.json         # Конфиг MCP серверов
└── keybindings.json # Горячие клавиши
```

## Быстрые ссылки

- [Команды](./commands/README.md)
- [Агенты](./agents/README.md)
- [Хуки](./hooks/README.md)
- [MCP](./mcp/README.md)
- [Навыки](./skills/README.md)

# MCP Servers Configuration

## Настройка MCP серверов

Добавьте MCP серверы в этот файл:

```json
{
  "mcpServers": {
    "server-name": {
      "command": "path/to/server",
      "args": ["arg1", "arg2"]
    }
  }
}
```

## Примеры MCP серверов

- `filesystem` - файловая система
- `github` - интеграция с GitHub
- `gitlab` - интеграция с GitLab
- Другие по документации MCP

## Документация

См. https://docs.anthropic.com/en/docs/claude-code/mcp

#!/bin/bash
# Hook: Before writing any file

# Проверяет, что файл не содержит debug print или временный код
# Выход 0 - продолжить, выход 1 - остановить

# Получаем путь к файлу из аргумента
if [ -z "$CLAUDE_FILE_PATH" ]; then
    exit 0
fi

# Пропускаем бинарные файлы и файлы node_modules
if [[ "$CLAUDE_FILE_PATH" == *"node_modules"* ]] || [[ "$CLAUDE_FILE_PATH" == *".pyc"* ]]; then
    exit 0
fi

# Пропускаем .claude директорию
if [[ "$CLAUDE_FILE_PATH" == *".claude"* ]]; then
    exit 0
fi

# Проверяем на TODO комментарии
if grep -q "TODO\|FIXME\|XXX\|HACK" "$CLAUDE_FILE_PATH" 2>/dev/null; then
    echo "Warning: $CLAUDE_FILE_PATH contains TODO/FIXME comments"
fi

exit 0

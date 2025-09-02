/**
 * Дополнительная функциональность редактора
 * Additional Editor Functionality
 */

// Настройки CodeMirror для лучшей поддержки Markdown
CodeMirror.defineMode("markdown_extended", function(config, parserConfig) {
    return CodeMirror.overlayMode(CodeMirror.getMode(config, "text/markdown"), {
        token: function(stream, state) {
            // Подсветка русского текста
            if (stream.match(/[а-яё]+/i)) {
                return "russian-text";
            }
            
            // Подсветка ссылок
            if (stream.match(/https?:\/\/[^\s)]+/)) {
                return "url";
            }
            
            // Подсветка эмодзи
            if (stream.match(/:\w+:/)) {
                return "emoji";
            }
            
            stream.next();
            return null;
        }
    });
});

// Дополнительные команды для редактора
CodeMirror.commands.insertDateTime = function(cm) {
    const now = new Date();
    const dateTime = now.toLocaleString('ru-RU');
    cm.replaceSelection(dateTime);
};

CodeMirror.commands.insertTable = function(cm) {
    const table = `
| Заголовок 1 | Заголовок 2 | Заголовок 3 |
|-------------|-------------|-------------|
| Ячейка 1    | Ячейка 2    | Ячейка 3    |
| Ячейка 4    | Ячейка 5    | Ячейка 6    |
`;
    cm.replaceSelection(table);
};

CodeMirror.commands.insertCodeBlock = function(cm) {
    const cursor = cm.getCursor();
    const selection = cm.getSelection();
    
    if (selection) {
        cm.replaceSelection('```\n' + selection + '\n```');
    } else {
        cm.replaceSelection('```javascript\n// Ваш код здесь\nconsole.log("Привет, мир!");\n```');
        cm.setCursor(cursor.line + 1, 0);
    }
};

CodeMirror.commands.insertTaskList = function(cm) {
    const tasks = `
- [ ] Задача 1
- [ ] Задача 2
- [x] Выполненная задача
- [ ] Задача 4
`;
    cm.replaceSelection(tasks);
};

// Автодополнение для Markdown
CodeMirror.registerHelper("hint", "markdown", function(cm) {
    const cursor = cm.getCursor();
    const line = cm.getLine(cursor.line);
    const start = cursor.ch;
    const end = cursor.ch;
    
    // Словарь автодополнений
    const completions = [
        // Заголовки
        "# Заголовок 1",
        "## Заголовок 2", 
        "### Заголовок 3",
        "#### Заголовок 4",
        
        // Форматирование
        "**жирный текст**",
        "*курсив*",
        "~~зачёркнутый~~",
        "`код`",
        
        // Ссылки и изображения
        "[текст ссылки](URL)",
        "![alt текст](URL изображения)",
        
        // Списки
        "- элемент списка",
        "1. нумерованный список",
        "- [ ] задача",
        "- [x] выполненная задача",
        
        // Блоки
        "> цитата",
        "```javascript\n// код\n```",
        "---",
        
        // Таблицы
        "| Колонка 1 | Колонка 2 |\n|-----------|-----------|",
        
        // Эмодзи
        ":smile:", ":heart:", ":thumbsup:", ":warning:", ":info:",
        ":fire:", ":rocket:", ":star:", ":check:", ":x:",
        
        // Русские фразы
        "Важно:", "Примечание:", "Внимание:", "Совет:",
        "Пример:", "Результат:", "Заключение:"
    ];
    
    const word = line.slice(0, cursor.ch).match(/\S*$/)[0];
    const suggestions = completions.filter(comp => 
        comp.toLowerCase().includes(word.toLowerCase())
    ).map(comp => ({
        text: comp,
        displayText: comp,
        render: function(element, self, data) {
            element.innerHTML = `<span class="completion-text">${comp}</span>`;
        }
    }));
    
    return {
        list: suggestions,
        from: CodeMirror.Pos(cursor.line, start - word.length),
        to: CodeMirror.Pos(cursor.line, end)
    };
});

// Функции для работы с буфером обмена
class ClipboardManager {
    static async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            return true;
        } catch (err) {
            console.error('Ошибка копирования в буфер обмена:', err);
            return false;
        }
    }
    
    static async pasteFromClipboard() {
        try {
            const text = await navigator.clipboard.readText();
            return text;
        } catch (err) {
            console.error('Ошибка чтения из буфера обмена:', err);
            return null;
        }
    }
}

// Функции для работы с выделением текста
class SelectionHelper {
    static getSelectedText(cm) {
        return cm.getSelection();
    }
    
    static selectAll(cm) {
        cm.execCommand('selectAll');
    }
    
    static selectLine(cm) {
        const cursor = cm.getCursor();
        cm.setSelection(
            CodeMirror.Pos(cursor.line, 0),
            CodeMirror.Pos(cursor.line)
        );
    }
    
    static selectWord(cm) {
        const cursor = cm.getCursor();
        const line = cm.getLine(cursor.line);
        
        let start = cursor.ch;
        let end = cursor.ch;
        
        // Найти начало слова
        while (start > 0 && /\w/.test(line.charAt(start - 1))) {
            start--;
        }
        
        // Найти конец слова
        while (end < line.length && /\w/.test(line.charAt(end))) {
            end++;
        }
        
        cm.setSelection(
            CodeMirror.Pos(cursor.line, start),
            CodeMirror.Pos(cursor.line, end)
        );
    }
}

// Функции для форматирования
class MarkdownFormatter {
    static formatDocument(cm) {
        const content = cm.getValue();
        const lines = content.split('\n');
        const formatted = [];
        
        let inCodeBlock = false;
        
        for (let i = 0; i < lines.length; i++) {
            let line = lines[i];
            
            // Проверяем код блоки
            if (line.trim().startsWith('```')) {
                inCodeBlock = !inCodeBlock;
                formatted.push(line);
                continue;
            }
            
            // Не форматируем содержимое кода
            if (inCodeBlock) {
                formatted.push(line);
                continue;
            }
            
            // Форматирование заголовков
            if (line.match(/^#+\s/)) {
                const match = line.match(/^(#+)\s*(.+)$/);
                if (match) {
                    line = match[1] + ' ' + match[2].trim();
                }
            }
            
            // Форматирование списков
            if (line.match(/^\s*[-*+]\s/)) {
                line = line.replace(/^\s*[-*+]\s*/, '- ');
            }
            
            // Форматирование нумерованных списков
            if (line.match(/^\s*\d+\.\s/)) {
                const indent = line.match(/^\s*/)[0];
                const number = line.match(/\d+/)[0];
                const text = line.replace(/^\s*\d+\.\s*/, '');
                line = indent + number + '. ' + text;
            }
            
            formatted.push(line);
        }
        
        cm.setValue(formatted.join('\n'));
    }
    
    static cleanupContent(cm) {
        const content = cm.getValue();
        
        // Удаляем лишние пробелы в конце строк
        const cleaned = content
            .split('\n')
            .map(line => line.trimEnd())
            .join('\n')
            .replace(/\n{3,}/g, '\n\n'); // Максимум 2 переноса подряд
        
        cm.setValue(cleaned);
    }
}

// Функции для статистики документа
class DocumentStats {
    static getStats(content) {
        const lines = content.split('\n').length;
        const words = content.trim() ? content.trim().split(/\s+/).length : 0;
        const chars = content.length;
        const charsNoSpaces = content.replace(/\s/g, '').length;
        
        // Подсчёт заголовков
        const headings = (content.match(/^#+\s/gm) || []).length;
        
        // Подсчёт ссылок
        const links = (content.match(/\[.*?\]\(.*?\)/g) || []).length;
        
        // Подсчёт изображений
        const images = (content.match(/!\[.*?\]\(.*?\)/g) || []).length;
        
        // Подсчёт блоков кода
        const codeBlocks = (content.match(/```[\s\S]*?```/g) || []).length;
        const inlineCode = (content.match(/`[^`]+`/g) || []).length;
        
        return {
            lines,
            words,
            chars,
            charsNoSpaces,
            headings,
            links,
            images,
            codeBlocks,
            inlineCode
        };
    }
    
    static displayStats(content) {
        const stats = this.getStats(content);
        
        return `
Статистика документа:
• Строк: ${stats.lines}
• Слов: ${stats.words}
• Символов: ${stats.chars}
• Символов без пробелов: ${stats.charsNoSpaces}
• Заголовков: ${stats.headings}
• Ссылок: ${stats.links}
• Изображений: ${stats.images}
• Блоков кода: ${stats.codeBlocks}
• Инлайн-кода: ${stats.inlineCode}
        `.trim();
    }
}

// Функции для экспорта
class ExportManager {
    static exportAsHTML(content, title = 'Документ') {
        const html = marked.parse(content);
        const fullHTML = `
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${title}</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #2c3e50;
            margin-top: 2em;
            margin-bottom: 0.5em;
        }
        pre {
            background: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }
        blockquote {
            border-left: 4px solid #3498db;
            margin: 0;
            padding-left: 20px;
            color: #666;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
    </style>
</head>
<body>
${html}
</body>
</html>
        `;
        
        const blob = new Blob([fullHTML], { type: 'text/html;charset=utf-8' });
        return blob;
    }
    
    static downloadFile(blob, filename) {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
}

// Функции для работы с темами
class ThemeManager {
    static themes = {
        'default': 'default',
        'dark': 'monokai',
        'light': 'eclipse',
        'github': 'github',
        'material': 'material'
    };
    
    static setTheme(cm, themeName) {
        if (this.themes[themeName]) {
            cm.setOption('theme', this.themes[themeName]);
            localStorage.setItem('markdown-editor-theme', themeName);
        }
    }
    
    static getTheme() {
        return localStorage.getItem('markdown-editor-theme') || 'dark';
    }
    
    static initTheme(cm) {
        const savedTheme = this.getTheme();
        this.setTheme(cm, savedTheme);
    }
}

// Экспорт функций для глобального доступа
window.ClipboardManager = ClipboardManager;
window.SelectionHelper = SelectionHelper;
window.MarkdownFormatter = MarkdownFormatter;
window.DocumentStats = DocumentStats;
window.ExportManager = ExportManager;
window.ThemeManager = ThemeManager;
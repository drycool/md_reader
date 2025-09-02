/**
 * Главное приложение веб-редактора Markdown
 * Main Web Markdown Editor Application
 */

class MarkdownEditor {
    constructor() {
        this.currentFile = null;
        this.editor = null;
        this.isModified = false;
        this.autoSaveInterval = null;
        this.currentTab = 'editor';
        
        // Русские сообщения
        this.messages = {
            FILE_SAVED: 'Файл сохранён',
            FILE_LOADED: 'Файл загружен',
            ERROR_OCCURRED: 'Произошла ошибка',
            CONFIRM_NEW_FILE: 'Вы уверены? Несохранённые изменения будут потеряны.',
            AUTO_SAVE_ENABLED: 'Автосохранение включено',
            AUTO_SAVE_DISABLED: 'Автосохранение отключено',
            UNSAVED_CHANGES: 'Есть несохранённые изменения',
            SAVING: 'Сохранение...',
            LOADING: 'Загрузка...',
            READY: 'Готов'
        };
        
        this.init();
    }
    
    init() {
        this.initEditor();
        this.initEventListeners();
        this.initTabs();
        this.loadFileList();
        this.initAutoSave();
        this.initKeyboardShortcuts();
        
        // Показываем приветственное сообщение
        this.showNotification('success', 'Добро пожаловать!', 'Веб-редактор Markdown готов к работе');
    }
    
    initEditor() {
        const textarea = document.getElementById('markdownEditor');
        
        this.editor = CodeMirror.fromTextArea(textarea, {
            mode: 'markdown',
            theme: 'monokai',
            lineNumbers: true,
            lineWrapping: true,
            autoCloseBrackets: true,
            matchBrackets: true,
            extraKeys: {
                'Ctrl-S': () => this.saveCurrentFile(),
                'Ctrl-O': () => this.openFileDialog(),
                'Ctrl-N': () => this.createNewFile(),
                'F11': (cm) => {
                    cm.setOption('fullScreen', !cm.getOption('fullScreen'));
                },
                'Esc': (cm) => {
                    if (cm.getOption('fullScreen')) cm.setOption('fullScreen', false);
                }
            }
        });
        
        // Обновляем превью при изменении контента
        this.editor.on('change', () => {
            this.isModified = true;
            this.updateFileStatus();
            this.updatePreview();
            this.updateEditorInfo();
            this.updateWordCount();
        });
        
        // Обновляем информацию о курсоре
        this.editor.on('cursorActivity', () => {
            this.updateEditorInfo();
        });
    }
    
    initEventListeners() {
        // Кнопки в шапке
        document.getElementById('newFileBtn').addEventListener('click', () => this.showNewFileDialog());
        document.getElementById('openFileBtn').addEventListener('click', () => this.openFileDialog());
        document.getElementById('saveFileBtn').addEventListener('click', () => this.saveCurrentFile());
        document.getElementById('downloadBtn').addEventListener('click', () => this.downloadCurrentFile());
        document.getElementById('refreshFilesBtn').addEventListener('click', () => this.loadFileList());
        
        // Обработка загрузки файлов
        document.getElementById('fileInput').addEventListener('change', (e) => this.handleFileUpload(e));
        
        // Кнопки тулбара редактора
        document.querySelectorAll('.tool-btn').forEach(btn => {
            const action = btn.getAttribute('data-action');
            if (action) {
                btn.addEventListener('click', () => this.executeEditorAction(action));
            }
        });
        
        // Модальные окна
        this.initModalHandlers();
        
        // TOC toggle
        document.getElementById('tocToggle').addEventListener('click', () => this.toggleTOC());
        
        // Печать
        document.getElementById('printBtn').addEventListener('click', () => window.print());
    }
    
    initModalHandlers() {
        // Новый файл
        document.getElementById('confirmNewFile').addEventListener('click', () => this.createNewFileFromDialog());
        document.getElementById('cancelNewFile').addEventListener('click', () => this.hideModal('newFileModal'));
        
        // Ссылка
        document.getElementById('confirmLink').addEventListener('click', () => this.insertLinkFromDialog());
        document.getElementById('cancelLink').addEventListener('click', () => this.hideModal('linkModal'));
        
        // Изображение
        document.getElementById('confirmImage').addEventListener('click', () => this.insertImageFromDialog());
        document.getElementById('cancelImage').addEventListener('click', () => this.hideModal('imageModal'));
        
        // Закрытие модальных окон
        document.querySelectorAll('.close-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const modal = e.target.closest('.modal');
                this.hideModal(modal.id);
            });
        });
        
        // Закрытие по клику вне модального окна
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.hideModal(modal.id);
                }
            });
        });
    }
    
    initTabs() {
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', () => {
                const tabName = tab.getAttribute('data-tab');
                this.switchTab(tabName);
            });
        });
    }
    
    initAutoSave() {
        this.autoSaveInterval = setInterval(() => {
            if (this.isModified && this.currentFile) {
                this.saveCurrentFile(true); // true = автосохранение
            }
        }, 30000); // автосохранение каждые 30 секунд
    }
    
    initKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl+S - сохранить
            if (e.ctrlKey && e.key === 's') {
                e.preventDefault();
                this.saveCurrentFile();
            }
            
            // Ctrl+O - открыть
            if (e.ctrlKey && e.key === 'o') {
                e.preventDefault();
                this.openFileDialog();
            }
            
            // Ctrl+N - новый файл
            if (e.ctrlKey && e.key === 'n') {
                e.preventDefault();
                this.showNewFileDialog();
            }
            
            // F1 - справка
            if (e.key === 'F1') {
                e.preventDefault();
                this.showHelp();
            }
        });
    }
    
    switchTab(tabName) {
        // Обновляем активную вкладку
        document.querySelectorAll('.tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        
        // Показываем соответствующую панель
        document.querySelectorAll('.panel').forEach(panel => {
            panel.classList.remove('active');
        });
        
        if (tabName === 'split') {
            // Разделённый режим
            document.getElementById('editorPanel').classList.add('active');
            document.getElementById('previewPanel').classList.add('active');
            document.querySelector('.content-panels').classList.add('split-view');
        } else {
            document.querySelector('.content-panels').classList.remove('split-view');
            if (tabName === 'editor') {
                document.getElementById('editorPanel').classList.add('active');
            } else if (tabName === 'preview') {
                document.getElementById('previewPanel').classList.add('active');
            }
        }
        
        this.currentTab = tabName;
        
        // Обновляем превью при переключении на него
        if (tabName === 'preview' || tabName === 'split') {
            this.updatePreview();
        }
        
        // Обновляем редактор при переключении на него
        if (tabName === 'editor' || tabName === 'split') {
            setTimeout(() => this.editor.refresh(), 100);
        }
    }
    
    async loadFileList() {
        try {
            const response = await fetch('/api/files');
            const data = await response.json();
            
            if (data.status === 'success') {
                this.renderFileList(data.files);
            } else {
                this.showNotification('error', 'Ошибка', data.message);
            }
        } catch (error) {
            this.showNotification('error', 'Ошибка', `Не удалось загрузить список файлов: ${error.message}`);
        }
    }
    
    renderFileList(files) {
        const fileList = document.getElementById('fileList');
        
        if (files.length === 0) {
            fileList.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-folder-open"></i>
                    <p>Нет файлов</p>
                    <button class="btn btn-primary btn-sm" onclick="editor.showNewFileDialog()">
                        Создать первый файл
                    </button>
                </div>
            `;
            return;
        }
        
        fileList.innerHTML = files.map(file => {
            const size = this.formatFileSize(file.size);
            const modified = new Date(file.modified * 1000).toLocaleString('ru-RU');
            
            return `
                <div class="file-item" data-filename="${file.name}">
                    <i class="fas fa-file-text"></i>
                    <div class="file-info">
                        <div class="file-name">${file.name}</div>
                        <div class="file-meta">${size} • ${modified}</div>
                    </div>
                </div>
            `;
        }).join('');
        
        // Добавляем обработчики кликов на файлы
        document.querySelectorAll('.file-item').forEach(item => {
            item.addEventListener('click', () => {
                const filename = item.getAttribute('data-filename');
                this.loadFile(filename);
            });
        });
    }
    
    async loadFile(filename) {
        if (this.isModified && !confirm(this.messages.CONFIRM_NEW_FILE)) {
            return;
        }
        
        this.setFileStatus('loading', this.messages.LOADING);
        
        try {
            const response = await fetch(`/api/file/${filename}`);
            const data = await response.json();
            
            if (data.status === 'success') {
                this.editor.setValue(data.content);
                this.currentFile = filename;
                this.isModified = false;
                
                // Обновляем UI
                document.getElementById('currentFileName').textContent = filename;
                this.updateFileStatus();
                this.updatePreview();
                this.updateTOC(data.toc);
                
                // Выделяем файл в списке
                document.querySelectorAll('.file-item').forEach(item => {
                    item.classList.remove('active');
                });
                document.querySelector(`[data-filename="${filename}"]`)?.classList.add('active');
                
                this.showNotification('success', this.messages.FILE_LOADED, `Файл "${filename}" загружен`);
            } else {
                this.showNotification('error', this.messages.ERROR_OCCURRED, data.message);
            }
        } catch (error) {
            this.showNotification('error', this.messages.ERROR_OCCURRED, `Ошибка загрузки файла: ${error.message}`);
        } finally {
            this.setFileStatus('ready', this.messages.READY);
        }
    }
    
    async saveCurrentFile(isAutoSave = false) {
        if (!this.currentFile) {
            this.showNewFileDialog();
            return;
        }
        
        if (!isAutoSave) {
            this.setFileStatus('saving', this.messages.SAVING);
        }
        
        try {
            const response = await fetch(`/api/file/${this.currentFile}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    content: this.editor.getValue()
                })
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                this.isModified = false;
                this.updateFileStatus();
                
                if (!isAutoSave) {
                    this.showNotification('success', this.messages.FILE_SAVED, `Файл "${this.currentFile}" сохранён`);
                }
            } else {
                this.showNotification('error', this.messages.ERROR_OCCURRED, data.message);
            }
        } catch (error) {
            this.showNotification('error', this.messages.ERROR_OCCURRED, `Ошибка сохранения: ${error.message}`);
        } finally {
            if (!isAutoSave) {
                this.setFileStatus('ready', this.messages.READY);
            }
        }
    }
    
    showNewFileDialog() {
        if (this.isModified && !confirm(this.messages.CONFIRM_NEW_FILE)) {
            return;
        }
        
        document.getElementById('newFileName').value = '';
        this.showModal('newFileModal');
        document.getElementById('newFileName').focus();
    }
    
    async createNewFileFromDialog() {
        const filename = document.getElementById('newFileName').value.trim();
        
        if (!filename) {
            this.showNotification('error', 'Ошибка', 'Введите название файла');
            return;
        }
        
        try {
            const response = await fetch('/api/new', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ filename })
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                this.editor.setValue(data.content);
                this.currentFile = data.filename;
                this.isModified = false;
                
                document.getElementById('currentFileName').textContent = data.filename;
                this.updateFileStatus();
                this.updatePreview();
                this.loadFileList();
                
                this.hideModal('newFileModal');
                this.showNotification('success', 'Файл создан', `Новый файл "${data.filename}" создан`);
            } else {
                this.showNotification('error', this.messages.ERROR_OCCURRED, data.message);
            }
        } catch (error) {
            this.showNotification('error', this.messages.ERROR_OCCURRED, `Ошибка создания файла: ${error.message}`);
        }
    }
    
    openFileDialog() {
        document.getElementById('fileInput').click();
    }
    
    async handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                this.loadFileList();
                this.loadFile(data.filename);
                this.showNotification('success', 'Файл загружен', data.message);
            } else {
                this.showNotification('error', this.messages.ERROR_OCCURRED, data.message);
            }
        } catch (error) {
            this.showNotification('error', this.messages.ERROR_OCCURRED, `Ошибка загрузки: ${error.message}`);
        }
        
        // Очищаем input
        event.target.value = '';
    }
    
    downloadCurrentFile() {
        if (!this.currentFile) {
            this.showNotification('warning', 'Предупреждение', 'Нет файла для загрузки');
            return;
        }
        
        window.open(`/api/download/${this.currentFile}`, '_blank');
    }
    
    updatePreview() {
        const content = this.editor.getValue();
        const previewContent = document.getElementById('previewContent');
        
        if (!content.trim()) {
            previewContent.innerHTML = `
                <div class="welcome-message">
                    <h2>Начните печатать...</h2>
                    <p>Ваш Markdown будет отображён здесь</p>
                </div>
            `;
            return;
        }
        
        try {
            const html = marked.parse(content, {
                highlight: function(code, lang) {
                    if (lang && hljs.getLanguage(lang)) {
                        return hljs.highlight(code, { language: lang }).value;
                    }
                    return hljs.highlightAuto(code).value;
                },
                breaks: true,
                gfm: true
            });
            
            previewContent.innerHTML = html;
            
            // Генерируем TOC из заголовков
            this.generateTOC(previewContent);
            
        } catch (error) {
            console.error('Ошибка при рендеринге Markdown:', error);
            previewContent.innerHTML = `<div class="error">Ошибка при рендеринге Markdown: ${error.message}</div>`;
        }
    }
    
    generateTOC(container) {
        const headings = container.querySelectorAll('h1, h2, h3, h4, h5, h6');
        const tocContent = document.getElementById('tocContent');
        
        if (headings.length === 0) {
            tocContent.innerHTML = '<p>Заголовки не найдены</p>';
            return;
        }
        
        const tocItems = Array.from(headings).map((heading, index) => {
            const level = parseInt(heading.tagName.substring(1));
            const text = heading.textContent;
            const id = `heading-${index}`;
            
            heading.id = id;
            
            return `
                <div class="toc-item level-${level}" data-target="${id}">
                    ${text}
                </div>
            `;
        }).join('');
        
        tocContent.innerHTML = tocItems;
        
        // Добавляем обработчики кликов для навигации
        document.querySelectorAll('.toc-item').forEach(item => {
            item.addEventListener('click', () => {
                const targetId = item.getAttribute('data-target');
                const target = document.getElementById(targetId);
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            });
        });
    }
    
    updateTOC(tocData) {
        const tocContent = document.getElementById('tocContent');
        
        if (!tocData || tocData.length === 0) {
            tocContent.innerHTML = '<p>Заголовки не найдены</p>';
            return;
        }
        
        const tocItems = tocData.map((item, index) => {
            const [title, level, line] = item;
            return `
                <div class="toc-item level-${level}" data-line="${line}">
                    ${title}
                </div>
            `;
        }).join('');
        
        tocContent.innerHTML = tocItems;
        
        // Добавляем обработчики кликов для перехода к строке в редакторе
        document.querySelectorAll('.toc-item').forEach(item => {
            item.addEventListener('click', () => {
                const line = parseInt(item.getAttribute('data-line'));
                this.editor.setCursor(line, 0);
                this.editor.focus();
                
                // Переключаемся на редактор, если он не активен
                if (this.currentTab === 'preview') {
                    this.switchTab('split');
                }
            });
        });
    }
    
    toggleTOC() {
        const tocSidebar = document.getElementById('tocSidebar');
        tocSidebar.classList.toggle('visible');
        
        const toggleBtn = document.getElementById('tocToggle');
        if (tocSidebar.classList.contains('visible')) {
            toggleBtn.classList.add('active');
        } else {
            toggleBtn.classList.remove('active');
        }
    }
    
    executeEditorAction(action) {
        const cursor = this.editor.getCursor();
        const selection = this.editor.getSelection();
        
        switch (action) {
            case 'bold':
                this.wrapText('**', '**');
                break;
            case 'italic':
                this.wrapText('*', '*');
                break;
            case 'strikethrough':
                this.wrapText('~~', '~~');
                break;
            case 'heading':
                this.insertAtLineStart('## ');
                break;
            case 'link':
                this.showModal('linkModal');
                break;
            case 'image':
                this.showModal('imageModal');
                break;
            case 'code':
                if (selection.includes('\n')) {
                    this.wrapText('```\n', '\n```');
                } else {
                    this.wrapText('`', '`');
                }
                break;
            case 'quote':
                this.insertAtLineStart('> ');
                break;
            case 'list':
                this.insertAtLineStart('- ');
                break;
            case 'table':
                this.insertTable();
                break;
            case 'hr':
                this.insertText('\n---\n');
                break;
        }
        
        this.editor.focus();
    }
    
    wrapText(before, after) {
        const selection = this.editor.getSelection();
        if (selection) {
            this.editor.replaceSelection(before + selection + after);
        } else {
            this.editor.replaceSelection(before + after);
            const cursor = this.editor.getCursor();
            this.editor.setCursor(cursor.line, cursor.ch - after.length);
        }
    }
    
    insertAtLineStart(prefix) {
        const cursor = this.editor.getCursor();
        const line = this.editor.getLine(cursor.line);
        this.editor.replaceRange(prefix, { line: cursor.line, ch: 0 });
    }
    
    insertText(text) {
        this.editor.replaceSelection(text);
    }
    
    insertTable() {
        const table = `
| Колонка 1 | Колонка 2 | Колонка 3 |
|-----------|-----------|-----------|
| Ячейка 1  | Ячейка 2  | Ячейка 3  |
| Ячейка 4  | Ячейка 5  | Ячейка 6  |
`;
        this.insertText(table);
    }
    
    insertLinkFromDialog() {
        const text = document.getElementById('linkText').value;
        const url = document.getElementById('linkUrl').value;
        
        if (url) {
            const linkText = text || url;
            this.insertText(`[${linkText}](${url})`);
            this.hideModal('linkModal');
            
            // Очищаем поля
            document.getElementById('linkText').value = '';
            document.getElementById('linkUrl').value = '';
        }
    }
    
    insertImageFromDialog() {
        const alt = document.getElementById('imageAlt').value;
        const url = document.getElementById('imageUrl').value;
        
        if (url) {
            const altText = alt || 'Изображение';
            this.insertText(`![${altText}](${url})`);
            this.hideModal('imageModal');
            
            // Очищаем поля
            document.getElementById('imageAlt').value = '';
            document.getElementById('imageUrl').value = '';
        }
    }
    
    updateFileStatus() {
        const statusElement = document.getElementById('fileStatus');
        
        if (this.isModified) {
            statusElement.textContent = this.messages.UNSAVED_CHANGES;
            statusElement.className = 'status-saving';
        } else {
            statusElement.textContent = this.messages.READY;
            statusElement.className = 'status-ready';
        }
    }
    
    setFileStatus(type, message) {
        const statusElement = document.getElementById('fileStatus');
        statusElement.textContent = message;
        statusElement.className = `status-${type}`;
    }
    
    updateEditorInfo() {
        const cursor = this.editor.getCursor();
        const info = document.getElementById('editorInfo');
        info.textContent = `Строка: ${cursor.line + 1}, Столбец: ${cursor.ch + 1}`;
    }
    
    updateWordCount() {
        const content = this.editor.getValue();
        const words = content.trim() ? content.trim().split(/\s+/).length : 0;
        const chars = content.length;
        
        document.getElementById('wordCount').textContent = `Слов: ${words} • Символов: ${chars}`;
    }
    
    showModal(modalId) {
        document.getElementById(modalId).classList.add('active');
    }
    
    hideModal(modalId) {
        document.getElementById(modalId).classList.remove('active');
    }
    
    showNotification(type, title, message) {
        const notifications = document.getElementById('notifications');
        const notificationId = 'notification-' + Date.now();
        
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.id = notificationId;
        notification.innerHTML = `
            <div class="notification-content">
                <div class="notification-icon">
                    <i class="${icons[type] || icons.info}"></i>
                </div>
                <div class="notification-text">
                    <div class="notification-title">${title}</div>
                    <div class="notification-message">${message}</div>
                </div>
            </div>
            <button class="notification-close" onclick="editor.hideNotification('${notificationId}')">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        notifications.appendChild(notification);
        
        // Автоматически скрываем через 5 секунд
        setTimeout(() => {
            this.hideNotification(notificationId);
        }, 5000);
    }
    
    hideNotification(notificationId) {
        const notification = document.getElementById(notificationId);
        if (notification) {
            notification.style.animation = 'notificationSlide 0.3s ease reverse';
            setTimeout(() => {
                notification.remove();
            }, 300);
        }
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Б';
        
        const k = 1024;
        const sizes = ['Б', 'КБ', 'МБ', 'ГБ'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }
    
    showHelp() {
        this.showNotification('info', 'Справка', 'Горячие клавиши: Ctrl+S (сохранить), Ctrl+O (открыть), Ctrl+N (новый файл)');
    }
    
    // Очистка при закрытии
    destroy() {
        if (this.autoSaveInterval) {
            clearInterval(this.autoSaveInterval);
        }
    }
}

// Инициализация приложения
let editor;

document.addEventListener('DOMContentLoaded', () => {
    editor = new MarkdownEditor();
});

// Обработка закрытия окна
window.addEventListener('beforeunload', (e) => {
    if (editor && editor.isModified) {
        e.preventDefault();
        e.returnValue = 'У вас есть несохранённые изменения. Вы уверены, что хотите покинуть страницу?';
        return e.returnValue;
    }
});

// Экспорт для глобального доступа
window.editor = editor;
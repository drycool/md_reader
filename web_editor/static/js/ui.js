/**
 * UI компоненты и интерактивность
 * UI Components and Interactivity
 */

// Класс для управления пользовательским интерфейсом
class UIManager {
    constructor() {
        this.sidebar = document.querySelector('.sidebar');
        this.workspace = document.querySelector('.workspace');
        this.mobileBreakpoint = 768;
        
        this.init();
    }
    
    init() {
        this.initResponsive();
        this.initDragAndDrop();
        this.initContextMenu();
        this.initTooltips();
        this.initKeyboardNavigation();
    }
    
    initResponsive() {
        // Проверяем размер экрана и адаптируем интерфейс
        const checkScreenSize = () => {
            if (window.innerWidth <= this.mobileBreakpoint) {
                this.enableMobileMode();
            } else {
                this.disableMobileMode();
            }
        };
        
        checkScreenSize();
        window.addEventListener('resize', checkScreenSize);
        
        // Кнопка для показа/скрытия сайдбара на мобильных
        this.createMobileToggle();
    }
    
    createMobileToggle() {
        const toggle = document.createElement('button');
        toggle.className = 'mobile-sidebar-toggle';
        toggle.innerHTML = '<i class="fas fa-bars"></i>';
        toggle.addEventListener('click', () => this.toggleSidebar());
        
        document.querySelector('.header-content').insertBefore(
            toggle, 
            document.querySelector('.header-actions')
        );
    }
    
    enableMobileMode() {
        document.body.classList.add('mobile-mode');
        this.sidebar.classList.remove('visible');
    }
    
    disableMobileMode() {
        document.body.classList.remove('mobile-mode');
        this.sidebar.classList.add('visible');
    }
    
    toggleSidebar() {
        this.sidebar.classList.toggle('visible');
    }
    
    initDragAndDrop() {
        const dropZone = document.querySelector('.workspace');
        
        // Предотвращаем стандартное поведение браузера
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, this.preventDefaults, false);
            document.body.addEventListener(eventName, this.preventDefaults, false);
        });
        
        // Подсвечиваем область при перетаскивании
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => this.highlight(dropZone), false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => this.unhighlight(dropZone), false);
        });
        
        // Обрабатываем сброс файлов
        dropZone.addEventListener('drop', this.handleDrop.bind(this), false);
    }
    
    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    highlight(element) {
        element.classList.add('drag-over');
    }
    
    unhighlight(element) {
        element.classList.remove('drag-over');
    }
    
    async handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            const file = files[0];
            
            // Проверяем, что это Markdown файл
            if (file.name.endsWith('.md') || file.type === 'text/markdown') {
                await this.loadDroppedFile(file);
            } else {
                window.editor?.showNotification('warning', 'Неподдерживаемый формат', 'Поддерживаются только .md файлы');
            }
        }
    }
    
    async loadDroppedFile(file) {
        try {
            const content = await this.readFileAsText(file);
            
            if (window.editor) {
                // Проверяем на несохранённые изменения
                if (window.editor.isModified && !confirm('У вас есть несохранённые изменения. Продолжить?')) {
                    return;
                }
                
                window.editor.editor.setValue(content);
                window.editor.currentFile = file.name;
                window.editor.isModified = false;
                
                document.getElementById('currentFileName').textContent = file.name;
                window.editor.updateFileStatus();
                window.editor.updatePreview();
                
                window.editor.showNotification('success', 'Файл загружен', `Файл "${file.name}" загружен из буфера`);
            }
        } catch (error) {
            window.editor?.showNotification('error', 'Ошибка', `Не удалось загрузить файл: ${error.message}`);
        }
    }
    
    readFileAsText(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = e => resolve(e.target.result);
            reader.onerror = e => reject(new Error('Ошибка чтения файла'));
            reader.readAsText(file, 'UTF-8');
        });
    }
    
    initContextMenu() {
        // Создаём контекстное меню для редактора
        const contextMenu = this.createContextMenu();
        document.body.appendChild(contextMenu);
        
        // Показываем меню по правому клику
        document.addEventListener('contextmenu', (e) => {
            // Показываем только в области редактора
            if (e.target.closest('.CodeMirror')) {
                e.preventDefault();
                this.showContextMenu(e, contextMenu);
            }
        });
        
        // Скрываем меню при клике в другом месте
        document.addEventListener('click', () => {
            this.hideContextMenu(contextMenu);
        });
    }
    
    createContextMenu() {
        const menu = document.createElement('div');
        menu.className = 'context-menu';
        menu.innerHTML = `
            <div class="context-menu-item" data-action="cut">
                <i class="fas fa-cut"></i> Вырезать
            </div>
            <div class="context-menu-item" data-action="copy">
                <i class="fas fa-copy"></i> Копировать
            </div>
            <div class="context-menu-item" data-action="paste">
                <i class="fas fa-paste"></i> Вставить
            </div>
            <div class="context-menu-separator"></div>
            <div class="context-menu-item" data-action="selectAll">
                <i class="fas fa-check-square"></i> Выделить всё
            </div>
            <div class="context-menu-item" data-action="selectLine">
                <i class="fas fa-minus"></i> Выделить строку
            </div>
            <div class="context-menu-separator"></div>
            <div class="context-menu-item" data-action="format">
                <i class="fas fa-align-left"></i> Форматировать
            </div>
            <div class="context-menu-item" data-action="stats">
                <i class="fas fa-chart-bar"></i> Статистика
            </div>
        `;
        
        // Добавляем обработчики
        menu.addEventListener('click', (e) => {
            const action = e.target.closest('.context-menu-item')?.getAttribute('data-action');
            if (action) {
                this.executeContextAction(action);
                this.hideContextMenu(menu);
            }
        });
        
        return menu;
    }
    
    showContextMenu(e, menu) {
        menu.style.display = 'block';
        menu.style.left = e.pageX + 'px';
        menu.style.top = e.pageY + 'px';
        
        // Проверяем, не выходит ли меню за границы экрана
        const rect = menu.getBoundingClientRect();
        if (rect.right > window.innerWidth) {
            menu.style.left = (e.pageX - rect.width) + 'px';
        }
        if (rect.bottom > window.innerHeight) {
            menu.style.top = (e.pageY - rect.height) + 'px';
        }
    }
    
    hideContextMenu(menu) {
        menu.style.display = 'none';
    }
    
    executeContextAction(action) {
        const editor = window.editor?.editor;
        if (!editor) return;
        
        switch (action) {
            case 'cut':
                editor.execCommand('cut');
                break;
            case 'copy':
                editor.execCommand('copy');
                break;
            case 'paste':
                editor.execCommand('paste');
                break;
            case 'selectAll':
                SelectionHelper.selectAll(editor);
                break;
            case 'selectLine':
                SelectionHelper.selectLine(editor);
                break;
            case 'format':
                MarkdownFormatter.formatDocument(editor);
                break;
            case 'stats':
                const content = editor.getValue();
                const stats = DocumentStats.displayStats(content);
                window.editor?.showNotification('info', 'Статистика документа', stats);
                break;
        }
    }
    
    initTooltips() {
        // Создаём простые tooltip'ы для кнопок
        document.querySelectorAll('[title]').forEach(element => {
            element.addEventListener('mouseenter', (e) => {
                this.showTooltip(e.target, e.target.getAttribute('title'));
            });
            
            element.addEventListener('mouseleave', () => {
                this.hideTooltip();
            });
        });
    }
    
    showTooltip(element, text) {
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = text;
        document.body.appendChild(tooltip);
        
        const rect = element.getBoundingClientRect();
        tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
        tooltip.style.top = rect.bottom + 5 + 'px';
        
        this.currentTooltip = tooltip;
    }
    
    hideTooltip() {
        if (this.currentTooltip) {
            this.currentTooltip.remove();
            this.currentTooltip = null;
        }
    }
    
    initKeyboardNavigation() {
        // Навигация по файлам с клавиатуры
        document.addEventListener('keydown', (e) => {
            // Ctrl+Shift+O - быстрое открытие файла
            if (e.ctrlKey && e.shiftKey && e.key === 'O') {
                e.preventDefault();
                this.showQuickOpen();
            }
            
            // Escape - закрыть модальные окна
            if (e.key === 'Escape') {
                this.closeAllModals();
            }
            
            // F1 - справка
            if (e.key === 'F1') {
                e.preventDefault();
                this.showHelp();
            }
        });
    }
    
    showQuickOpen() {
        // Создаём быстрый поиск файлов
        const quickOpen = document.createElement('div');
        quickOpen.className = 'quick-open-overlay';
        quickOpen.innerHTML = `
            <div class="quick-open-dialog">
                <input type="text" class="quick-open-input" placeholder="Начните печатать название файла...">
                <div class="quick-open-results"></div>
                <div class="quick-open-help">
                    <kbd>↑↓</kbd> навигация • <kbd>Enter</kbd> открыть • <kbd>Esc</kbd> отмена
                </div>
            </div>
        `;
        
        document.body.appendChild(quickOpen);
        
        const input = quickOpen.querySelector('.quick-open-input');
        const results = quickOpen.querySelector('.quick-open-results');
        
        input.focus();
        
        // Обработка поиска
        input.addEventListener('input', async (e) => {
            const query = e.target.value.toLowerCase();
            await this.searchFiles(query, results);
        });
        
        // Обработка навигации
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                quickOpen.remove();
            } else if (e.key === 'Enter') {
                const selected = results.querySelector('.selected');
                if (selected) {
                    const filename = selected.getAttribute('data-filename');
                    window.editor?.loadFile(filename);
                    quickOpen.remove();
                }
            } else if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
                e.preventDefault();
                this.navigateResults(results, e.key === 'ArrowDown' ? 1 : -1);
            }
        });
        
        // Закрытие при клике вне диалога
        quickOpen.addEventListener('click', (e) => {
            if (e.target === quickOpen) {
                quickOpen.remove();
            }
        });
        
        // Загружаем начальный список файлов
        this.searchFiles('', results);
    }
    
    async searchFiles(query, resultsContainer) {
        try {
            const response = await fetch('/api/files');
            const data = await response.json();
            
            if (data.status === 'success') {
                const filtered = data.files.filter(file => 
                    file.name.toLowerCase().includes(query)
                );
                
                resultsContainer.innerHTML = filtered.map((file, index) => `
                    <div class="quick-open-result ${index === 0 ? 'selected' : ''}" data-filename="${file.name}">
                        <i class="fas fa-file-text"></i>
                        <span class="filename">${this.highlightMatch(file.name, query)}</span>
                        <span class="file-size">${this.formatFileSize(file.size)}</span>
                    </div>
                `).join('');
                
                // Добавляем обработчики кликов
                resultsContainer.querySelectorAll('.quick-open-result').forEach(item => {
                    item.addEventListener('click', () => {
                        const filename = item.getAttribute('data-filename');
                        window.editor?.loadFile(filename);
                        document.querySelector('.quick-open-overlay').remove();
                    });
                });
            }
        } catch (error) {
            resultsContainer.innerHTML = '<div class="error">Ошибка загрузки файлов</div>';
        }
    }
    
    navigateResults(container, direction) {
        const items = container.querySelectorAll('.quick-open-result');
        const current = container.querySelector('.selected');
        const currentIndex = Array.from(items).indexOf(current);
        
        let newIndex = currentIndex + direction;
        if (newIndex < 0) newIndex = items.length - 1;
        if (newIndex >= items.length) newIndex = 0;
        
        items.forEach(item => item.classList.remove('selected'));
        if (items[newIndex]) {
            items[newIndex].classList.add('selected');
            items[newIndex].scrollIntoView({ block: 'nearest' });
        }
    }
    
    highlightMatch(text, query) {
        if (!query) return text;
        
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Б';
        
        const k = 1024;
        const sizes = ['Б', 'КБ', 'МБ', 'ГБ'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }
    
    closeAllModals() {
        document.querySelectorAll('.modal.active').forEach(modal => {
            modal.classList.remove('active');
        });
    }
    
    showHelp() {
        const helpContent = `
        <h3>Горячие клавиши</h3>
        <ul>
            <li><kbd>Ctrl+S</kbd> - Сохранить файл</li>
            <li><kbd>Ctrl+O</kbd> - Открыть файл</li>
            <li><kbd>Ctrl+N</kbd> - Новый файл</li>
            <li><kbd>Ctrl+Shift+O</kbd> - Быстрое открытие</li>
            <li><kbd>F11</kbd> - Полноэкранный режим</li>
            <li><kbd>F1</kbd> - Справка</li>
        </ul>
        
        <h3>Markdown синтаксис</h3>
        <ul>
            <li><code># Заголовок</code> - Заголовок</li>
            <li><code>**текст**</code> - Жирный текст</li>
            <li><code>*текст*</code> - Курсив</li>
            <li><code>[ссылка](URL)</code> - Ссылка</li>
            <li><code>![alt](URL)</code> - Изображение</li>
            <li><code>\`код\`</code> - Инлайн-код</li>
        </ul>
        `;
        
        window.editor?.showNotification('info', 'Справка', helpContent);
    }
}

// Класс для работы с настройками
class SettingsManager {
    static defaults = {
        theme: 'dark',
        fontSize: 14,
        lineHeight: 1.6,
        wordWrap: true,
        autoSave: true,
        autoSaveInterval: 30000,
        showLineNumbers: true,
        tabSize: 4
    };
    
    static get(key) {
        const value = localStorage.getItem(`markdown-editor-${key}`);
        return value !== null ? JSON.parse(value) : this.defaults[key];
    }
    
    static set(key, value) {
        localStorage.setItem(`markdown-editor-${key}`, JSON.stringify(value));
    }
    
    static getAll() {
        const settings = {};
        Object.keys(this.defaults).forEach(key => {
            settings[key] = this.get(key);
        });
        return settings;
    }
    
    static reset() {
        Object.keys(this.defaults).forEach(key => {
            localStorage.removeItem(`markdown-editor-${key}`);
        });
    }
}

// Инициализация UI при загрузке DOM
document.addEventListener('DOMContentLoaded', () => {
    window.uiManager = new UIManager();
});

// Экспорт для глобального доступа
window.UIManager = UIManager;
window.SettingsManager = SettingsManager;
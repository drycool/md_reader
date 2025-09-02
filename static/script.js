// Глобальные переменные
let currentFile = '';
let hasUnsavedChanges = false;

// Элементы DOM
const editor = document.getElementById('editor');
const preview = document.getElementById('preview');
const fileSelect = document.getElementById('fileSelect');
const saveBtn = document.getElementById('saveBtn');
const newFileBtn = document.getElementById('newFileBtn');
const statusElement = document.getElementById('status');
const currentFileElement = document.getElementById('currentFile');
const newFileModal = document.getElementById('newFileModal');
const newFileName = document.getElementById('newFileName');
const createFileBtn = document.getElementById('createFileBtn');
const cancelBtn = document.getElementById('cancelBtn');

// Инициализация
document.addEventListener('DOMContentLoaded', function() {
    initializeEditor();
    loadFilesList();
    
    // Загружаем демо файл если он есть
    if (fileSelect.options.length > 1) {
        const demoOption = Array.from(fileSelect.options).find(option => option.value === 'demo.md');
        if (demoOption) {
            fileSelect.value = 'demo.md';
            loadFile('demo.md');
        }
    }
});

// Инициализация редактора
function initializeEditor() {
    // Обновление предпросмотра при вводе
    editor.addEventListener('input', function() {
        updatePreview();
        markAsChanged();
    });

    // Сохранение при Ctrl+S
    editor.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 's') {
            e.preventDefault();
            saveCurrentFile();
        }
    });

    // Обработчики событий
    fileSelect.addEventListener('change', handleFileSelect);
    saveBtn.addEventListener('click', saveCurrentFile);
    newFileBtn.addEventListener('click', showNewFileModal);
    createFileBtn.addEventListener('click', createNewFile);
    cancelBtn.addEventListener('click', hideNewFileModal);

    // Закрытие модального окна при клике вне его
    newFileModal.addEventListener('click', function(e) {
        if (e.target === newFileModal) {
            hideNewFileModal();
        }
    });

    // Создание файла по Enter
    newFileName.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            createNewFile();
        }
    });
}

// Обновление предпросмотра
function updatePreview() {
    const markdownText = editor.value;
    if (markdownText.trim() === '') {
        preview.innerHTML = '<p class="placeholder">Предпросмотр будет отображен здесь...</p>';
        return;
    }
    
    try {
        const html = marked.parse(markdownText);
        preview.innerHTML = html;
    } catch (error) {
        preview.innerHTML = '<p style="color: red;">Ошибка обработки Markdown: ' + error.message + '</p>';
    }
}

// Загрузка списка файлов
function loadFilesList() {
    fetch('/api/files')
        .then(response => response.json())
        .then(files => {
            const currentValue = fileSelect.value;
            fileSelect.innerHTML = '<option value="">Выберите файл...</option>';
            
            files.forEach(file => {
                const option = document.createElement('option');
                option.value = file;
                option.textContent = file;
                fileSelect.appendChild(option);
            });
            
            // Восстанавливаем выбранный файл
            if (currentValue && files.includes(currentValue)) {
                fileSelect.value = currentValue;
            }
        })
        .catch(error => {
            showStatus('Ошибка загрузки списка файлов: ' + error.message, 'error');
        });
}

// Обработка выбора файла
function handleFileSelect() {
    const filename = fileSelect.value;
    if (filename) {
        if (hasUnsavedChanges) {
            if (confirm('У вас есть несохраненные изменения. Продолжить без сохранения?')) {
                loadFile(filename);
            } else {
                fileSelect.value = currentFile;
            }
        } else {
            loadFile(filename);
        }
    }
}

// Загрузка файла
function loadFile(filename) {
    showStatus('Загрузка файла...', 'loading');
    
    fetch(`/api/file/${filename}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                editor.value = data.content;
                currentFile = filename;
                hasUnsavedChanges = false;
                updateCurrentFileDisplay();
                updatePreview();
                showStatus('Файл загружен', 'success');
            } else {
                showStatus('Ошибка загрузки файла: ' + data.error, 'error');
            }
        })
        .catch(error => {
            showStatus('Ошибка загрузки файла: ' + error.message, 'error');
        });
}

// Сохранение текущего файла
function saveCurrentFile() {
    if (!currentFile) {
        showStatus('Выберите файл для сохранения', 'error');
        return;
    }
    
    showStatus('Сохранение...', 'loading');
    
    const content = editor.value;
    
    fetch(`/api/file/${currentFile}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content: content })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            hasUnsavedChanges = false;
            updateCurrentFileDisplay();
            showStatus('Файл сохранен', 'success');
        } else {
            showStatus('Ошибка сохранения: ' + data.error, 'error');
        }
    })
    .catch(error => {
        showStatus('Ошибка сохранения: ' + error.message, 'error');
    });
}

// Показать модальное окно создания файла
function showNewFileModal() {
    newFileModal.style.display = 'block';
    newFileName.value = '';
    newFileName.focus();
}

// Скрыть модальное окно
function hideNewFileModal() {
    newFileModal.style.display = 'none';
}

// Создание нового файла
function createNewFile() {
    const filename = newFileName.value.trim();
    if (!filename) {
        alert('Введите имя файла');
        return;
    }
    
    showStatus('Создание файла...', 'loading');
    
    fetch('/api/new', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ filename: filename })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            hideNewFileModal();
            loadFilesList();
            
            // Выбираем и загружаем новый файл
            const fullFilename = filename.endsWith('.md') ? filename : filename + '.md';
            setTimeout(() => {
                fileSelect.value = fullFilename;
                loadFile(fullFilename);
            }, 100);
            
            showStatus('Файл создан', 'success');
        } else {
            showStatus('Ошибка создания файла: ' + data.error, 'error');
        }
    })
    .catch(error => {
        showStatus('Ошибка создания файла: ' + error.message, 'error');
    });
}

// Пометка как измененный
function markAsChanged() {
    if (!hasUnsavedChanges) {
        hasUnsavedChanges = true;
        updateCurrentFileDisplay();
    }
}

// Обновление отображения текущего файла
function updateCurrentFileDisplay() {
    if (currentFile) {
        const displayName = hasUnsavedChanges ? currentFile + ' *' : currentFile;
        currentFileElement.textContent = displayName;
    } else {
        currentFileElement.textContent = 'Файл не выбран';
    }
}

// Показать статус
function showStatus(message, type = 'info') {
    statusElement.textContent = message;
    statusElement.className = 'status-' + type;
    
    // Автоматически очищаем статус через 3 секунды для success и error
    if (type === 'success' || type === 'error') {
        setTimeout(() => {
            statusElement.textContent = 'Готов';
            statusElement.className = '';
        }, 3000);
    }
}

// Предупреждение при закрытии страницы с несохраненными изменениями
window.addEventListener('beforeunload', function(e) {
    if (hasUnsavedChanges) {
        e.preventDefault();
        e.returnValue = '';
    }
});

// Обработка ошибок JavaScript
window.addEventListener('error', function(e) {
    console.error('JavaScript ошибка:', e.error);
    showStatus('Произошла ошибка в приложении', 'error');
});

// Экспорт функций для отладки (только в разработке)
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    window.debugFunctions = {
        loadFile,
        saveCurrentFile,
        updatePreview,
        loadFilesList
    };
}
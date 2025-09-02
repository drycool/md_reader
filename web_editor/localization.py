#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Локализация для веб-редактора Markdown
Localization for Web Markdown Editor

Все сообщения интерфейса и уведомления на русском языке
"""

class RussianMessages:
    """Русские сообщения для веб-редактора"""
    
    # ========== ОСНОВНЫЕ СООБЩЕНИЯ ==========
    APP_TITLE = "Веб-редактор Markdown"
    WELCOME = "Добро пожаловать в веб-редактор Markdown!"
    READY = "Готов к работе"
    LOADING = "Загрузка..."
    SAVING = "Сохранение..."
    PROCESSING = "Обработка..."
    
    # ========== ФАЙЛОВЫЕ ОПЕРАЦИИ ==========
    FILE_OPERATIONS = {
        'new_file': "Новый файл",
        'open_file': "Открыть файл", 
        'save_file': "Сохранить файл",
        'download_file': "Скачать файл",
        'upload_file': "Загрузить файл",
        'file_loaded': "Файл загружен",
        'file_saved': "Файл сохранён",
        'file_created': "Файл создан",
        'file_uploaded': "Файл загружен",
        'file_downloaded': "Файл загружен"
    }
    
    # ========== СООБЩЕНИЯ ОБ ОШИБКАХ ==========
    ERRORS = {
        'generic_error': "Произошла ошибка",
        'file_not_found': "Файл не найден",
        'invalid_file_type': "Неподдерживаемый тип файла",
        'file_too_large': "Файл слишком большой (максимум 16МБ)",
        'upload_error': "Ошибка загрузки файла",
        'save_error': "Ошибка сохранения файла",
        'load_error': "Ошибка загрузки файла",
        'network_error': "Ошибка сети",
        'permission_error': "Недостаточно прав доступа",
        'disk_full': "Недостаточно места на диске",
        'connection_lost': "Соединение потеряно"
    }
    
    # ========== ПРЕДУПРЕЖДЕНИЯ ==========
    WARNINGS = {
        'unsaved_changes': "У вас есть несохранённые изменения",
        'confirm_new_file': "Вы уверены? Несохранённые изменения будут потеряны.",
        'confirm_close': "Закрыть без сохранения?",
        'large_file': "Файл большой, загрузка может занять время",
        'old_browser': "Ваш браузер устарел, некоторые функции могут не работать"
    }
    
    # ========== ЭЛЕМЕНТЫ ИНТЕРФЕЙСА ==========
    UI_ELEMENTS = {
        # Главное меню
        'editor': "Редактор",
        'preview': "Предварительный просмотр", 
        'split_mode': "Разделённый режим",
        'file_manager': "Менеджер файлов",
        'settings': "Настройки",
        
        # Панель инструментов
        'bold': "Жирный",
        'italic': "Курсив", 
        'strikethrough': "Зачёркнутый",
        'heading': "Заголовок",
        'link': "Ссылка",
        'image': "Изображение",
        'code': "Код",
        'quote': "Цитата",
        'list': "Список",
        'table': "Таблица",
        'horizontal_rule': "Горизонтальная линия",
        
        # Дополнительные инструменты
        'toc': "Оглавление",
        'print': "Печать",
        'fullscreen': "Полный экран",
        'word_wrap': "Перенос строк",
        'line_numbers': "Номера строк",
        'search': "Поиск",
        'replace': "Замена",
        'format': "Форматирование",
        'statistics': "Статистика"
    }
    
    # ========== МОДАЛЬНЫЕ ОКНА ==========
    MODALS = {
        # Новый файл
        'new_file_title': "Создать новый файл",
        'new_file_name': "Название файла:",
        'new_file_placeholder': "новый_документ.md",
        'new_file_help': "Файл будет создан с расширением .md",
        
        # Ссылка
        'link_title': "Вставить ссылку", 
        'link_text': "Текст ссылки:",
        'link_url': "URL:",
        'link_text_placeholder': "Описание ссылки",
        'link_url_placeholder': "https://example.com",
        
        # Изображение
        'image_title': "Вставить изображение",
        'image_alt': "Описание изображения:",
        'image_url': "URL изображения:",
        'image_alt_placeholder': "Описание изображения",
        'image_url_placeholder': "https://example.com/image.jpg",
        
        # Кнопки
        'cancel': "Отмена",
        'create': "Создать", 
        'insert': "Вставить",
        'save': "Сохранить",
        'close': "Закрыть"
    }
    
    # ========== СТАТУСЫ И УВЕДОМЛЕНИЯ ==========
    STATUS = {
        'ready': "Готов",
        'modified': "Изменён", 
        'saving': "Сохранение...",
        'saved': "Сохранено",
        'loading': "Загрузка...",
        'loaded': "Загружено",
        'error': "Ошибка",
        'offline': "Не в сети",
        'online': "В сети"
    }
    
    # ========== АВТОСОХРАНЕНИЕ ==========
    AUTOSAVE = {
        'enabled': "Автосохранение включено",
        'disabled': "Автосохранение отключено", 
        'saving': "Автосохранение...",
        'saved': "Автосохранено",
        'failed': "Автосохранение не удалось"
    }
    
    # ========== СТАТИСТИКА ДОКУМЕНТА ==========
    STATISTICS = {
        'title': "Статистика документа",
        'lines': "Строк",
        'words': "Слов", 
        'characters': "Символов",
        'characters_no_spaces': "Символов без пробелов",
        'headings': "Заголовков",
        'links': "Ссылок",
        'images': "Изображений", 
        'code_blocks': "Блоков кода",
        'inline_code': "Инлайн-кода",
        'reading_time': "Время чтения"
    }
    
    # ========== ГОРЯЧИЕ КЛАВИШИ ==========
    SHORTCUTS = {
        'title': "Горячие клавиши",
        'save': "Сохранить",
        'open': "Открыть",
        'new': "Новый файл",
        'quick_open': "Быстрое открытие", 
        'fullscreen': "Полный экран",
        'help': "Справка",
        'search': "Поиск",
        'replace': "Замена",
        'bold': "Жирный", 
        'italic': "Курсив",
        'undo': "Отменить",
        'redo': "Повторить"
    }
    
    # ========== ПОМОЩЬ И СПРАВКА ==========
    HELP = {
        'title': "Справка по редактору",
        'markdown_syntax': "Синтаксис Markdown",
        'keyboard_shortcuts': "Горячие клавиши",
        'features': "Возможности редактора",
        'about': "О программе",
        
        # Описания возможностей
        'live_preview': "Живой предварительный просмотр",
        'live_preview_desc': "Видите результат в реальном времени при печати",
        'syntax_highlighting': "Подсветка синтаксиса", 
        'syntax_highlighting_desc': "Цветное выделение элементов Markdown",
        'auto_toc': "Автоматическое оглавление",
        'auto_toc_desc': "Навигация по заголовкам документа",
        'file_management': "Управление файлами",
        'file_management_desc': "Создание, открытие, сохранение файлов",
        'auto_save': "Автосохранение",
        'auto_save_desc': "Автоматическое сохранение каждые 30 секунд"
    }
    
    # ========== MARKDOWN СИНТАКСИС ==========
    MARKDOWN_SYNTAX = {
        'heading': "# Заголовок",
        'heading_desc': "Создаёт заголовок (# - H1, ## - H2, и т.д.)",
        'bold': "**жирный текст**",
        'bold_desc': "Выделяет текст жирным шрифтом",
        'italic': "*курсив*",
        'italic_desc': "Выделяет текст курсивом", 
        'strikethrough': "~~зачёркнутый~~",
        'strikethrough_desc': "Зачёркивает текст",
        'link': "[текст](URL)",
        'link_desc': "Создаёт ссылку",
        'image': "![описание](URL)",
        'image_desc': "Вставляет изображение",
        'code': "`код`",
        'code_desc': "Выделяет код в строке",
        'code_block': "```\nблок кода\n```",
        'code_block_desc': "Создаёт блок кода",
        'quote': "> цитата",
        'quote_desc': "Создаёт цитату",
        'list': "- элемент списка",
        'list_desc': "Создаёт маркированный список",
        'numbered_list': "1. элемент списка", 
        'numbered_list_desc': "Создаёт нумерованный список",
        'table': "| Колонка 1 | Колонка 2 |",
        'table_desc': "Создаёт таблицу",
        'hr': "---",
        'hr_desc': "Создаёт горизонтальную линию"
    }
    
    # ========== ПЛЕЙСХОЛДЕРЫ ==========
    PLACEHOLDERS = {
        'editor': "Начните печатать ваш Markdown здесь...",
        'search': "Поиск в документе...",
        'replace': "Заменить на...",
        'filename': "название_файла.md",
        'quick_open': "Начните печатать название файла...",
        'no_files': "Файлы не найдены",
        'empty_document': "Документ пуст"
    }
    
    # ========== КОНТЕКСТНОЕ МЕНЮ ==========
    CONTEXT_MENU = {
        'cut': "Вырезать",
        'copy': "Копировать", 
        'paste': "Вставить",
        'select_all': "Выделить всё",
        'select_line': "Выделить строку",
        'select_word': "Выделить слово",
        'format_document': "Форматировать документ",
        'show_statistics': "Показать статистику",
        'insert_date': "Вставить дату",
        'insert_time': "Вставить время"
    }
    
    # ========== НАВИГАЦИЯ ==========
    NAVIGATION = {
        'previous': "Предыдущий",
        'next': "Следующий",
        'first': "Первый", 
        'last': "Последний",
        'go_to_line': "Перейти к строке",
        'go_to_heading': "Перейти к заголовку",
        'scroll_to_top': "К началу",
        'scroll_to_bottom': "К концу"
    }

# Дополнительные утилиты для локализации
class LocalizationUtils:
    """Утилиты для работы с локализацией"""
    
    @staticmethod
    def format_file_size(bytes_count):
        """Форматирует размер файла на русском языке"""
        if bytes_count == 0:
            return "0 байт"
        
        units = ["байт", "КБ", "МБ", "ГБ", "ТБ"]
        k = 1024
        i = 0
        
        while bytes_count >= k and i < len(units) - 1:
            bytes_count /= k
            i += 1
        
        if i == 0:
            return f"{int(bytes_count)} {units[i]}"
        else:
            return f"{bytes_count:.1f} {units[i]}"
    
    @staticmethod
    def format_time_ago(timestamp):
        """Форматирует время на русском языке"""
        import datetime
        
        now = datetime.datetime.now()
        diff = now - datetime.datetime.fromtimestamp(timestamp)
        
        if diff.days > 0:
            if diff.days == 1:
                return "вчера"
            elif diff.days < 7:
                return f"{diff.days} дня назад" if diff.days < 5 else f"{diff.days} дней назад"
            else:
                return datetime.datetime.fromtimestamp(timestamp).strftime("%d.%m.%Y")
        
        hours = diff.seconds // 3600
        if hours > 0:
            if hours == 1:
                return "час назад"
            elif hours < 5:
                return f"{hours} часа назад"
            else:
                return f"{hours} часов назад"
        
        minutes = diff.seconds // 60
        if minutes > 0:
            if minutes == 1:
                return "минуту назад"
            elif minutes < 5:
                return f"{minutes} минуты назад"
            else:
                return f"{minutes} минут назад"
        
        return "только что"
    
    @staticmethod
    def pluralize(count, forms):
        """Возвращает правильную форму слова в зависимости от числа"""
        if count % 10 == 1 and count % 100 != 11:
            return forms[0]  # 1, 21, 31, ...
        elif 2 <= count % 10 <= 4 and (count % 100 < 10 or count % 100 >= 20):
            return forms[1]  # 2-4, 22-24, ...
        else:
            return forms[2]  # 0, 5-20, 25-30, ...
    
    @staticmethod
    def format_reading_time(word_count):
        """Рассчитывает время чтения на русском языке"""
        # Средняя скорость чтения русского текста - 200 слов в минуту
        minutes = max(1, round(word_count / 200))
        
        minute_forms = ["минута", "минуты", "минут"]
        return f"{minutes} {LocalizationUtils.pluralize(minutes, minute_forms)}"

# Экспорт сообщений
messages = RussianMessages()
utils = LocalizationUtils()

# Для использования в шаблонах Flask
def get_messages():
    return messages

def get_utils():
    return utils
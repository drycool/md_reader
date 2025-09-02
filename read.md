# **📚 Документация по логированию**

## **📝 Введение**

Этот документ описывает стандартизированную систему логирования для проекта. Мы используем единый модуль конфигурации, именованные логгеры для компонентов (worker, publication, synchronizer), ротацию файлов, консольный вывод и безопасное подключение без конфликтов.

### **Цели**

* Единая точка настройки логирования для всего приложения.  
* Разделение логов по компонентам.  
* Ротация логов, единый формат и временные метки.  
* Исключение дублирования обработчиков и конфликтов basicConfig.  
* Простое подключение в любом модуле без повторной инициализации.

## **⚙️ Структура и соглашения**

* **Путь к логам**: по умолчанию каталог logs (изменяется через переменную окружения LOG\_DIR).  
* **Уровень логирования**: по умолчанию INFO (изменяется через LOG\_LEVEL).  
* **Формат записи**: %(asctime)s | %(levelname)8s | %(name)s | %(message)s.  
* **Именованные логгеры**:  
  * app.worker — для фоновых задач.  
  * app.publication — для публикаций.  
  * app.synchronizer — для синхронизатора.

## **💻 Реализация модуля logger.py**

Вставьте следующий код в ваш файл logger.py:
```python
import logging  
import os  
from logging.handlers import RotatingFileHandler  
from typing import Optional

\_LOGGING\_CONFIGURED \= False  
LOG\_DIR \= os.getenv("LOG\_DIR", "logs")  
LOG\_LEVEL \= os.getenv("LOG\_LEVEL", "INFO").upper()  
LOG\_FORMAT \= "%(asctime)s | %(levelname)8s | %(name)s | %(message)s"  
DATE\_FORMAT \= "%Y-%m-%d %H:%M:%S"

WORKER\_LOGGER\_NAME \= "app.worker"  
PUBLICATION\_LOGGER\_NAME \= "app.publication"  
SYNCHRONIZER\_LOGGER\_NAME \= "app.synchronizer"

def \_make\_rotating\_file\_handler(file\_path: str) \-\> RotatingFileHandler:  
    handler \= RotatingFileHandler(  
        file\_path,  
        maxBytes=5 \* 1024 \* 1024,  \# 5 MB  
        backupCount=5,  
        encoding="utf-8"  
    )  
    handler.setFormatter(logging.Formatter(LOG\_FORMAT, DATE\_FORMAT))  
    return handler

def \_make\_console\_handler() \-\> logging.Handler:  
    handler \= logging.StreamHandler()  
    handler.setFormatter(logging.Formatter(LOG\_FORMAT, DATE\_FORMAT))  
    return handler

def setup\_logging(force: bool \= False) \-\> None:  
     
    Централизованная настройка логирования.  
    Вызывать один раз при старте приложения (например, в main.py).  
    Если force=True — перенастроит root и дочерние логгеры.  
    
    global \_LOGGING\_CONFIGURED  
    if \_LOGGING\_CONFIGURED and not force:  
        return

    os.makedirs(LOG\_DIR, exist\_ok=True)  
    root \= logging.getLogger()  
    if force:  
        for h in list(root.handlers):  
            root.removeHandler(h)  
      
    root.setLevel(getattr(logging, LOG\_LEVEL, logging.INFO))  
    root.addHandler(\_make\_console\_handler())

    components \= {  
        WORKER\_LOGGER\_NAME: os.path.join(LOG\_DIR, "worker.log"),  
        PUBLICATION\_LOGGER\_NAME: os.path.join(LOG\_DIR, "publication.log"),  
        SYNCHRONIZER\_LOGGER\_NAME: os.path.join(LOG\_DIR, "synchronizer.log"),  
    }  
      
    for logger\_name, file\_path in components.items():  
        logger \= logging.getLogger(logger\_name)  
        logger.setLevel(getattr(logging, LOG\_LEVEL, logging.INFO))  
        has\_file\_handler \= any(isinstance(h, RotatingFileHandler) for h in logger.handlers)  
        if not has\_file\_handler:  
            logger.addHandler(\_make\_rotating\_file\_handler(file\_path))  
        \# Оставляем propagate=True, чтобы записи были видны в консоли через root.  
        logger.propagate \= True  
      
    \_LOGGING\_CONFIGURED \= True

def get\_logger(name: Optional\[str\] \= None) \-\> logging.Logger:  
    """Хелпер для получения логгера по имени (или root, если имя не задано)."""  
    return logging.getLogger(name) if name else logging.getLogger()
```
## **🔌 Подключение в приложении**

### **Инициализация один раз**

Создайте или используйте точку входа (например, main_fixed.py) и вызовите настройку логирования ровно один раз:
```python
\# main.py  
from logger import setup\_logging

def main():  
    setup\_logging()  \# Инициализация логирования  
    \# ... запуск приложения ...

if \_\_name\_\_ \== "\_\_main\_\_":  
    main()
```
**Важно**:

* Не вызывайте ```logging.basicConfig() ``` в других местах.  
* Не инициализируйте обработчики в каждом модуле — это делает logger.setup\_logging().

### **Использование в модулях**

Используйте именованные логгеры и общий формат.

#### **worker.py**
```python
import logging  
from logger import WORKER\_LOGGER\_NAME

logger \= logging.getLogger(WORKER\_LOGGER\_NAME)

def run\_worker():  
    logger.info("Worker started")  
    logger.debug("Worker debug details")

#### **publication.py**

import logging  
from logger import PUBLICATION\_LOGGER\_NAME

logger \= logging.getLogger(PUBLICATION\_LOGGER\_NAME)

def publish():  
    logger.info("Publication task queued")  
    logger.warning("Publication rate limit approaching")

#### **telegram\_synchronizer.py**

import logging  
from logger import SYNCHRONIZER\_LOGGER\_NAME

logger \= logging.getLogger(SYNCHRONIZER\_LOGGER\_NAME)

def sync():  
    logger.info("Synchronizer tick")  
    try:  
        \# ... логика синхронизации ...  
        pass  
    except Exception as e:  
        logger.exception("Sync failed: %s", e)
```
## **💡 Рекомендации и настройка**

* Ротация и хранение логов:  
  Используется RotatingFileHandler:  
  * **Размер файла**: до 5 MB.  
  * **Резервных копий**: до 5\.  
  * **Имена файлов**: logs/worker.log, logs/publication.log, logs/synchronizer.log.  
* Настройка поведения вывода:  
  По умолчанию propagate=True: записи из компонентных логгеров идут в консоль через root и в файл своего компонента. Чтобы отключить вывод конкретного логгера в консоль, установите propagate=False:  
  ```
  import logging  
  from logger import SYNCHRONIZER\_LOGGER\_NAME

  logging.getLogger(SYNCHRONIZER\_LOGGER\_NAME).propagate \= False

*  *Настройка через переменные окружения**:  
  * LOG\_DIR — каталог для логов (по умолчанию logs).  
  * LOG\_LEVEL — уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL).

**Примеры**:\# Linux/macOS 
```
export LOG\_LEVEL=DEBUG  
export LOG\_DIR=/var/log/myapp
```
\# Windows (PowerShell) 
```
$env:LOG\_LEVEL="DEBUG"  
$env:LOG\_DIR="C:\\logs\\myapp"
```
## **🔄 Миграция со старой схемы**

1. Замените содержимое вашего текущего logger.py на модуль из раздела "Реализация".  
2. Удалите/закомментируйте все места, где создавались FileHandler/StreamHandler вручную.  
3. Во всех модулях замените прямые объекты логгеров на ``` logging.getLogger(\<имя\>)```.  
4. Убедитесь, что ``` setup\_logging()```  вызывается ровно один раз при старте.

## **📂 Пример структуры проекта**
```
project/  
  logger.py  
  main.py  
  worker.py  
  publication.py  
  telegram\_synchronizer.py  
  logs/  
    worker.log  
    publication.log  
    synchronizer.log  
```
### 🔄 Ротация логов
Ротация — это автоматическое архивирование и ограничение размера лог-файлов, чтобы они:

❌ Не занимали всё место на диске
❌ Не разрастались до гигантских размеров
✅ Сохраняли только актуальную информацию
⚙️ Настройка ротации
### У тебя настроено:



```python
handler = RotatingFileHandler(
    file_path,
    maxBytes=5 * 1024 * 1024,  # 5 MB
    backupCount=5,
    encoding="utf-8"
)
```

### Параметры:

|maxBytes    | 5 мегабайт                   |
|------------|------------------------------|
|backupCount | максимум 5 архивных копий    |


### 📁 Как работает на практике
Когда текущий worker.log достигает 5 МБ, происходит следующее:

1. worker.log переименовывается в worker.log.1
2. Создаётся новый пустой worker.log
3. Если worker.log.5 уже существует — он удаляется
4. Все остальные .log.N сдвигаются на 1 (.log.4 → .log.5, и т.д.)

### 🧾 Пример последовательности

Допустим, воркер работает долго и пишет много логов:

| Начало работы  |   worker.log                               |
|----------------|----------------------------------|
| Достиг 5 МБ    | worker.log, worker.log.1         |
| Достиг 10 МБ   | worker.log, worker.log.1,worker.log.2|
| ...            |...|
| Достиг 30 МБ   |worker.log,worker.log.1, ...,worker.log.5|
| Превысил 30 МБ |worker.log,worker.log.1, ...,worker.log.5 (старый worker.log.5 удаляется)|

### 🧼 Когда и зачем очищать вручную?
Ты можешь очищать лог вручную только в целях отладки, например:

```python
log_file = os.path.join("logs", "worker.log")
if os.path.exists(log_file):
    open(log_file, 'w').close()  # очистить содержимое
```

### ✅ Когда это полезно:

* При запуске тестов
* При отладке нового функционала
* Чтобы не искать новые записи среди старых

 ### ❌ Когда не нужно:

* В production — ротация сама всё управляет
* При обычной работе — логи сами "крутятся"

### ✅ Вывод
| Условие       | Что происходит |
|---------------|----------|
| Лог < 5 МБ    | Пишется в worker.log|
|Лог = 5 МБ|Создаётся worker.log.1 , начинается новый worker.log|
|Есть 5 архивов |При следующей ротации самый старый (worker.log.5) удаляется|

## Цель:
использовать твой общий logger.py, чтобы логи от разных частей приложения (включая потенциальный воркер, запущенный через API) шли в правильные файлы и консоль.

### ✅ Шаг 1: Импортируй ```setup_logging``` в main_fixed.py
Добавь импорт в самом начале файла main_fixed.py, до создания app = FastAPI() и любых других импортов твоих модулей:

```python
# main_fixed.py
# --- Импорт и настройка логирования ---
from logger import setup_logging

# Вызываем настройку логирования один раз при старте приложения
setup_logging()

# --- Остальные импорты ---
from fastapi import FastAPI, Request, Form, File, UploadFile, Depends, HTTPException, status
# ... (все остальные импорты)
```
⚠️ Важно: ```setup_logging()``` должен быть вызван до любого использования ```get_logger()``` в других модулях. 

### ✅ Шаг 2: В каждом модуле, где нужны логи, используй get_logger
Например, если ты хочешь логировать действия в telegram_service.py, сделай так:

Было (пример):
```python
# telegram_service.py
import logging

logger = logging.getLogger(__name__)
```
Стало:
```python
# telegram_service.py
from logger import get_logger

# Используем конкретное имя, например, для публикаций
logger = get_logger("app.publication")
# или просто по имени модуля:
# logger = get_logger(__name__)
```
То же самое — для любого другого модуля, где ты хочешь писать логи:

Для воркера — ```get_logger("app.worker")```
Для синхронизатора — ```get_logger("app.synchronizer")```
Для основного сервера — можно использовать ```get_logger("app.server")``` или оставить корневой.

### ✅ Шаг 3: Убедись, что logger.py находится в доступном месте
Убедись, что logger.py находится рядом с main_fixed.py или в пакете, который доступен из PYTHONPATH.

### ✅ Шаг 4: Проверь, что логи пишутся
После запуска приложения:

Проверь, что в папке logs/ появились файлы:

* worker.log
* publication.log
* synchronizer.log

Проверь, что в консоли выводятся сообщения с правильным форматом.

✅ Пример использования в main_fixed.py (если нужно)
Если ты хочешь добавить логирование прямо в main_fixed.py:

```python
# main_fixed.py
from logger import setup_logging, get_logger
setup_logging()

# Получаем логгер для сервера
server_logger = get_logger("app.server")

# ... (создание app, маршруты и т.д.)

@app.on_event("startup")
def on_startup():
    server_logger.info("--- Событие 'startup': Создание таблиц ---")
    create_db_and_tables()

 ... остальной код ```
```
✅ Если ты запускаешь воркер через subprocess...
В main_fixed.py у тебя есть:

```python

@app.post("/admin/telegram-publisher/publish")
async def publish_to_telegram(...):
    ...
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
```
Если cmd запускает worker_publish.py, то в этом скрипте тоже нужно вызвать setup_logging():

```python
# worker_publish.py
from logger import setup_logging, get_logger
setup_logging()  # <-- обязательно
worker_logger = get_logger("app.worker")
# ... остальной код
```
### ✅ Резюме: Что изменилось
1. Добавить ```setup_logging()```в main_fixed.py до всех импортов
2. В каждом модуле заменить ```logging.getLogger(...)``` на ```get_logger(...)```
3. Убедиться, что logger.py доступен 
4. В worker_publish.py (если запускается отдельно) тоже вызвать ```
setup_logging()```






@echo off
chcp 65001 >nul
echo ========================================
echo       Сборка MarkdownEditor.exe
echo ========================================
echo.

:: Проверка виртуального окружения
if not exist "venv\Scripts\python.exe" (
    echo Создание виртуального окружения...
    py -3 -m venv venv
    if errorlevel 1 (
        echo ОШИБКА: Не удалось создать виртуальное окружение.
        pause
        exit /b 1
    )
)

:: Активация виртуального окружения
echo Активация виртуального окружения...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ОШИБКА: Не удалось активировать виртуальное окружение.
    pause
    exit /b 1
)

:: Проверка установки Python в виртуальном окружении
python --version >nul 2>&1
if errorlevel 1 (
    echo ОШИБКА: Python в виртуальном окружении не найден.
    pause
    exit /b 1
)

:: Обновление pip
echo Обновление pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo ПРЕДУПРЕЖДЕНИЕ: Не удалось обновить pip, продолжаем...
)

:: Установка зависимостей
echo Установка зависимостей...
pip install -r requirements.txt
if errorlevel 1 (
    echo ОШИБКА: Не удалось установить зависимости.
    pause
    exit /b 1
)

echo.
echo Создание исполняемого файла...
echo Это может занять несколько минут...

:: Создание exe с помощью PyInstaller
pyinstaller --onefile ^
    --windowed ^
    --name=MarkdownEditor ^
    --add-data="templates;templates" ^
    --add-data="static;static" ^
    --hidden-import=flask ^
    --hidden-import=werkzeug ^
    --hidden-import=jinja2 ^
    --hidden-import=markupsafe ^
    --hidden-import=itsdangerous ^
    --hidden-import=click ^
    --hidden-import=blinker ^
    --collect-submodules=flask ^
    --collect-submodules=werkzeug ^
    app.py

if errorlevel 1 (
    echo.
    echo ОШИБКА: Сборка не удалась.
    echo Попробуйте запустить:
    echo pip install --upgrade pyinstaller
    echo.
    pause
    exit /b 1
)

:: Проверка создания файла
if exist "dist\MarkdownEditor.exe" (
    echo.
    echo ========================================
    echo   УСПЕШНО! MarkdownEditor.exe создан
    echo ========================================
    echo.
    echo Файл находится в папке: dist\MarkdownEditor.exe
    echo.
    echo Вы можете скопировать его в любое место
    echo и запускать без установки Python.
    echo.
) else (
    echo.
    echo ОШИБКА: Файл MarkdownEditor.exe не был создан.
    echo.
)

echo Очистка временных файлов...
if exist "build" rmdir /s /q "build"
if exist "MarkdownEditor.spec" del "MarkdownEditor.spec"

echo.
echo Готово!
pause

@echo off
chcp 65001 >nul
echo ========================================
echo  Расширенная сборка MarkdownEditor.exe
echo ========================================
echo.

:: Проверка окружения
python --version >nul 2>&1
if errorlevel 1 (
    echo ОШИБКА: Python не найден.
    pause
    exit /b 1
)

echo Обновление pip и setuptools...
python -m pip install --upgrade pip setuptools wheel

echo Установка зависимостей...
pip install -r requirements.txt

echo.
echo Сборка с расширенными параметрами...

:: Расширенная сборка с максимальными настройками
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
    --hidden-import=threading ^
    --hidden-import=socket ^
    --hidden-import=webbrowser ^
    --hidden-import=pathlib ^
    --hidden-import=multiprocessing ^
    --collect-submodules=flask ^
    --collect-submodules=werkzeug ^
    --collect-all=flask ^
    --copy-metadata=flask ^
    --copy-metadata=werkzeug ^
    --copy-metadata=jinja2 ^
    --exclude-module=tkinter ^
    --exclude-module=matplotlib ^
    --exclude-module=numpy ^
    --exclude-module=pandas ^
    --upx-dir=. ^
    --clean ^
    app.py

if errorlevel 1 (
    echo.
    echo Расширенная сборка не удалась. Пробуем базовую...
    
    :: Fallback к простой сборке
    pyinstaller --onefile ^
        --name=MarkdownEditor ^
        --add-data="templates;templates" ^
        --add-data="static;static" ^
        app.py
        
    if errorlevel 1 (
        echo ОШИБКА: Все попытки сборки не удались.
        pause
        exit /b 1
    )
)

if exist "dist\MarkdownEditor.exe" (
    echo.
    echo ========================================
    echo        СБОРКА ЗАВЕРШЕНА УСПЕШНО!
    echo ========================================
    echo.
    echo Размер файла:
    for %%F in ("dist\MarkdownEditor.exe") do echo %%~zF байт
    echo.
    echo Файл: dist\MarkdownEditor.exe
    echo.
) else (
    echo ОШИБКА: EXE файл не создан.
)

echo Очистка...
if exist "build" rmdir /s /q "build"
if exist "MarkdownEditor.spec" del "MarkdownEditor.spec"

pause
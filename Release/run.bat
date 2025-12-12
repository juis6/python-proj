@echo off
chcp 65001 >nul
echo ========================================
echo    GreenLeaf Guide - Запуск програми
echo ========================================
echo.

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ПОМИЛКА] Python не встановлено!
    echo Завантажте з: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Перевірка залежностей...
pip install requests --quiet 2>nul

echo Запуск програми...
python main_launcher.py
pause

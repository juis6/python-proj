#!/bin/bash
echo "========================================"
echo "   GreenLeaf Guide - Запуск програми"
echo "========================================"
echo

if ! command -v python3 &> /dev/null; then
    echo "[ПОМИЛКА] Python3 не встановлено!"
    exit 1
fi

echo "Перевірка залежностей..."
pip3 install requests --quiet 2>/dev/null

echo "Запуск програми..."
python3 main_launcher.py

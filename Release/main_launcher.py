import os
import sys
import json
import requests
import subprocess
from datetime import datetime
from pathlib import Path

from log import log, log_error


def setup_project_structure():  # Створює необхідну структуру папок
    folders = ["tasks"]
    for folder in folders:
        Path(folder).mkdir(exist_ok=True)


def download_plants_data():  # Завантажує дані з API або створює тестові дані
    API_URL = "https://plantsm.art/api/plants.json"
    DATA_FILE = "plants.json"

    if os.path.exists(DATA_FILE):
        log(f"Файл {DATA_FILE} вже існує")
        file_date = datetime.fromtimestamp(os.path.getmtime(DATA_FILE)).date()
        today = datetime.now().date()

        if file_date == today:
            log("Дані за сьогодні вже завантажені")
            return True
        else:
            log_error(f"Дані застарілі (останнє оновлення: {file_date})")

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
        }

        response = requests.get(API_URL, headers=headers, timeout=30)  #  Запит до API
        response.raise_for_status()  # Перевірка на помилки HTTP

        data = response.json()  # Парсинг JSON відповіді
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)  # Збереження у файл

        log(f"Дані успішно завантажено! Збережено в {DATA_FILE}")

        with open("protocol.txt", "a", encoding="utf-8") as f:
            f.write(
                f"[{datetime.now()}] Завантажено {len(data.get('data', []))} рослин з API\n"
            )

        return True

    except requests.exceptions.RequestException as e:
        log_error(f"Помилка завантаження: {e}")
        log_error("Використовуються тестові дані...")
        return create_sample_data()


def create_sample_data():  # Створює тестові дані, якщо завантаження не вдалося
    sample_data = {
        "data": [
            {
                "name": "Ricinus communis",
                "common_name": "Castor Bean",
                "family": "Euphorbiaceae",
                "severity": {"label": "Severe", "level": 4},
                "animals": ["dogs", "cats", "horses"],
                "symptoms": [{"name": "Vomiting"}, {"name": "Diarrhea"}],
            },
            {
                "name": "Nerium oleander",
                "common_name": "Oleander",
                "family": "Apocynaceae",
                "severity": {"label": "High", "level": 3},
                "animals": ["dogs", "cats", "horses"],
                "symptoms": [{"name": "Heart arrhythmia"}],
            },
        ]
    }

    with open("plants.json", "w", encoding="utf-8") as f:
        json.dump(sample_data, f, ensure_ascii=False, indent=2)

    log("Створено тестові дані (2 рослини)")
    return True


def compile_java_project():  # Компілює Java проект
    JAVA_SOURCE = "PlantGuide.java"  # Ім'я Java файлу

    if not os.path.exists(JAVA_SOURCE):  # Перевірка наявності файлу
        log_error(f"Файл {JAVA_SOURCE} не знайдено!")
        return False

    log("Компіляція Java коду...")  # Компіляція Java коду
    try:
        result = subprocess.run(
            ["javac", "-encoding", "UTF-8", JAVA_SOURCE],
            capture_output=True,
            text=True,
            timeout=60,
        )  # Запуск процесу компіляції

        if result.returncode == 0:
            log("Java код успішно скомпільовано")
            return True
        else:
            log_error(f"Помилка компіляції Java:\n{result.stderr}")
            return False

    except FileNotFoundError:
        log_error("Java Development Kit (JDK) не встановлено або javac не знайдено")
        return False
    except Exception as e:
        log_error(f"{e}")
        return False


def create_release_folder():
    """Створює повноцінну папку Release з усіма необхідними файлами для розповсюдження."""
    import shutil
    from datetime import datetime

    release_dir = Path("Release")

    # Очистити попередню версію Release
    if release_dir.exists():
        shutil.rmtree(release_dir)
    release_dir.mkdir()

    log("Створення папки Release...")

    # Список файлів для копіювання
    files_to_copy = [
        "main_launcher.py",
        "log.py",
        "plants.json",
        "PlantGuide.java",
        "instructions.md",
        "Архітектура проєкту.md",
    ]

    for file_path in files_to_copy:
        src = Path(file_path)
        if src.exists():
            shutil.copy2(src, release_dir / src.name)
            log(f"  Скопійовано: {src.name}")

    # Копіювання папки tasks
    tasks_src = Path("tasks")
    if tasks_src.exists():
        shutil.copytree(tasks_src, release_dir / "tasks", dirs_exist_ok=True)
        log("  Скопійовано: tasks/")

    # Створення JAR файлу
    if Path("PlantGuide.class").exists():
        shutil.copy2("PlantGuide.class", release_dir / "PlantGuide.class")

        manifest_content = "Manifest-Version: 1.0\nMain-Class: PlantGuide\n\n"
        (release_dir / "MANIFEST.MF").write_text(manifest_content)

        try:
            result = subprocess.run(
                ["jar", "cfm", "GreenLeaf.jar", "MANIFEST.MF", "PlantGuide.class"],
                cwd=release_dir,
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                log("  Створено: GreenLeaf.jar")
            else:
                log_error(f"Помилка створення JAR: {result.stderr}")
        except FileNotFoundError:
            log_error("Команда 'jar' не знайдена. JAR файл не створено.")

    # Створення скрипта запуску для Windows
    run_bat = """@echo off
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
"""
    (release_dir / "run.bat").write_text(run_bat, encoding="utf-8")
    log("  Створено: run.bat")

    # Створення скрипта запуску для Linux/macOS
    run_sh = """#!/bin/bash
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
"""
    (release_dir / "run.sh").write_text(run_sh, encoding="utf-8")
    log("  Створено: run.sh")

    # Створення README файлу
    readme_content = f"""GreenLeaf Guide - Release Package
==================================

Дата збірки: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Вміст папки:
------------
- run.bat           - запуск для Windows
- run.sh            - запуск для Linux/macOS
- main_launcher.py  - головний сценарій Python
- PlantGuide.java   - вихідний код Java GUI
- PlantGuide.class  - скомпільований Java клас
- GreenLeaf.jar     - виконуваний JAR файл
- plants.json       - база даних рослин
- tasks/            - аналітичні скрипти Python
- instructions.md   - інструкція користувача

Системні вимоги:
----------------
- Python 3.9+
- Java 8+ (JRE для запуску, JDK для компіляції)
- Бібліотека requests (встановлюється автоматично)

Швидкий старт:
--------------
Windows:
    Двічі клікніть на run.bat

Linux/macOS:
    chmod +x run.sh
    ./run.sh

Запуск Java GUI окремо:
-----------------------
    java -jar GreenLeaf.jar
    або
    java PlantGuide plants.json
"""
    (release_dir / "README.txt").write_text(readme_content, encoding="utf-8")
    log("  Створено: README.txt")

    # Копіювання протоколу
    if Path("protocol.txt").exists():
        shutil.copy2("protocol.txt", release_dir / "protocol.txt")

    log(f" Папка Release створена: {release_dir.absolute()}")

    # Статистика збірки
    total_size = sum(f.stat().st_size for f in release_dir.rglob("*") if f.is_file())
    file_count = sum(1 for _ in release_dir.rglob("*") if _.is_file())
    log(f"Загалом файлів: {file_count}, розмір: {total_size / 1024:.1f} KB")


def main():
    """Головна функція для запуску процесів."""
    setup_project_structure()

    if not download_plants_data():
        log_error("Не вдалося отримати дані")
        return 1

    if not compile_java_project():
        log("Продовжую без Java GUI...")

    print("   1. Аналіз топ родин (tasks/top_families.py)")
    print("   2. Пошук небезпечних рослин для тварин (tasks/search_animals.py)")
    print("   3. Статистика рівнів небезпеки (tasks/severity_stats.py)")
    print("   4. Пошук рослин за симптомом (tasks/search_symptoms.py)")
    print("   5. Перша допомога при отруєнні (tasks/first_aid.py)")
    print("   6. Пошук безпечних альтернатив (tasks/safe_alternatives.py)")
    print("   7. Запуск Java GUI (PlantGuide)")
    print("   8. Створити папку Release")

    choice = input("\nОберіть дію (1-6) або Enter для завершення: ")

    if choice == "1":
        subprocess.run(
            [sys.executable, "tasks/top_families.py"]
        )  # Запуск скрипту топ родин
    elif choice == "2":
        animal = input("Введіть назву тварини: ")
        subprocess.run(
            [sys.executable, "tasks/search_animals.py", animal]
        )  # Запуск скрипту пошуку рослин для тварин
    elif choice == "3":
        subprocess.run(
            [sys.executable, "tasks/severity_stats.py"]
        )  # Запуск скрипту статистики рівнів небезпеки
    elif choice == "4":
        subprocess.run(
            [sys.executable, "tasks/search_symptoms.py"]
        )  # Запуск скрипту пошуку за симптомом
    elif choice == "5":
        subprocess.run(
            [sys.executable, "tasks/first_aid.py"]
        )  # Запуск скрипту першої допомоги
    elif choice == "6":
        subprocess.run(
            [sys.executable, "tasks/safe_alternatives.py"]
        )  # Запуск скрипту пошуку безпечних альтернатив
    elif choice == "7":
        if Path("PlantGuide.class").exists():
            log("Запуск Java GUI...")
            subprocess.run(["java", "PlantGuide", "plants.json"])
        else:
            log_error("Java клас не скомпільовано")
    elif choice == "8":
        create_release_folder()
    return 0


if __name__ == "__main__":
    sys.exit(main())

import os
import sys
import json
import requests
import subprocess
from datetime import datetime
from pathlib import Path

from log import log, log_error

def setup_project_structure(): # Створює необхідну структуру папок
    folders = ['tasks']
    for folder in folders:
        Path(folder).mkdir(exist_ok=True)

def download_plants_data(): # Завантажує дані з API або створює тестові дані
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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        }
        
        response = requests.get(API_URL, headers=headers, timeout=30) #  Запит до API
        response.raise_for_status() # Перевірка на помилки HTTP

        data = response.json() # Парсинг JSON відповіді
        with open(DATA_FILE, 'w', encoding='utf-8') as f: 
            json.dump(data, f, ensure_ascii=False, indent=2) # Збереження у файл
        
        log(f"Дані успішно завантажено! Збережено в {DATA_FILE}")

        with open('protocol.txt', 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now()}] Завантажено {len(data.get('data', []))} рослин з API\n")
        
        return True
        
    except requests.exceptions.RequestException as e:
        log_error(f"Помилка завантаження: {e}")
        log_error("Використовуються тестові дані...")
        return create_sample_data()

def create_sample_data(): # Створює тестові дані, якщо завантаження не вдалося
    sample_data = {
        "data": [
            {
                "name": "Ricinus communis",
                "common_name": "Castor Bean",
                "family": "Euphorbiaceae",
                "severity": {"label": "Severe", "level": 4},
                "animals": ["dogs", "cats", "horses"],
                "symptoms": [{"name": "Vomiting"}, {"name": "Diarrhea"}]
            },
            {
                "name": "Nerium oleander",
                "common_name": "Oleander",
                "family": "Apocynaceae",
                "severity": {"label": "High", "level": 3},
                "animals": ["dogs", "cats", "horses"],
                "symptoms": [{"name": "Heart arrhythmia"}]
            }
        ]
    }
    
    with open('plants.json', 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, ensure_ascii=False, indent=2)
    
    log("Створено тестові дані (2 рослини)")
    return True

def compile_java_project(): # Компілює Java проект
    JAVA_SOURCE = "PlantGuide.java" # Ім'я Java файлу
    
    if not os.path.exists(JAVA_SOURCE): # Перевірка наявності файлу
        log_error(f"Файл {JAVA_SOURCE} не знайдено!")
        return False
    
    log("Компіляція Java коду...") # Компіляція Java коду
    try:
        result = subprocess.run(
            ["javac", "-encoding", "UTF-8", JAVA_SOURCE],
            capture_output=True,
            text=True,
            timeout=60
        ) # Запуск процесу компіляції
        
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

def create_release_folder(): # Створює папку Release з необхідними файлами
    release_dir = Path("Release")
    release_dir.mkdir(exist_ok=True)

    files_to_copy = [
        "main_launcher.py",
        "tasks/",
        "plants.json",
        "protocol.txt"
    ]
    
    for file_path in files_to_copy:
        src = Path(file_path)
        if src.exists():
            if src.is_dir():
                import shutil
                shutil.copytree(src, release_dir / src.name, dirs_exist_ok=True)
            else:
                import shutil
                shutil.copy2(src, release_dir / src.name)

    if Path("PlantGuide.class").exists():
        try:
            manifest_content = "Main-Class: PlantGuide\n"
            (release_dir / "MANIFEST.MF").write_text(manifest_content)

            subprocess.run([
                "jar", "cfm", "GreenLeaf.jar", "MANIFEST.MF", 
                "PlantGuide.class"
            ], cwd=release_dir, capture_output=True)
            
            log(f"Створено JAR файл: {release_dir}/GreenLeaf.jar")
        except:
            log_error("Не вдалося створити JAR файл")
    
    log(f" Папка Release створена: {release_dir.absolute()}")

def main():    # Головна функція для запуску процесів
    setup_project_structure()

    if not download_plants_data():
        log_error("Не вдалося отримати дані")
        return 1
    
    if not compile_java_project():
        log("Продовжую без Java GUI...")
    
    print("   1. Аналіз топ родин (tasks/top_families.py)")
    print("   2. Пошук небезпечних рослин для тварин (tasks/search_animals.py)")
    print("   3. Статистика рівнів небезпеки (tasks/severity_stats.py)")
    print("   4. Запуск Java GUI (PlantGuide)")
    print("   5. Створити папку Release")
    
    choice = input("\nОберіть дію (1-5) або Enter для завершення: ")
    
    if choice == "1":
        subprocess.run([sys.executable, "tasks/top_families.py"]) # Запуск скрипту топ родин
    elif choice == "2":
        animal = input("Введіть назву тварини: ")
        subprocess.run([sys.executable, "tasks/search_animals.py", animal]) # Запуск скрипту пошуку рослин для тварин
    elif choice == "3":
        subprocess.run([sys.executable, "tasks/severity_stats.py"]) # Запуск скрипту статистики рівнів небезпеки
    elif choice == "4":
        if Path("PlantGuide.class").exists():
            log("Запуск Java GUI...")
            subprocess.run(["java", "PlantGuide", "plants.json"])
        else:
            log_error("Java клас не скомпільовано")
    elif choice == "5":
        create_release_folder()
    return 0

if __name__ == "__main__":
    sys.exit(main())
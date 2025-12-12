GreenLeaf Guide - Release Package
==================================

Дата збірки: 2025-12-12 21:47:30

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

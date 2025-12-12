# tasks/safe_alternatives.py
"""
Задача 7: Пошук безпечних альтернатив.
Знаходить безпечні рослини тієї ж родини замість небезпечних.
"""
import sys
import os
from collections import defaultdict

try:
    from .utils import load_plants_data, save_results, log_protocol
except ImportError:
    from utils import load_plants_data, save_results, log_protocol

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from log import log, log_error


KNOWN_SAFE_PLANTS = [
    {
        "name": "Spider Plant",
        "family": "Asparagaceae",
        "note": "Безпечна для котів та собак",
    },
    {
        "name": "Boston Fern",
        "family": "Nephrolepidaceae",
        "note": "Безпечна, очищує повітря",
    },
    {
        "name": "African Violet",
        "family": "Gesneriaceae",
        "note": "Безпечна, красиво цвіте",
    },
    {
        "name": "Bamboo Palm",
        "family": "Arecaceae",
        "note": "Безпечна, тропічний вигляд",
    },
    {"name": "Peperomia", "family": "Piperaceae", "note": "Безпечна, багато сортів"},
    {
        "name": "Calathea",
        "family": "Marantaceae",
        "note": "Безпечна, декоративне листя",
    },
    {
        "name": "Polka Dot Plant",
        "family": "Acanthaceae",
        "note": "Безпечна, яскраве листя",
    },
    {
        "name": "Haworthia",
        "family": "Asphodelaceae",
        "note": "Безпечна альтернатива алое",
    },
    {
        "name": "Christmas Cactus",
        "family": "Cactaceae",
        "note": "Безпечна, цвіте взимку",
    },
    {"name": "Areca Palm", "family": "Arecaceae", "note": "Безпечна, очищує повітря"},
    {"name": "Parlor Palm", "family": "Arecaceae", "note": "Безпечна для всіх тварин"},
    {"name": "Swedish Ivy", "family": "Lamiaceae", "note": "Безпечна, легка у догляді"},
]


def find_safe_alternatives(dangerous_plant, user_animals, input_file="plants.json"):
    """Знаходить безпечні альтернативи для небезпечної рослини."""
    plants_db = load_plants_data(input_file)
    if not plants_db:
        return {"error": "Не вдалося завантажити базу даних"}

    plant_lower = dangerous_plant.lower().strip()
    found_plant = None

    for plant in plants_db:
        if plant_lower in plant.get("name", "").lower():
            found_plant = plant
            break
        for common in plant.get("common", []):
            common_name = (
                common.get("name", "") if isinstance(common, dict) else str(common)
            )
            if plant_lower in common_name.lower():
                found_plant = plant
                break
        if found_plant:
            break

    user_animals_lower = [a.lower().strip() for a in user_animals]

    mild_plants = []
    for plant in plants_db:
        severity = plant.get("severity", {})
        sev_label = (
            severity.get("label", "").lower()
            if isinstance(severity, dict)
            else str(severity).lower()
        )

        if sev_label != "mild":
            continue

        plant_animals = []
        for a in plant.get("animals", []):
            if isinstance(a, dict):
                plant_animals.append(str(list(a.values())[0]).lower())
            else:
                plant_animals.append(str(a).lower())

        is_safe_for_user = True
        for user_animal in user_animals_lower:
            for plant_animal in plant_animals:
                if user_animal in plant_animal or plant_animal in user_animal:
                    is_safe_for_user = False
                    break
            if not is_safe_for_user:
                break

        if is_safe_for_user:
            common_names = []
            for c in plant.get("common", []):
                if isinstance(c, dict):
                    common_names.append(c.get("name", ""))

            mild_plants.append(
                {
                    "scientific_name": plant.get("name", ""),
                    "common_name": common_names[0] if common_names else "",
                    "family": plant.get("family", ""),
                    "severity": "Mild",
                }
            )

    result = {
        "task": "safe_alternatives",
        "timestamp": __import__("datetime").datetime.now().isoformat(),
        "query_plant": dangerous_plant,
        "user_animals": user_animals,
        "dangerous_plant_info": None,
        "alternatives_from_db": mild_plants[:10],
        "known_safe_plants": KNOWN_SAFE_PLANTS,
    }

    if found_plant:
        severity = found_plant.get("severity", {})
        result["dangerous_plant_info"] = {
            "scientific_name": found_plant.get("name", ""),
            "family": found_plant.get("family", ""),
            "severity": (
                severity.get("label", "")
                if isinstance(severity, dict)
                else str(severity)
            ),
        }

    log_protocol(f"Пошук альтернатив для: {dangerous_plant}")
    return result


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Пошук безпечних альтернатив рослинам")
    parser.add_argument("--input", default="plants.json", help="JSON файл з даними")
    parser.add_argument(
        "--output", default="results_alternatives.json", help="Файл результатів"
    )

    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("   ПОШУК БЕЗПЕЧНИХ АЛЬТЕРНАТИВ РОСЛИНАМ")
    print("=" * 60)

    print("\nВведіть назву небезпечної рослини, яку хочете замінити:")
    print("Приклади: lily, oleander, aloe, azalea, philodendron")
    plant = input("\nРослина: ").strip()

    if not plant:
        log_error("Назва рослини не вказана")
        return 1

    print("\nЯкі тварини є у вас вдома?")
    print("Варіанти: dogs, cats, birds, reptiles, small mammals")
    animals_input = input("Тварини (через кому): ").strip()

    if not animals_input:
        animals_input = "dogs, cats"
        print(f"Використовую за замовчуванням: {animals_input}")

    user_animals = [a.strip() for a in animals_input.split(",")]

    results = find_safe_alternatives(plant, user_animals, args.input)

    if "error" in results:
        log_error(results["error"])
        return 1

    if save_results(results, args.output):
        log(f"Результати збережено у {args.output}")

    print("\n" + "=" * 60)
    print("              РЕЗУЛЬТАТИ ПОШУКУ")
    print("=" * 60)

    if results["dangerous_plant_info"]:
        info = results["dangerous_plant_info"]
        print(f"\nНебезпечна рослина: {info['scientific_name']}")
        print(f"Родина: {info['family']}")
        print(f"Рівень небезпеки: {info['severity']}")

    print("\n" + "-" * 60)
    print("РЕКОМЕНДОВАНІ БЕЗПЕЧНІ АЛЬТЕРНАТИВИ:")
    print("-" * 60)

    for i, plant in enumerate(results["known_safe_plants"][:8], 1):
        print(f"\n  {i}. {plant['name']}")
        print(f"     Родина: {plant['family']}")
        print(f"     {plant['note']}")

    if results["alternatives_from_db"]:
        print("\n" + "-" * 60)
        print("РОСЛИНИ З НИЗЬКИМ РІВНЕМ НЕБЕЗПЕКИ (Mild):")
        print("-" * 60)

        for plant in results["alternatives_from_db"][:5]:
            name = plant["common_name"] or plant["scientific_name"]
            print(f"  - {name} ({plant['family']})")

    print("\n" + "=" * 60)
    print("ПОРАДА: Завжди перевіряйте рослину перед покупкою!")
    print("Навіть 'безпечні' рослини можуть викликати легке")
    print("розладнання шлунку при надмірному споживанні.")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())

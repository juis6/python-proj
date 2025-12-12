# tasks/first_aid.py
"""
Задача 6: Інструкція першої допомоги при отруєнні.
Показує симптоми та рекомендації при контакті тварини з отруйною рослиною.
"""
import sys
import os

try:
    from .utils import load_plants_data, save_results, log_protocol
except ImportError:
    from utils import load_plants_data, save_results, log_protocol

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from log import log, log_error


FIRST_AID_TIPS = {
    "vomiting": "Не давайте їжу протягом 12-24 годин. Забезпечте доступ до води.",
    "diarrhea": "Запобігайте зневодненню. Давайте воду малими порціями.",
    "tremors": "Тримайте тварину в теплі та спокої. Терміново до ветеринара!",
    "seizures": "Не тримайте тварину. Приберіть небезпечні предмети навколо. ТЕРМІНОВО до ветеринара!",
    "cardiac": "Не навантажуйте тварину. Негайно викличте ветеринара!",
    "breathing": "Забезпечте свіже повітря. Терміново до ветеринара!",
    "drooling": "Промийте рот чистою водою. Спостерігайте за станом.",
    "skin": "Промийте уражену ділянку водою з милом.",
    "depression": "Забезпечте спокій та тепло. Спостерігайте за станом.",
    "death": "КРИТИЧНА НЕБЕЗПЕКА! Негайна ветеринарна допомога!",
}

EMERGENCY_INFO = """
ЕКСТРЕНІ КОНТАКТИ:
- Ветеринарна клініка (цілодобово): знайдіть найближчу
- При отруєнні: НЕ викликайте блювоту без консультації ветеринара
- Візьміть зразок рослини до клініки для ідентифікації
"""


def get_first_aid_info(plant_name, input_file="plants.json"):
    """Отримує інформацію про першу допомогу при отруєнні рослиною."""
    plants_db = load_plants_data(input_file)
    if not plants_db:
        return {"error": "Не вдалося завантажити базу даних"}

    plant_name_lower = plant_name.lower().strip()
    found_plant = None

    for plant in plants_db:
        if plant_name_lower in plant.get("name", "").lower():
            found_plant = plant
            break

        for common in plant.get("common", []):
            common_name = (
                common.get("name", "") if isinstance(common, dict) else str(common)
            )
            if plant_name_lower in common_name.lower():
                found_plant = plant
                break
        if found_plant:
            break

    if not found_plant:
        return {"error": f"Рослина '{plant_name}' не знайдена в базі даних"}

    severity = found_plant.get("severity", {})
    if isinstance(severity, dict):
        sev_label = severity.get("label", "Unknown")
        sev_level = severity.get("level", 0)
    else:
        sev_label = str(severity)
        sev_level = 2

    symptoms = []
    first_aid_actions = []

    for s in found_plant.get("symptoms", []):
        symptom_name = s.get("name", "") if isinstance(s, dict) else str(s)
        symptoms.append(symptom_name)

        for key, tip in FIRST_AID_TIPS.items():
            if key in symptom_name.lower():
                if tip not in first_aid_actions:
                    first_aid_actions.append(tip)

    if sev_level >= 3 or "death" in str(symptoms).lower():
        urgency = "КРИТИЧНА - НЕГАЙНО ДО ВЕТЕРИНАРА!"
    elif sev_level >= 2:
        urgency = "ВИСОКА - зверніться до ветеринара найближчим часом"
    else:
        urgency = "ПОМІРНА - спостерігайте за станом тварини"

    animals = []
    for a in found_plant.get("animals", []):
        if isinstance(a, dict):
            animals.append(str(list(a.values())[0]))
        else:
            animals.append(str(a))

    result = {
        "task": "first_aid",
        "timestamp": __import__("datetime").datetime.now().isoformat(),
        "plant_query": plant_name,
        "plant": {
            "scientific_name": found_plant.get("name", ""),
            "family": found_plant.get("family", ""),
            "severity": sev_label,
            "severity_level": sev_level,
            "affected_animals": animals,
        },
        "symptoms": symptoms,
        "urgency": urgency,
        "first_aid_actions": first_aid_actions,
        "emergency_info": EMERGENCY_INFO,
    }

    log_protocol(f"Перша допомога: запит про {found_plant.get('name', plant_name)}")
    return result


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Перша допомога при отруєнні рослиною")
    parser.add_argument("plant", nargs="?", help="Назва рослини")
    parser.add_argument("--input", default="plants.json", help="JSON файл з даними")
    parser.add_argument(
        "--output", default="results_first_aid.json", help="Файл результатів"
    )

    args = parser.parse_args()

    if not args.plant:
        print("\n" + "=" * 60)
        print("   ПЕРША ДОПОМОГА ПРИ ОТРУЄННІ РОСЛИНОЮ")
        print("=" * 60)
        print("\nВведіть назву рослини, якою отруїлась тварина:")
        print("Приклади: lily, oleander, aloe, tulip, ivy, azalea")
        args.plant = input("\nНазва рослини: ").strip()

    if not args.plant:
        log_error("Назва рослини не вказана")
        return 1

    results = get_first_aid_info(args.plant, args.input)

    if "error" in results:
        log_error(results["error"])
        print("\nСпробуйте ввести іншу назву або перевірте правопис.")
        return 1

    if save_results(results, args.output):
        log(f"Результати збережено у {args.output}")

    plant = results["plant"]

    print("\n" + "!" * 60)
    print("   ІНФОРМАЦІЯ ПРО ОТРУЙНУ РОСЛИНУ")
    print("!" * 60)

    print(f"\nРослина: {plant['scientific_name']}")
    print(f"Родина: {plant['family']}")
    print(f"Рівень небезпеки: {plant['severity']}")

    print("\n" + "-" * 60)
    print(f"ТЕРМІНОВІСТЬ: {results['urgency']}")
    print("-" * 60)

    print("\nСИМПТОМИ ОТРУЄННЯ:")
    for symptom in results["symptoms"]:
        print(f"  - {symptom}")

    print("\nНЕБЕЗПЕЧНА ДЛЯ:")
    print(f"  {', '.join(plant['affected_animals'])}")

    if results["first_aid_actions"]:
        print("\n" + "-" * 60)
        print("ДІЇ ПЕРШОЇ ДОПОМОГИ:")
        print("-" * 60)
        for i, action in enumerate(results["first_aid_actions"], 1):
            print(f"  {i}. {action}")

    print("\n" + "=" * 60)
    print(results["emergency_info"])
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())

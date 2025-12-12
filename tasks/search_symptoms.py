# tasks/search_symptoms.py
"""
Задача 4: Пошук рослин за симптомом отруєння.
Знаходить усі рослини, що викликають вказаний симптом.
"""
from collections import Counter
import sys
import os

try:
    from .utils import load_plants_data, save_results, log_protocol
except ImportError:
    from utils import load_plants_data, save_results, log_protocol

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from log import log, log_error


def search_plants_by_symptom(symptom_query, input_file="plants.json"):
    """Пошук рослин за симптомом отруєння."""
    plants = load_plants_data(input_file)
    if not plants:
        return {"error": "Не вдалося завантажити дані"}

    query_lower = symptom_query.lower()
    matching_plants = []
    all_symptoms = []

    for plant in plants:
        raw_symptoms = plant.get("symptoms", [])
        plant_symptoms = []

        for symptom in raw_symptoms:
            if isinstance(symptom, dict):
                name = symptom.get("name", "")
            else:
                name = str(symptom)
            plant_symptoms.append(name)
            all_symptoms.append(name)

        matched = [s for s in plant_symptoms if query_lower in s.lower()]

        if matched:
            severity = plant.get("severity", {})
            if isinstance(severity, dict):
                sev_label = severity.get("label", "Unknown")
            else:
                sev_label = str(severity) if severity else "Unknown"

            matching_plants.append(
                {
                    "scientific_name": plant.get("name", "Unknown"),
                    "common_name": (
                        plant.get("common", [{}])[0].get("name", "")
                        if plant.get("common")
                        else ""
                    ),
                    "family": plant.get("family", "Unknown"),
                    "severity": sev_label,
                    "matched_symptoms": matched,
                    "all_symptoms": plant_symptoms,
                }
            )

    matching_plants.sort(key=lambda x: len(x["matched_symptoms"]), reverse=True)

    symptom_counts = Counter(all_symptoms)
    related_symptoms = [
        {"symptom": s, "count": c}
        for s, c in symptom_counts.most_common(10)
        if query_lower in s.lower()
    ]

    result = {
        "task": "search_symptoms",
        "timestamp": __import__("datetime").datetime.now().isoformat(),
        "search_query": symptom_query,
        "total_plants_checked": len(plants),
        "plants_with_symptom": len(matching_plants),
        "related_symptoms": related_symptoms,
        "matching_plants": matching_plants[:20],
    }

    log_message = (
        f"Пошук симптому '{symptom_query}': знайдено {len(matching_plants)} рослин"
    )
    log_protocol(log_message)

    return result


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Пошук рослин за симптомом отруєння")
    parser.add_argument(
        "symptom",
        nargs="?",
        default=None,
        help="Симптом для пошуку (наприклад: vomiting, diarrhea, pain)",
    )
    parser.add_argument("--input", default="plants.json", help="JSON файл з даними")
    parser.add_argument(
        "--output",
        default="results_symptoms.json",
        help="Файл для збереження результатів",
    )

    args = parser.parse_args()

    if not args.symptom:
        print("\n" + "=" * 50)
        print("   ПОШУК РОСЛИН ЗА СИМПТОМОМ ОТРУЄННЯ")
        print("=" * 50)
        print("\nПоширені симптоми для пошуку:")
        print("  - vomiting     (блювота)")
        print("  - diarrhea     (діарея)")
        print("  - pain         (біль)")
        print("  - breathing    (проблеми з диханням)")
        print("  - cardiac      (серцеві проблеми)")
        print("  - skin         (подразнення шкіри)")
        print("  - salivation   (слиновиділення)")
        print("  - tremor       (тремор)")
        print()
        args.symptom = input("Введіть симптом для пошуку: ").strip()

        if not args.symptom:
            log_error("Симптом не вказано")
            return 1

    results = search_plants_by_symptom(args.symptom, args.input)

    if "error" in results:
        log_error(results["error"])
        return 1

    if save_results(results, args.output):
        log(f"Результати збережено у {args.output}")

    print("\n" + "=" * 60)
    print(f"  РЕЗУЛЬТАТИ ПОШУКУ: '{args.symptom}'")
    print("=" * 60)
    print(
        f"Знайдено рослин: {results['plants_with_symptom']} з {results['total_plants_checked']}"
    )

    if results["related_symptoms"]:
        print("\nПов'язані симптоми:")
        for item in results["related_symptoms"][:5]:
            print(f"  - {item['symptom']} ({item['count']} рослин)")

    if results["matching_plants"]:
        print("\n" + "-" * 60)
        print("Топ рослин з цим симптомом:")
        print("-" * 60)

        for i, plant in enumerate(results["matching_plants"][:10], 1):
            sev = plant["severity"]
            if "critical" in sev.lower() or "severe" in sev.lower():
                danger = "[!!!]"
            elif "high" in sev.lower() or "moderate" in sev.lower():
                danger = "[!!]"
            else:
                danger = "[!]"

            print(f"\n{i}. {danger} {plant['scientific_name']}")
            if plant["common_name"]:
                print(f"   Назва: {plant['common_name']}")
            print(f"   Родина: {plant['family']}")
            print(f"   Небезпека: {sev}")
            print(f"   Симптоми: {', '.join(plant['matched_symptoms'][:3])}")
    else:
        print("\nРослин з таким симптомом не знайдено.")
        print("Спробуйте інший пошуковий запит.")

    print("\n" + "=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())

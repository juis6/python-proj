# tasks/top_families.py
from collections import Counter
import sys

from log import log, log_error
try:
    from .utils import load_plants_data, save_results, log_protocol
except ImportError:
    from utils import load_plants_data, save_results, log_protocol

def analyze_top_families(input_file="plants.json", limit=5):
    plants = load_plants_data(input_file)
    if not plants:
        return {"error": "Не вдалося завантажити дані"}

    families = []
    for plant in plants:
        family = plant.get('family')
        if family:
            families.append(family)

    family_counts = Counter(families).most_common(limit)

    result = {
        "task": "top_families",
        "timestamp": __import__('datetime').datetime.now().isoformat(),
        "total_plants_processed": len(plants),
        "unique_families_count": len(set(families)),
        "top_families": []
    }
    
    for rank, (family, count) in enumerate(family_counts, 1):
        result["top_families"].append({
            "rank": rank,
            "family": family,
            "count": count,
            "percentage": round(count / len(plants) * 100, 2)
        })

    log_message = f"Завдання 'top_families': проаналізовано {len(plants)} рослин"
    log_protocol(log_message)
    return result

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Аналіз топ родин отруйних рослин')
    parser.add_argument('input_file', nargs='?', default='plants.json', 
                       help='JSON файл з даними (за замовчуванням: plants.json)')
    parser.add_argument('--limit', type=int, default=5,
                       help='Кількість родин для виведення (за замовчуванням: 5)')
    parser.add_argument('--output', default='results_top_families.json',
                       help='Файл для збереження результатів')
    
    args = parser.parse_args()

    results = analyze_top_families(args.input_file, args.limit)

    if save_results(results, args.output):
        log(f"Результати збережено у {args.output}")
        log(f"Топ {args.limit} найпоширеніших родин:")
        for item in results.get("top_families", []):
            print(f"    {item['rank']}. {item['family']} - {item['count']} видів ({item['percentage']}%)")
        log(f"Всього унікальних родин: {results.get('unique_families_count')}")
        
        return 0
    else:
        log_error("Помилка збереження результатів")
        return 1

if __name__ == "__main__":
    sys.exit(main())
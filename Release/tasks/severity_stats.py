# tasks/severity_stats.py
from collections import Counter
import sys

from log import log, log_error
try:
    from .utils import load_plants_data, save_results, log_protocol
except ImportError:
    from utils import load_plants_data, save_results, log_protocol

def analyze_severity_statistics(input_file="plants.json"):
    plants = load_plants_data(input_file)
    if not plants:
        return {"error": "Не вдалося завантажити дані"}
    
    severity_levels = []
    
    for plant in plants:
        severity_obj = plant.get('severity', {})
        
        if isinstance(severity_obj, dict):
            label = severity_obj.get('label')
            if label:
                severity_levels.append(label)
            else:
                for key in ['name', 'level', 'severity']:
                    if key in severity_obj:
                        severity_levels.append(str(severity_obj[key]))
                        break
                else:
                    severity_levels.append('Unknown')
        elif severity_obj:
            severity_levels.append(str(severity_obj))
        else:
            severity_levels.append('Unknown')

    severity_counts = Counter(severity_levels)

    result = {
        "task": "severity_stats",
        "timestamp": __import__('datetime').datetime.now().isoformat(),
        "total_plants_analyzed": len(plants),
        "severity_distribution": [],
        "summary": {}
    }

    for level, count in severity_counts.most_common():
        percentage = round(count / len(plants) * 100, 2)
        result["severity_distribution"].append({
            "level": level,
            "count": count,
            "percentage": percentage
        })

    most_common_level = severity_counts.most_common(1)[0] if severity_counts else ("None", 0)
    unique_levels = len(severity_counts)
    
    result["summary"] = {
        "most_common_severity": most_common_level[0],
        "most_common_count": most_common_level[1],
        "unique_severity_levels": unique_levels,
        "plants_without_severity": severity_counts.get('Unknown', 0)
    }

    log_message = f"Статистика небезпеки: {unique_levels} рівнів, найпоширеніший - {most_common_level[0]}"
    log_protocol(log_message)
    
    return result

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Статистика рівнів небезпеки рослин')
    parser.add_argument('input_file', nargs='?', default='plants.json', 
                       help='JSON файл з даними (за замовчуванням: plants.json)')
    parser.add_argument('--output', default='results_severity_stats.json',
                       help='Файл для збереження результатів')
    
    args = parser.parse_args()

    results = analyze_severity_statistics(args.input_file)

    if save_results(results, args.output):
        log(f"Результати збережено у {args.output}")

        log(f"Статистика рівнів небезпеки:")
        log(f"Всього проаналізовано рослин: {results['total_plants_analyzed']}")
        log(f"Унікальних рівнів небезпеки: {results['summary']['unique_severity_levels']}")
        log(f"Найпоширеніший рівень: {results['summary']['most_common_severity']} "
              f"({results['summary']['most_common_count']} рослин)")
        log("Детальний розподіл:")
        print("" * 50)
        
        for item in results["severity_distribution"]:
            bar_length = int(item["percentage"] / 2)  # Смужка 50 символів = 100%
            bar = "█" * bar_length + "░" * (50 - bar_length)
            log(f"{item['level']:20s} | {bar} | {item['count']:3d} ({item['percentage']:5.1f}%)")
        
        return 0
    else:
        log_error("Помилка збереження результатів")
        return 1

if __name__ == "__main__":
    sys.exit(main())
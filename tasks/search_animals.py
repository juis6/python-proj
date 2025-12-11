# tasks/search_animals.py
try:
    from .utils import load_plants_data, save_results, log_protocol
except ImportError:
    from utils import load_plants_data, save_results, log_protocol
import sys

from log import log, log_error

def search_dangerous_plants_for_animal(animal_name, input_file="plants.json"):
    plants = load_plants_data(input_file)
    if not plants:
        return {"error": "Не вдалося завантажити дані"}
    
    animal_lower = animal_name.lower()
    dangerous_plants = []
    
    for plant in plants:
        animals_list = plant.get('animals', [])
        if not animals_list:
            continue

        animals_lower = []
        for animal in animals_list:
            if isinstance(animal, dict):
                animal_value = str(list(animal.values())[0]) if animal else ""
            else:
                animal_value = str(animal)
            animals_lower.append(animal_value.lower())

        found = any(animal_lower in a or a in animal_lower for a in animals_lower)
        
        if found:
            plant_info = {
                "scientific_name": plant.get('name', 'Unknown'),
                "common_name": plant.get('common_name', ''),
                "family": plant.get('family', 'Unknown'),
                "severity": plant.get('severity', {}).get('label', 'Unknown'),
                "animals_affected": animals_list
            }

            symptoms = []
            raw_symptoms = plant.get('symptoms', [])
            for symptom in raw_symptoms:
                if isinstance(symptom, dict):
                    symptoms.append(symptom.get('name', str(symptom)))
                else:
                    symptoms.append(str(symptom))
            plant_info["symptoms"] = symptoms
            
            dangerous_plants.append(plant_info)

    result = {
        "task": "search_animals",
        "timestamp": __import__('datetime').datetime.now().isoformat(),
        "search_animal": animal_name,
        "total_plants_checked": len(plants),
        "dangerous_plants_found": len(dangerous_plants),
        "dangerous_plants": dangerous_plants
    }

    log_message = f"Пошук для тварини '{animal_name}': знайдено {len(dangerous_plants)} рослин"
    log_protocol(log_message)
    
    return result

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Пошук рослин, небезпечних для тварин')
    parser.add_argument('animal', help='Назва тварини (наприклад: dogs, cats, horses)')
    parser.add_argument('--input', default='plants.json',
                       help='JSON файл з даними (за замовчуванням: plants.json)')
    parser.add_argument('--output', default='results_animal_search.json',
                       help='Файл для збереження результатів')
    
    args = parser.parse_args()

    results = search_dangerous_plants_for_animal(args.animal, args.input)

    if save_results(results, args.output):
        log(f"Результати збережено у {args.output}")

        log(f"Результати пошуку для тварини: {args.animal}")
        
        if results["dangerous_plants_found"] == 0:
            log_error(f"Рослин, небезпечних для {args.animal}, не знайдено")
        else:
            log(f"Знайдено {results['dangerous_plants_found']} небезпечних рослин:")
            print(" " * 60)
            
            for i, plant in enumerate(results["dangerous_plants"], 1):
                print(f"{i}. {plant['scientific_name']}")
                print(f"   Поширена назва: {plant['common_name']}")
                print(f"   Родина: {plant['family']}")
                print(f"   Небезпека: {plant['severity']}")
                
                symptoms_str = ", ".join(plant['symptoms'][:3])
                if len(plant['symptoms']) > 3:
                    symptoms_str += f"... (+{len(plant['symptoms'])-3})"
                print(f"   Симптоми: {symptoms_str}")
                print()
        
        return 0
    else:
        log_error("Помилка збереження результатів")
        return 1

if __name__ == "__main__":
    sys.exit(main())
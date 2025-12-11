# tasks/utils.py
import json
import os
import datetime

from log import log_error

def log_protocol(message):
    protocol_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'protocol.txt')

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(protocol_path, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception as e:
        log_error(f"{e}")

def load_plants_data(filename="plants.json"):
    if not os.path.exists(filename):
        parent_file = os.path.join("..", filename)
        if os.path.exists(parent_file):
            filename = parent_file
        else:
            return []
            
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return data
    except Exception as e:
        log_error(f"{e}")
        return []

def save_results(data, filename):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        log_error(f"{e}")
        return False
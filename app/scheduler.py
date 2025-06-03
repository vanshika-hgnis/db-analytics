import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
STATE_FILE = os.path.join(DATA_DIR, 'training_state.json')

def load_training_state():
    if not os.path.exists(STATE_FILE):
        return {}
    with open(STATE_FILE, 'r') as f:
        return json.load(f)

def save_training_state(state):
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

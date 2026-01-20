import pickle, os
DB_FILE = "tahaji_data.pkl"
def save_data(data):
    with open(DB_FILE, 'wb') as f: pickle.dump(data, f)
def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'rb') as f: return pickle.load(f)
    return {'words': ["أسد"], 'audio': {}, 'limit': 30, 'bg': ""}
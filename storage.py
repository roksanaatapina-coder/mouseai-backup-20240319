import json

class Storage:
    def __init__(self, filename):
        self.filename = filename

    def save_session_data(self, session_data):
        with open(self.filename, 'w') as file:
            json.dump(session_data, file)

    def load_session_data(self):
        try:
            with open(self.filename, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

import json
import os 

# save and load data from json files

class FileHandler:
    def load_file(self, filename):
        filedestination = f"data/{filename}.json"
        if os.path.exists(filedestination):
            with open(filedestination, 'r') as file:
                result = json.load(file)
            return result 
        return None 

    def save_file(self, data, filename):
        with open(f"data/{filename}.json", 'w') as file:
            json.dump(data, file, indent = 4)


# from .filehandler import FileHandler
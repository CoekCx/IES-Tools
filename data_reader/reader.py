import json
import os
import re

from common.constants.constants import DATA_PATH


class DataReader:
    @staticmethod
    def __read_classes(file_path: str) -> (str, [str]):
        with open(file_path, 'r') as file:
            xml_code = file.read()

        # Extract the value of the Path tag
        path_match = re.search(r'<Path>(.*?)<\/Path>', xml_code, re.DOTALL)
        path_value = path_match.group(1).strip() if path_match else None

        # Extract the classes in the top layer of tags
        classes_match = re.findall(r'<\/?cim:(\w+)', xml_code)
        classes = list(set(classes_match))

        return path_value, classes

    @staticmethod
    def __read_classes_from_folder(folder_path: str = DATA_PATH) -> dict:
        result = {}

        for file_name in os.listdir(folder_path):
            if file_name.endswith('.xml'):
                file_path = os.path.join(folder_path, file_name)
                path_value, classes = DataReader.__read_classes(file_path)
                result[file_name] = {'Path': path_value, 'Classes': classes}

        return result

    @staticmethod
    def fetch_all_data() -> dict:
        return DataReader.__read_classes_from_folder()

    @staticmethod
    def fetch_classes() -> list:
        data = DataReader.fetch_all_data()
        all_class_lists = (value['Classes'] for key, value in data.items())
        all_class_set = set()
        for class_list in all_class_lists:
            all_class_set.update(class_list)
        return list(all_class_set)

    @staticmethod
    def load_data(folder_path: str = DATA_PATH, file_name: str = 'data.json') -> list:
        file_path = os.path.join(folder_path, file_name)
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            os.makedirs(folder_path, exist_ok=True)  # Create folder if it doesn't exist
            data = []  # Initialize with an empty list if file doesn't exist
        except json.JSONDecodeError:
            os.system('cls' if os.name in ('nt', 'dos') else 'clear')
            print(f"Error decoding JSON in file '{file_name}'")
            input()
            return None

        return data

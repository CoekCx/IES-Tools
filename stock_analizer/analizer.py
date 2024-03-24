import os

from PIL import Image
from tabulate import tabulate
from termcolor import colored

from common.constants.constants import IES_FOLDER_PATH
from data_reader.reader import DataReader
from prompter.prompter import Prompter


class Analyzer:
    @staticmethod
    def start_app() -> None:
        # fetch data
        data = DataReader.fetch_all_data()

        selected_classes = Prompter.prompt_user_for_classes()  # take user input
        sorted_data = Analyzer.__sort_data_by_overlap(data, selected_classes)  # analize data based on user input

        Analyzer.__await_user_input(sorted_data, selected_classes)

    @staticmethod
    def __sort_data_by_overlap(loaded_data: dict, target_classes: list) -> dict:
        sorted_data = {}

        for file_name, data in loaded_data.items():
            file_classes = data['Classes']
            common_classes = set(file_classes) & set(target_classes)
            overlap_percentage = len(common_classes) / len(target_classes) * 100 if target_classes else 0

            sorted_data[file_name] = {
                'Path': data['Path'],
                'Classes': file_classes,
                'OverlapPercentage': overlap_percentage
            }

        # Sort the data based on overlap percentage
        sorted_data = dict(sorted(sorted_data.items(), key=lambda x: x[1]['OverlapPercentage'], reverse=True))

        return sorted_data

    @staticmethod
    def __find_class_differences(src, selected):
        not_found = [item for item in selected if item not in src]
        found = [item for item in selected if item in src]
        return not_found, found

    @staticmethod
    def __print_sorted_data(sorted_data: dict, selected_classes: list):
        headers = ["File Name", "Path", "Overlap Percentage", "Missing Classes"]
        table_data = []

        for file_name, data in sorted_data.items():
            overlap_percentage = data['OverlapPercentage']
            not_found_classes, found_classes = Analyzer.__find_class_differences(data['Classes'], selected_classes)
            if overlap_percentage > 0:
                path = data['Path']
                table_data.append([colored(file_name, 'yellow'), colored(path, 'green'), f"{overlap_percentage:.2f}%",
                                   colored(not_found_classes.__str__().replace("[", "").replace("]", ""), 'red')])

        print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))

    @staticmethod
    def __handle_command(command, data):
        os.system('cls' if os.name == 'nt' else 'clear')
        if command.lower() in ["exit", "done", "q", "quit"]:
            return "exit"
        elif command.lower().startswith("open "):
            file_name = f'{command[5:]}.xml'
            folder_path = f'{IES_FOLDER_PATH}\\{data[file_name]["Path"]}'
            if os.path.exists(folder_path) and os.path.isdir(folder_path):
                os.system(f'explorer "{os.path.abspath(folder_path)}"')
            else:
                print("Invalid path or file type.")
        elif command.lower().startswith("img ") or command.lower().startswith("diagram "):
            file_name = f'{command[4:]}.xml' if command.lower().startswith("img ") else f'{command[8:]}.xml'
            img_path = f'{IES_FOLDER_PATH}\\{data[file_name]["Path"]}\\Diagram.jpg'
            img = Image.open(img_path)
            img.show()
        else:
            print("Unknown command.")

    @staticmethod
    def __await_user_input(data, selected_classes):
        while True:
            Analyzer.__print_sorted_data(data, selected_classes)
            user_input = input("Enter a command: ")
            result = Analyzer.__handle_command(user_input, data)
            if result == "exit":
                break

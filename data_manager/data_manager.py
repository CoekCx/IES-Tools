import json
import pprint
import re
import tkinter as tk
from tkinter import filedialog

from PIL import Image
from colorama import Fore, Style
from inquirer2 import prompt as pmt
from tabulate import tabulate
from termcolor import colored

import common
from common.constants.constants import DATA_PATH, IES_FOLDER_PATH_FORWARD_SLASH, IES_FOLDER_PATH
from common.enums.class_type import ClassType
from common.logging import *
from common.models.specification import Specification
from data_reader.reader import DataReader
from prompter.prompter import Prompter


class DataManager:
    @staticmethod
    def start_app() -> None:
        while not common.TRANSFER_TO_GENERATOR:
            questions = [
                {
                    'type': 'list',
                    'name': 'menu_choice',
                    'message': 'Select an option:',
                    'choices': [
                        'View Project Specifications',
                        'Filter Project Specifications',
                        'Create Project Specification',
                        'Copy Project Specification',
                        'Delete Project Specification',
                        'Back',
                    ],
                },
            ]

            os.system('cls' if os.name in ('nt', 'dos') else 'clear')
            answers = pmt.prompt(questions)

            choice = answers['menu_choice']

            if choice == 'View Project Specifications':
                DataManager.__view_project_specification()
            elif choice == 'Filter Project Specifications':
                DataManager.__view_filter_project_specifications()
            elif choice == 'Create Project Specification':
                DataManager.__create_project_specification()
            elif choice == 'Copy Project Specification':
                DataManager.__copy_project_specification()
            elif choice == 'Delete Project Specification':
                DataManager.__delete_project_specification()
            elif choice == 'Back':
                break

    @staticmethod
    def __select_folder():
        root = tk.Tk()
        root.withdraw()

        folder_path = filedialog.askdirectory(title="Select a Folder")

        if not folder_path.startswith(IES_FOLDER_PATH_FORWARD_SLASH):
            os.system('cls' if os.name in ('nt', 'dos') else 'clear')
            print(Fore.RED + 'Warning: Path selected is outside of the IES folder!' + Style.RESET_ALL)
            print(Fore.YELLOW + folder_path + Style.RESET_ALL)
            input()
        else:
            folder_path = folder_path.replace(IES_FOLDER_PATH_FORWARD_SLASH, '')

        return folder_path

    @staticmethod
    def __print_specifications_table(specifications: list[Specification] = None) -> None:
        if not specifications:
            specifications = DataManager.__load_data_using_models()

        headers = ["Index", "Path", "Classes", "References"]
        table_data = []

        for index, spec in enumerate(specifications):
            concrete_classes = ''
            num_of_refs = 0
            for el in spec.specification:
                num_of_refs += el.num_of_refs
                if el.type == ClassType.CONCRETE:
                    concrete_classes += el.name + ' '

            table_data.append(
                [index + 1, colored(spec.path, 'green'), colored(concrete_classes, 'cyan'),
                 colored(num_of_refs, 'yellow')])

        print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))

    @staticmethod
    def __print_filtered_specifications_table(specifications: list[Specification], selected_classes: list[str]) -> None:
        if not specifications:
            return

        headers = ["Index", "Path", "Classes", "References", "Overlap", "Missing"]
        table_data = []

        for index, spec in enumerate(specifications):
            concrete_classes = ''
            num_of_refs = 0
            for el in spec.specification:
                num_of_refs += el.num_of_refs
                if el.type == ClassType.CONCRETE:
                    concrete_classes += el.name + ' '

            missing_classes = ''
            for el_name in selected_classes:
                if not spec.includes_element(el_name):
                    missing_classes += el_name + ' '

            table_data.append(
                [index + 1, colored(spec.path, 'green'),
                 colored(concrete_classes, 'cyan'),
                 colored(num_of_refs, 'yellow'),
                 colored(f"{spec.overlap_percentage:.2f}%",
                         DataManager.__get_percentage_color(spec.overlap_percentage)),
                 colored(missing_classes, 'red')])

        print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))

    @staticmethod
    def __get_percentage_color(percentage: float) -> str:
        if 75 <= percentage <= 100:
            return 'green'
        elif 50 <= percentage <= 74:
            return 'yellow'
        elif 25 <= percentage <= 49:
            return 'light_red'
        else:
            return 'red'

    @staticmethod
    def json_colored_pprint(obj):
        os.system('cls' if os.name in ('nt', 'dos') else 'clear')
        for key, value in obj.items():
            print(Fore.YELLOW + str(key) + Style.RESET_ALL + ':', end=' ')
            if isinstance(value, dict):
                print('{')
                pprint.PrettyPrinter(indent=4).pprint(value)
                print('}')
            else:
                print(Fore.BLUE + str(value) + Style.RESET_ALL)
        input()

    @staticmethod
    def __view_project_specification():
        os.system('cls' if os.name in ('nt', 'dos') else 'clear')
        DataManager.__print_specifications_table()
        print('Press enter to continue...')
        input()

    @staticmethod
    def __create_project_specification():
        new_specification = {'path': DataManager.__select_folder()}
        if new_specification['path'] == '':
            os.system('cls' if os.name in ('nt', 'dos') else 'clear')
            print(Fore.RED + 'Warning: No folder selected for specification!' + Style.RESET_ALL)
            input()
        new_specification['specification'] = Prompter.prompt_user_for_project_specification()
        DataManager.__append_project_specification(new_specification)

    @staticmethod
    def __append_project_specification(new_specification: dict):
        existing_data = DataManager.__load_project_specifications()
        for existing_spec in existing_data:
            if existing_spec['path'] == new_specification['path']:
                log('Error: A specification with that path already exists!', LogLevel.CRITICAL)
                return

        existing_data.append(new_specification)
        DataManager.__save_project_specifications(existing_data)

    @staticmethod
    def __delete_project_specification():
        selected_specification = DataManager.__select_specification()
        if not selected_specification:
            return

        existing_data = DataManager.__load_data_using_models()
        for dp in existing_data:
            if dp.path == selected_specification.path:
                existing_data.remove(dp)
                break

        updated_data = DataManager.__convert_specifications_to_json_data(existing_data)
        DataManager.__save_project_specifications(updated_data)

    @staticmethod
    def __load_project_specifications() -> list:
        return DataReader.load_data()

    @staticmethod
    def __load_data_using_models():
        existing_data = DataManager.__load_project_specifications()

        specifications = []
        for dp in existing_data:
            specifications.append(Specification(dp))

        return specifications

    @staticmethod
    def __save_project_specifications(data: list[dict], folder_path: str = DATA_PATH, file_name: str = 'data.json'):
        data = sorted(data, key=lambda x: x['path'])

        file_path = os.path.join(folder_path, file_name)
        try:
            with open(file_path, 'w') as file:
                json.dump(data, file, indent=4)
            os.system('cls' if os.name in ('nt', 'dos') else 'clear')
            print(Fore.GREEN + f"Specification data updated" + Style.RESET_ALL)
            input()

        except Exception as e:
            log(f"Error saving data to '{file_name}' at '{folder_path}': {e}", LogLevel.CRITICAL, also_log_to_file=True)

    @staticmethod
    def __copy_project_specification():
        selected_specification = DataManager.__select_specification()
        if not selected_specification:
            return

        new_specification = {'path': DataManager.__select_folder()}
        if new_specification['path'] == '':
            os.system('cls' if os.name in ('nt', 'dos') else 'clear')
            print(Fore.RED + 'Warning: No folder selected for specification!' + Style.RESET_ALL)
            input()
        new_specification['specification'] = selected_specification.properties_to_json_data()
        DataManager.__append_project_specification(new_specification)

    @staticmethod
    def __select_specification():
        os.system('cls' if os.name in ('nt', 'dos') else 'clear')
        existing_data = DataManager.__load_data_using_models()
        if not existing_data:
            print(colored('Warning: No specification data!'))
            input()
            return

        DataManager.__print_specifications_table(existing_data)
        choices = [spec.path for spec in existing_data]
        choices.append('Back')

        index = Prompter.prompt_for_index(upper_limit=len(existing_data), msg='Select index (0 for Back)')
        if index == 0:  # Go Back
            return

        return existing_data[index - 1]

    @staticmethod
    def select_specification() -> Specification:
        os.system('cls' if os.name in ('nt', 'dos') else 'clear')
        existing_data = DataManager.__load_data_using_models()
        if not existing_data:
            print(colored('Warning: No specification data!'))
            input()
            return

        DataManager.__print_specifications_table(existing_data)
        choices = [spec.path for spec in existing_data]
        choices.append('Back')

        index = Prompter.prompt_for_index(upper_limit=len(existing_data), lower_limit=1)

        return existing_data[index - 1]

    @staticmethod
    def __convert_specifications_to_json_data(data: list[Specification]) -> list:
        json_data = []
        for dp in data:
            json_data.append({
                'path': dp.path,
                'specification': dp.properties_to_json_data()
            })
        return json_data

    @staticmethod
    def __view_filter_project_specifications():
        while not common.TRANSFER_TO_GENERATOR:
            filtered_data, selected_classes = DataManager.__filter_project_specifications()

            while not common.TRANSFER_TO_GENERATOR:
                os.system('cls' if os.name in ('nt', 'dos') else 'clear')
                DataManager.__print_filtered_specifications_table(filtered_data, selected_classes)

                questions = [
                    {
                        'type': 'input',
                        'name': 'command',
                        'message': 'Enter command',
                        'validate': lambda x: True if
                        DataManager.__validate_command(x, len(filtered_data)) else 'Invalid command'
                    },
                ]

                command: str = pmt.prompt(questions=questions)['command']
                if command.startswith('b') or command.startswith('B') or \
                        command.startswith('q') or command.startswith('Q'):
                    return
                if command.startswith('r') or command.startswith('R'):
                    break

                index = int(command.split(' ')[1]) - 1
                if command.startswith('img'):
                    DataManager.__img_command(filtered_data[index])
                elif command.startswith('open'):
                    DataManager.__open_command(filtered_data[index])
                elif command.startswith('load'):
                    DataManager.__load_command(filtered_data[index])

    @staticmethod
    def __filter_project_specifications():
        os.system('cls' if os.name in ('nt', 'dos') else 'clear')
        selected_classes = Prompter.prompt_user_for_classes()

        data = DataManager.__load_data_using_models()
        if not data:
            os.system('cls' if os.name in ('nt', 'dos') else 'clear')
            print(colored('Warning: No data found', 'red'))
            input()
            return

        filtered_data = []
        for spec in data:
            if spec.includes_any_element_of(selected_classes):
                filtered_data.append(spec)

            overlap_percentage = 100 - (spec.count_missing_elements(selected_classes) / len(selected_classes) * 100)
            spec.overlap_percentage = overlap_percentage

        sorted_data = sorted(filtered_data, key=lambda x: x.overlap_percentage, reverse=True)

        return sorted_data, selected_classes

    @staticmethod
    def __validate_command(input_str: str, upper_limit: int) -> bool:
        # Define the regex pattern for matching commands
        pattern = r"^(img|open|load)\s+(\d+)$|^q$|^quit$|^Q$|^Quit$|^b$|^B$|^back$|^Back$|^r$|^R$|^reset$|^Reset$"

        # Match the input string with the pattern
        match = re.match(pattern, input_str.strip())

        if match:
            # If the input matches any of the patterns
            if match.group(1) == "img" or match.group(1) == "open":
                # If the command is "img X" or "open X"
                number = int(match.group(2))
                return 1 <= number <= upper_limit
            else:
                # If the command is "q", "Q", "quit", or "Quit"
                return True
        else:
            # If no match found
            return False

    @staticmethod
    def __open_command(spec: Specification):
        try:
            folder_path = f'{IES_FOLDER_PATH}\\{spec.path}'
            if os.path.exists(folder_path) and os.path.isdir(folder_path):
                os.system(f'explorer "{os.path.abspath(folder_path)}"')
            else:
                log(f"[DATA MANAGER]: Failed to open {os.path.abspath(folder_path)}", LogLevel.WARNING,
                    also_log_to_file=True)
        except:
            log(f"[DATA MANAGER]: Failed to open folder", LogLevel.WARNING, also_log_to_file=True)

    @staticmethod
    def __img_command(spec: Specification):
        img_path = f'{IES_FOLDER_PATH}\\{spec.path}\\Diagram.jpg'
        try:
            img = Image.open(img_path)
            img.show()
        except:
            log(f"[DATA MANAGER]: Failed to open image {img_path}", LogLevel.WARNING, also_log_to_file=True)

    @staticmethod
    def __load_command(spec: Specification):
        common.TRANSFER_TO_GENERATOR = spec

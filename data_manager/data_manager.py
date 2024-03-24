import json
import os
from inquirer2 import prompt as pmt
import tkinter as tk
from tkinter import filedialog
from colorama import Fore, Style
import pprint

from common.constants.constants import DATA_PATH, IES_FOLDER_PATH_FORWARD_SLASH
from common.enums.class_type import ClassType
from common.models.specification import Specification
from prompter.prompter import Prompter
from data_reader.reader import DataReader
from tabulate import tabulate
from termcolor import colored


class DataManager:
    @staticmethod
    def start_app() -> None:
        while True:
            questions = [
                {
                    'type': 'list',
                    'name': 'menu_choice',
                    'message': 'Select an option:',
                    'choices': [
                        'View Project Specifications',
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
        new_specification = {}
        new_specification['path'] = DataManager.__select_folder()
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
                os.system('cls' if os.name in ('nt', 'dos') else 'clear')
                print(Fore.RED + 'Error: A specification with that path already exists!' + Style.RESET_ALL)
                input()
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
            os.system('cls' if os.name in ('nt', 'dos') else 'clear')
            print(Fore.RED + f"Error saving data to '{file_name}' at '{folder_path}': {e}" + Style.RESET_ALL)
            input()

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
    def select_specification_json_data():
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

        return existing_data[index - 1].properties_to_json_data()

    @staticmethod
    def __convert_specifications_to_json_data(data: list[Specification]) -> list:
        json_data = []
        for dp in data:
            json_data.append({
                'path': dp.path,
                'specification': dp.properties_to_json_data()
            })
        return json_data

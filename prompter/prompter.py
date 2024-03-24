import os
import sys

import inquirer as inq
from inquirer2 import prompt as pmt
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.shortcuts import CompleteStyle
from prompt_toolkit.styles import Style
from tqdm import tqdm

from common.models import models as data


class Prompter:
    __style = Style.from_dict({
        'prompt': 'bg:#66ff66 #ffffff',
        'input': '#44ff44',
        'placeholder': '#888888',
    })

    @staticmethod
    def prompt_user_for_classes(classes=None):
        if not classes:
            classes = data.classes

        completer = WordCompleter(classes, ignore_case=True, match_middle=True)

        # Prompt text with a green background
        prompt_text = [
            ('class:prompt', 'Enter classes (separated by space): '),
            ('class:input', ''),
        ]

        input_str = prompt(prompt_text, style=Prompter.__style, completer=completer,
                           complete_style=CompleteStyle.COLUMN)

        # Split the input string into a list of classes
        user_classes = input_str.split()

        return user_classes

    @staticmethod
    def __get_parent_classes_names(class_name: str, parent_classes: list = None) -> list:
        if not parent_classes:
            parent_classes = []

        parent_class_name = data.transformed_models[class_name]['inheritance']
        if parent_class_name != '':
            parent_classes.append(parent_class_name)
            Prompter.__get_parent_classes_names(parent_class_name, parent_classes)

        parent_classes = parent_classes[::-1]  # reverse list
        return parent_classes

    @staticmethod
    def prompt_user_for_project_specification():
        os.system('cls' if os.name in ('nt', 'dos') else 'clear')
        concrete_classes = Prompter.prompt_user_for_classes()

        os.system('cls' if os.name in ('nt', 'dos') else 'clear')
        print("\033[1;1H")

        all_classes = []
        for class_name in concrete_classes:
            parent_classes = Prompter.__get_parent_classes_names(class_name)
            for parent_class_name in parent_classes:
                if parent_class_name not in all_classes:
                    all_classes.append(parent_class_name)
            all_classes.append(class_name)

        result = {}

        for user_class in tqdm(all_classes, desc='Processing', unit='class', file=sys.stdout):
            # Get properties excluding 'inheritance' and 'type'
            properties = [(attr, data_type) for attr, data_type in data.models[user_class] if
                          data_type not in ['inheritance', 'type']]

            # Prepare questions for checkbox prompt
            questions = [
                {
                    'type': 'checkbox',
                    'name': 'selected_properties',
                    'message': f'Select properties for {user_class}',
                    'choices': [{'name': f'{attr} ({data_type})'} for attr, data_type in properties]
                }
            ]

            if properties:
                # Prompt user for property selection
                answers = pmt.prompt(questions)

                # Save selected properties in the result
                result[user_class] = [(attr, data_type) for selected_property in answers['selected_properties'] for
                                      attr, data_type in properties if selected_property.startswith(attr)]
            if user_class in concrete_classes:
                if user_class in result:
                    result[user_class].insert(0, ('concrete', 'type'))
                    result[user_class].insert(1,
                                              (data.transformed_models[user_class]['inheritance'], 'inheritance'))
                else:
                    result[user_class] = [('concrete', 'type')]
                    result[user_class].insert(1,
                                              (data.transformed_models[user_class]['inheritance'], 'inheritance'))
            else:
                if user_class in result:
                    result[user_class].insert(0, ('abstract', 'type'))
                    result[user_class].insert(1,
                                              (data.transformed_models[user_class]['inheritance'], 'inheritance'))
                else:
                    result[user_class] = [('abstract', 'type')]
                    result[user_class].insert(1,
                                              (data.transformed_models[user_class]['inheritance'], 'inheritance'))

            os.system('cls' if os.name in ('nt', 'dos') else 'clear')
            print("\033[1;1H")

        return result

    @staticmethod
    def prompt_user_for_environment_varialbes():
        os.system('cls' if os.name in ('nt', 'dos') else 'clear')
        namespace = Prompter.prompt_text_question('Environment variables setup', 'What is the namespace?')

        os.system('cls' if os.name in ('nt', 'dos') else 'clear')
        dll_name = Prompter.prompt_text_question('Environment variables setup',
                                                 'What is the DLL prefix? (____CIMProfile_Labs)')

        return namespace['Environment variables setup'], dll_name['Environment variables setup']

    @staticmethod
    def prompt_numeric_question(title='', message=''):
        questions = [
            inq.Text(title, message=message,
                     validate=lambda _, x: int(x) > 0)]
        return inq.prompt(questions)

    @staticmethod
    def prompt_text_question(title='', message=''):
        questions = [inq.Text(title, message=message)]
        return inq.prompt(questions) @ staticmethod

    @staticmethod
    def prompt_for_index(upper_limit: int, lower_limit: int = 0, msg: str = ''):
        questions = [
            {
                'type': 'input',
                'name': 'index',
                'message': 'Select index' if msg == '' else msg,
                'validate': lambda x: True if Prompter.__validate_int(x, upper_limit,
                                                                      lower_limit) else 'Invalid index value'
            },
        ]

        return int(pmt.prompt(questions=questions)['index'])

    @staticmethod
    def __validate_int(value, upper_limit: int, lower_limit: int):
        try:
            value = int(value)
            if lower_limit <= value <= upper_limit:
                return True
            return False
        except:
            return False

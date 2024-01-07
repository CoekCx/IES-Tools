import os
import sys

from inquirer2 import prompt as pmt
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.shortcuts import CompleteStyle
from prompt_toolkit.styles import Style
from tqdm import tqdm

import models.models as data


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
    def prompt_user_for_project_specification():
        os.system('cls' if os.name in ('nt', 'dos') else 'clear')
        classes = Prompter.prompt_user_for_classes()

        os.system('cls' if os.name in ('nt', 'dos') else 'clear')
        print("\033[1;1H")

        result = {}

        for user_class in tqdm(classes, desc='Processing', unit='class', file=sys.stdout):
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
            for attr, data_type in data.models[user_class]:
                if data_type in ['inheritance', 'type']:
                    if user_class in result:
                        result[user_class].insert(0, (attr, data_type))
                    else:
                        result[user_class] = [(attr, data_type)]
            os.system('cls' if os.name in ('nt', 'dos') else 'clear')
            print("\033[1;1H")

        return result

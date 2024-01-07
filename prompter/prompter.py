from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.shortcuts import CompleteStyle
from prompt_toolkit.styles import Style

from data_reader.reader import DataReader


class Prompter:
    __style = Style.from_dict({
        'prompt': 'bg:#66ff66 #ffffff',
        'input': '#44ff44',
        'placeholder': '#888888',
    })

    @staticmethod
    def prompt_user_for_classes(classes=None):
        if not classes:
            classes = DataReader.fetch_classes()

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
    def prompt_user_for_project_specification(classes=None):
        if not classes:
            classes = DataReader.fetch_classes()

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

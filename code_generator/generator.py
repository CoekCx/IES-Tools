import os

from PIL import Image
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.shortcuts import CompleteStyle
from prompt_toolkit.styles import Style
from tabulate import tabulate
from termcolor import colored

from constants.constants import IES_FOLDER_PATH
from data_reader.reader import DataReader


class Generator:
    @staticmethod
    def start_app() -> None:
        questions = [
            {
                'type': 'list',
                'name': 'menu_choice',
                'message': 'Select an option:',
                'choices': [
                    'Generate ModelCodes',
                    'Generate Converter Methods',
                    'Generate Importer Methods',
                ],
            },
        ]

        answers = prompt.prompt(questions)

        choice = answers['menu_choice']

    @staticmethod
    def __get_project_specifications() -> None:
        pass

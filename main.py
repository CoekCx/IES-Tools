import os

from inquirer2 import prompt

import common
from code_generator.generator import Generator
from data_manager.data_manager import DataManager


def main():
    while True:
        if common.TRANSFER_TO_GENERATOR:
            Generator.start_app(True)

        os.system('cls' if os.name in ('nt', 'dos') else 'clear')
        questions = [
            {
                'type': 'list',
                'name': 'menu_choice',
                'message': 'Select tool to use:',
                'choices': [
                    'Code Generator',
                    'Data Manager',
                    'Quit',
                ],
            },
        ]

        answers = prompt.prompt(questions)

        choice = answers['menu_choice']

        if choice == 'Code Generator':
            Generator.start_app()
        elif choice == 'Data Manager':
            DataManager.start_app()
        elif choice == 'Quit':
            os.system('cls' if os.name in ('nt', 'dos') else 'clear')
            break


if __name__ == '__main__':
    main()

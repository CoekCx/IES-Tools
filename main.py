import os

from inquirer2 import prompt

from data_reader.reader import DataReader
from stock_analizer.analizer import Analyzer
from code_generator.generator import Generator
from data_manager.data_manager import DataManager


def main():
    while True:
        os.system('cls' if os.name in ('nt', 'dos') else 'clear')
        questions = [
            {
                'type': 'list',
                'name': 'menu_choice',
                'message': 'Select tool to use:',
                'choices': [
                    'Code Generator',
                    'Data Manager',
                    'Stock Analyzer',
                    'Quit',
                ],
            },
        ]

        answers = prompt.prompt(questions)

        choice = answers['menu_choice']

        if choice == 'Stock Analyzer':
            Analyzer.start_app()
        elif choice == 'Data Manager':
            DataManager.start_app()
        elif choice == 'Code Generator':
            Generator.start_app()
        elif choice == 'Quit':
            os.system('cls' if os.name in ('nt', 'dos') else 'clear')
            break


if __name__ == '__main__':
    main()

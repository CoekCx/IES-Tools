from inquirer2 import prompt

from data_reader.reader import DataReader
from stock_analizer.analizer import Analyzer
from code_generator.generator import Generator


def main():
    questions = [
        {
            'type': 'list',
            'name': 'menu_choice',
            'message': 'Select tool to use:',
            'choices': [
                'Code Generator',
                'Stock Analyzer',
            ],
        },
    ]

    answers = prompt.prompt(questions)

    choice = answers['menu_choice']

    if choice == 'Stock Analyzer':
        Analyzer.start_app()
    elif choice == 'Code Generator':
        Generator.start_app()


if __name__ == '__main__':
    main()

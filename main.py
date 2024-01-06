from inquirer2 import prompt

from stock_analizer.analizer import Analyzer


def main():
    questions = [
        {
            'type': 'list',
            'name': 'menu_choice',
            'message': 'Select an option:',
            'choices': [
                'Stock Analyzer',
                'Code Generator',
            ],
        },
    ]

    answers = prompt.prompt(questions)

    choice = answers['menu_choice']

    if choice == 'Stock Analyzer':
        Analyzer.start_app()
    elif choice == 'Code Generator':
        pass


if __name__ == '__main__':
    main()

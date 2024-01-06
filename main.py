from inquirer2 import prompt


def stock_analyzer():
    # Your code for the stock analyzer goes here
    print("Stock Analyzer Selected")


def code_generator():
    # Your code for the code generator goes here
    print("Code Generator Selected")


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
        stock_analyzer()
    elif choice == 'Code Generator':
        code_generator()


if __name__ == '__main__':
    main()

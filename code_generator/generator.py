import os

from inquirer2 import prompt as pmt

from prompter.prompter import Prompter


class Generator:
    project_specification = {}

    @staticmethod
    def start_app() -> None:
        # Ask the user if they want to enter project specifications
        specification_question = [
            {
                'type': 'confirm',
                'name': 'enter_specifications',
                'message': 'Do you want to enter project specifications?',
                'default': True,
            }
        ]

        os.system('cls' if os.name in ('nt', 'dos') else 'clear')
        specification_answer = pmt.prompt(specification_question)

        if specification_answer['enter_specifications']:
            # If the user wants to enter specifications, call the method
            Generator.__get_project_specifications()

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

        os.system('cls' if os.name in ('nt', 'dos') else 'clear')
        answers = pmt.prompt(questions)

        choice = answers['menu_choice']

    @staticmethod
    def __get_project_specifications() -> None:
        Generator.project_specification = Prompter.prompt_user_for_project_specification()

    @staticmethod
    def __generate_model_codes() -> None:
        pass

    @staticmethod
    def __generate_converter_methods() -> None:
        pass

    @staticmethod
    def __generate_importer_methods() -> None:
        pass

import os

import pyperclip
from inquirer2 import prompt as pmt

from models.dms_type import DMSType
from models.model_code import ModelCode
from prompter.prompter import Prompter


class Generator:
    project_specification = {}
    depth = 0
    __type_mapping = {
        'bool': '01',
        'int': '03',
        'long': '04',
        'float': '05',
        'double': '06',
        'string': '07',
        'datetime': '08',
        'ref': '09',
        'reflist': '19',
        'enum': '0a'
    }
    __dms_types_code = ''
    __model_codes_code = ''
    __model_defines_code = ''

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

        Generator.__main_menu()

    @staticmethod
    def __main_menu() -> None:
        while True:
            questions = [
                {
                    'type': 'list',
                    'name': 'menu_choice',
                    'message': 'Select an option:',
                    'choices': [
                        'Set Project Specification',
                        'Generate Model Defines',
                        'Generate Converter Methods',
                        'Generate Importer Methods',
                    ],
                },
            ]

            os.system('cls' if os.name in ('nt', 'dos') else 'clear')
            answers = pmt.prompt(questions)

            choice = answers['menu_choice']

            if choice == 'Set Project Specification':
                Generator.__get_project_specifications()
            elif choice == 'Generate Model Defines':
                Generator.__generate_model_defines()
                pyperclip.copy(Generator.__model_defines_code)
                print(Generator.__model_defines_code)
                input()
            elif choice == 'Generate Converter Methods':
                Generator.__generate_converter_methods()
            elif choice == 'Generate Importer Methods':
                Generator.__generate_importer_methods()

    @staticmethod
    def __get_project_specifications() -> None:
        Generator.project_specification = Prompter.prompt_user_for_project_specification()

    @staticmethod
    def __generate_class_inheritance_values():
        # Create an empty dictionary to represent the tree structure
        inheritance_tree = {}

        # Populate the tree based on the inheritance relationships
        for class_name, properties in Generator.project_specification.items():
            inheritance = [prop[0] for prop in properties if prop[1] == 'inheritance' and prop[1][1] != '']
            if inheritance:
                parent_class = inheritance[0]
                if parent_class not in inheritance_tree:
                    inheritance_tree[parent_class] = []
                inheritance_tree[parent_class].append(class_name)

        def get_text_value():
            ret_val = ''
            for value in values:
                ret_val += value.__str__()
            return ret_val

        # Create a dictionary to store the calculated values for each class
        class_values = {}
        values = [0, 0, 0, 0, 0, 0, 0, 0]

        # Function to recursively assign values based on inheritance
        def assign_values(node):
            values[Generator.depth] += 1
            class_values[node] = get_text_value()
            children = inheritance_tree.get(node, [])
            # Print out formated class inheritance values
            # print(f'{" " * Generator.depth}{node.ljust(30 - Generator.depth)} = {get_text_value()}')
            for child in children:
                Generator.depth += 1
                assign_values(child)
            if values[Generator.depth + 1] > 0:
                values[Generator.depth + 1] = 0
            Generator.depth -= 1

        # Start assigning values from the root (the class with an empty string as inheritance)
        assign_values('IdentifiedObject')

        return class_values

    @staticmethod
    def __generate_dms_types() -> list[DMSType]:
        mask_type_str = f"{'MASK_TYPE': <45}"
        dms_types_code = '\tpublic enum DMSType : short\n\t{\n\t\t' + mask_type_str + '= unchecked((short)0xFFFF),\n{{dms_types}}\n\t}'
        dms_types_code_body = ''

        dms_types = []
        concrete_class_counter = 1

        for class_name, properties in Generator.project_specification.items():
            if properties.__contains__(('concrete', 'type')):
                new_dms_type = DMSType(class_name, concrete_class_counter)
                dms_types.append(new_dms_type)
                dms_types_code_body += f'\n\t\t{new_dms_type.__str__()}'
                concrete_class_counter += 1

        dms_types_code = dms_types_code.replace('{{dms_types}}', dms_types_code_body)
        Generator.__dms_types_code = dms_types_code
        return dms_types

    @staticmethod
    def __generate_model_defines() -> list:
        model_codes_code = '\t[Flags]\n\tpublic enum ModelCode : long\n\t{{{model_codes}}\n\t}'
        model_codes_code_body = ''
        model_codes = []
        dms_types = Generator.__generate_dms_types()
        class_inheritances = Generator.__generate_class_inheritance_values()

        for class_name, properties in Generator.project_specification.items():
            if dms_types.__contains__(DMSType(class_name)):
                dms_type = [x.get_value() for x in dms_types if x.name == class_name][0]
            else:
                dms_type = '0000'

            class_model_code = ModelCode(class_name, class_inheritances[class_name], dms_type, '00', '00')
            model_codes.append(class_model_code)
            model_codes_code_body += f'\n\t\t{class_model_code.__str__()},' if class_name == 'IdentifiedObject' else f'\n\n\t\t{class_model_code.__str__()},'

            property_serial_number = 0
            attribute_index = lambda: hex(property_serial_number)[-2:].replace("x", "0")
            for property_name, property_type in properties:
                # Skip 'inheritance' and 'type' properties
                if property_type in ['inheritance', 'type']:
                    continue

                property_serial_number += 1
                property_model_code = ModelCode(class_name, class_inheritances[class_name], dms_type, attribute_index(),
                                                Generator.__type_mapping.get(property_type, '0a'), property_name)
                model_codes.append(property_model_code)
                model_codes_code_body += f'\n\t\t{property_model_code.__str__()},'

        model_codes_code = model_codes_code.replace('{{model_codes}}', model_codes_code_body)
        Generator.__model_codes_code = model_codes_code
        Generator.__model_defines_code = f'{Generator.__dms_types_code}\n\n{Generator.__model_codes_code}'
        return model_codes

    @staticmethod
    def __generate_converter_methods() -> None:
        pass

    @staticmethod
    def __generate_importer_methods() -> None:
        pass

import os
import string
from datetime import datetime, timedelta
from random import randint, uniform, choice, sample

import pyperclip
from inquirer2 import prompt as pmt

from common.constants.templates import XML_FILE_TEMPLATE
from common.enums.enums import enums
from common.models.concrete_class_data_point import ConcreteClassDataPoint
from common.models.dms_type import DMSType
from common.models.model_code import ModelCode
from common.models.models import transform_properties
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
    __reference_property_names_map = {
        'RegularTimePoint_IntervalSchedule': 'RegularIntervalSchedule',
        'IrregularTimePoint_IntervalSchedule': 'IrregularIntervalSchedule',
    }
    __dms_types_code = ''
    __model_codes_code = ''
    __model_defines_code = ''
    __xml_data_code = ''

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
                        'Generate XML data',
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
            elif choice == 'Generate XML data':
                Generator.__generate_xml_data()
                pyperclip.copy(Generator.__xml_data_code)
                print(Generator.__xml_data_code)
                input()
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
        Generator.transformed_project_specification = transform_properties(Generator.project_specification)
        concrete_classes = {class_name: class_attribues for class_name, class_attribues in
                            Generator.project_specification.items() if
                            class_attribues[1][0] == 'concrete'}
        Generator.transformed_concrete_classes = transform_properties(concrete_classes)

    # <editor-fold desc="MODEL DEFINES GENERATION">

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
    def __generate_model_defines() -> None:
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

    # </editor-fold>

    # <editor-fold desc="XML DATA GENERATION">

    @staticmethod
    def __get_parent_classes(class_name: str, parent_classes=None) -> list:
        if parent_classes is None:
            parent_classes = []

        parent_class = [cls_props['inheritance'] for cls_name, cls_props in
                        Generator.transformed_project_specification.items() if cls_name == class_name][0]

        if parent_class != '':
            Generator.__get_parent_classes(parent_class, parent_classes)

        parent_classes.append(class_name)

        return parent_classes

    @staticmethod
    def __get_all_class_properties(class_name: str) -> list:
        parent_classes = Generator.__get_parent_classes(class_name)
        class_properties = []

        for parent_class in parent_classes:
            parent_class_properties = {prop: type_ for prop, type_ in
                                       Generator.transformed_project_specification[parent_class].items() if
                                       prop not in ['type', 'inheritance', 'gid']}

            for prop, type_ in parent_class_properties.items():
                property_data_point = {
                    'class_name': parent_class,
                    'property_name': prop,
                    'type': type_
                }
                class_properties.append(property_data_point)

        return class_properties

    @staticmethod
    def __generate_properties_value(class_property: dict):
        type_ = class_property.get('type')

        if type_ in ['int']:
            return randint(1, 10)
        elif type_ in ['float', 'double']:
            return round(uniform(1, 10), 1)
        elif type_ == 'string':
            return ''.join(choice(string.ascii_letters) for _ in range(randint(5, 10)))
        elif type_ == 'bool':
            return choice([True, False])
        elif type_ == 'datetime':
            return (datetime.now() + timedelta(days=randint(1, 365))).strftime('%Y-%m-%dT%H:%M:%S')
        elif type_ == 'ref':
            try:
                return sample(Generator.concrete_classes_ids[class_property['property_name']], 1)[0]
            except KeyError:
                try:
                    return sample(Generator.concrete_classes_ids[Generator.__reference_property_names_map[
                        f'{class_property["class_name"]}_{class_property["property_name"]}']], 1)[0]
                except KeyError:
                    err_msg = f"[ERROR]: Coudln't find a reference for {class_property['class_name']}_{class_property['property_name']}."
                    err_msg += f" Recommended action is to potentually expand the __reference_property_names_map."
                    print(err_msg)
                    return err_msg
        elif type_ == 'reflist':
            return ''
        else:  # enum
            try:
                return choice(enums[type_])
            except KeyError:
                err_msg = f"[ERROR]: Coudln't find enum {class_property['class_name']}_{class_property['property_name']}. (Enum: {type_})"
                err_msg += f" Recommended action is to potentually expand the enums dictionary."
                print(err_msg)
                return err_msg

    @staticmethod
    def __generate_class_properties_data(class_properties: list, instance_id: str) -> str:
        class_properties_code = ''
        for prop in class_properties:
            value = Generator.__generate_properties_value(prop)
            prop_code = ''

            if prop['type'] == 'reflist':
                if prop['class_name'] in Generator.concrete_classes_ids:
                    Generator.concrete_classes_ids[prop['class_name']].add(instance_id)
                else:
                    Generator.concrete_classes_ids[prop['class_name']] = {instance_id}
                continue
            elif prop['type'] == 'ref':
                prop_code = f'\t\t<cim:{prop["class_name"]}.{prop["property_name"]} rdf:resource="#{value}"/>'
            else:
                prop_code = f'\t\t<cim:{prop["class_name"]}.{prop["property_name"]}>{value}</cim:{prop["class_name"]}.{prop["property_name"]}>'

            if class_properties_code:
                prop_code = f'\n{prop_code}'
            class_properties_code += prop_code

        return class_properties_code

    @staticmethod
    def __generate_xml_data() -> None:
        data_points_count = int(
            Prompter.prompt_numeric_question('Concrete data generation', 'How many data points do you want per class')[
                'Concrete data generation'])
        os.system('cls' if os.name in ('nt', 'dos') else 'clear')

        xml_code = XML_FILE_TEMPLATE
        xml_data_code = ''

        for class_name, class_attr in Generator.transformed_concrete_classes.items():
            xml_data_code += f'\n\n\t<!-- {class_name} -->'
            class_properties = Generator.__get_all_class_properties(class_name)

            for data_point in range(data_points_count):
                concrete_data_point = ConcreteClassDataPoint(randint(10 ** 9, (10 ** 10) - 1), class_name)
                data_code = Generator.__generate_class_properties_data(class_properties, concrete_data_point.id)
                concrete_data_point.code = concrete_data_point.code.replace('{{class_data}}', data_code)
                xml_data_code += concrete_data_point.code

        xml_code = xml_code.replace('{{data}}', xml_data_code)
        Generator.__xml_data_code = xml_code
        return

    # </editor-fold>

    # <editor-fold desc="CONVERTER METHODS GENERATION">

    @staticmethod
    def __generate_converter_methods() -> None:
        pass

    # </editor-fold>

    # <editor-fold desc="IMPORTER METHODS GENERATION">

    @staticmethod
    def __generate_importer_methods() -> None:
        pass

    # </editor-fold>

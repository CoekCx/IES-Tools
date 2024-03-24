import os
import string
from datetime import datetime, timedelta
from random import randint, uniform, choice, sample

import pyperclip
from inquirer2 import prompt as pmt
import tkinter as tk
from tkinter import filedialog

from common.constants.templates import *
from common.enums.enums import enums
from common.models.concrete_class_data_point import ConcreteClassDataPoint
from common.models.dms_type import DMSType
from common.models.model_code import ModelCode
from common.models.models import transform_properties, transformed_models
from data_manager.data_manager import DataManager
from prompter.prompter import Prompter


class Generator:
    project_specification = {}
    transformed_project_specification = {}
    transformed_concrete_classes = {}
    concrete_classes_ids = {}
    project_enums = []
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
    __reference_property_model_code_names_map = {
        'REGULARTIMEPOINT_REGULARINTERVALSCHEDULE': 'REGULARTIMEPOINT_INTERVALSCHEDULE',
        'IRREGULARTIMEPOINT_IRREGULARINTERVALSCHEDULE': 'IRREGULARTIMEPOINT_INTERVALSCHEDULE',
    }
    __namespace = ''
    __dll_file_prefix = ''
    __depth = 0
    __dms_types_code = ''
    __property_model_codes = {}
    __class_model_codes = []
    __model_codes_code = ''
    __model_defines_code = ''
    __enums_code = ''
    __xml_data_code = ''
    __converter_methods_code = ''
    __import_methods_code = ''
    server_classes_codes = {}

    @staticmethod
    def start_app() -> None:
        Generator.__set_project_specification()
        Generator.__generate_xml_data(1)  # need to call this so that we can scan all the project enums
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
                        'Generate Enumes',
                        'Generate XML data',
                        'Generate Converter Methods',
                        'Generate Importer Methods',
                        'Generate Server Classes',
                        'Generate Server Enum Classes',
                        'Back',
                    ],
                },
            ]

            os.system('cls' if os.name in ('nt', 'dos') else 'clear')
            answers = pmt.prompt(questions)

            choice = answers['menu_choice']

            if choice == 'Set Project Specification':
                Generator.__set_project_specification()
            elif choice == 'Generate Model Defines':
                Generator.__generate_model_defines()
            elif choice == 'Generate Enumes':
                Generator.__generate_enums()
            elif choice == 'Generate XML data':
                Generator.__generate_xml_data()
            elif choice == 'Generate Converter Methods':
                Generator.__generate_converter_methods()
            elif choice == 'Generate Importer Methods':
                Generator.__generate_importer_methods()
            elif choice == 'Generate Server Classes':
                Generator.__generate_server_classes()
            elif choice == 'Generate Server Enum Classes':
                Generator.__generate_server_enums()
            elif choice == 'Back':
                break

    # <editor-fold desc="PROJECT SETUP">

    @staticmethod
    def __set_project_specification():
        specification_question = [
            {
                'type': 'list',
                'name': 'specification_choice',
                'message': 'Select an option:',
                'choices': [
                    'Enter Specifications',
                    'Load Specifications',
                    'Back',
                ],
            },
        ]

        os.system('cls' if os.name in ('nt', 'dos') else 'clear')
        specification_answer = pmt.prompt(specification_question)['specification_choice']

        if specification_answer == 'Enter Specifications':
            Generator.__get_environment_variables()
            Generator.__get_project_specifications(True)
            Generator.__detect_project_enums()
        elif specification_answer == 'Load Specifications':
            Generator.__get_environment_variables()
            Generator.__get_project_specifications(False)
            Generator.__detect_project_enums()
        elif specification_answer == 'Back':
            return

    @staticmethod
    def __get_environment_variables() -> None:
        Generator.__namespace, Generator.__dll_file_prefix = Prompter.prompt_user_for_environment_varialbes()

    @staticmethod
    def __get_project_specifications(manual_entry) -> None:
        if manual_entry:
            Generator.project_specification = Prompter.prompt_user_for_project_specification()
        else:
            Generator.project_specification = DataManager.select_specification_json_data()
        Generator.transformed_project_specification = transform_properties(Generator.project_specification)
        concrete_classes = {class_name: class_attribues for class_name, class_attribues in
                            Generator.project_specification.items() if
                            class_attribues[0][0] == 'concrete'}
        Generator.transformed_concrete_classes = transform_properties(concrete_classes)

    @staticmethod
    def __detect_project_enums():
        for class_name, class_attr in Generator.transformed_concrete_classes.items():
            class_properties = Generator.__get_all_class_properties(class_name)
            concrete_data_point = ConcreteClassDataPoint(randint(10 ** 9, (10 ** 10) - 1), class_name)
            Generator.__generate_class_properties_data(class_properties, concrete_data_point.id)

    # </editor-fold>

    # <editor-fold desc="MODEL DEFINES GENERATION">

    @staticmethod
    def __generate_class_inheritance_values():
        # Create an empty dictionary to represent the tree structure
        inheritance_tree = {}

        # Populate the tree based on the inheritance relationships
        for class_name, properties in Generator.project_specification.items():
            parent_class = transformed_models[class_name]['inheritance']
            if parent_class != '':
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
            values[Generator.__depth] += 1
            class_values[node] = get_text_value()
            children = inheritance_tree.get(node, [])
            # Print out formated class inheritance values
            # print(f'{" " * Generator.depth}{node.ljust(30 - Generator.depth)} = {get_text_value()}')
            for child in children:
                Generator.__depth += 1
                assign_values(child)
            if values[Generator.__depth + 1] > 0:
                values[Generator.__depth + 1] = 0
            Generator.__depth -= 1

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
                dms_types_code_body += f'\n\t\t{new_dms_type.__str__()},'
                concrete_class_counter += 1

        dms_types_code = dms_types_code.replace('{{dms_types}}', dms_types_code_body)
        Generator.__dms_types_code = dms_types_code
        return dms_types

    @staticmethod
    def __generate_model_defines() -> None:
        model_codes_code = '\t[Flags]\n\tpublic enum ModelCode : long\n\t{{{model_codes}}\n\t}'
        model_codes_code_body = ''
        class_model_codes = []
        property_model_codes = {}
        dms_types = Generator.__generate_dms_types()
        class_inheritances = Generator.__generate_class_inheritance_values()

        for class_name, properties in Generator.project_specification.items():
            if dms_types.__contains__(DMSType(class_name)):
                dms_type = [x.get_value() for x in dms_types if x.name == class_name][0]
            else:
                dms_type = '0000'

            class_model_code = ModelCode(class_name, class_inheritances[class_name], dms_type, '00', '00')
            class_model_codes.append(class_model_code)
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
                class_property_name = Generator.get_property_model_code_name(class_name, property_name)
                property_model_codes[class_property_name] = property_model_code
                model_codes_code_body += f'\n\t\t{property_model_code.__str__()},'

        model_codes_code = model_codes_code.replace('{{model_codes}}', model_codes_code_body)
        Generator.__class_model_codes = class_model_codes
        Generator.__property_model_codes = property_model_codes
        Generator.__model_codes_code = model_codes_code
        Generator.__model_defines_code = f'{Generator.__dms_types_code}\n\n{Generator.__model_codes_code}'
        pyperclip.copy(Generator.__model_defines_code)

    # </editor-fold>

    # <editor-fold desc="MODEL ENUMES">

    @staticmethod
    def __generate_enums() -> None:
        enums_code = ''
        for enum_name in Generator.project_enums:
            if enums_code != '':
                enums_code += '\n\n'

            enum_code = ENUM_CODE_TEMPLATE.replace('{{enum_name}}', enum_name)
            enum_options = ''
            options_counter = 0
            for option in enums[enum_name]:
                if enum_options != '':
                    enum_options += '\n'

                enum_options += ENUM_OPTION_TEMPLATE \
                    .replace('{{option_name}}', option).replace('{{index}}', str(options_counter))
                options_counter += 1
            enum_code = enum_code.replace('{{options}}', enum_options)
            enums_code += enum_code
        Generator.__enums_code = enums_code
        pyperclip.copy(Generator.__enums_code)

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
                if type_ not in Generator.project_enums:
                    Generator.project_enums.append(type_)
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
    def __generate_xml_data(data_points: int = 0) -> None:
        Generator.concrete_classes_ids = {}
        data_points_count = int(
            Prompter.prompt_numeric_question('Concrete data generation', 'How many data points do you want per class')[
                'Concrete data generation']) if data_points == 0 else 1
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
        if data_points == 0:
            Generator.__xml_data_code = xml_code
            pyperclip.copy(Generator.__xml_data_code)

    # </editor-fold>

    # <editor-fold desc="CONVERTER METHODS GENERATION">

    @staticmethod
    def __class_has_ref(class_name: str) -> bool:
        return any(value == 'ref' for value in Generator.transformed_project_specification[class_name].values())

    @staticmethod
    def __get_class_parent(class_name: str) -> str:
        return [value for key, value in Generator.transformed_project_specification[class_name].items() if
                key == 'inheritance'][0]

    @staticmethod
    def __get_model_code_by_class_property(class_property_name: str) -> ModelCode:
        return Generator.__property_model_codes.get(class_property_name, None)

    @staticmethod
    def __generate_class_converter_method_properties_code(class_name: str, class_attributes: dict) -> str:
        parent_class = Generator.__get_class_parent(class_name)
        count_reflist = sum(1 for value in class_attributes.values() if value == 'reflist')
        properties_code = '\n' if len(class_attributes) > 2 + count_reflist and parent_class != '' else ''

        for attr, type_ in class_attributes.items():
            attr_model_code = f'{class_name.upper()}_{attr.upper()}'
            capitalized_attr = Generator.capitalize_attr(attr)
            if type_ in ['int', 'float', 'double', 'string', 'bool', 'datetime']:
                properties_code += PROPERTY_CODE_TEMPLATE.replace('{{class_name}}', class_name) \
                    .replace('{{property_name}}', capitalized_attr).replace('{{property_model_code}}',
                                                                            attr_model_code)
            elif type_ == 'ref':
                properties_code += REFERENCE_PROPERTY_CODE_TEMPLATE.replace('{{class_name}}', class_name) \
                    .replace('{{property_name}}', capitalized_attr).replace('{{property_model_code}}',
                                                                            attr_model_code)
            elif type_ in ['reflist'] or attr in ['inheritance', 'type', 'gid']:
                continue
            else:  # enum
                ret_val = ENUM_PROPERTY_CODE_TEMPLATE
                ret_val = ret_val.replace('{{class_name}}', class_name)
                ret_val = ret_val.replace('{{property_name}}', capitalized_attr)
                ret_val = ret_val.replace('{{property_model_code}}', attr_model_code)
                ret_val = ret_val.replace('{{enum_name}}', type_)
                properties_code += ret_val

        return properties_code

    @staticmethod
    def __generate_populate_methods() -> str:
        class_codes = ''
        for class_name, class_attributes in Generator.transformed_project_specification.items():
            class_code = '\n\n' if class_name != 'IdentifiedObject' else ''
            class_code += POPULATE_CLASS_PROPERTIES_METHOD_TEMPLATE \
                .replace('{{class_name}}', class_name).replace('{{namespace}}', Generator.__namespace)

            class_has_ref = Generator.__class_has_ref(class_name)
            if class_has_ref:
                class_code = class_code.replace('{{reference_parameters}}', REFERENCE_PARAMETERS_TEMPLATE)
            else:
                class_code = class_code.replace('{{reference_parameters}}', '')

            # inheritance method call
            parent_class = Generator.__get_class_parent(class_name)
            if parent_class != '':
                parent_method_call = INHERITANCE_METHOD_CALL_TEMPLATE.replace('{{parent_class}}', parent_class).replace(
                    '{{class_name}}', class_name)
                parent_class_has_ref = Generator.__class_has_ref(parent_class)
                if parent_class_has_ref:
                    parent_method_call = parent_method_call.replace('{{reference_parameters}}',
                                                                    INHERITANCE_REFERENCE_PARAMETERS)
                else:
                    parent_method_call = parent_method_call.replace('{{reference_parameters}}', '')

                class_code = class_code.replace('{{inheritance_class_method}}', parent_method_call)
            else:
                class_code = class_code.replace('{{inheritance_class_method}}', '')

            class_properties_code = Generator.__generate_class_converter_method_properties_code(class_name,
                                                                                                class_attributes)
            class_code = class_code.replace('{{properties}}', class_properties_code)
            class_codes += class_code

        return class_codes

    @staticmethod
    def __generate_get_dms_method_cases(enum_name: str) -> str:
        values = enums.get(enum_name, None)
        if not values:
            err_msg = f"[ERROR]: Coudln't find enum: {enum_name}."
            err_msg += f" Recommended action is to potentually expand the enums dictionary."
            return err_msg

        cases_code = ''
        for value in values:
            case_code = '\n' if cases_code != '' else ''
            case_code += GET_DMS_ENUM_CASE_TEMPLATE
            case_code = case_code.replace('{{namespace}}', Generator.__namespace)
            case_code = case_code.replace('{{enum_name}}', enum_name)
            case_code = case_code.replace('{{enum_value}}', value)
            cases_code += case_code

        return cases_code

    @staticmethod
    def __generate_get_dms_methods() -> str:
        if len(Generator.project_enums) == 0:
            return ''

        methods_code = ''
        for enum_name in Generator.project_enums:
            enum_var_name = enum_name[0].lower() + enum_name[1:]
            method_code = '\n\n' if methods_code != '' else ''
            method_code += GET_DMS_ENUM_METHOD_TEMPLATE
            method_cases_code = Generator.__generate_get_dms_method_cases(enum_name)
            method_code = method_code.replace('{{enum_name}}', enum_name)
            method_code = method_code.replace('{{namespace}}', Generator.__namespace)
            method_code = method_code.replace('{{var_enum_name}}', enum_var_name)
            method_code = method_code.replace('{{cases}}', method_cases_code)
            methods_code += method_code

        return methods_code

    @staticmethod
    def __generate_converter_methods() -> None:
        convreter_methods_code = CONVERTER_METHODS_CODE_TEMPLATE
        popualate_methods_code = Generator.__generate_populate_methods()
        get_dms_enum_methods_code = Generator.__generate_get_dms_methods()
        convreter_methods_code = convreter_methods_code.replace('{{populate_methods}}', popualate_methods_code)
        convreter_methods_code = convreter_methods_code.replace('{{enums_methods}}', get_dms_enum_methods_code)
        Generator.__converter_methods_code = convreter_methods_code
        pyperclip.copy(convreter_methods_code)

    # </editor-fold>

    # <editor-fold desc="IMPORTER METHODS GENERATION">

    @staticmethod
    def __generate_import_methods_calls_function() -> str:
        import_methods_calls_function_code = IMPORT_METHOD_CALLS_FUNCTION_TEMPLATE
        import_function_calls_code = ''

        for class_name, attribues in Generator.transformed_concrete_classes.items():
            import_function_call_code = '\n' if import_function_calls_code != '' else ''
            import_function_call_code += IMPORT_METHOD_CALL_TEMPLATE.replace('{{class_name}}', class_name)
            import_function_calls_code += import_function_call_code

        import_methods_calls_function_code = import_methods_calls_function_code.replace('{{import_calls}}',
                                                                                        import_function_calls_code)
        return import_methods_calls_function_code

    @staticmethod
    def __generate_importer_methods_pair_for_class(class_name: str) -> str:
        import_class_method_pair_code = IMPORT_CLASS_METHOD_PAIR
        import_class_method_code = IMPORT_CLASS_METHOD_TEMPLATE.replace('{{class_name}}', class_name) \
            .replace('{{namespace}}', Generator.__namespace)
        create_class_descriptio_method_code = CREATE_CLASS_DESCRIPTION_METHOD_TEMPLATE \
            .replace('{{class_name}}', class_name).replace('{{model_code_name}}', class_name.upper()) \
            .replace('{{namespace}}', Generator.__namespace)
        create_class_descriptio_method_code = create_class_descriptio_method_code.replace(
            '{{reference_parameters}}',
            INHERITANCE_REFERENCE_PARAMETERS if Generator.__class_has_ref(class_name) else '')
        import_class_method_pair_code = import_class_method_pair_code \
            .replace('{{import_method}}', import_class_method_code) \
            .replace('{{create_description_method}}', create_class_descriptio_method_code)
        return import_class_method_pair_code

    @staticmethod
    def __generate_importer_methods() -> None:
        import_methods_code = IMPORT_METHODS_CODE_TEMPLATE
        import_methods_calls_function_code = Generator.__generate_import_methods_calls_function()

        import_class_methods_code = ''
        for class_name, attribues in Generator.transformed_concrete_classes.items():
            importer_method_pair_code = Generator.__generate_importer_methods_pair_for_class(class_name)
            if import_class_methods_code != '':
                importer_method_pair_code = '\n\n' + importer_method_pair_code
            import_class_methods_code += importer_method_pair_code

        import_methods_code = import_methods_code.replace('{{import_methods_calls_function}}',
                                                          import_methods_calls_function_code)
        import_methods_code = import_methods_code.replace('{{import_methods}}', import_class_methods_code)

        Generator.__import_methods_code = import_methods_code
        pyperclip.copy(import_methods_code)

    # </editor-fold>

    # <editor-fold desc="SEVER CLASSES GENERATION">

    @staticmethod
    def __generate_server_classes() -> None:
        Generator.server_classes_codes = {}
        classes_folder_path = Generator.select_folder()

        for class_name, attributes in Generator.transformed_project_specification.items():
            if class_name == 'IdentifiedObject':
                Generator.server_classes_codes[class_name] = IDENTIFIED_OBJECT_CLASS_CODE
                Generator.create_file(classes_folder_path, 'IdentifiedObject', IDENTIFIED_OBJECT_CLASS_CODE)
                continue

            # properties code
            parent_class_name = Generator.__get_class_parent(class_name)
            server_class_code = SERVER_CLASS_TEMPLATE.replace('{{class_name}}', class_name) \
                .replace('{{parent_class_name}}', parent_class_name)
            properties_code = '' if len(attributes) <= 2 else '\n'
            for attribute_key, attribute_value in attributes.items():
                if attribute_key in ['type', 'inheritance']:
                    continue

                if properties_code != '\n':
                    properties_code += '\n'
                capitalizes_attribute_key = Generator.capitalize_attr(attribute_key)
                property_code = SERVER_CLASS_PROPERTY_TEMPLATE
                if attribute_value not in ['ref', 'reflist']:
                    if attribute_value == 'datetime':
                        property_code = property_code.replace('{{prop_type}}', 'DateTime') \
                            .replace('{{prop_name}}', capitalizes_attribute_key)
                    else:
                        property_code = property_code.replace('{{prop_type}}', attribute_value) \
                            .replace('{{prop_name}}', capitalizes_attribute_key)
                elif attribute_value == 'ref':
                    property_code = property_code.replace('{{prop_type}}', 'long') \
                        .replace('{{prop_name}}', capitalizes_attribute_key)
                elif attribute_value == 'reflist':
                    property_code = SERVER_CLASS_REFLIST_PROPERTY_TEMPLATE.replace('{{prop_name}}',
                                                                                   capitalizes_attribute_key)

                properties_code += property_code
            server_class_code = server_class_code.replace('{{properties}}', properties_code)

            # IAccess region code
            iaccess_region_code = IACCESS_IMPLEMENTATION_CODE_TEMPLATE

            # HasProperty
            has_property_code = HAS_PROPERTY_CODE_TEMPLATE
            has_property_cases_code = HAS_PROPERTY_CASES_CODE_TEMPLATE if len(attributes) > 2 else ''
            if len(attributes) > 2:
                has_property_inner_cases_code = ''
                for attribute_key, attribute_value in attributes.items():
                    if attribute_key in ['type', 'inheritance']:
                        continue

                    if has_property_inner_cases_code != '':
                        has_property_inner_cases_code += '\n'
                    has_property_case_code = HAS_PROPERTY_CASE_CODE_TEMPLATE.replace(
                        '{{prop_model_code}}', Generator.get_property_model_code_name(class_name, attribute_key))
                    has_property_inner_cases_code += has_property_case_code
                has_property_cases_code = has_property_cases_code.replace('{{cases_code}}',
                                                                          has_property_inner_cases_code)
            has_property_code = has_property_code.replace('{{cases_code}}', has_property_cases_code)
            iaccess_region_code = iaccess_region_code.replace('{{has_property_code}}', has_property_code)

            # GetProperty
            get_property_code = GET_PROPERTY_CODE_TEMPLATE
            get_property_cases_code = ''
            if len(attributes) > 2:  # has properties
                get_property_cases_code += '\n'
                for attribute_key, attribute_value in attributes.items():
                    if attribute_key in ['type', 'inheritance']:
                        continue

                    if get_property_cases_code != '':
                        get_property_cases_code += '\n\n'
                    capitalizes_attribute_key = Generator.capitalize_attr(attribute_key)
                    if attribute_value in Generator.project_enums:
                        get_property_case_code = GET_ENUM_PROPERTY_CASE_CODE_TEMPLATE.replace(
                            '{{prop_model_code}}', Generator.get_property_model_code_name(class_name, attribute_key)) \
                            .replace('{{prop_name}}', capitalizes_attribute_key)
                    else:
                        get_property_case_code = GET_PROPERTY_CASE_CODE_TEMPLATE.replace(
                            '{{prop_model_code}}', Generator.get_property_model_code_name(class_name, attribute_key)) \
                            .replace('{{prop_name}}', capitalizes_attribute_key)

                    get_property_cases_code += get_property_case_code

            if len(attributes) > 2:  # has properties
                get_property_cases_code += '\n\n'
            get_property_code = get_property_code.replace('{{cases_code}}', get_property_cases_code)
            iaccess_region_code = iaccess_region_code.replace('{{get_property_code}}', get_property_code)

            # SetProperty
            set_property_code = SET_PROPERTY_CODE_TEMPLATE
            set_property_cases_code = ''
            if len(attributes) > 2:  # has properties
                set_property_cases_code += '\n'
                for attribute_key, attribute_value in attributes.items():
                    if attribute_key in ['type', 'inheritance']:
                        continue

                    if set_property_cases_code != '\n':
                        set_property_cases_code += '\n\n'
                    capitalizes_attribute_key = Generator.capitalize_attr(attribute_key)
                    capitalizes_attribute_value = Generator.capitalize_attr(attribute_value)
                    set_property_case_code = SET_PROPERTY_CASE_CODE_TEMPLATE.replace(
                        '{{prop_model_code}}', Generator.get_property_model_code_name(class_name, attribute_key)) \
                        .replace('{{prop_name}}', capitalizes_attribute_key)
                    if attribute_value in ['bool', 'float', 'int', 'string']:
                        set_property_case_code = set_property_case_code.replace('{{prop_type}}',
                                                                                capitalizes_attribute_value)
                    elif attribute_value == 'datetime':
                        set_property_case_code = set_property_case_code.replace('{{prop_type}}', 'DateTime')
                    elif attribute_value == 'ref':
                        set_property_case_code = set_property_case_code.replace('{{prop_type}}', 'Long')
                    elif attribute_value == 'reflist':
                        set_property_case_code = set_property_case_code.replace('{{prop_type}}', 'Longs')
                    else:
                        set_property_case_code = SET_PROPERTY_ENUM_CASE_CODE_TEMPLATE \
                            .replace('{{prop_model_code}}',
                                     Generator.get_property_model_code_name(class_name, attribute_key)) \
                            .replace('{{prop_name}}', capitalizes_attribute_key) \
                            .replace('{{enum_name}}', capitalizes_attribute_value)

                    set_property_cases_code += set_property_case_code

            if len(attributes) > 2:  # has properties
                set_property_cases_code += '\n\n'
            set_property_code = set_property_code.replace('{{cases_code}}', set_property_cases_code)
            iaccess_region_code = iaccess_region_code.replace('{{set_property_code}}', set_property_code)

            server_class_code = server_class_code.replace('{{iaccess_implementation}}', iaccess_region_code)

            # IReference region code
            this_class_has_reflist = Generator.class_contains_reflist(class_name)
            this_class_has_ref = Generator.class_contains_ref(class_name)
            ireference_region_code = IREFERENCE_IMPLEMENTATION_CODE_TEMPLATE

            if not this_class_has_reflist and not this_class_has_ref:
                server_class_code = server_class_code.replace('{{ireference_implementation}}', '')
            else:
                if this_class_has_reflist:
                    reflists = Generator.get_class_reflists(class_name)

                    # is referenced
                    is_referenced_code = IS_REFERENCED_CODE_TEMPLATE
                    is_referenced_inner_code = ''
                    for reflist in reflists.keys():
                        if is_referenced_inner_code != '':
                            is_referenced_inner_code += ' && '
                        capitalized_reflist = Generator.capitalize_attr(reflist)
                        is_referenced_inner_code += IS_REFERENCED_INNER_CODE_TEMPLATE.replace('{{prop_name}}',
                                                                                              capitalized_reflist)
                    is_referenced_code = is_referenced_code.replace('{{is_referenced_inner_code}}',
                                                                    is_referenced_inner_code)
                    ireference_region_code = ireference_region_code.replace('{{is_referenced_code}}',
                                                                            is_referenced_code)

                    # add reference
                    add_reference_code = ADD_REFERENCE_CODE_TEMPLATE
                    cases_code = ''
                    for reflist in reflists.keys():
                        if cases_code != '':
                            cases_code += '\n'
                        capitalized_reflist = Generator.capitalize_attr(reflist)
                        cases_code += ADD_REFERENCE_CASE_CODE_TEMPLATE \
                            .replace('{{prop_name}}', capitalized_reflist) \
                            .replace('{{prop_model_code_name}}',
                                     Generator.get_property_model_code_name(reflist[:-1], class_name))
                    add_reference_code = add_reference_code.replace('{{cases_code}}', cases_code)
                    ireference_region_code = ireference_region_code.replace('{{add_reference_code}}',
                                                                            add_reference_code)

                    # remove reference
                    remove_reference_code = REMOVE_REFERENCE_CODE_TEMPLATE
                    cases_code = ''
                    for reflist in reflists.keys():
                        if cases_code != '':
                            cases_code += '\n'
                        capitalized_reflist = Generator.capitalize_attr(reflist)
                        cases_code += REMOVE_REFERENCE_CASE_CODE_TEMPLATE \
                            .replace('{{prop_name}}', capitalized_reflist) \
                            .replace('{{prop_model_code_name}}',
                                     Generator.get_property_model_code_name(reflist[:-1], class_name))
                    remove_reference_code = remove_reference_code.replace('{{cases_code}}', cases_code)
                    ireference_region_code = ireference_region_code.replace('{{remove_reference_code}}',
                                                                            remove_reference_code)
                else:
                    ireference_region_code = ireference_region_code \
                        .replace('{{is_referenced_code}}', '') \
                        .replace('{{add_reference_code}}', '') \
                        .replace('{{remove_reference_code}}', '')

                if this_class_has_ref:
                    refs = Generator.get_class_refs(class_name)

                    # get references
                    get_references_code = GET_REFERENCES_CODE_TEMPLATE
                    reference_codes = ''
                    for ref in refs.keys():
                        if reference_codes != '':
                            reference_codes += '\n'
                        capitalized_ref = Generator.capitalize_attr(ref)

                        reference_codes += GET_REFERENCES_REFERENCE_CODE_TEMPLATE \
                            .replace('{{prop_name}}', capitalized_ref) \
                            .replace('{{prop_model_code_name}}',
                                     Generator.get_property_model_code_name(class_name, ref))
                    get_references_code = get_references_code.replace('{{reference_codes}}', reference_codes)
                    ireference_region_code = ireference_region_code.replace('{{get_references_code}}',
                                                                            get_references_code)
                else:
                    ireference_region_code = ireference_region_code.replace('{{get_references_code}}', '')

                server_class_code = server_class_code.replace('{{ireference_implementation}}', ireference_region_code)

            Generator.server_classes_codes[class_name] = server_class_code
            Generator.create_file(classes_folder_path, class_name, server_class_code)
            # os.system('cls' if os.name in ('nt', 'dos') else 'clear')
            # pyperclip.copy(server_class_code)
            # print(f'Copied server class code for the class: {class_name}')
            # input()
            # os.system('cls' if os.name in ('nt', 'dos') else 'clear')
        os.system('cls' if os.name in ('nt', 'dos') else 'clear')
        print(f'Classes generated at: {classes_folder_path}')
        input()
        os.system('cls' if os.name in ('nt', 'dos') else 'clear')

    @staticmethod
    def __generate_server_enums() -> None:
        classes_folder_path = Generator.select_folder()

        for enum_name in Generator.project_enums:
            server_enum_code = SERVER_ENUM_TEMPLATE.replace('{{enum_name}}', enum_name)

            enum_values = ''
            for value in enums[enum_name]:
                if enum_values != '':
                    enum_values += '\n'
                enum_values += f'\t\t{"@" if value == "fixed" else ""}{value},'
            server_enum_code = server_enum_code.replace('{{enum_values}}', enum_values)
            Generator.create_file(classes_folder_path, enum_name, server_enum_code)

            # os.system('cls' if os.name in ('nt', 'dos') else 'clear')
            # pyperclip.copy(server_enum_code)
            # print(f'Copied server class code for the enum: {enum_name}')
            # input()
            # os.system('cls' if os.name in ('nt', 'dos') else 'clear')
        os.system('cls' if os.name in ('nt', 'dos') else 'clear')
        print(f'Classes generated at: {classes_folder_path}')
        input()
        os.system('cls' if os.name in ('nt', 'dos') else 'clear')

    # </editor-fold>

    # <editor-fold desc="FILE OPERATIONS">

    @staticmethod
    def create_file(folder_path, filename, content):
        file_path = f"{folder_path}/{filename}.cs"
        with open(file_path, 'w') as file:
            file.write(content)
        print(f"File '{file}.cs' created at: {file_path}")

    @staticmethod
    def select_folder():
        root = tk.Tk()
        root.withdraw()

        folder_path = filedialog.askdirectory(title="Select a Folder")
        return folder_path

    # </editor-fold>

    # <editor-fold desc="OTHER">

    capitalize_attr = lambda attr: attr[0].upper() + attr[1:] if attr != 'mRID' else attr.upper()

    @staticmethod
    def get_property_model_code_name(class_name, property_name):
        prop_model_code = f'{class_name.upper()}_{property_name.upper()}'
        adapted_model_code_name = Generator.__reference_property_model_code_names_map.get(prop_model_code, None)
        if adapted_model_code_name:
            return adapted_model_code_name
        return prop_model_code

    class_contains_reflist = lambda class_name: any(
        value == 'reflist' for value in Generator.transformed_project_specification.get(class_name, {}).values())

    class_contains_ref = lambda class_name: any(
        value == 'ref' for value in Generator.transformed_project_specification.get(class_name, {}).values())

    get_class_reflists = lambda class_name: {key: value for key, value in
                                             Generator.transformed_project_specification.get(class_name, {}).items() if
                                             value == 'reflist'}

    get_class_refs = lambda class_name: {key: value for key, value in
                                         Generator.transformed_project_specification.get(class_name, {}).items() if
                                         value == 'ref'}

    # </editor-fold>

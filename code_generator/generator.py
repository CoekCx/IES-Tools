import os
import string
import sys
from datetime import datetime, timedelta
from random import randint, uniform, choice, sample

import pyperclip
from inquirer2 import prompt as pmt

from common.constants.templates import XML_FILE_TEMPLATE, POPULATE_CLASS_PROPERTIES_METHOD_TEMPLATE, \
    REFERENCE_PARAMETERS_TEMPLATE, \
    INHERITANCE_METHOD_CALL_TEMPLATE, INHERITANCE_REFERENCE_PARAMETERS, PROPERTY_CODE_TEMPLATE, \
    REFERENCE_PROPERTY_CODE_TEMPLATE, \
    ENUM_PROPERTY_CODE_TEMPLATE, CONVERTER_METHODS_CODE_TEMPLATE, GET_DMS_ENUM_METHOD_TEMPLATE, \
    GET_DMS_ENUM_CASE_TEMPLATE, IMPORT_METHODS_CODE_TEMPLATE, IMPORT_METHOD_CALLS_FUNCTION_TEMPLATE, \
    IMPORT_METHOD_CALL_TEMPLATE, IMPORT_CLASS_METHOD_TEMPLATE, IMPORT_CLASS_METHOD_PAIR, \
    CREATE_CLASS_DESCRIPTION_METHOD_TEMPLATE
from common.enums.enums import enums
from common.models.concrete_class_data_point import ConcreteClassDataPoint
from common.models.dms_type import DMSType
from common.models.model_code import ModelCode
from common.models.models import transform_properties, transformed_models
from prompter.prompter import Prompter


class Generator:
    __project_specification = {}
    __transformed_project_specification = {}
    __transformed_concrete_classes = {}
    __concrete_classes_ids = {}
    __project_enums = []
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
    __namespace = ''
    __dll_file_prefix = ''
    __depth = 0
    __dms_types_code = ''
    __property_model_codes = {}
    __class_model_codes = []
    __model_codes_code = ''
    __model_defines_code = ''
    __xml_data_code = ''
    __converter_methods_code = ''
    __import_methods_code = ''

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
            Generator.__get_environment_variables()
            Generator.__get_project_specifications()
            Generator.__detect_project_enums()
        else:
            Generator.__namespace = 'FTN1'
            Generator.__dll_file_prefix = 'classes'
            Generator.__get_project_specifications(True)

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
                Generator.__get_environment_variables()
                Generator.__get_project_specifications()
                Generator.__detect_project_enums()
            elif choice == 'Generate XML data':
                Generator.__generate_xml_data()
            elif choice == 'Generate Model Defines':
                Generator.__generate_model_defines()
            elif choice == 'Generate Converter Methods':
                Generator.__generate_converter_methods()
            elif choice == 'Generate Importer Methods':
                Generator.__generate_importer_methods()

    # <editor-fold desc="PROJECT SETUP">

    @staticmethod
    def __get_environment_variables() -> None:
        Generator.__namespace, Generator.__dll_file_prefix = Prompter.prompt_user_for_environment_varialbes()

    @staticmethod
    def __get_project_specifications(autoset: bool = False) -> None:
        if autoset:
            Generator.__project_specification = {
                'IdentifiedObject': [('', 'inheritance'), ('abstract', 'type'), ('gid', 'long'), ('mRID', 'string'),
                                     ('aliasName', 'string'), ('name', 'string')],
                'Curve': [('IdentifiedObject', 'inheritance'), ('concrete', 'type'), ('CurveDatas', 'reflist'),
                          ('curveStyle', 'CurveStyle'), ('xMultiplier', 'UnitMultiplier'), ('xUnit', 'UnitSymbol'),
                          ('y1Multiplier', 'UnitMultiplier'), ('y1Unit', 'UnitSymbol'),
                          ('y2Multiplier', 'UnitMultiplier'), ('y2Unit', 'UnitSymbol'),
                          ('y3Multiplier', 'UnitMultiplier'), ('y3Unit', 'UnitSymbol')],
                'CurveData': [('IdentifiedObject', 'inheritance'), ('concrete', 'type'), ('Curve', 'ref'),
                              ('xvalue', 'float'), ('y1value', 'float'), ('y2value', 'float'), ('y3value', 'float')],
                'PowerSystemResource': [('IdentifiedObject', 'inheritance'), ('abstract', 'type'),
                                        ('OutageSchedules', 'reflist')],
                'Equipment': [('PowerSystemResource', 'inheritance'), ('abstract', 'type'), ('aggregate', 'bool'),
                              ('normallyInService', 'bool')],
                'ConductingEquipment': [('Equipment', 'inheritance'), ('abstract', 'type')],
                'Switch': [('ConductingEquipment', 'inheritance'), ('abstract', 'type'), ('normalOpen', 'bool'),
                           ('retaned', 'bool'), ('switchOnCount', 'int'), ('switchOnDate', 'datetime'),
                           ('ratedCurrent', 'float'), ('SwitchSchedules', 'reflist')],
                'Disconnector': [('Switch', 'inheritance'), ('concrete', 'type')],
                'BasicIntervalSchedule': [('IdentifiedObject', 'inheritance'), ('abstract', 'type'),
                                          ('startTime', 'datetime'), ('value1Multiplier', 'UnitMultiplier'),
                                          ('value1Unit', 'UnitSymbol'), ('value2Multiplier', 'UnitMultiplier'),
                                          ('value2Unit', 'UnitSymbol')],
                'IrregularIntervalSchedule': [('BasicIntervalSchedule', 'inheritance'), ('abstract', 'type'),
                                              ('IrregularTimePoints', 'reflist')],
                'OutageSchedule': [('IrregularIntervalSchedule', 'inheritance'), ('concrete', 'type'),
                                   ('PowerSystemResource', 'ref')],
                'RegularIntervalSchedule': [('BasicIntervalSchedule', 'inheritance'), ('concrete', 'type'),
                                            ('RegularTimePoints', 'reflist'), ('endTime', 'datetime'),
                                            ('timeStep', 'float')],
                'IrregularTimePoint': [('IdentifiedObject', 'inheritance'), ('concrete', 'type'),
                                       ('IntervalSchedule', 'ref'), ('time', 'float'), ('value1', 'float'),
                                       ('value2', 'float')],
                'RegularTimePoint': [('IdentifiedObject', 'inheritance'), ('concrete', 'type'),
                                     ('IntervalSchedule', 'ref'), ('sequenceNumber', 'int'), ('value1', 'float'),
                                     ('value2', 'float')]}
        else:
            Generator.__project_specification = Prompter.prompt_user_for_project_specification()
        Generator.__transformed_project_specification = transform_properties(Generator.__project_specification)
        concrete_classes = {class_name: class_attribues for class_name, class_attribues in
                            Generator.__project_specification.items() if
                            class_attribues[0][0] == 'concrete'}
        Generator.__transformed_concrete_classes = transform_properties(concrete_classes)

    @staticmethod
    def __detect_project_enums():
        for class_name, class_attr in Generator.__transformed_concrete_classes.items():
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
        for class_name, properties in Generator.__project_specification.items():
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

        for class_name, properties in Generator.__project_specification.items():
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
        class_model_codes = []
        property_model_codes = {}
        dms_types = Generator.__generate_dms_types()
        class_inheritances = Generator.__generate_class_inheritance_values()

        for class_name, properties in Generator.__project_specification.items():
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
                class_property_name = f'{class_name.upper()}_{property_name.upper()}'
                property_model_codes[class_property_name] = property_model_code
                model_codes_code_body += f'\n\t\t{property_model_code.__str__()},'

        model_codes_code = model_codes_code.replace('{{model_codes}}', model_codes_code_body)
        Generator.__class_model_codes = class_model_codes
        Generator.__property_model_codes = property_model_codes
        Generator.__model_codes_code = model_codes_code
        Generator.__model_defines_code = f'{Generator.__dms_types_code}\n\n{Generator.__model_codes_code}'
        pyperclip.copy(Generator.__model_defines_code)

    # </editor-fold>

    # <editor-fold desc="XML DATA GENERATION">

    @staticmethod
    def __get_parent_classes(class_name: str, parent_classes=None) -> list:
        if parent_classes is None:
            parent_classes = []

        parent_class = [cls_props['inheritance'] for cls_name, cls_props in
                        Generator.__transformed_project_specification.items() if cls_name == class_name][0]

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
                                       Generator.__transformed_project_specification[parent_class].items() if
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
                return sample(Generator.__concrete_classes_ids[class_property['property_name']], 1)[0]
            except KeyError:
                try:
                    return sample(Generator.__concrete_classes_ids[Generator.__reference_property_names_map[
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
                if type_ not in Generator.__project_enums:
                    Generator.__project_enums.append(type_)
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
                if prop['class_name'] in Generator.__concrete_classes_ids:
                    Generator.__concrete_classes_ids[prop['class_name']].add(instance_id)
                else:
                    Generator.__concrete_classes_ids[prop['class_name']] = {instance_id}
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

        for class_name, class_attr in Generator.__transformed_concrete_classes.items():
            xml_data_code += f'\n\n\t<!-- {class_name} -->'
            class_properties = Generator.__get_all_class_properties(class_name)

            for data_point in range(data_points_count):
                concrete_data_point = ConcreteClassDataPoint(randint(10 ** 9, (10 ** 10) - 1), class_name)
                data_code = Generator.__generate_class_properties_data(class_properties, concrete_data_point.id)
                concrete_data_point.code = concrete_data_point.code.replace('{{class_data}}', data_code)
                xml_data_code += concrete_data_point.code

        xml_code = xml_code.replace('{{data}}', xml_data_code)
        Generator.__xml_data_code = xml_code
        pyperclip.copy(Generator.__xml_data_code)

    # </editor-fold>

    # <editor-fold desc="CONVERTER METHODS GENERATION">

    @staticmethod
    def __class_has_ref(class_name: str) -> bool:
        return any(value == 'ref' for value in Generator.__transformed_project_specification[class_name].values())

    @staticmethod
    def __get_class_parent(class_name: str) -> str:
        return [value for key, value in Generator.__transformed_project_specification[class_name].items() if
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
            capitalized_attr = attr.capitalize() if attr != 'mRID' else attr.upper()
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
        for class_name, class_attributes in Generator.__transformed_project_specification.items():
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
        if len(Generator.__project_enums) == 0:
            return ''

        methods_code = ''
        for enum_name in Generator.__project_enums:
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

        for class_name, attribues in Generator.__transformed_concrete_classes.items():
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
        import_class_method_pair_code = import_class_method_pair_code \
            .replace('{{import_method}}', import_class_method_code) \
            .replace('{{create_description_method}}', create_class_descriptio_method_code)
        return import_class_method_pair_code

    @staticmethod
    def __generate_importer_methods() -> None:
        import_methods_code = IMPORT_METHODS_CODE_TEMPLATE
        import_methods_calls_function_code = Generator.__generate_import_methods_calls_function()

        import_class_methods_code = ''
        for class_name, attribues in Generator.__transformed_concrete_classes.items():
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

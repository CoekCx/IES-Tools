class ModelCode:
    class_name: str = ''
    attribute_name: str = None
    inheritance: str = ''
    dms_type: str = ''
    attribute_index: str = ''
    attribute_type: str = ''

    def __init__(self, class_name, inheritance, dms_type, attribute_index, attribute_type, attribute_name=None):
        self.class_name = class_name
        self.inheritance = inheritance
        self.dms_type = dms_type
        self.attribute_index = attribute_index
        self.attribute_type = attribute_type

        if attribute_name is not None:
            self.attribute_name = attribute_name

    def get_model_code_str(self):
        if self.attribute_name:
            return f'{self.class_name.upper()}_{self.attribute_name.upper()}'
        else:
            return self.class_name.upper()

    def __str__(self):
        class_width = 45  # Adjust the width for names

        if self.attribute_name:
            name = f'{self.class_name.upper()}_{self.attribute_name.upper()}'
            return f'{name: <{class_width}}' \
                   f'= 0x{self.inheritance}{self.dms_type}{self.attribute_index}{self.attribute_type}'
        else:
            return f'{self.class_name.upper(): <{class_width}}= 0x{self.inheritance}{self.dms_type}{self.attribute_index}' \
                   f'{self.attribute_type}'

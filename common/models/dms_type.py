class DMSType:
    name: str = ''
    value: str = ''

    def __init__(self, name, value=''):
        self.name = name
        self.value = value

    def __str__(self):
        class_width = 45  # Adjust the width for names
        return f'{self.name.upper(): <{class_width}}= 0x{self.value:04x}'

    def __eq__(self, other):
        if isinstance(other, DMSType):
            return self.name == other.name
        return False

    def get_value(self):
        return f'{self.value:04x}'

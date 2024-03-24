from common import invert_dict
from common.enums.property_type import PropertyType


class Property:
    property_type_map = {
        'ref': PropertyType.REF,
        'reflist': PropertyType.REFLIST,
        'int': PropertyType.INT,
        'long': PropertyType.LONG,
        'float': PropertyType.FLOAT,
        'double': PropertyType.DOUBLE,
        'string': PropertyType.STRING,
        'datetime': PropertyType.DATETIME,
        'bool': PropertyType.BOOL
    }
    property_type_map_inverted = invert_dict(property_type_map)

    def __init__(self, data: ()):
        self.prop_value = data[0]
        self.type_value = data[1]
        self.type = Property.map_type(data[1])

    @staticmethod
    def map_type(type_value: str):
        return Property.property_type_map.get(type_value, PropertyType.ENUM)

    def __repr__(self):
        return f'{self.prop_value}: {self.type.name}'

    def to_json_data(self) -> ():
        return self.prop_value, self.type_value

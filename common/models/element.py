from common import invert_dict
from common.enums.class_type import ClassType
from common.enums.property_type import PropertyType
from common.models.property import Property


class Element:
    class_type_map = {
        'abstract': ClassType.ABSTRACT,
        'concrete': ClassType.CONCRETE
    }
    class_type_map_inverted = invert_dict(class_type_map)

    def __init__(self, data: list = None,
                 name: str = '', inheritance: str = '', properties: list[Property] = None, type: ClassType = None):
        if data:
            self.map_data(data)
        if name:
            self.name = name
        if inheritance:
            self.inheritance = inheritance
        if properties:
            self.properties: list[Property] = properties
        if type:
            self.type = type

        self.num_of_refs = len([prop for prop in self.properties if prop.type == PropertyType.REF])
        self.num_of_ref_lists = len([prop for prop in self.properties if prop.type == PropertyType.REFLIST])

    def map_data(self, data: list) -> None:
        self.inheritance = Element.find_type('inheritance', data)
        self.type = Element.class_type_map.get(Element.find_type('type', data), 'NOT FOUND')

        self.properties = []
        properties_data = [dp for dp in data if dp[1] not in ('inheritance', 'type')]
        for dp in properties_data:
            self.properties.append(Property(dp))

    @staticmethod
    def find_type(type: str, data: list) -> str:
        for datapoint in data:
            value, data_type = datapoint
            if data_type == type:
                return value

        return 'NOT FOUND'

    def __repr__(self):
        return f"{self.name}({self.inheritance}) REFS={self.num_of_refs} LISTS={self.num_of_ref_lists}"

    def print_info(self):
        header = self.__repr__()
        properties = ''
        for prop in self.properties:
            properties += prop.__repr__()
        return header + properties

    def to_json_data(self):
        json_data = [(Element.class_type_map_inverted.get(self.type, 'NOT FOUND'), 'type'),
                     (self.inheritance, 'inheritance')]
        for prop in self.properties:
            json_data.append(prop.to_json_data())
        return json_data

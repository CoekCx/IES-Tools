from common.enums.class_type import ClassType
from common.models.element import Element


class Specification:
    def __init__(self, data):
        self.path = data['path']
        self.specification = Specification.map_spec_data(data['specification'])
        self.overlap_percentage = 0

    @staticmethod
    def map_spec_data(data: dict):
        specification = []
        for el_name, el_data in data.items():
            specification.append(Element(data=el_data, name=el_name))
        return specification

    def count_missing_elements(self, element_names: str) -> int:
        count = 0
        for el in element_names:
            if not self.includes_element(el):
                count += 1
        return count

    def includes_element(self, element_name: str) -> bool:
        for el in self.specification:
            if el.name == element_name:
                return True
        return False

    def includes_any_element_of(self, element_names: list) -> bool:
        for el in self.specification:
            if el.name in element_names:
                return True
        return False

    def __repr__(self):
        txt = f'{self.path}: '
        for el in self.specification:
            if el.type == ClassType.CONCRETE:
                txt += el.name + ' '
        return txt

    def to_json_data(self):
        spec_json = {
            'path': self.path,
            'specification': {element.name: element.to_json_data() for element in self.specification}
        }
        return spec_json

    def properties_to_json_data(self):
        return {element.name: element.to_json_data() for element in self.specification}

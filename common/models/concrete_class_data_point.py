from common.constants.templates import DATA_POINT_TEMPLATE


class ConcreteClassDataPoint:
    id: str
    name: str
    code: str

    def __init__(self, id: int, name: str, code: str = DATA_POINT_TEMPLATE) -> None:
        self.id = id.__str__()
        self.name = name
        self.code = code.replace('{{class_name}}', self.name).replace('{{class_id}}', self.id)

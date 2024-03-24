from enum import Enum


class PropertyType(Enum):
    REF = 1
    REFLIST = 2
    INT = 3
    LONG = 4
    FLOAT = 5
    DOUBLE = 6
    STRING = 7
    DATETIME = 8
    ENUM = 9
    BOOL = 10

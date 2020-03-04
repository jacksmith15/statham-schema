from typing import Dict, Tuple, Type

from statham import validators as val
from statham.dsl.elements.base import Element
from statham.dsl.property import _Property
from statham.dsl.constants import NotPassed


class JSONSchemaClassDict(dict):

    default: bool
    properties: Dict[str, _Property]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        schema_keys = [
            key for key, value in self.items() if isinstance(value, Property)
        ]
        self.default = self.get("default", NotPassed())
        self.properties = {key: self.pop(key) for key in schema_keys}

    def __setitem__(self, key, value):
        if key == "default":
            self.default = value
        if isinstance(value, _Property):
            return self.properties.__setitem__(key, value)
        return super().__setitem__(key, value)


class ObjectMeta(type, Element):

    properties: Dict[str, _Property]

    @staticmethod
    def __subclasses__():
        return []

    @classmethod
    def __prepare__(mcs, _name, _bases):
        return JSONSchemaClassDict()

    def __new__(
        mcs, name: str, bases: Tuple[Type], classdict: JSONSchemaClassDict
    ):
        cls: Type[ObjectMeta] = type.__new__(mcs, name, bases, dict(classdict))
        cls.properties = classdict.properties
        for attr_name, property_ in cls.properties.items():
            property_.bind(cls, attr_name)
        cls.default = classdict.default
        return cls

    def __repr__(cls):
        return f"{cls.__name__}"

    @property
    def type_validator(cls):
        return val.instance_of(dict, cls)

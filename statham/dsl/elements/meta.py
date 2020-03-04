from typing import Dict, Tuple, Type

from statham import validators as val
from statham.dsl.elements.base import Element
from statham.dsl.property import Property
from statham.dsl.constants import NotPassed


class JSONSchemaClassDict(dict):

    default: bool
    schema_properties: Dict[str, Property]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        schema_keys = [
            key for key, value in self.items() if isinstance(value, Property)
        ]
        self.default = self.get("default", NotPassed())
        self.schema_properties = {key: self.pop(key) for key in schema_keys}

    def __setitem__(self, key, value):
        if key == "default":
            self.default = value
        if isinstance(value, Property):
            return self.schema_properties.__setitem__(key, value)
        return super().__setitem__(key, value)


class JSONSchemaModelMeta(type, Element):

    schema_properties: Dict[str, Property]

    @staticmethod
    def __subclasses__():
        return []

    @classmethod
    def __prepare__(mcs, _name, _bases):
        return JSONSchemaClassDict()

    def __new__(
        mcs, name: str, bases: Tuple[Type], classdict: JSONSchemaClassDict
    ):
        cls: Type[JSONSchemaModelMeta] = type.__new__(
            mcs, name, bases, dict(classdict)
        )
        cls.schema_properties = classdict.schema_properties
        for attr_name, property_ in cls.schema_properties.items():
            property_.bind(cls, attr_name)
        cls.default = classdict.default
        return cls

    def __repr__(cls):
        return f"{cls.__name__}"

    @property
    def type_validator(cls):
        return val.instance_of(dict, cls)

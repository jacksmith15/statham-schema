from typing import Any, Dict, Tuple, Type

from statham.dsl import validators as val
from statham.dsl.elements.base import Element
from statham.dsl.property import _Property
from statham.dsl.constants import NotPassed


class ObjectClassDict(dict):
    """Overriden class dictionary for the metaclass of Object.

    Collects schema properties and default value if present.
    """

    default: Any
    properties: Dict[str, _Property]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        schema_keys = [
            key for key, value in self.items() if isinstance(value, _Property)
        ]
        self.default = self.get("default", NotPassed())
        self.properties = {key: self.pop(key) for key in schema_keys}

    def __setitem__(self, key, value):
        if key == "default":
            self.default = value
        if isinstance(value, _Property):
            return self.properties.__setitem__(key, value)
        return super().__setitem__(key, value)


# TODO: Handle properties called `default` or `self`.
class ObjectMeta(type, Element):
    """Metaclass to allow declaring Object schemas as classes.

    Collects default value and properties defined as class variables,
    and binds information to those properties.
    """

    properties: Dict[str, _Property]

    @staticmethod
    def __subclasses__():
        return []

    @classmethod
    def __prepare__(mcs, _name, _bases):
        return ObjectClassDict()

    def __new__(mcs, name: str, bases: Tuple[Type], classdict: ObjectClassDict):
        cls: Type[ObjectMeta] = type.__new__(mcs, name, bases, dict(classdict))
        cls.properties = classdict.properties
        for attr_name, property_ in cls.properties.items():
            property_.bind(cls, attr_name)
        cls.default = classdict.default
        return cls

    def __hash__(cls):
        return hash(tuple([cls.__name__] + [prop for prop in cls.properties]))

    @property
    def annotation(cls) -> str:
        return cls.__name__

    def __repr__(cls):
        return cls.__name__

    @property
    def type_validator(cls):
        return val.instance_of(dict, cls)

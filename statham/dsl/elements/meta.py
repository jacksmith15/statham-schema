from typing import Any, Dict, Tuple, Type

from statham.dsl import validators as val
from statham.dsl.elements.base import Element
from statham.dsl.property import _Property
from statham.dsl.constants import NotPassed


class ObjectClassDict(dict):

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


class ObjectMeta(type, Element):

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
    def code(cls):
        super_cls = next(iter(cls.mro()[1:]))
        cls_args = (
            f"metaclass={type(cls).__name__}"
            if super_cls is object
            else super_cls.__name__
        )
        class_def = f"""class {repr(cls)}({cls_args}):
"""
        if not cls.properties and isinstance(cls.default, NotPassed):
            class_def = (
                class_def
                + """
    pass
"""
            )
        if not isinstance(cls.default, NotPassed):
            class_def = (
                class_def
                + f"""
    default = {repr(cls.default)}
"""
            )
        for attr_name, property_ in cls.properties.items():
            class_def = (
                class_def
                + f"""
    {attr_name}: {property_.annotation} = {property_.code}
"""
            )
        return class_def

    @property
    def type_validator(cls):
        return val.instance_of(dict, cls)

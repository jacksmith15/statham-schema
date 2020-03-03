from typing import Dict, Tuple, Type


class JSONSchemaClassDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        schema_keys = [
            key for key, value in self.items() if isinstance(value, Element)
        ]
        self.schema_properties = {key: self.pop(key) for key in schema_keys}

    def __setitem__(self, key, value):
        if isinstance(value, Element):
            return self.schema_properties.__setitem__(key, value)
        return super().__setitem__(key, value)


# Base element must be imported last.
# pylint: disable=wrong-import-position
from statham.dsl.elements.base import Element


class JSONSchemaModelMeta(type):

    schema_properties: Dict[str, "Element"]

    @classmethod
    def __prepare__(mcs, _name, _bases):
        return JSONSchemaClassDict()

    def __new__(
        mcs, name: str, bases: Tuple[Type], classdict: JSONSchemaClassDict
    ):
        result: Type[JSONSchemaModelMeta] = type.__new__(
            mcs, name, bases, dict(classdict)
        )
        result.schema_properties = classdict.schema_properties
        return result

    def __repr__(cls):
        return f"{cls.__name__}"

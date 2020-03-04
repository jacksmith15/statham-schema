from typing import Any, ClassVar, Dict, Union

from statham.dsl.elements.meta import JSONSchemaModelMeta
from statham.dsl.elements.base import Element
from statham.dsl.property import Property, UNBOUND_PROPERTY
from statham.exceptions import ValidationError
from statham.dsl.constants import NotPassed


class JSONSchemaModel(metaclass=JSONSchemaModelMeta):
    """Base model for JSONSchema objects.

    Recursively validates and construct properties.
    """

    schema_properties: ClassVar[Dict[str, Union[JSONSchemaModelMeta, Element]]]
    default: ClassVar[Any]

    @classmethod
    def _parse_args(cls, *args):
        max_args = 2
        min_args = 1
        if len(args) > max_args:
            raise TypeError(
                f"Got {len(args)} to {cls.__name__}. Expected no more "
                f"than {max_args}."
            )
        if len(args) < min_args:
            raise TypeError(
                f"Got {len(args)} to {cls.__name__}. Expected no fewer "
                f"than {min_args}."
            )
        if len(args) == 1:
            return UNBOUND_PROPERTY, args[0]
        return args[0], args[1]

    def __new__(cls, *args):
        property_, value = cls._parse_args(*args)
        for validator in cls.validators:
            validator(property_, value)
        if isinstance(value, (NotPassed, cls)):
            return value
        return object.__new__(cls)

    def __init__(self, *args):
        property_, value = self._parse_args(*args)
        if value is self:
            return
        unexpected_kwargs = set(value) - set(self.schema_properties)
        if unexpected_kwargs:
            raise ValidationError(
                f"Unexpected attributes passed to {self.__class__}: "
                f"{unexpected_kwargs}. Accepted kwargs: "
                f"{set(self.schema_properties)}"
            )
        for attr_name, property_ in self.schema_properties.items():
            setattr(
                self, attr_name, property_(value.get(attr_name, NotPassed()))
            )

    def __repr__(self):
        attr_repr = ", ".join(
            [
                f"{attr}={repr(getattr(self, attr))}"
                for attr in self.schema_properties
            ]
        )
        return f"{self.__class__.__name__}({attr_repr})"

    def __str__(self):
        return repr(self)

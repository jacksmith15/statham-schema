from typing import Any, ClassVar, Dict, overload, Tuple, Union

from statham.dsl.elements.meta import ObjectMeta
from statham.dsl.elements.base import Element
from statham.dsl.property import _Property, UNBOUND_PROPERTY
from statham.exceptions import ValidationError
from statham.dsl.constants import NotPassed


class Object(metaclass=ObjectMeta):
    """Base model for JSONSchema objects.

    Recursively validates and construct properties.
    """

    properties: ClassVar[Dict[str, Union[ObjectMeta, Element]]]
    default: ClassVar[Any]

    @classmethod
    def _parse_args(cls, *args) -> Tuple[_Property, Any]:
        max_args = 2
        min_args = 1 if isinstance(cls.default, NotPassed) else 0
        if len(args) > max_args:
            raise TypeError(
                f"Got {len(args)} args to {cls.__name__}. Expected no more "
                f"than {max_args}."
            )
        if len(args) < min_args:
            raise TypeError(
                f"Got {len(args)} args to {cls.__name__}. Expected no fewer "
                f"than {min_args}."
            )
        if not args:
            return UNBOUND_PROPERTY, cls.default
        if len(args) == 1:
            if isinstance(args[0], _Property):
                if isinstance(cls.default, NotPassed):
                    raise TypeError(
                        f"Missing `value` argument to {cls.__name__}."
                    )
                return args[0], cls.default
            return UNBOUND_PROPERTY, args[0]
        return args[0], args[1]

    @overload
    def __new__(cls, _value: Any):
        ...

    @overload
    def __new__(cls, _property: _Property, _value: Any):
        ...

    def __new__(cls, *args):
        property_, value = cls._parse_args(*args)
        for validator in cls.validators:
            validator(property_, value)
        if isinstance(value, (NotPassed, cls)):
            return value
        return object.__new__(cls)

    @overload
    def __init__(self, _value: Any):
        ...

    @overload
    def __init__(self, _property: _Property, _value: Any):
        ...

    def __init__(self, *args):
        _, value = self._parse_args(*args)
        if value is self:
            return
        unexpected_kwargs = set(value) - set(self.properties)
        if unexpected_kwargs:
            raise ValidationError(
                f"Unexpected attributes passed to {self.__class__}: "
                f"{unexpected_kwargs}. Accepted kwargs: "
                f"{set(self.properties)}"
            )
        for attr_name, property_ in self.properties.items():
            setattr(
                self, attr_name, property_(value.get(attr_name, NotPassed()))
            )

    def __repr__(self):
        attr_repr = ", ".join(
            [f"{attr}={repr(getattr(self, attr))}" for attr in self.properties]
        )
        return f"{self.__class__.__name__}({attr_repr})"

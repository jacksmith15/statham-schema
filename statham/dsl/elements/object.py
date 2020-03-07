from typing import Any, ClassVar, Dict, overload, Tuple

from statham.dsl.elements.meta import ObjectMeta
from statham.dsl.exceptions import ValidationError
from statham.dsl.property import _Property, UNBOUND_PROPERTY
from statham.dsl.constants import NotPassed


class Object(metaclass=ObjectMeta):
    """Base model for JSONSchema objects.

    New object schemas are defined by implementing subclasses of Object.

    For example:
    ```python
    from statham.dsl.elements import Object, String
    from statham.dsl.property import Property

    class Poll(Object):

        questions: List[str] = Property(String(), required=True)

    poll = Poll({"questions": ["What's up?"]})
    ```
    """

    properties: ClassVar[Dict[str, _Property]]
    default: ClassVar[Any]

    # TODO: Can we avoid this parameter nonsense by swapping the
    #   call interface and making property optional.
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
        ...  # pragma: no cover

    @overload
    def __new__(cls, _property: _Property, _value: Any):
        ...  # pragma: no cover

    def __new__(cls, *args):
        property_, value = cls._parse_args(*args)
        for validator in cls.validators:
            validator(property_, value)
        if isinstance(value, (NotPassed, cls)):
            return value
        return object.__new__(cls)

    @overload
    def __init__(self, _value: Any):
        ...  # pragma: no cover

    @overload
    def __init__(self, _property: _Property, _value: Any):
        ...  # pragma: no cover

    def __init__(self, *args):
        """Initialise the object.

        Accepts either an enclosing property and an input value, or just
        the value if unbound to an outer property.
        """
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
        attr_values = {attr: getattr(self, attr) for attr in self.properties}
        attr_repr = ", ".join(
            [
                f"{attr}={repr(value)}"
                for attr, value in attr_values.items()
                if not isinstance(value, NotPassed)
            ]
        )
        return f"{self.__class__.__name__}({attr_repr})"

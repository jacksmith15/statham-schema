from typing import Any, ClassVar, Dict, Union

from statham.dsl.elements.base import Element, UNBOUND_PROPERTY
from statham.dsl.elements.meta import ObjectMeta
from statham.dsl.exceptions import ValidationError
from statham.dsl.property import _Property
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
    # TODO: propertyNames
    # TODO: minProperties
    # TODO: maxProperties
    """

    properties: ClassVar[Dict[str, _Property]]
    default: ClassVar[Any]
    additionalProperties: ClassVar[Union[Element, bool]]

    def __new__(
        cls, value: Any = NotPassed(), property_: _Property = UNBOUND_PROPERTY
    ):
        """Preprocess new instances.

        If value isn't passed, attempt to instantiate the default, but
        allow non-matching defaults.

        This is the equivalent of `Element.__call__`.
        """
        if isinstance(value, cls):
            return value
        if not isinstance(cls.default, NotPassed) and isinstance(
            value, NotPassed
        ):
            try:
                return cls(cls.default, property_)
            except (TypeError, ValidationError):
                return cls.default
        if isinstance(value, NotPassed):
            return value
        for validator in cls.validators:
            validator(value, property_)
        return object.__new__(cls)

    def __init__(
        self, value: Any = NotPassed(), _property: _Property = UNBOUND_PROPERTY
    ):
        """Initialise the object.

        The equivalent of `Element.__call__`, but on a class/instance.
        """
        if value is self:
            return
        if isinstance(value, NotPassed) and not isinstance(
            self.default, NotPassed
        ):
            value = self.default
        self._dict: Dict[str, Any] = {}
        for attr_name, attr_value in type(self).__properties__(value).items():
            if attr_name in self.properties:
                setattr(self, attr_name, attr_value)
            self._dict[attr_name] = attr_value

    def __repr__(self):
        attr_values = {
            attr: getattr(self, attr) for attr in type(self).properties
        }
        attr_repr = ", ".join(
            [
                f"{attr}={repr(value)}"
                for attr, value in attr_values.items()
                if not isinstance(value, NotPassed)
            ]
        )
        return f"{self.__class__.__name__}({attr_repr})"

    def __eq__(self, other):
        return (
            type(self) is type(other)
            # pylint: disable=protected-access
            and self._dict == other._dict
        )

    def __getitem__(self, key: str) -> Any:
        return self._dict[key]

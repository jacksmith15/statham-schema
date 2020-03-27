from typing import Any, ClassVar, Dict

from statham.dsl.elements.meta import ObjectMeta, ObjectOptions
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
    # TODO: patternProperties
    # TODO: propertyNames
    # TODO: minProperties
    # TODO: maxProperties
    """

    properties: ClassVar[Dict[str, _Property]]
    default: ClassVar[Any]
    options: ClassVar[ObjectOptions]
    additional_properties: Dict[str, Any]

    def __new__(
        cls, value: Any = NotPassed(), property_: _Property = UNBOUND_PROPERTY
    ):
        for validator in cls.validators:
            validator(value, property_)
        if isinstance(value, cls):
            return value
        if isinstance(value, NotPassed) and isinstance(cls.default, NotPassed):
            raise TypeError(f"Missing value argument to {cls}.")
        return object.__new__(cls)

    def __init__(
        self, value: Any = NotPassed(), _property: _Property = UNBOUND_PROPERTY
    ):
        """Initialise the object."""
        if isinstance(value, NotPassed) and not isinstance(
            self.default, NotPassed
        ):
            value = self.default
        if value is self:
            return
        self.additional_properties = {}
        for attr_name, property_ in self.properties.items():
            setattr(
                self,
                attr_name,
                property_(value.pop(property_.source, NotPassed())),
            )
        if not value:
            return
        if not self.options.additionalProperties:
            raise ValidationError(
                f"Unexpected attributes passed to {self.__class__}: "
                f"{set(value)}. Accepted kwargs: "
                f"{set(self.properties)}"
            )
        constructor = self.options.additionalProperties
        additional_property = _Property(constructor)
        for name, argument in value.items():
            additional_property.bind_name(name)
            additional_property.bind_class(type(self))
            self.additional_properties[name] = additional_property(argument)

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

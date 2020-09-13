from typing import Any, ClassVar, Dict, Union

from statham.dsl.elements.base import Element, UNBOUND_PROPERTY
from statham.dsl.elements.meta import ObjectClassDict, ObjectMeta
from statham.dsl.exceptions import ValidationError
from statham.dsl.property import _Property
from statham.dsl.constants import NotPassed


# TODO: Test and support limited recursive models.


class Object(metaclass=ObjectMeta):
    """Base model for JSON Schema ``"object"`` elements.

    ``"object"`` schemas are defined by declaring subclasses of
    :class:`Object`. Properties are declared as class attributes, and
    other keywords are set as class arguments.

    For example:

    .. code:: python

        from statham.dsl.elements import Object, String
        from statham.dsl.property import Property

        class Poll(Object, additionalProperties=False):

            questions: List[str] = Property(String(), required=True)

        poll = Poll({"questions": ["What's up?"]})

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
            if attr_name in type(self).properties:
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

    @staticmethod
    def inline(
        name: str, *, properties: Dict[str, Any] = None, **kwargs
    ) -> ObjectMeta:
        """Inline constructor for object schema elements.

        Useful for minor objects, at the cost of reduced type checking
        support.

        :param name: The name of the schema element.
        :param properties: Dictionary of properties accepted by the schema
            element.
        :param kwargs: Any accepted class args to `Object` subclasses.
        :return: A new subclass of `Object` with the appropriate validation
            rules.
        """
        properties = properties or {}
        object_properties = ObjectClassDict()
        for prop_name, prop in properties.items():
            object_properties[prop_name] = prop
        return ObjectMeta(name, (Object,), object_properties, **kwargs)

# False positive. The cycle exists but is avoided by importing last.
# pylint: disable=cyclic-import
from typing import Any, cast, Dict, List, Generic, TypeVar, Union

from statham.schema.constants import NotPassed, Maybe
from statham.schema.exceptions import ValidationError
from statham.schema.helpers import custom_repr
from statham.schema.property import _Property, _PropertyDict
from statham.schema.validation import (
    get_validators,
    InstanceOf,
    NoMatch,
    Validator,
)


T = TypeVar("T")

Numeric = Union[int, float]


# This emulates the options available to a general JSON Schema object.
# pylint: disable=too-many-instance-attributes
class Element(Generic[T]):
    # pylint: disable=line-too-long
    """An un-typed schema element.

    Accepts JSON Schema keywords as arguments.

    :param default:
        The default value this element should return when not provided.
    :param const:
        Restrict this element to a constant value.
    :param enum:
        Restrict this element to an enumeration of provided values.
    :param items:
        The :class:`Element` with which to validate list items. If
        :paramref:`~Element.items` is a list of :class:`Element`, then
        each :class:`Element` validates the corresponding index of the
        value. Subsequent values are validated by
        :paramref:`~Element.additionalItems`.
    :param additionalItems:
        The :class:`Element` with which to validate additional items in a
        list, when :paramref:`items` is a list and shorter than the
        passed list.
    :param minItems:
        The minimum number of items to allow in list values.
    :param maxItems:
        The maximum number of items to allow in list values.
    :param uniqueItems:
        If :const:`True`, validate that list values contain unique
        elements.
    :param contains:
        Validate that list values contain at least one element
        matching this :class:`Element`.
    :param minimum:
        Validate that numeric values are greater than or equal
        to this value.
    :param maximum:
        Validate that numeric values are less than or equal
        to this value.
    :param exclusiveMinimum:
        Validate that numeric values are strictly greater than
        this value.
    :param exclusiveMaximum:
        Validate that numeric values are strictly less than
        this value.
    :param multipleOf:
        Validate that numeric values are are multiple of this
        value.
    :param format:
        Validate that string values conform to the specified
        format. See :func:`~statham.schema.validation.format.format_checker`
        to learn about included formats and how to add your own.
    :param pattern:
        Validate that string values match this value as a regular
        expression.
    :param minLength:
        Validate that string values are at least as long as this
        value.
    :param maxLength:
        Validate that string values are at most as long as this
        value.
    :param required:
        Validate that dictionary values contain each of these
        keys.
    :param properties:
        Validate that dictionary values match these properties.
        See :class:`statham.schema.property.Property` for more information.
    :param patternProperties:
        Validate that keys of dictionaries matching these
        patterns conform to the provided :class:`Element`. Keys may match
        on multiple :paramref:`~Element.patternProperties` and
        :paramref:`~Element.properties` at the same time.
    :param additionalProperties:
        Validate properties not matched by either
        :paramref:`~Element.properties` or
        :paramref:`~Element.patternProperties` against this element. If
        :const:`True`, any value is allowed. If :const:`False`, no
        additional properties are allowed.
    :param minProperties:
        Validate that dictionary values contain at least this
        many members.
    :param maxProperties:
        Validate that dictionary values contain at most this
        many members.
    :param propertyNames:
        Validate that keys of dictionary values match are accepted
        by this :class:`Element`. Any :class:`Element` is allowed here,
        but it is not useful to use any other than
        :class:`statham.schema.elements.String`.
    :param dependencies:
        Define JSON Schema dependencies. There are two types of
        dependencies. If the dict value is a list, then the each property
        name in that list must be present when the property name of the
        key is present. If the value is an :class:`Element`, then it's
        validation applies whenever the property name of the key is present. See
        `Object Dependencies <https://json-schema.org/understanding-json-schema/reference/object.html#dependencies>`_
        for more detail.
    """
    # pylint: enable=line-too-long

    _properties: Maybe[_PropertyDict]

    # This is how many options there are!
    # pylint: disable=too-many-locals
    def __init__(
        self,
        *,
        # Bad name to match JSON Schema keywords.
        # pylint: disable=redefined-builtin
        default: Maybe[Any] = NotPassed(),
        const: Maybe[Any] = NotPassed(),
        enum: Maybe[List[Any]] = NotPassed(),
        items: Maybe[Union["Element", List["Element"]]] = NotPassed(),
        additionalItems: Union["Element", bool] = True,
        minItems: Maybe[int] = NotPassed(),
        maxItems: Maybe[int] = NotPassed(),
        uniqueItems: bool = False,
        contains: Maybe["Element"] = NotPassed(),
        minimum: Maybe[Numeric] = NotPassed(),
        maximum: Maybe[Numeric] = NotPassed(),
        exclusiveMinimum: Maybe[Numeric] = NotPassed(),
        exclusiveMaximum: Maybe[Numeric] = NotPassed(),
        multipleOf: Maybe[Numeric] = NotPassed(),
        format: Maybe[str] = NotPassed(),
        pattern: Maybe[str] = NotPassed(),
        minLength: Maybe[int] = NotPassed(),
        maxLength: Maybe[int] = NotPassed(),
        required: Maybe[List[str]] = NotPassed(),
        properties: Maybe[Dict[str, "_Property"]] = NotPassed(),
        patternProperties: Maybe[Dict[str, "Element"]] = NotPassed(),
        additionalProperties: Union["Element", bool] = True,
        minProperties: Maybe[int] = NotPassed(),
        maxProperties: Maybe[int] = NotPassed(),
        propertyNames: Maybe["Element"] = NotPassed(),
        dependencies: Maybe[
            Dict[str, Union[List[str], "Element"]]
        ] = NotPassed(),
    ):
        self.default = default
        self.const = const
        self.enum = enum
        self.items = items
        self.additionalItems = additionalItems
        self.minItems = minItems
        self.maxItems = maxItems
        self.uniqueItems = uniqueItems
        self.contains = contains
        self.minimum = minimum
        self.maximum = maximum
        self.exclusiveMinimum = exclusiveMinimum
        self.exclusiveMaximum = exclusiveMaximum
        self.multipleOf = multipleOf
        self.format = format
        self.pattern = pattern
        self.minLength = minLength
        self.maxLength = maxLength
        self.required = required
        # https://github.com/python/mypy/issues/3004
        self.properties = properties  # type: ignore
        self.patternProperties = patternProperties
        self.additionalProperties = additionalProperties
        self.minProperties = minProperties
        self.maxProperties = maxProperties
        self.propertyNames = propertyNames
        self.dependencies = dependencies

    @property
    def properties(self) -> Maybe[_PropertyDict]:
        return self._properties

    @properties.setter
    def properties(self, value: Maybe[Dict[str, _Property]]):
        if isinstance(value, NotPassed):
            self._properties = value
            return
        self._properties = _PropertyDict(cast(Dict[str, _Property], value))
        self._properties.parent = self

    def __repr__(self):
        """Dynamically construct the repr to match value instantiation."""
        return custom_repr(self)

    def __eq__(self, other):
        """Check if two elements are equivalent.

        This just checks the type and public attribute values. Useful for
        testing parser logic, and could be used to automatically DRY up
        messy schemas in future.
        """
        if not isinstance(other, self.__class__):
            return False
        pub_vars = lambda x: {
            k: v
            for k, v in vars(x).items()
            if not k.startswith("_") or k == "_properties"
        }
        return pub_vars(self) == pub_vars(other)

    @property
    def annotation(self) -> str:
        generic = type(self).__orig_bases__[0].__args__[0]  # type: ignore
        if isinstance(generic, TypeVar):  # type: ignore
            return "Any"
        return generic.__name__

    @property
    def type_validator(self) -> Validator:
        return InstanceOf()

    @property
    def validators(self) -> List[Validator]:
        validators: List[Validator] = [self.type_validator] + list(
            get_validators(self)
        )
        return validators

    def construct(self, value, property_):
        if isinstance(value, list):
            return self.__items__(value, property_)
        if isinstance(value, dict):
            return _AnonymousObject(**self.__properties__(value))
        return value

    @property
    def __properties__(self) -> "Properties":
        return Properties(
            self,
            getattr(self, "properties", NotPassed()),
            getattr(self, "patternProperties", NotPassed()),
            getattr(self, "additionalProperties", True),
        )

    @property
    def __items__(self) -> "Items":
        return Items(
            getattr(self, "items", NotPassed()),
            getattr(self, "additionalItems", True),
        )

    def __call__(self, value: Any, property_=None) -> Maybe[T]:
        """Validate and convert input data against this :class:`Element`.

        Dictionary (object) values which pass validation are returned as
        a subclass of :const:`dict` allowing attribute access.

        :param value: The input data.
        :param property_: Optionally specify the outer property scope
            enclosing this :class:`Element`. Used automatically by object
            validation to produce more useful error messages.
        :return: The parsed value.
        """
        property_ = property_ or UNBOUND_PROPERTY

        def create(value):
            for validator in self.validators:
                validator(value, property_)
            return self.construct(value, property_)

        if not isinstance(self.default, NotPassed) and isinstance(
            value, NotPassed
        ):
            try:
                return create(self.default)
            except (TypeError, ValidationError):
                return self.default
        if isinstance(value, NotPassed):
            return value
        return create(value)


UNBOUND_PROPERTY: _Property = _Property(Element(), required=False)
UNBOUND_PROPERTY.bind(parent=Element(), name="<unbound>")


class Nothing(Element):
    """Element which matches nothing. Equivalent to :const:`False`."""

    def __init__(self):
        super().__init__()  # Don't allow args to Nothing.

    def __bool__(self):
        return False

    @property
    def annotation(self) -> str:
        return "None"

    @property
    def validators(self) -> List[Validator]:
        return [NoMatch()]


# Needs to be imported last to prevent cyclic import.
# pylint: disable=wrong-import-position
from statham.schema.elements.properties import Properties
from statham.schema.elements.items import Items


class _AnonymousObject(dict):
    """Anonymous object type.

    Allows dictionaries passed to untyped objects to use attribute access,
    to match `Object` instances.
    """

    def __getattr__(self, key: str) -> Any:
        return self.__getitem__(key)

    def __setattr__(self, key: str, value: Any):
        return self.__setitem__(key, value)

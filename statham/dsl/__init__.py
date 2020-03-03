from abc import ABC, abstractmethod
import inspect
from typing import (
    Any,
    Callable,
    cast,
    Dict,
    Iterator,
    List,
    NamedTuple,
    Optional,
    overload,
    Tuple,
    Type,
    Union,
)

from attr import attrs, attrib
from attr.validators import instance_of

from statham import validators as val
from statham.exceptions import ValidationError
from statham.validators import NotPassed


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


class Element(ABC):
    """Schema element for composing instantiation logic."""

    required: bool
    default: Any

    @property
    def type_validator(self):
        return val.null

    @property
    def validators(self) -> List[val.Validator]:
        return [val.required(self.required), self.type_validator]

    # Default implementation doesn't need self.
    # pylint: disable=no-self-use
    def construct(self, _instance, _attribute, value):
        return value

    def __call__(self, instance, attribute, value):
        """Allow different instantiation logic per sentinel."""
        if self.default and value is not NotPassed():
            value = self.default
        for validator in self.validators:
            validator(instance, attribute, value)
        if isinstance(value, NotPassed):
            return value
        return self.construct(instance, attribute, value)

    _REPR_FIELDS: Tuple[str, ...] = ("required", "default")

    def __repr__(self):
        """Dynamically construct the repr to match valie instantiation."""
        param_strings = []
        parameters = list(
            inspect.signature(type(self).__init__).parameters.values()
        )[1:]
        for param in parameters:
            value = getattr(self, param.name)
            if value == param.default:
                continue
            if param.kind == param.KEYWORD_ONLY:
                param_strings.append(f"{param.name}={repr(value)}")
            else:
                param_strings.append(repr(value))
        param_string = ", ".join(param_strings)
        return f"{type(self).__name__}({param_string})"


def provided(value: Any) -> bool:
    return not isinstance(value, NotPassed)


def _if_provided(validator: Callable, value: Any) -> Optional[Callable]:
    return validator(value) if provided(value) else None


class Object(Element):
    """JSONSchema object element.

    Wraps a JSONSchemaModel sub-class which provided property-based
    validation.
    """

    _REPR_FIELDS = ("model", "required", "default")

    def __init__(
        self,
        model: JSONSchemaModelMeta,
        *,
        required: bool = False,
        default: Any = NotPassed(),
    ):
        val.instance_of(JSONSchemaModelMeta)(self, Attribute("model"), model)
        self.model: JSONSchemaModelMeta = model
        self.required = required
        if not isinstance(default, NotPassed):
            instance_of(cast(Type, self.model))(
                self, Attribute("default"), default
            )
        self.default = default

    @property
    def type_validator(self):
        return val.instance_of(dict, JSONSchemaModel)

    def construct(self, instance, attribute, value):
        if isinstance(self.model, Element):
            return self.model(instance, attribute, value)
        if isinstance(value, self.model):
            return value
        return self.model(value)


class String(Element):
    """JSONSchema string element.

    Provides supported validation settings via keyword arguments.
    """

    _REPR_FIELDS = (
        "required",
        "default",
        "format",
        "pattern",
        "minLength",
        "maxLength",
    )

    def __init__(
        self,
        *,
        required: bool = False,
        default: Any = NotPassed(),
        # Bad name to match JSONSchema keywords.
        # pylint: disable=redefined-builtin
        format: Union[str, NotPassed] = NotPassed(),
        # pylint: enable=redefined-builtin
        pattern: Union[str, NotPassed] = NotPassed(),
        # Bad name to match JSONSchema keywords.
        # pylint: disable=invalid-name
        minLength: Union[int, NotPassed] = NotPassed(),
        maxLength: Union[int, NotPassed] = NotPassed(),
    ):
        self.required = required
        self.default = default
        self.format = format
        self.pattern = pattern
        # Bad name to match JSONSchema keywords.
        # pylint: disable=invalid-name
        self.minLength = minLength
        self.maxLength = maxLength

    @property
    def type_validator(self):
        return val.instance_of(str)

    @property
    def validators(self):
        validators: List[val.Validator] = super().validators
        if not isinstance(self.format, NotPassed):
            validators.append(val.has_format(self.format))
        if not isinstance(self.pattern, NotPassed):
            validators.append(val.pattern(self.pattern))
        if not isinstance(self.minLength, NotPassed):
            validators.append(val.min_length(self.minLength))
        if not isinstance(self.maxLength, NotPassed):
            validators.append(val.max_length(self.maxLength))
        return validators


class Array(Element):
    """JSONSchema array element.

    Requires schema element for "items" keyword as first positional
    argument. Supported validation keywords provided via keyword arguments.
    """

    _REPR_FIELDS = ("required", "default", "minItems", "maxItems")

    def __init__(
        self,
        items: Element,
        *,
        required: bool = False,
        default: Union[list, NotPassed] = NotPassed(),
        # Bad name to match JSONSchema keywords.
        # pylint: disable=invalid-name
        minItems: Union[int, NotPassed] = NotPassed(),
        maxItems: Union[int, NotPassed] = NotPassed(),
    ):
        self.items = items
        self.required = required
        self.default = default
        # Bad name to match JSONSchema keywords.
        # pylint: disable=invalid-name
        self.minItems = minItems
        self.maxItems = maxItems

    @property
    def type_validator(self):
        return val.instance_of(list)

    @property
    def validators(self):
        validators = super().validators
        if not isinstance(self.minItems, NotPassed):
            validators.append(val.min_items(self.minItems))
        if not isinstance(self.maxItems, NotPassed):
            validators.append(val.max_items(self.maxItems))
        return validators

    def construct(self, instance, attribute, value):
        return [
            self.items(instance, Attribute(attribute.name + f"[{idx}]"), item)
            for idx, item in enumerate(value)
        ]


class CompositionElement(Element):
    """Composition Base Element.

    The "oneOf", "anyOf" and "allOf" schemas share the same interface.
    """

    _REPR_FIELDS = ("elements", "required", "default")

    def __init__(
        self,
        *elements: Union[JSONSchemaModelMeta, Element],
        required: bool = False,
        default: Any = NotPassed(),
    ):
        self.elements = elements
        self.required = required
        self.default = default

    @abstractmethod
    def construct(self, _instance, _attribute, _value):
        raise NotImplementedError


class AnyOf(CompositionElement):
    """Any one of a list of possible models/sub-schemas."""

    def construct(self, instance, attribute, value):
        try:
            return next(
                _attempt_schemas(self.elements, instance, attribute, value)
            )
        except StopIteration:
            raise ValidationError.no_composition_match(self.elements, value)


class OneOf(CompositionElement):
    """Exactly one of a list of possible models/sub-schemas."""

    def construct(self, instance, attribute, value):
        instantiated = list(
            _attempt_schemas(self.elements, instance, attribute, value)
        )
        if not instantiated:
            raise ValidationError.no_composition_match(self.elements, value)
        if len(instantiated) > 1:
            raise ValidationError.mutliple_composition_match(
                [type(instance) for instance in instantiated], value
            )
        return instantiated[0]


def _attempt_schema(
    element: Element, instance: Any, attribute: str, value: Any
) -> Tuple[bool, Any]:
    try:
        return True, element(instance, attribute, value)
    except (TypeError, ValidationError):
        return False, None


def _attempt_schemas(
    elements: List[Element], instance: Any, attribute: str, value: Any
) -> Iterator[Any]:
    return iter(
        map(
            lambda res: res[1],
            filter(
                lambda res: res[0],
                [
                    _attempt_schema(element, instance, attribute, value)
                    for element in elements
                ],
            ),
        )
    )


class Attribute(NamedTuple):
    """Schema in context of enclosing attribute."""

    name: str
    schema: Optional[Element] = None


class JSONSchemaModel(metaclass=JSONSchemaModelMeta):
    """Base model for JSONSchema objects.

    Recursively validates and construct properties.
    """

    schema_properties: Dict[str, Union[JSONSchemaModelMeta, Element]]

    def __init__(self, kwargs):
        unexpected_kwargs = set(kwargs) - set(self.schema_properties)
        if unexpected_kwargs:
            raise ValidationError(
                f"Unexpected attributes passed to {self.__class__}: "
                f"{unexpected_kwargs}. Accepted kwargs: "
                f"{set(self.schema_properties)}"
            )
        for attr_name, sub_schema in self.schema_properties.items():
            setattr(
                self,
                attr_name,
                sub_schema(
                    self,
                    Attribute(attr_name, sub_schema),
                    kwargs.get(attr_name, NotPassed()),
                ),
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


class StringWrapper(JSONSchemaModel):

    value = String(minLength=3, required=True)


class MyModel(JSONSchemaModel):

    list_of_stuff = Array(
        OneOf(Object(StringWrapper), String(minLength=3)), minItems=1
    )


if __name__ == "__main__":
    from contextlib import contextmanager

    @contextmanager
    def assert_raises(*exception_types: Type[Exception]):
        exception_types = exception_types or (Exception,)
        try:
            yield
        except exception_types:
            return
        assert False, f"Did not raise"

    assert StringWrapper({"value": "foo"})
    for idx, bad_args in enumerate([dict(value="fo"), dict(), dict(value=3)]):
        print(idx)
        with assert_raises(ValidationError):
            StringWrapper(bad_args)

    for idx, good_args in enumerate(
        [
            dict(),
            dict(list_of_stuff=["foo"]),
            dict(list_of_stuff=[{"value": "foo"}]),
            dict(list_of_stuff=[StringWrapper({"value": "foo"})]),
            dict(
                list_of_stuff=[
                    "foo",
                    {"value": "foo"},
                    StringWrapper({"value": "foo"}),
                ]
            ),
            dict(list_of_stuff=[1, {"value": "foo"}]),
        ]
    ):
        print(idx)
        assert MyModel(good_args)

    for idx, bad_args in enumerate(
        [
            dict(list_of_stuff=[]),
            dict(list_of_stuff=["fo"]),
            dict(list_of_stuff=[1]),
            dict(list_of_stuff=[{"value": 1}]),
            dict(list_of_stuff=["foo", {"value": 1}]),
            dict(list_of_stuff=[1, {"value": "foo"}]),
        ]
    ):
        print(idx)
        with assert_raises(ValidationError):
            MyModel(bad_args)

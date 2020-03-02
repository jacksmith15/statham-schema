from abc import ABC, abstractmethod
from typing import (
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
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
    @classmethod
    def __prepare__(mcs, _name, _bases):
        return JSONSchemaClassDict()

    def __new__(
        mcs, name: str, bases: Tuple[Type], classdict: JSONSchemaClassDict
    ):
        result = type.__new__(mcs, name, bases, dict(classdict))
        result.schema_properties = classdict.schema_properties
        return result

    def __repr__(self):
        props = ", ".join(
            [f"{key}={elem}" for key, elem in self.schema_properties.items()]
        )
        return f"{self.__name__}(properties={self.schema_properties})"


@attrs(kw_only=True)
class Element(ABC):
    """Schema element for composing instantiation logic."""

    required: bool = attrib(validator=[instance_of(bool)], default=False)

    @property
    def validators(self):
        return [val.required(self.required)]

    def construct(self, _instance, _attribute, value):
        return value

    def __call__(self, instance, attribute, value):
        """Allow different instantiation logic per sentinel."""
        for validator in self.validators:
            validator(instance, attribute, value)
        if isinstance(value, NotPassed):
            return value
        return self.construct(instance, attribute, value)


def provided(value: Any) -> bool:
    return not isinstance(value, NotPassed)


def _if_provided(validator: Callable, value: Any) -> Optional[Callable]:
    return validator(value) if provided(value) else None


class Object(Element):
    def __init__(
        self, model: Union[JSONSchemaModelMeta, Element], required: bool = False
    ):
        instance_of((JSONSchemaModelMeta, Element))(self, "model", model)
        self.model: Union[JSONSchemaModelMeta, Element] = model
        self.required = required

    def __repr__(self):
        if isinstance(self.model, Element):
            return repr(Element)
        return (
            f"{self.__class__.__name__}"
            f"(properties={repr(self.model)}, required={self.required})"
        )

    @property
    def validators(self):
        return super().validators + [val.instance_of(dict, JSONSchemaModel)]

    def construct(self, instance, attribute, value):
        if isinstance(self.model, Element):
            return self.model(instance, attribute, value)
        if isinstance(value, self.model):
            return value
        return self.model(**value)


@attrs(kw_only=True)
class String(Element):

    default: Union[str, NotPassed] = attrib(
        validator=[instance_of((str, NotPassed))], default=NotPassed()
    )
    format: Union[str, NotPassed] = attrib(
        validator=[instance_of((str, NotPassed))], default=NotPassed()
    )
    pattern: Union[str, NotPassed] = attrib(
        validator=[instance_of((str, NotPassed))], default=NotPassed()
    )
    # pylint: disable=invalid-name
    minLength: Union[int, NotPassed] = attrib(
        validator=[instance_of((int, NotPassed))], default=NotPassed()
    )
    maxLength: Union[int, NotPassed] = attrib(
        validator=[instance_of((int, NotPassed))], default=NotPassed()
    )

    @property
    def validators(self):
        return super().validators + list(
            filter(
                None,
                [
                    val.instance_of(str),
                    _if_provided(val.has_format, self.format),
                    _if_provided(val.pattern, self.pattern),
                    _if_provided(val.min_length, self.minLength),
                    _if_provided(val.max_length, self.maxLength),
                ],
            )
        )


class Array(Element):
    """Schema element for instantiating objects in a list."""

    def __init__(
        self,
        items: Union[JSONSchemaModelMeta, Element],
        minItems: Union[int, NotPassed] = NotPassed(),
        maxItems: Union[int, NotPassed] = NotPassed(),
        required: bool = False,
    ):
        self.items = items
        self.minItems = minItems
        self.maxItems = maxItems
        self.required = required

    @property
    def validators(self):
        return super().validators + list(
            filter(
                None,
                [
                    _if_provided(val.min_items, self.minItems),
                    _if_provided(val.max_items, self.maxItems),
                ],
            )
        )

    def construct(self, instance, attribute, value):
        return [
            self.items(instance, Attribute(attribute.name + f"[{idx}]"), item)
            for idx, item in enumerate(value)
        ]


class AnyOf(Element):
    """Any one of a list of possible models/sub-schemas."""

    def __init__(
        self,
        *elements: Union[JSONSchemaModelMeta, Element],
        required: bool = False,
    ):
        self.elements = elements
        self.required = required

    def construct(self, instance, attribute, value):
        try:
            return next(
                _attempt_schemas(self.elements, instance, attribute, value)
            )
        except StopIteration:
            raise ValidationError.no_composition_match(self.elements, value)


class OneOf(Element):
    """Exactly one of a list of possible models/sub-schemas."""

    def __init__(self, *elements: Element, required: bool = False):
        self.elements = elements
        self.required = required

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


# def _instantiate(model: Union[Type, Element]):
#     """Converter factory for instantiating a model from dictionary.

#     This allow passing either a model instance or instantiating a new
#     one from a dictionary.
#     """

#     def _convert(instance, attribute, value):
#         if isinstance(model, Element):
#             return model(instance, attribute, value)
#         if isinstance(value, (model, NotPassed)):
#             return value
#         return model(**value)

#     return _convert


# def _safe_instantiate(model: Union[Type, Element]):
#     """Converter which attempts to instantiate, returning None on a failure."""
#     instantiator = _instantiate(model)

#     def _convert(instance, attribute, value):
#         try:
#             return instantiator(value)
#         except (TypeError, ValidationError):
#             return None

#     return _convert


class Attribute:
    def __init__(self, name):
        self.name = name


class JSONSchemaModel(metaclass=JSONSchemaModelMeta):

    schema_properties: Dict[str, Union[JSONSchemaModelMeta, Element]]

    def __init__(self, **kwargs):
        unexpected_kwargs = set(kwargs) - set(self.schema_properties)
        if unexpected_kwargs:
            raise ValidationError(
                f"Unexpected kwargs to {self.__class__}: "
                f"{unexpected_kwargs}. Accepted kwargs: "
                f"{set(self.schema_properties)}"
            )
        for attr_name, sub_schema in self.schema_properties.items():
            setattr(
                self,
                attr_name,
                sub_schema(
                    self,
                    Attribute(attr_name),
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


class StringWrapper(JSONSchemaModel):
    value = String(minLength=3, required=True)


class MyModel(JSONSchemaModel):
    list_of_stuff = Array(
        OneOf(Object(StringWrapper), String(minLength=3)), minItems=1
    )

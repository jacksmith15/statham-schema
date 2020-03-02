from abc import ABC, abstractmethod
from typing import Any, Callable, List, Tuple, Type, Union

from attr import attrs, attrib

from statham import validators as val
from statham.exceptions import ValidationError
from statham.validators import NotPassed


class JSONSchemaClassDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        schema_keys = [
            key
            for key, value in self.items()
            if isinstance(value, (JSONSchemaModel, SchemaElement))
        ]
        self._schema_properties = {key: self.pop(key) for key in schema_keys}

    def __setitem__(self, key, value):
        if isinstance(value, (JSONSchemaModel, SchemaElement)):
            return self._schema_properties.__setitem__(key, value)
        return super().__setitem__(key, value)


class JSONSchemaModel(type):
    @classmethod
    def __prepare__(cls, _name, _bases):
        return JSONSchemaClassDict()

    def __new__(
        cls, name: str, bases: Tuple[Type], classdict: JSONSchemaClassDict
    ):
        result = type.__new__(cls, name, bases, dict(classdict))
        result._schema_properties = classdict._schema_properties
        return result


class SchemaElement(ABC):
    """Schema element for composing instantiation logic."""

    @property
    def validators(self) -> List[Callable]:
        return []

    def __call__(self, data):
        """Allow different instantiation logic per sentinel."""


def provided(value: Any) -> bool:
    return not isinstance(value, NotPassed)


@attrs(kw_only=True, frozen=True)
class String(SchemaElement):

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
        return list(
            filter(
                None,
                [
                    val.instance_of(str),
                    val.has_format(self.format)
                    if provided(self.has_format)
                    else None,
                    val.pattern(self.pattern)
                    if provided(self.pattern)
                    else None,
                    val.minLength(self.minLength)
                    if provided(self.minLength)
                    else None,
                    val.maxLength(self.maxLength)
                    if provided(self.maxLength)
                    else None,
                ],
            )
        )


class Array(SchemaElement):
    """Schema element for instantiating objects in a list."""

    def __init__(self, model: SchemaElement):
        self.model = model
        self._factory = _instantiate(model)

    def __call__(self, data):
        if isinstance(data, NotPassed):
            return data
        return [self._factory(data) for data in data]


class AnyOf(SchemaElement):
    """Schema element for any one of a list of possible models/sub-schemas."""

    def __init__(self, *models: Type):
        self.models = models

    def __call__(self, data):
        if not isinstance(data, (dict, list)):
            return data
        try:
            return next(
                filter(
                    None,
                    [_safe_instantiate(model)(data) for model in self.models],
                )
            )
        except StopIteration:
            raise ValidationError.no_composition_match(self.models, data)


class OneOf(SchemaElement):
    """Schema element for exactly one of a list of possible models/sub-schemas."""

    def __init__(self, *models: Type):
        self.models = models

    def __call__(self, data):
        if not isinstance(data, (dict, list)):
            return data
        instantiated = list(
            filter(
                None, [_safe_instantiate(model)(data) for model in self.models]
            )
        )
        if not instantiated:
            raise ValidationError.no_composition_match(self.models, data)
        if len(instantiated) > 1:
            raise ValidationError.mutliple_composition_match(
                [type(instance) for instance in instantiated], data
            )
        return instantiated[0]


def _instantiate(model: Union[Type, SchemaElement]):
    """Converter factory for instantiating a model from dictionary.

    This allow passing either a model instance or instantiating a new
    one from a dictionary.
    """

    def _convert(data):
        if isinstance(model, SchemaElement):
            return model.instantiate(data)
        if isinstance(data, (model, NotPassed)):
            return data
        return model(**data)

    return _convert


def _safe_instantiate(model: Union[Type, SchemaElement]):
    """Converter which attempts to instantiate, returning None on a failure."""
    instantiator = _instantiate(model)

    def _convert(data):
        try:
            return instantiator(data)
        except (TypeError, ValidationError):
            return None

    return _convert


class StringWrapper(metaclass=JSONSchemaModel):
    value = String(minLength=3, required=True)


class MyModel(metaclass=JSONSchemaModel):
    list_of_stuff = Array(
        OneOf(
            StringWrapper,
            String(minLength=3),
            Array(String(minLength=1, maxLength=1), minItems=1),
        )
    )

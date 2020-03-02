from abc import ABC, abstractmethod

from typing import Type, Union

from statham.exceptions import ValidationError
from statham.validators import NotPassed


class Constructor(ABC):
    """Constructor for composing instantiation logic."""

    @abstractmethod
    def __repr__(self):
        """Representation should show full hierarchy."""

    @abstractmethod
    def instantiate(self, data):
        """Allow different instantiation logic per sentinel."""


TypeItem = Union[Type, Constructor]


def _repr(type_item: TypeItem) -> str:
    if isinstance(type_item, Constructor):
        return repr(type_item)
    return type_item.__name__


class Array(Constructor):
    """Constructor for instantiating objects in a list."""

    def __init__(self, model: TypeItem):
        self.model = model
        self._factory = instantiate(model)

    def __repr__(self):
        return f"{type(self).__name__}({_repr(self.model)})"

    def instantiate(self, data):
        if isinstance(data, NotPassed):
            return data
        return [self._factory(data) for data in data]


class AnyOf(Constructor):
    """Constructor for any one of a list of possible models/sub-schemas."""

    def __init__(self, *models: Type):
        self.models = models

    def __repr__(self):
        models = ", ".join((_repr(model) for model in self.models))
        return f"{type(self).__name__}({models})"

    def instantiate(self, data):
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


class OneOf(Constructor):
    """Constructor for exactly one of a list of possible models/sub-schemas."""

    def __init__(self, *models: Type):
        self.models = models

    def __repr__(self):
        models = ", ".join((_repr(model) for model in self.models))
        return f"{type(self).__name__}({models})"

    def instantiate(self, data):
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


def instantiate(model: TypeItem):
    """Converter factory for instantiating a model from dictionary.

    This allow passing either a model instance or instantiating a new
    one from a dictionary.
    """

    def _convert(data):
        if isinstance(model, Constructor):
            return model.instantiate(data)
        if isinstance(data, (model, NotPassed)):
            return data
        return model(**data)

    return _convert


def _safe_instantiate(model: TypeItem):
    """Converter which attempts to instantiate, returning None on a failure."""
    instantiator = instantiate(model)

    def _convert(data):
        try:
            return instantiator(data)
        except (TypeError, ValidationError):
            return None

    return _convert

from typing import Type

from statham.exceptions import ValidationError
from statham.validators import NotPassed


def instantiate(model: Type):
    """Converter factory for instantiating a model from dictionary.

    This allow passing either a model instance or instantiating a new
    one from a dictionary.
    """

    def _convert(data):
        if isinstance(data, (model, NotPassed)):
            return data
        return model(**data)

    return _convert


def map_instantiate(model: Type):
    """Converter factory for instantiating a list of models.

    This allows passing a mixed list of instances and dictionaries and
    receiving a list of instances.
    """
    _factory = instantiate(model)

    def _convert(list_data):
        if isinstance(list_data, NotPassed):
            return list_data
        return [_factory(data) for data in list_data]

    return _convert


def _safe_instantiate(model: Type):
    """Converter which attempts to instantiate, returning None on a failure."""
    instantiator = instantiate(model)

    def _convert(data):
        try:
            return instantiator(data)
        except (TypeError, ValidationError):
            return None

    return _convert


def any_of_instantiate(*models: Type):
    """Instantiate against any of the provided models.

    Fail if none of the models instantiate succesfully.
    """

    def _convert(data):
        if not isinstance(data, (dict, list)):
            return data
        try:
            return next(
                filter(
                    None, [_safe_instantiate(model)(data) for model in models]
                )
            )
        except StopIteration:
            raise ValidationError.no_composition_match(models, data)

    return _convert


def one_of_instantiate(*models: Type):
    """Instantiate against one of the provided models.

    Fails if more than one model matches the input.
    """

    def _convert(data):
        if not isinstance(data, (dict, list)):
            return data
        instantiated = list(
            filter(None, [_safe_instantiate(model)(data) for model in models])
        )
        if not instantiated:
            raise ValidationError.no_composition_match(models, data)
        if len(instantiated) > 1:
            raise ValidationError.mutliple_composition_match(
                [type(instance) for instance in instantiated], data
            )
        return instantiated[0]

    return _convert

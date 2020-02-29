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


def any_of_instantiate(*models: Type):
    def _convert(data):
        if not isinstance(data, (dict, list)):
            return data
        for model in models:
            try:
                return instantiate(model)(data)
            except (TypeError, ValidationError):
                continue
        raise ValidationError.from_composition(models, data)

    return _convert

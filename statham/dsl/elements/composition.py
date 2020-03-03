from abc import abstractmethod
from typing import Any, Iterator, List, Tuple, Union

from statham.dsl.elements.base import Element
from statham.dsl.elements.meta import JSONSchemaModelMeta
from statham.exceptions import ValidationError
from statham.validators import NotPassed


class CompositionElement(Element):
    """Composition Base Element.

    The "oneOf", "anyOf" and "allOf" schemas share the same interface.
    """

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

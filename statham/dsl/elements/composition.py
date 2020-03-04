from abc import abstractmethod
from typing import Any, Iterator, List, Tuple

from statham.dsl.elements.base import Element
from statham.dsl.property import _Property
from statham.exceptions import ValidationError
from statham.dsl.constants import NotPassed


class CompositionElement(Element):
    """Composition Base Element.

    The "oneOf", "anyOf" and "allOf" schemas share the same interface.
    """

    def __init__(self, *elements: Element, default: Any = NotPassed()):
        self.elements = list(elements)
        self.default = default

    @abstractmethod
    def construct(self, property_: _Property, _value: Any):
        raise NotImplementedError


class AnyOf(CompositionElement):
    """Any one of a list of possible models/sub-schemas."""

    def construct(self, property_: _Property, value: Any):
        try:
            return next(_attempt_schemas(self.elements, property_, value))
        except StopIteration:
            raise ValidationError.no_composition_match(self.elements, value)


class OneOf(CompositionElement):
    """Exactly one of a list of possible models/sub-schemas."""

    def construct(self, property_: _Property, value: Any):
        instantiated = list(_attempt_schemas(self.elements, property_, value))
        if not instantiated:
            raise ValidationError.no_composition_match(self.elements, value)
        if len(instantiated) > 1:
            raise ValidationError.mutliple_composition_match(
                [type(instance) for instance in instantiated], value
            )
        return instantiated[0]


def _attempt_schema(
    element: Element, property_: _Property, value: Any
) -> Tuple[bool, Any]:
    try:
        return True, element(property_, value)
    except (TypeError, ValidationError):
        return False, None


def _attempt_schemas(
    elements: List[Element], property_: _Property, value: Any
) -> Iterator[Any]:
    return iter(
        map(
            lambda res: res[1],
            filter(
                lambda res: res[0],
                [
                    _attempt_schema(element, property_, value)
                    for element in elements
                ],
            ),
        )
    )

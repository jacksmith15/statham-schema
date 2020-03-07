from abc import abstractmethod
from typing import Any, List, NamedTuple, Optional

from statham.dsl.elements.base import Element
from statham.dsl.property import _Property
from statham.exceptions import ValidationError
from statham.dsl.constants import NotPassed


class CompositionElement(Element):
    """Composition Base Element.

    The "oneOf", "anyOf" and "allOf" schemas share the same interface.
    """

    def __init__(self, *elements: Element, default: Any = NotPassed()):
        super().__init__()
        self.elements = list(elements)
        if not self.elements:
            raise TypeError(f"{type(self)} requires at least one sub-schema.")
        self.default = default

    @property
    def annotation(self):
        if len(self.elements) == 1:
            return self.elements[0].annotation
        annotations = ", ".join(
            [element.annotation for element in self.elements]
        )
        return f"Union[{annotations}]"

    @abstractmethod
    def construct(self, property_: _Property, _value: Any):
        raise NotImplementedError


class AnyOf(CompositionElement):
    """Any one of a list of possible models/sub-schemas."""

    def construct(self, property_: _Property, value: Any):
        return _attempt_schemas(self.elements, property_, value)[0].result


class OneOf(CompositionElement):
    """Exactly one of a list of possible models/sub-schemas."""

    def construct(self, property_: _Property, value: Any):
        instantiated = _attempt_schemas(self.elements, property_, value)
        if len(instantiated) > 1:
            raise ValidationError.mutliple_composition_match(
                [type(instance) for instance in instantiated], value
            )
        return instantiated[0].result


class Outcome(NamedTuple):

    target: Element
    result: Optional[Any] = None
    error: Optional[str] = None


def _attempt_schema(
    element: Element, property_: _Property, value: Any
) -> Outcome:
    try:
        return Outcome(element, result=element(property_, value), error=None)
    except (TypeError, ValidationError) as exc:
        return Outcome(element, result=None, error=str(exc))


def _attempt_schemas(
    elements: List[Element], property_: _Property, value: Any
) -> List[Outcome]:
    outcomes = [
        _attempt_schema(element, property_, value) for element in elements
    ]
    results = [outcome for outcome in outcomes if not outcome.error]
    if results:
        return results
    errors = ", ".join(filter(None, [outcome.error for outcome in outcomes]))
    message = f"Does not match any accepted schema. Individual errors: {errors}"
    raise ValidationError.from_validator(property_, value, message)

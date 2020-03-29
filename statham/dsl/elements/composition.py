from typing import Any, List, NamedTuple, Optional
from typing_extensions import Literal

from statham.dsl.elements.base import Element
from statham.dsl.exceptions import ValidationError
from statham.dsl.property import _Property
from statham.dsl.constants import NotPassed


# TODO: if, then, else

# This is a type annotation.
Mode = Literal["anyOf", "oneOf", "allOf"]  # pylint: disable=invalid-name


class CompositionElement(Element):
    """Composition Base Element.

    The "oneOf" and "anyOf" schemas share the same interface.
    # TODO: not
    # TODO: allOf
    # TODO: Support outer keywords
    """

    mode: Mode

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

    def construct(self, value: Any, property_: _Property):
        if not getattr(self, "mode", None):
            raise NotImplementedError
        return _attempt_schemas(self.elements, value, property_, mode=self.mode)


class AnyOf(CompositionElement):
    """Must match at least on of the provided schemas."""

    mode: Mode = "anyOf"


class OneOf(CompositionElement):
    """Must match exactly one of the provided schemas.."""

    mode: Mode = "oneOf"


class AllOf(CompositionElement):
    """Must match all provided schemas."""

    mode: Mode = "allOf"


class Outcome(NamedTuple):

    target: Element
    result: Optional[Any] = None
    error: Optional[Exception] = None


def _attempt_schema(
    element: Element, value: Any, property_: _Property
) -> Outcome:
    """Attempt to pass an input to a schema element.

    :return: An `Outcome` object describing containing success/failure
        information and a result if successful.
    """
    try:
        return Outcome(element, result=element(value, property_), error=None)
    except (TypeError, ValidationError) as exc:
        return Outcome(element, result=None, error=exc)


def _attempt_schemas(
    elements: List[Element],
    value: Any,
    property_: _Property,
    mode: str = "anyOf",
) -> Any:
    """Attempt to instantiate a given input against many elements.

    :param elements: The elements against which to validate.
    :param property_: The enclosing property.
    :param value: The data to validate against.
    :param mode: The matching stategy to use. "allOf", "anyOf" or "oneOf".
    :return: A list of successful instantiations against `elements`.
    :raises ValidationError: if there are no matching schemas.
    :raises ValueError: if passed an invalid mode.
    """
    outcomes = [
        _attempt_schema(element, value, property_) for element in elements
    ]
    results = [outcome.result for outcome in outcomes if not outcome.error]
    errors = [outcome.error for outcome in outcomes if outcome.error]
    if not results:
        raise ValidationError.combine(
            property_, value, errors, "Does not match any accepted schema."
        )

    if mode == "anyOf":
        return results[0]
    if mode == "oneOf":
        if len(results) > 1:
            raise ValidationError.multiple_composition_match(
                [type(instance) for instance in results], value
            )
        return results[0]
    if mode == "allOf":
        if errors:
            raise ValidationError.combine(
                property_, value, errors, "Does not match all required schemas."
            )
        return results[0]
    raise ValueError(f"Got bad argument for `mode`: {mode}")  # pragma: no cover

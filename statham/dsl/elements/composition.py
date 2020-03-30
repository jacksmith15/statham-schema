from typing import Any, Iterable, List, NamedTuple, Optional, Set, TypeVar
from typing_extensions import Literal

from statham.dsl.elements.base import Element
from statham.dsl.exceptions import ValidationError
from statham.dsl.property import _Property
from statham.dsl.constants import NotPassed


# TODO: if, then, else

# This is a type annotation.
Mode = Literal["anyOf", "oneOf", "allOf"]  # pylint: disable=invalid-name
T = TypeVar("T")


def _dedupe(seq: Iterable[T]) -> List[T]:
    seen: Set[T] = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


class Not(Element[T]):
    """JSONSchema "not" element.

    Element fails to validate if enclosed schema validates.
    """

    def __init__(self, element: Element, default: Any = NotPassed()):
        self.element = element
        super().__init__(default=default)

    def construct(self, value: Any, property_: _Property):
        if value is NotPassed():
            return value
        try:
            _ = self.element(value, property_)
        except (TypeError, ValidationError):
            return value
        raise ValidationError.from_validator(
            property_, value, f"Must not match {self.element}."
        )


class CompositionElement(Element):
    """Composition Base Element.

    The "oneOf", "anyOf" and "allOf" elements share the same interface.
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
        annotations = _dedupe(elem.annotation for elem in self.elements)
        if len(annotations) == 1:
            return annotations[0]
        if "Any" in annotations:
            return "Any"
        joined = ", ".join([annotation for annotation in annotations])
        return f"Union[{joined}]"

    def construct(self, value: Any, property_: _Property):
        if not getattr(self, "mode", None):
            raise NotImplementedError
        return _attempt_schemas(self.elements, value, property_, mode=self.mode)


class AnyOf(CompositionElement):
    """Must match at least one of the provided schemas."""

    mode: Mode = "anyOf"


class OneOf(CompositionElement):
    """Must match exactly one of the provided schemas.."""

    mode: Mode = "oneOf"


class AllOf(CompositionElement):
    """Must match all provided schemas."""

    mode: Mode = "allOf"

    @property
    def annotation(self):
        """Get type annotation for element.

        With an AllOf element, this should be the most restrictive
        type. On the assumption that the composition is possible, this
        is chosen by returning the first explicit type annotation, or the
        first union type annotation if no explicit annotations are
        present.
        """
        return next(
            (
                elem.annotation
                for elem in self.elements
                if elem.annotation != "Any"
                and not elem.annotation.startswith("Union")
            ),
            next(
                (
                    elem.annotation
                    for elem in self.elements
                    if elem.annotation != "Any"
                ),
                "Any",
            ),
        )


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
                [outcome.target for outcome in outcomes if not outcome.error],
                value,
            )
        return results[0]
    if mode == "allOf":
        if errors:
            raise ValidationError.combine(
                property_, value, errors, "Does not match all required schemas."
            )
        return results[0]
    raise ValueError(f"Got bad argument for `mode`: {mode}")  # pragma: no cover

from typing import Iterator, Type

from statham.dsl.validation.array import AdditionalItems, MinItems, MaxItems
from statham.dsl.validation.base import InstanceOf, NoMatch, Validator
from statham.dsl.validation.numeric import (
    Minimum,
    Maximum,
    ExclusiveMinimum,
    ExclusiveMaximum,
    MultipleOf,
)
from statham.dsl.validation.object import AdditionalProperties, Required
from statham.dsl.validation.string import MinLength, MaxLength, Format, Pattern


def _all_subclasses(klass: Type):
    """Get all explicit and implicit subclasses of a type."""
    return set(klass.__subclasses__()).union(
        [s for c in klass.__subclasses__() for s in _all_subclasses(c)]
    )


def get_validators(element) -> Iterator[Validator]:
    """Iterate all applicable validators for an DSL Element.

    Validators identify whether they are applicable for an element via the
    `from_element` class method. In general, this checks whether its
    parameters are present on the element with correct values.
    """
    for validator_type in _all_subclasses(Validator):
        if validator_type in (InstanceOf, NoMatch):
            continue
        validator = validator_type.from_element(element)
        if validator:
            yield validator

from typing import Iterator, Type

from statham.dsl.validation.array import MinItems, MaxItems
from statham.dsl.validation.base import Validator
from statham.dsl.validation.numeric import (
    Minimum,
    Maximum,
    ExclusiveMinimum,
    ExclusiveMaximum,
    MultipleOf,
)
from statham.dsl.validation.object import AdditionalProperties, Required
from statham.dsl.validation.string import MinLength, MaxLength, Format, Pattern


def all_subclasses(klass: Type):
    return set(klass.__subclasses__()).union(
        [s for c in klass.__subclasses__() for s in all_subclasses(c)]
    )


def validators(element) -> Iterator[Validator]:
    """Get all validators relevant to a DSL element."""
    for validator_type in all_subclasses(Validator):
        validator = validator_type.from_element(element)
        if validator:
            yield validator

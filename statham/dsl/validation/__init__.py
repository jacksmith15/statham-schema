from typing import Iterator, Type

from statham.dsl.validation.array import MinItems, MaxItems
from statham.dsl.validation.base import InstanceOf, Validator
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


def get_validators(element) -> Iterator[Validator]:
    for validator_type in all_subclasses(Validator):
        if validator_type is InstanceOf:
            continue
        validator = validator_type.from_element(element)
        if validator:
            yield validator

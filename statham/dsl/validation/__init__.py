from typing import Iterator, Type

from statham.dsl.validation.base import Validator


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

"""This module contains implementation of JSON Schema validation keywords.

Each keyword is implemented as a subclass of
:class:`~statham.schema.validation.base.Validator`, and is instantiated with
the relevant keywords. :class:`~statham.schema.validation.base.Validator`
instances may then be called to validate values.

:class:`~statham.schema.elements.Element` automatically detects and instantiates
its relevant validators, but validators may be used directly:

.. code:: python

    from statham.schema.validation import Minimum

    validator = Minimum(minimum=3)
    validator(5, None)  # OK
    validator(2, None)  # ValidationError

"""
from typing import Iterator, Type

from statham.schema.validation.array import (
    AdditionalItems,
    Contains,
    MinItems,
    MaxItems,
    UniqueItems,
)
from statham.schema.validation.base import (
    Const,
    Enum,
    InstanceOf,
    NoMatch,
    Validator,
)
from statham.schema.validation.format import format_checker
from statham.schema.validation.numeric import (
    Minimum,
    Maximum,
    ExclusiveMinimum,
    ExclusiveMaximum,
    MultipleOf,
)
from statham.schema.validation.object import (
    AdditionalProperties,
    Dependencies,
    MaxProperties,
    MinProperties,
    PropertyNames,
    Required,
)
from statham.schema.validation.string import (
    MinLength,
    MaxLength,
    Format,
    Pattern,
)


def _all_subclasses(klass: Type):
    """Get all explicit and implicit subclasses of a type."""
    return set(klass.__subclasses__()).union(
        [s for c in klass.__subclasses__() for s in _all_subclasses(c)]
    )


def get_validators(element) -> Iterator[Validator]:
    """Iterate all applicable validators for an Element.

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

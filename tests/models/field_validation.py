from typing import List, Union

from statham.dsl.constants import Maybe
from statham.dsl.elements import (
    AnyOf,
    Array,
    Boolean,
    Integer,
    Null,
    Number,
    OneOf,
    Object,
    String,
)
from statham.dsl.property import Property


class Model(Object):

    string_no_validation: Maybe[str] = Property(String())

    string_default: str = Property(String(default="foo"))

    string_format_uuid: Maybe[str] = Property(String(format="uuid"))

    string_format_date_time: Maybe[str] = Property(String(format="date-time"))

    string_format_uri: Maybe[str] = Property(String(format="uri"))

    string_pattern: Maybe[str] = Property(String(pattern="^(foo|bar).*"))

    string_minLength: Maybe[str] = Property(String(minLength=3))

    string_maxLength: Maybe[str] = Property(String(maxLength=3))

    integer_no_validation: Maybe[int] = Property(Integer())

    integer_default: int = Property(Integer(default=1))

    integer_minimum: Maybe[int] = Property(Integer(minimum=3))

    integer_exclusiveMinimum: Maybe[int] = Property(Integer(exclusiveMinimum=3))

    integer_maximum: Maybe[int] = Property(Integer(maximum=3))

    integer_exclusiveMaximum: Maybe[int] = Property(Integer(exclusiveMaximum=3))

    integer_multipleOf: Maybe[int] = Property(Integer(multipleOf=2))

    number_no_validation: Maybe[float] = Property(Number())

    number_default: float = Property(Number(default=1.5))

    number_minimum: Maybe[float] = Property(Number(minimum=2.5))

    number_exclusiveMinimum: Maybe[float] = Property(
        Number(exclusiveMinimum=2.5)
    )

    number_maximum: Maybe[float] = Property(Number(maximum=2.5))

    number_exclusiveMaximum: Maybe[float] = Property(
        Number(exclusiveMaximum=2.5)
    )

    number_multipleOf: Maybe[float] = Property(Number(multipleOf=2.5))

    boolean_no_validation: Maybe[bool] = Property(Boolean())

    boolean_default: bool = Property(Boolean(default=True))

    null_no_validation: Maybe[None] = Property(Null())

    array_no_validation: Maybe[List[int]] = Property(Array(Integer()))

    array_minItems: Maybe[List[int]] = Property(Array(Integer(), minItems=1))

    array_maxItems: Maybe[List[int]] = Property(Array(Integer(), maxItems=2))

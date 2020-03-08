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


class NestedSchema(Object):

    id: str = Property(
        String(
            format="uuid",
            pattern="^[0-9a-fA-F]{8}\\-[0-9a-fA-F]{4}\\-[0-9a-fA-F]{4}\\-[0-9a-fA-F]{4}\\-[0-9a-fA-F]{12}$",
        ),
        required=True,
    )

    timestamp: Maybe[str] = Property(
        String(
            format="date-time",
            pattern="^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$",
        )
    )

    version: int = Property(Integer(default=0))

    annotation: str = Property(String(default="unannotated"))


class SimpleSchema(Object):

    related: NestedSchema = Property(NestedSchema, required=True)

    amount: Maybe[float] = Property(Number())

    children: Maybe[List[NestedSchema]] = Property(Array(NestedSchema))

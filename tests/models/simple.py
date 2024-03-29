from typing import List

from statham.schema.constants import Maybe
from statham.schema.elements import Array, Integer, Number, Object, String
from statham.schema.property import Property


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
    """This is a simple object."""

    related: NestedSchema = Property(NestedSchema, required=True)

    amount: Maybe[float] = Property(Number(description="int-bar"))

    children: Maybe[List[NestedSchema]] = Property(Array(NestedSchema))

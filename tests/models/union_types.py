from typing import Any, Union

from statham.schema.elements import AnyOf, Integer, Null, Number, Object, String
from statham.schema.property import Property


class Model(Object):

    number_integer: Union[float, int] = Property(
        AnyOf(
            Number(minimum=2.5, exclusiveMaximum=5),
            Integer(minimum=2.5, exclusiveMaximum=5),
            default=3.5,
        )
    )

    string_integer: Union[str, int] = Property(
        AnyOf(
            String(format="date-time"),
            Integer(minimum=1970, exclusiveMaximum=2050),
            default=2000,
        )
    )

    string_null: Union[str, None] = Property(
        AnyOf(
            String(
                pattern="^[0-9a-fA-F]{8}\\-[0-9a-fA-F]{4}\\-[0-9a-fA-F]{4}\\-[0-9a-fA-F]{4}\\-[0-9a-fA-F]{12}$"
            ),
            Null(),
            default=None,
        )
    )

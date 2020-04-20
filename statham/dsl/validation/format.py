from typing import Callable, Dict
from uuid import UUID
import warnings

from dateutil.parser import parse as parse_datetime, ParserError  # type: ignore


class _FormatString:
    """Extendable format string register.

    # TODO: Built-in formats.
    """

    def __init__(self, name: str):
        self._callable_register: Dict[str, Callable[[str], bool]] = {}
        self.__name__: str = name

    def register(self, format_string: str) -> Callable:
        def _register_callable(is_format: Callable[[str], bool]):
            self._callable_register[format_string] = is_format

        return _register_callable

    def __call__(self, format_string: str, value: str) -> bool:
        if format_string not in self._callable_register:
            full_name = f"{self.__module__}.{self.__name__}"
            warnings.warn(
                (
                    f"""No validator found for format string {format_string}.
To register new formats, please register a checker with
{full_name} as follows:
```
@{self.__name__}({format_string})
def is_{format_string.replace('-', '_')}(value) -> bool:
    ...
```
"""
                ),
                RuntimeWarning,
            )
            return True
        return self._callable_register[format_string](value)


format_checker: _FormatString = _FormatString("format_checker")
"""Extensible implementation of the ``"format"`` keyword.

Validators for new formats may be registered as follows:

.. code:: python

    @format_checker.register("my_format")
    def _validate_my_format(value: str) -> bool:
        # Return True if `value` matches `my_format`.
        ...
"""


@format_checker.register("uuid")
def _is_uuid(value: str) -> bool:
    try:
        UUID(value)
    except (ValueError, TypeError):
        return False
    return True


@format_checker.register("date-time")
def _is_date_time(value: str) -> bool:
    try:
        parse_datetime(value)
    except (ParserError, TypeError):
        return False
    return True

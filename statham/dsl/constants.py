from typing import Any, Dict, List, TypeVar, Union


JSONElement = Union[Dict[str, Any], List[Any], int, float, bool, None, str]


class NotPassed:
    """Singleton similar to NoneType.

    To distinguish between arguments not passed, and arguments passed as
    None.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """Enforce singleton."""
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __repr__(self) -> str:
        return "NotPassed"

    def __bool__(self) -> bool:
        return False


T = TypeVar("T")

Maybe = Union[T, NotPassed]


COMPOSITION_KEYWORDS = ("anyOf", "oneOf")

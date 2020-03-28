from typing import Any, ClassVar, Optional, Tuple, Type

from statham.dsl.constants import NotPassed
from statham.dsl.exceptions import ValidationError


def _is_instance(value, type_args):
    """Variant of isinstance to handle booleans correctly.

    In CPython, isinstance(True, int) evaluates True.
    """
    if isinstance(value, bool):
        if bool in type_args:
            return True
        return False
    return isinstance(value, type_args)


class Validator:

    types: ClassVar[Optional[Tuple[Type, ...]]] = None
    message: ClassVar[str] = ""
    keywords: Tuple[str, ...] = tuple()

    def __init__(self, *args):
        if len(self.keywords) != len(args):
            raise TypeError(
                f"{type(self).__name__}.__init__ takes exactly "
                f"{len(self.keywords)} ({len(args)} given)"
            )
        self.params = dict(zip(self.keywords, args))

    @classmethod
    def from_element(cls, element) -> Optional["Validator"]:
        params = tuple(
            getattr(element, keyword, NotPassed()) for keyword in cls.keywords
        )
        if NotPassed() in params:
            return None
        return cls(*params)

    # pylint: disable=no-self-use
    def validate(self, _value: Any):
        return

    def error_message(self):
        return self.message.format(**self.params)

    def __call__(self, value: Any, property_: Any):
        if self.types and not _is_instance(value, self.types):
            return
        try:
            self.validate(value)
        except ValidationError:
            raise ValidationError.from_validator(
                property_, value, self.error_message()
            )


class InstanceOf(Validator):
    message = "Must be of type {type_names}."

    def __init__(self, *args):
        super().__init__()
        self.params["types"] = args
        names = (type_.__name__ for type_ in self.params["types"])
        self.params["type_names"] = f"({','.join(names)})"

    def validate(self, value: Any):
        if value == NotPassed() or not self.params["types"]:
            return
        if not _is_instance(value, self.params["types"]):
            raise ValidationError

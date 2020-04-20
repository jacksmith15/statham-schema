from typing import Any, ClassVar, Optional, Tuple, Type

from statham.dsl.constants import NotPassed
from statham.dsl.exceptions import ValidationError


_TRUE = object()
_FALSE = object()


def replace_bool(value: Any) -> Any:
    return _TRUE if value is True else _FALSE if value is False else value


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
    """Base validator type.

    Logic for given validation keywords is implemented in subclasses by
    overriding class variables and implementing the ``_validate()``
    method.
    """

    types: ClassVar[Optional[Tuple[Type, ...]]] = None
    """Types on which this validator applies.

    If ``None``, apply to all values.
    """

    message: ClassVar[str] = ""
    """The error message to display on validation failure.

    Can be tamplated on :attr:`Validator.keywords`.
    """

    keywords: Tuple[str, ...] = tuple()
    """Keywords which configure this validator.

    These are used to configure the validator based on the
    :class:`statham.dsl.elements.Element`.
    """

    def __init__(self, *args):
        """Accepts the parameters specified by the `keywords` class variable."""
        if len(self.keywords) != len(args):
            raise TypeError(
                f"{type(self).__name__}.__init__ takes exactly "
                f"{len(self.keywords)} ({len(args)} given)"
            )
        self.params = dict(zip(self.keywords, args))

    @classmethod
    def from_element(cls, element) -> Optional["Validator"]:
        """Construct validator from a DSL Element instance.

        Check for attributes matching keywords for this validator. If
        none are present, then return None.
        """
        params = tuple(
            getattr(element, keyword, NotPassed()) for keyword in cls.keywords
        )
        if NotPassed() in params:
            return None
        return cls(*params)

    # pylint: disable=no-self-use
    def _validate(self, _value: Any):
        """Validate a value.

        Validation logic should be added by base classes, and raise a
        bare `ValidationError` on a failure. The error message will be
        automatically generated from the `message` class variable for
        consistency.
        """
        return

    def error_message(self):
        """Generate the error message on failed validation."""
        return self.message.format(**self.params)

    def __call__(self, value: Any, property_: Any):
        """Apply the validator to a value.

        Checks that `value` has correct type for this validator, runs
        validation logic and constructs the error message on failure.

        :param value: The value to validate.
        :param property_: The enclosing property if present - used for
            error reporting.
        :raises: :class:`~statham.dsl.exceptions.ValidationError` if
            :paramref:`~Validator.__call__.value` fails validation.
        """
        if self.types and not _is_instance(value, self.types):
            return
        try:
            self._validate(value)
        except ValidationError:
            raise ValidationError.from_validator(
                property_, value, self.error_message()
            )


class InstanceOf(Validator):
    """Validate the type of a value."""

    message = "Must be of type {type_names}."

    def __init__(self, *args):
        super().__init__()
        self.params["types"] = args
        names = (type_.__name__ for type_ in self.params["types"])
        self.params["type_names"] = f"({','.join(names)})"

    def _validate(self, value: Any):
        if value == NotPassed() or not self.params["types"]:
            return
        if not _is_instance(value, self.params["types"]):
            raise ValidationError


class NoMatch(Validator):
    """Don't accept any passed value.

    Used exclusively by :class:`~statham.dsl.elements.base.Nothing`.
    """

    message = "Schema does not accept any values."

    def _validate(self, value: Any):
        if value is NotPassed():
            return
        raise ValidationError


class Const(Validator):
    """Validate that passed values match a constant value."""

    keywords = ("const",)
    message = "Must match constant value: {const}"

    def _validate(self, value: Any):
        aliased = replace_bool(value)
        const = replace_bool(self.params["const"])
        if aliased != const:
            raise ValidationError


class Enum(Validator):
    """Validate that passed values are members of an enumeration."""

    keywords = ("enum",)
    message = "Must be one of these values: {enum}"

    def _validate(self, value: Any):
        aliased = replace_bool(value)
        enum = list(map(replace_bool, self.params["enum"]))
        if aliased not in enum:
            raise ValidationError

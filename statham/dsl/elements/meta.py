from typing import Any, cast, Dict, Optional, Tuple, Type, Union

from statham.dsl import validators as val
from statham.dsl.elements.base import Element
from statham.dsl.helpers import custom_repr_args
from statham.dsl.property import _Property
from statham.dsl.constants import NotPassed
from statham.dsl.exceptions import SchemaDefinitionError


class ObjectOptions:

    additionalProperties: Optional[Element]

    def __init__(self, *, additionalProperties: Union[Element, bool] = True):
        # Name used to match JSONSchema.
        # pylint: disable=invalid-name
        if additionalProperties is False:
            self.additionalProperties = None
        elif additionalProperties is True:
            self.additionalProperties = Element()
        else:
            self.additionalProperties = cast(Element, additionalProperties)

    def __eq__(self, other) -> bool:
        if not isinstance(other, ObjectOptions):
            return False
        return self.additionalProperties == other.additionalProperties

    def __repr__(self):
        args = custom_repr_args(self)
        if args.kwargs["additionalProperties"] == Element():
            del args.kwargs["additionalProperties"]
        if args.kwargs["additionalProperties"] is None:
            args.kwargs["additionalProperties"] = False
        return f"{type(self).__name__}{repr(args)}"


RESERVED_PROPERTIES = dir(object) + ["default", "options", "properties"]


class ObjectClassDict(dict):
    """Overriden class dictionary for the metaclass of Object.

    Collects schema properties and default value if present.
    """

    default: Any
    properties: Dict[str, _Property]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.properties = {}
        self.default = self.get("default", NotPassed())
        self.options = self.get("options", ObjectOptions())

    def __setitem__(self, key, value):
        if key in RESERVED_PROPERTIES and isinstance(value, _Property):
            raise SchemaDefinitionError.reserved_attribute(key)
        if key == "default":
            self.default = value
        if key == "options":
            self.options = value
        if isinstance(value, _Property):
            value.bind_name(key)
            return self.properties.__setitem__(key, value)
        return super().__setitem__(key, value)


# TODO: Handle properties called `default` or `self`.
class ObjectMeta(type, Element):
    """Metaclass to allow declaring Object schemas as classes.

    Collects default value and properties defined as class variables,
    and binds information to those properties.
    """

    properties: Dict[str, _Property]
    options: ObjectOptions

    @staticmethod
    def __subclasses__():
        # This is overriden to prevent errors.
        # TODO: Is there a more elegant way to achieve this? Perhaps
        #   __init_subclass__ should error to prevent this from being
        #   wrong.
        return []

    @classmethod
    def __prepare__(mcs, _name, _bases):
        return ObjectClassDict()

    def __new__(mcs, name: str, bases: Tuple[Type], classdict: ObjectClassDict):
        cls: Type[ObjectMeta] = type.__new__(mcs, name, bases, dict(classdict))
        cls.properties = classdict.properties
        for property_ in cls.properties.values():
            property_.bind_class(cls)
        cls.default = classdict.default
        cls.options = classdict.options
        return cls

    def __hash__(cls):
        return hash(tuple([cls.__name__] + [prop for prop in cls.properties]))

    @property
    def annotation(cls) -> str:
        return cls.__name__

    def __repr__(cls):
        return cls.__name__

    @property
    def type_validator(cls):
        return val.instance_of(dict, cls)

    def python(cls) -> str:
        super_cls = next(iter(cls.mro()[1:]))
        class_def = f"""class {repr(cls)}({super_cls.__name__}):
"""
        if (
            not cls.properties
            and isinstance(cls.default, NotPassed)
            and cls.options == ObjectOptions()
        ):
            class_def = (
                class_def
                + """
    pass
"""
            )
        if not isinstance(cls.default, NotPassed):
            class_def = (
                class_def
                + f"""
    default = {repr(cls.default)}
"""
            )
        if cls.options != ObjectOptions():
            class_def = class_def + (
                f"""
    options = {repr(cls.options)}
"""
            )
        for property_ in cls.properties.values():
            class_def = (
                class_def
                + f"""
    {property_.python()}
"""
            )
        return class_def

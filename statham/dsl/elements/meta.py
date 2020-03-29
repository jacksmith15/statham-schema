import keyword
from typing import Any, Dict, List, Optional, Tuple, Type, Union

from statham.dsl.elements.base import Element
from statham.dsl.helpers import custom_repr
from statham.dsl.property import _Property
from statham.dsl.constants import NotPassed
from statham.dsl.exceptions import SchemaDefinitionError
from statham.dsl.validation import (
    AdditionalProperties,
    InstanceOf,
    Required,
    Validator,
)


class ObjectOptions:

    additionalProperties: Optional[Union[Element, bool]]

    def __init__(self, *, additionalProperties: Union[Element, bool] = True):
        # Name used to match JSONSchema.
        # pylint: disable=invalid-name
        self.additionalProperties = additionalProperties

    def __eq__(self, other) -> bool:
        if not isinstance(other, ObjectOptions):
            return False
        return self.additionalProperties == other.additionalProperties

    def __repr__(self):
        return custom_repr(self)


RESERVED_PROPERTIES = (
    dir(object)
    + list(keyword.kwlist)
    + ["default", "options", "properties", "additional_properties"]
)


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
    def type_validator(cls) -> Validator:
        return InstanceOf(dict, cls)

    @property
    def validators(cls) -> List[Validator]:
        return [
            cls.type_validator,
            Required(
                [
                    prop.name
                    for prop in cls.properties.values()
                    if prop.required and not prop.element.default
                ]
            ),
            AdditionalProperties(
                {prop.source for prop in cls.properties.values()},
                cls.options.additionalProperties,
            ),
        ]

    def construct_additional(cls, name: str, value: Any) -> Any:
        """Construct properties not specified in `properties`."""
        element: Element = Element()
        if isinstance(cls.options.additionalProperties, Element):
            element = cls.options.additionalProperties
        additional_property = _Property(element)
        additional_property.bind_class(cls)
        additional_property.bind_name(name)
        return additional_property(value)

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

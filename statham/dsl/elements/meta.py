import keyword
from typing import Any, Dict, List, Tuple, Type, Union

from statham.dsl.constants import Maybe, NotPassed
from statham.dsl.elements.base import Element
from statham.dsl.property import _Property
from statham.dsl.exceptions import SchemaDefinitionError
from statham.dsl.validation import (
    AdditionalProperties,
    Const,
    Dependencies,
    Enum,
    InstanceOf,
    MaxProperties,
    MinProperties,
    PropertyNames,
    Required,
    Validator,
)


RESERVED_PROPERTIES = (
    dir(object) + list(keyword.kwlist) + ["default", "properties", "_dict"]
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
        self.default = self.pop("default", NotPassed())

    def __setitem__(self, key, value):
        if key in RESERVED_PROPERTIES and isinstance(value, _Property):
            raise SchemaDefinitionError.reserved_attribute(key)
        if key == "default":
            self.default = value
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
    additionalProperties: Union[Element, bool]
    patternProperties: Dict[str, Element]
    minProperties: Maybe[int]
    maxProperties: Maybe[int]
    propertyNames: Maybe[Element]
    const: Maybe[Any]
    enum: Maybe[List[Any]]
    dependencies: Maybe[Dict[str, Union[List[str], Element]]]

    @staticmethod
    def __subclasses__():
        # This is overriden to prevent errors.
        # TODO: Is there a more elegant way to achieve this? Perhaps
        #   __init_subclass__ should error to prevent this from being
        #   wrong.
        return []

    @classmethod
    def __prepare__(mcs, _name, _bases, **_kwargs):
        return ObjectClassDict()

    def __new__(
        mcs, name: str, bases: Tuple[Type], classdict: ObjectClassDict, **kwargs
    ):
        cls: Type[ObjectMeta] = type.__new__(mcs, name, bases, dict(classdict))
        cls.properties = classdict.properties
        for property_ in cls.properties.values():
            property_.bind_class(cls)
        cls.default = classdict.default  # TODO: Make this a class arg.
        cls.additionalProperties = kwargs.get("additionalProperties", True)
        cls.patternProperties = kwargs.get("patternProperties", {})
        cls.minProperties = kwargs.get("minProperties", NotPassed())
        cls.maxProperties = kwargs.get("maxProperties", NotPassed())
        cls.propertyNames = kwargs.get("propertyNames", NotPassed())
        cls.dependencies = kwargs.get("dependencies", NotPassed())
        cls.const = kwargs.get("const", NotPassed())
        cls.enum = kwargs.get("enum", NotPassed())
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
        possible_validators = [
            cls.type_validator,
            Required(
                [
                    prop.name
                    for prop in cls.properties.values()
                    if prop.required and not prop.element.default
                ]
            ),
            AdditionalProperties(cls.__properties__),
            MinProperties.from_element(cls),
            MaxProperties.from_element(cls),
            PropertyNames.from_element(cls),
            Const.from_element(cls),
            Enum.from_element(cls),
            Dependencies.from_element(cls),
        ]
        return [validator for validator in possible_validators if validator]

    def python(cls) -> str:
        super_cls = next(iter(cls.mro()[1:]))
        cls_args = [super_cls.__name__]
        if not isinstance(cls.const, NotPassed):
            cls_args.append(f"const={cls.const}")
        if not isinstance(cls.enum, NotPassed):
            cls_args.append(f"enum={cls.enum}")
        if cls.minProperties:
            cls_args.append(f"minProperties={cls.minProperties}")
        if not isinstance(cls.maxProperties, NotPassed):
            cls_args.append(f"maxProperties={cls.maxProperties}")
        if cls.patternProperties:
            cls_args.append(f"patternProperties={cls.patternProperties}")
        if cls.additionalProperties not in (True, Element()):
            cls_args.append(f"additionalProperties={cls.additionalProperties}")
        if not isinstance(cls.propertyNames, NotPassed):
            cls_args.append(f"propertyNames={cls.propertyNames}")
        if not isinstance(cls.dependencies, NotPassed):
            cls_args.append(f"dependencies={cls.dependencies}")
        class_def = f"""class {repr(cls)}({', '.join(cls_args)}):
"""
        if not cls.properties and isinstance(cls.default, NotPassed):
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
        for property_ in cls.properties.values():
            class_def = (
                class_def
                + f"""
    {property_.python()}
"""
            )
        return class_def

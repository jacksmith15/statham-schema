import inspect
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


RESERVED_PROPERTIES = dir(object) + list(keyword.kwlist) + ["_dict"]


class ObjectClassDict(dict):
    """Overriden class dictionary for the metaclass of Object.

    Collects schema properties and default value if present.
    """

    properties: Dict[str, _Property]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.properties = {}

    def __setitem__(self, key, value):
        if key in RESERVED_PROPERTIES and isinstance(value, _Property):
            raise SchemaDefinitionError.reserved_attribute(key)
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
    patternProperties: Maybe[Dict[str, Element]]
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

    # pylint: disable=too-many-locals
    def __new__(
        mcs,
        name: str,
        bases: Tuple[Type],
        classdict: ObjectClassDict,
        *,
        default: Maybe[Any] = NotPassed(),
        const: Maybe[Any] = NotPassed(),
        enum: Maybe[List[Any]] = NotPassed(),
        minProperties: Maybe[int] = NotPassed(),
        maxProperties: Maybe[int] = NotPassed(),
        patternProperties: Maybe[Dict[str, Element]] = NotPassed(),
        additionalProperties: Union[Element, bool] = True,
        propertyNames: Maybe[Element] = NotPassed(),
        dependencies: Maybe[Dict[str, Union[List[str], Element]]] = NotPassed(),
    ):
        cls: Type[ObjectMeta] = type.__new__(mcs, name, bases, dict(classdict))
        cls.properties = classdict.properties
        for property_ in cls.properties.values():
            property_.bind_class(cls)
        cls.default = default
        cls.const = const
        cls.enum = enum
        cls.minProperties = minProperties
        cls.maxProperties = maxProperties
        cls.patternProperties = patternProperties
        cls.additionalProperties = additionalProperties
        cls.propertyNames = propertyNames
        cls.dependencies = dependencies
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
        parameters = list(
            inspect.signature(type(cls).__new__).parameters.values()
        )
        for param in parameters:
            if param.kind != param.KEYWORD_ONLY:
                continue
            value = getattr(cls, param.name, NotPassed())
            if value == param.default:
                continue
            cls_args.append(f"{param.name}={repr(value)}")
        class_def = f"""class {repr(cls)}({', '.join(cls_args)}):
"""
        if not cls.properties:
            class_def = (
                class_def
                + """
    pass
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

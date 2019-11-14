from functools import lru_cache, partial, reduce
from typing import Any, ClassVar, Dict, List, Type, Union

from attr import attrs, attrib, validators

from jsonschema_objects.constants import (
    get_flag,
    get_type,
    NotProvidedType,
    NOT_PROVIDED,
    TypeEnum,
)
from jsonschema_objects.helpers import all_subclasses, counter, dict_map


# This wrapper falls back on complex typing declared by attrs.
def type_attrib(*types: Type):
    return partial(attrib, validator=[validators.instance_of(tuple(types))])


# This wrapper falls back on complex typing declared by attrs.
def optional_type_attrib(*types: Type):
    return partial(type_attrib(NotProvidedType, *types), default=NOT_PROVIDED)


def title_format(string: str) -> str:
    return string.title().replace("_", "")


@attrs(kw_only=True)
class Schema:

    type: ClassVar[TypeEnum]

    title: str = type_attrib(str)(converter=title_format)
    description: str = type_attrib(str)()
    nullable: Union[bool, NotProvidedType] = optional_type_attrib(bool)()


def parse_schema(schema: Dict[str, Any]) -> Schema:
    """Convert a JSON Schema schema to a Model Instance.

    Looks up subclasses of Schema and matches on the `type` class
    variable.
    """
    try:
        type_prop = schema.pop("type")
    except KeyError:
        raise ValueError(f"No type or ref defined in schema: {schema}")
    types = type_prop if isinstance(type_prop, list) else [type_prop]
    schema["title"] = schema.get("title") or counter(".".join(types))
    schema["description"] = schema.get("description") or schema["title"]
    return model_from_types(*types)(**schema)  # type: ignore


@attrs(kw_only=True)
class ArraySchema(Schema):

    type: ClassVar[TypeEnum] = TypeEnum.ARRAY

    items: Schema = type_attrib(Schema)(converter=parse_schema)
    minItems: Union[int, NotProvidedType] = optional_type_attrib(int)()
    maxItems: Union[int, NotProvidedType] = optional_type_attrib(int)()


@attrs(kw_only=True)
class ObjectSchema(Schema):

    type: ClassVar[TypeEnum] = TypeEnum.OBJECT

    properties: Dict[str, Schema] = type_attrib(dict)(
        converter=partial(dict_map, parse_schema)
    )
    required: List[str] = type_attrib(list)(factory=list)


@attrs(kw_only=True)
class PrimitiveSchema(Schema):

    default: Any = attrib(default=NOT_PROVIDED)


@attrs(kw_only=True)
class NumberSchema(PrimitiveSchema):

    type: ClassVar[TypeEnum] = TypeEnum.NUMBER

    minimum: Union[float, NotProvidedType] = optional_type_attrib(float)()
    exclusiveMinimum: Union[float, NotProvidedType] = optional_type_attrib(
        float
    )()
    maximum: Union[float, NotProvidedType] = optional_type_attrib(float)()
    exclusiveMaximum: Union[float, NotProvidedType] = optional_type_attrib(
        float
    )()
    multipleOf: Union[float, NotProvidedType] = optional_type_attrib(float)()


@attrs(kw_only=True)
class IntegerSchema(PrimitiveSchema):

    type: ClassVar[TypeEnum] = TypeEnum.INTEGER

    minimum: Union[int, NotProvidedType] = optional_type_attrib(int)()
    exclusiveMinimum: Union[int, NotProvidedType] = optional_type_attrib(int)()
    maximum: Union[int, NotProvidedType] = optional_type_attrib(int)()
    exclusiveMaximum: Union[int, NotProvidedType] = optional_type_attrib(int)()
    multipleOf: Union[int, NotProvidedType] = optional_type_attrib(int)()


@attrs(kw_only=True)
class StringSchema(PrimitiveSchema):

    type: ClassVar[TypeEnum] = TypeEnum.STRING

    format: Union[str, NotProvidedType] = optional_type_attrib(str)()
    pattern: Union[str, NotProvidedType] = optional_type_attrib(str)()


@attrs(kw_only=True)
class NullSchema(Schema):

    type: ClassVar[TypeEnum] = TypeEnum.NULL


def _union_model(*models: Type[Schema]) -> Type[Schema]:
    """Get a model which represents the union of two types."""
    invalid = {ObjectSchema, ArraySchema, PrimitiveSchema, Schema} & set(models)
    if invalid:
        raise ValueError(f"Can't produce a union for these types: {invalid}.")
    model_type = reduce(lambda x, y: x | y, map(lambda _: _.type, models))
    type_names = [name.title() for name in get_type(model_type)]
    name = "Or".join(type_names)
    attribs = {"type": model_type}
    return attrs(kw_only=True)(
        type(name, tuple(model for model in models), attribs)
    )


@lru_cache(maxsize=None)
def _model_from_types_cached(*types: str) -> Type[Schema]:
    """Get the correct schema model from the schema dictionary."""
    flag = get_flag(*types)
    matching_models = [
        SubSchema
        for SubSchema in all_subclasses(Schema)
        if hasattr(SubSchema, "type")
        and (flag & SubSchema.type) == SubSchema.type
    ]
    if not matching_models:
        raise TypeError(
            f"No existing models found construct which can construct this type!"
        )
    if len(matching_models) == 1:
        return next(iter(matching_models))
    return _union_model(*matching_models)


def model_from_types(*types: str) -> Type[Schema]:
    """Helper to get schema model from type strings.

    Wraps a cached helper to ensure unions are declared multiple times.
    """
    return _model_from_types_cached(*sorted(types))

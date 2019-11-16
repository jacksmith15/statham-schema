from functools import lru_cache, reduce
from typing import Any, ClassVar, Dict, List, Type, Union

from attr import attrs, attrib, Factory
from attr.validators import instance_of

from jsonschema_objects.constants import (
    get_flag,
    get_type,
    JSONElement,
    NotProvidedType,
    NOT_PROVIDED,
    TypeEnum,
)
from jsonschema_objects.helpers import all_subclasses, counter, dict_map


def convert_int(value: Any) -> Any:
    """If value is an int, cast it to a float.

    JSON doesn't distinguish, so integer values for float validation are
    acceptable.
    """
    if isinstance(value, int):
        return float(value)
    return value


def title_format(string: str) -> str:
    return string.title().replace("_", "").replace(" ", "")


@attrs(kw_only=True, frozen=True, slots=True)
class Schema:

    type: ClassVar[TypeEnum]

    _type: Union[str, List[str]] = attrib(validator=[instance_of((str, list))])

    title: str = attrib(validator=[instance_of(str)], converter=title_format)
    description: str = attrib(
        validator=[instance_of(str)],
        default=Factory(lambda self: self.title, takes_self=True),
    )
    nullable: Union[bool, NotProvidedType] = attrib(
        validator=[instance_of((bool, NotProvidedType))], default=NOT_PROVIDED
    )


def parse_schema(schema: Dict[str, JSONElement]) -> Schema:
    """Convert a JSON Schema schema to a Model Instance.

    Looks up subclasses of Schema and matches on the `type` class
    variable.
    """
    try:
        type_prop = schema["type"]
    except KeyError:
        raise ValueError(f"No type or ref defined in schema: {schema}")
    types = type_prop if isinstance(type_prop, list) else [type_prop]
    schema["title"] = schema.get("title") or counter(".".join(types))
    schema["description"] = schema.get("description") or schema["title"]
    return model_from_types(*types)(**schema)  # type: ignore


@attrs(kw_only=True, frozen=True, slots=True)
class ArraySchema(Schema):

    type: ClassVar[TypeEnum] = TypeEnum.ARRAY

    items: Schema = attrib(
        validator=[instance_of(Schema)], converter=parse_schema
    )
    minItems: Union[int, NotProvidedType] = attrib(
        validator=[instance_of((int, NotProvidedType))], default=NOT_PROVIDED
    )
    maxItems: Union[int, NotProvidedType] = attrib(
        validator=[instance_of((int, NotProvidedType))], default=NOT_PROVIDED
    )


def _dict_property_convert(
    dictionary: Dict[str, JSONElement]
) -> Dict[str, Schema]:
    return dict_map(parse_schema, dictionary)


@attrs(kw_only=True, frozen=True, slots=True)
class ObjectSchema(Schema):

    type: ClassVar[TypeEnum] = TypeEnum.OBJECT

    properties: Dict[str, Schema] = attrib(
        validator=[instance_of(dict)], converter=_dict_property_convert
    )
    required: List[str] = attrib(validator=[instance_of(list)], factory=list)


@attrs(kw_only=True, frozen=True, slots=True)
class PrimitiveSchema(Schema):

    default: Any = attrib(default=NOT_PROVIDED)


@attrs(kw_only=True, frozen=True, slots=True)
class BooleanSchema(PrimitiveSchema):

    type: ClassVar[TypeEnum] = TypeEnum.BOOLEAN


@attrs(kw_only=True, frozen=True, slots=True)
class NumberSchema(PrimitiveSchema):

    type: ClassVar[TypeEnum] = TypeEnum.NUMBER

    minimum: Union[float, NotProvidedType] = attrib(
        validator=[instance_of((float, NotProvidedType))],
        default=NOT_PROVIDED,
        converter=convert_int,
    )
    exclusiveMinimum: Union[float, NotProvidedType] = attrib(
        validator=[instance_of((float, NotProvidedType))],
        default=NOT_PROVIDED,
        converter=convert_int,
    )
    maximum: Union[float, NotProvidedType] = attrib(
        validator=[instance_of((float, NotProvidedType))],
        default=NOT_PROVIDED,
        converter=convert_int,
    )
    exclusiveMaximum: Union[float, NotProvidedType] = attrib(
        validator=[instance_of((float, NotProvidedType))],
        default=NOT_PROVIDED,
        converter=convert_int,
    )
    multipleOf: Union[float, NotProvidedType] = attrib(
        validator=[instance_of((float, NotProvidedType))],
        default=NOT_PROVIDED,
        converter=convert_int,
    )


@attrs(kw_only=True, frozen=True, slots=True)
class IntegerSchema(PrimitiveSchema):

    type: ClassVar[TypeEnum] = TypeEnum.INTEGER

    minimum: Union[int, NotProvidedType] = attrib(
        validator=[instance_of((int, NotProvidedType))], default=NOT_PROVIDED
    )
    exclusiveMinimum: Union[int, NotProvidedType] = attrib(
        validator=[instance_of((int, NotProvidedType))], default=NOT_PROVIDED
    )
    maximum: Union[int, NotProvidedType] = attrib(
        validator=[instance_of((int, NotProvidedType))], default=NOT_PROVIDED
    )
    exclusiveMaximum: Union[int, NotProvidedType] = attrib(
        validator=[instance_of((int, NotProvidedType))], default=NOT_PROVIDED
    )
    multipleOf: Union[int, NotProvidedType] = attrib(
        validator=[instance_of((int, NotProvidedType))], default=NOT_PROVIDED
    )


@attrs(kw_only=True, frozen=True, slots=True)
class StringSchema(PrimitiveSchema):

    type: ClassVar[TypeEnum] = TypeEnum.STRING

    format: Union[str, NotProvidedType] = attrib(
        validator=[instance_of((str, NotProvidedType))], default=NOT_PROVIDED
    )
    pattern: Union[str, NotProvidedType] = attrib(
        validator=[instance_of((str, NotProvidedType))], default=NOT_PROVIDED
    )
    minLength: Union[int, NotProvidedType] = attrib(
        validator=[instance_of((int, NotProvidedType))], default=NOT_PROVIDED
    )
    maxLength: Union[int, NotProvidedType] = attrib(
        validator=[instance_of((int, NotProvidedType))], default=NOT_PROVIDED
    )


@attrs(kw_only=True, frozen=True, slots=True)
class NullSchema(Schema):

    type: ClassVar[TypeEnum] = TypeEnum.NULL


def _union_model(*models: Type[Schema]) -> Type[Schema]:
    """Get a model which represents the union of two types."""
    invalid = {ObjectSchema, ArraySchema, PrimitiveSchema, Schema} & set(models)
    if invalid:
        raise ValueError(
            f"Can't produce a union for these types: {invalid}. "
            f"The following union was requested: {models}"
        )
    model_type = reduce(lambda x, y: x | y, map(lambda _: _.type, models))
    type_names = [name.title() for name in get_type(model_type)]
    name = "Or".join(type_names)
    attribs = {"type": model_type}
    return attrs(kw_only=True, frozen=True, slots=True)(
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
        # This block shouldn't be hit!
        raise TypeError(  # pragma: no cover
            "No existing models found construct which can construct "
            "this type! Does every declared flag on "
            "`jsonschema_objects.constants.TypeEnum` have an equivalent "
            "model declared?"
        )
    if len(matching_models) == 1:
        return next(iter(matching_models))
    return _union_model(*matching_models)


def model_from_types(*types: str) -> Type[Schema]:
    """Helper to get schema model from type strings.

    Wraps a cached helper to ensure unions are declared multiple times.
    """
    return _model_from_types_cached(*sorted(types))

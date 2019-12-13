from functools import lru_cache, reduce
from typing import Any, ClassVar, Dict, List, Type, Union

from attr import attrs, attrib, Factory
from attr.validators import instance_of

from statham.constants import (
    get_flag,
    get_type,
    JSONElement,
    NotProvidedType,
    NOT_PROVIDED,
    TypeEnum,
)
from statham.exceptions import SchemaParseError
from statham.helpers import (
    all_subclasses,
    counter,
    dict_map,
    dict_filter,
    _title_format,
)


@attrs(kw_only=True, frozen=True)
class Schema:

    type: ClassVar[TypeEnum]

    _type: Union[str, List[str]] = attrib(validator=[instance_of((str, list))])

    title: str = attrib(validator=[instance_of(str)], converter=_title_format)
    description: str = attrib(
        validator=[instance_of(str)],
        default=Factory(lambda self: self.title, takes_self=True),
    )


def parse_schema(schema: Dict[str, JSONElement]) -> Schema:
    """Convert a JSON Schema schema to a Model Instance.

    Looks up subclasses of Schema and matches on the `type` class
    variable.
    """
    try:
        type_prop = schema["type"]
    except KeyError:
        raise SchemaParseError.missing_type(schema)
    types = type_prop if isinstance(type_prop, list) else [type_prop]
    schema["title"] = schema.get("title") or counter(".".join(types))
    schema["description"] = schema.get("description") or schema["title"]
    try:
        return model_from_types(*types)(**schema)  # type: ignore
    except TypeError as exc:
        raise SchemaParseError.from_exception(schema, exc) from exc


@attrs(kw_only=True, frozen=True)
class ArraySchema(Schema):

    type: ClassVar[TypeEnum] = TypeEnum.ARRAY

    items: Schema = attrib(
        validator=[instance_of(Schema)], converter=parse_schema
    )
    # pylint: disable=invalid-name
    minItems: Union[int, NotProvidedType] = attrib(
        validator=[instance_of((int, NotProvidedType))], default=NOT_PROVIDED
    )
    maxItems: Union[int, NotProvidedType] = attrib(
        validator=[instance_of((int, NotProvidedType))], default=NOT_PROVIDED
    )
    # pylint: enable=invalid-name


def _dict_property_convert(
    dictionary: Dict[str, JSONElement]
) -> Dict[str, Schema]:
    return dict_map(
        parse_schema, dict_filter(lambda val: isinstance(val, dict), dictionary)
    )


@attrs(kw_only=True, frozen=True)
class ObjectSchema(Schema):

    type: ClassVar[TypeEnum] = TypeEnum.OBJECT

    properties: Dict[str, Schema] = attrib(
        validator=[instance_of(dict)], converter=_dict_property_convert
    )
    required: List[str] = attrib(validator=[instance_of(list)], factory=list)


@attrs(kw_only=True, frozen=True)
class PrimitiveSchema(Schema):

    default: Any = attrib(default=NOT_PROVIDED)


@attrs(kw_only=True, frozen=True)
class BooleanSchema(PrimitiveSchema):

    type: ClassVar[TypeEnum] = TypeEnum.BOOLEAN


@attrs(kw_only=True, frozen=True)
class BaseNumericSchema(PrimitiveSchema):

    minimum: Union[int, float, NotProvidedType] = attrib(
        validator=[instance_of((int, float, NotProvidedType))],
        default=NOT_PROVIDED,
    )
    maximum: Union[int, float, NotProvidedType] = attrib(
        validator=[instance_of((int, float, NotProvidedType))],
        default=NOT_PROVIDED,
    )
    # pylint: disable=invalid-name
    exclusiveMinimum: Union[int, float, NotProvidedType] = attrib(
        validator=[instance_of((int, float, NotProvidedType))],
        default=NOT_PROVIDED,
    )
    exclusiveMaximum: Union[int, float, NotProvidedType] = attrib(
        validator=[instance_of((int, float, NotProvidedType))],
        default=NOT_PROVIDED,
    )
    multipleOf: Union[int, float, NotProvidedType] = attrib(
        validator=[instance_of((int, float, NotProvidedType))],
        default=NOT_PROVIDED,
    )
    # pylint: enable=invalid-name


@attrs(kw_only=True, frozen=True)
class IntegerSchema(BaseNumericSchema):

    type: ClassVar[TypeEnum] = TypeEnum.INTEGER


@attrs(kw_only=True, frozen=True)
class NumberSchema(BaseNumericSchema):

    type: ClassVar[TypeEnum] = TypeEnum.NUMBER


@attrs(kw_only=True, frozen=True)
class StringSchema(PrimitiveSchema):

    type: ClassVar[TypeEnum] = TypeEnum.STRING

    format: Union[str, NotProvidedType] = attrib(
        validator=[instance_of((str, NotProvidedType))], default=NOT_PROVIDED
    )
    pattern: Union[str, NotProvidedType] = attrib(
        validator=[instance_of((str, NotProvidedType))], default=NOT_PROVIDED
    )
    # pylint: disable=invalid-name
    minLength: Union[int, NotProvidedType] = attrib(
        validator=[instance_of((int, NotProvidedType))], default=NOT_PROVIDED
    )
    maxLength: Union[int, NotProvidedType] = attrib(
        validator=[instance_of((int, NotProvidedType))], default=NOT_PROVIDED
    )
    # pylint: enable=invalid-name


@attrs(kw_only=True, frozen=True)
class NullSchema(Schema):

    type: ClassVar[TypeEnum] = TypeEnum.NULL


def _union_model(*models: Type[Schema]) -> Type[Schema]:
    """Get a model which represents the union of two types."""
    invalid = {ObjectSchema, ArraySchema, PrimitiveSchema, Schema} & set(models)
    if invalid:
        raise SchemaParseError.unsupported_type_union(invalid, set(models))
    model_type = reduce(lambda x, y: x | y, map(lambda _: _.type, models))
    type_names = sorted([name.title() for name in get_type(model_type)])
    name = "Or".join(type_names) + "Schema"
    attribs = {"type": model_type}
    return attrs(kw_only=True, frozen=True)(
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
        # Ensure the Sub Schema is one of the fundamental set.
        and (flag & SubSchema.type) is SubSchema.type
        and SubSchema.type in TypeEnum
    ]
    if not matching_models:
        # This block shouldn't be hit!
        # If every type flag has a corresponding fundamental model,
        # there should always be a match.
        raise RuntimeError(  # pragma: no cover
            "No existing models found construct which can construct "
            "the requested type! Does every declared flag on "
            f"`{TypeEnum.__module__}.{TypeEnum.__name__}` have an "
            "equivalent model declared?"
        )
    if len(matching_models) == 1:
        return next(iter(matching_models))
    return _union_model(*matching_models)


def model_from_types(*types: str) -> Type[Schema]:
    """Helper to get schema model from type strings.

    Wraps a cached helper to ensure unions are declared multiple times.
    """
    return _model_from_types_cached(*sorted(types))

from functools import partial
from typing import Any, ClassVar, Dict, List, Type

from attr import attrs, attrib, validators

from jsonschema_objects.constants import (
    INDENT,
    not_required,
    NotProvidedType,
    NOT_PROVIDED,
    TypeEnum,
)
from jsonschema_objects.helpers import all_subclasses, counter, dict_map


TYPE_ANNOTATION = {
    TypeEnum.OBJECT: "Dict",
    TypeEnum.ARRAY: "List",
    TypeEnum.NUMBER: "float",
    TypeEnum.INTEGER: "int",
    TypeEnum.STRING: "str",
    TypeEnum.NULL: "type(None)",
}


def type_attrib(*types: Type):
    return partial(attrib, validator=[validators.instance_of(tuple(types))])


def optional_type_attrib(*types: Type):
    return partial(type_attrib(NotProvidedType, *types), default=NOT_PROVIDED)


# Dataclasses
# pylint: disable=too-few-public-methods


@attrs(kw_only=True)
class Schema:

    type: ClassVar[TypeEnum]

    title: str = type_attrib(str)(converter=lambda x: x.title().replace("_", ""))
    description: str = type_attrib(str)()
    nullable: not_required(bool) = optional_type_attrib(bool)()

    @property
    def base_type_annotation(self):
        return TYPE_ANNOTATION[self.type]

    @property
    def type_annotation(self):
        return (
            self.base_type_annotation
            if not self.nullable
            else f"Optional[{self.base_type_annotation}]"
        )

    def as_arg(self, key: str) -> str:
        return f"{key}: {self.type_annotation} = NOT_PASSED"

    def as_init(self, key: str, indent=None) -> str:
        indent = indent or INDENT
        if not self.nullable:
            return [
                f"{key} = None if {key} == NOT_PASSED else {key}",
                f"if {key} is None:",
                f'{indent}raise ValueError("{key} cannot be None.")',
                f"self.{key}: {self.type_annotation} = {key}",
            ]
        return [f"self.{key}: {self.type_annotation} = {key}"]


def parse_schema(schema: Dict[str, Any]) -> Schema:
    """Convert a JSON Schema schema to a Model Instance.

    Looks up subclasses of Schema and matches on the `type` class
    variable.
    """
    model_lookup = {
        SubSchema.type.value: SubSchema
        for SubSchema in all_subclasses(Schema)
        if hasattr(SubSchema, "type")
    }
    try:
        type_string = schema.pop("type")
    except KeyError:
        raise ValueError(f"No type or ref defined in schema: {schema}")
    schema["title"] = schema.get("title") or counter(type_string)
    schema["description"] = schema.get("description") or schema["title"]
    return model_lookup[type_string](**schema)


@attrs(kw_only=True)
class ArraySchema(Schema):

    type: ClassVar[TypeEnum] = TypeEnum.ARRAY

    items: Schema = type_attrib(Schema)(converter=parse_schema)
    minItems: not_required(int) = optional_type_attrib(int)()
    maxItems: not_required(int) = optional_type_attrib(int)()

    @property
    def base_type_annotation(self):
        nested_type = self.items.base_type_annotation
        return f"List[{nested_type}]"


@attrs(kw_only=True)
class ObjectSchema(Schema):

    type: ClassVar[TypeEnum] = TypeEnum.OBJECT

    properties: Dict[str, Schema] = type_attrib(dict)(
        converter=partial(dict_map, parse_schema)
    )
    required: List[str] = type_attrib(list)(factory=list)

    @property
    def base_type_annotation(self):
        nested_types = {value.base_type_annotation for value in self.properties.values()}
        allows_none = any(value.nullable for value in self.properties.values())
        if len(nested_types) > 1:
            inner_type_def = "Union[" + ", ".join(nested_types) + "]"
        else:
            inner_type_def = next(iter(nested_types))
        if allows_none:
            inner_type_def = "Optional[" + inner_type_def + "]"
        return f"Dict[str, {inner_type_def}]"

    def as_init(self, key: str, indent=None) -> str:
        lines = super().as_init(key, indent)
        lines[-1] = f"self.{key} = {self.title}(**{key})"
        return lines


@attrs(kw_only=True)
class PrimitiveSchema(Schema):

    default: Any = attrib(default=NOT_PROVIDED)


@attrs(kw_only=True)
class NumberSchema(PrimitiveSchema):

    type: ClassVar[TypeEnum] = TypeEnum.NUMBER

    minimum: not_required(float) = optional_type_attrib(float)()
    exclusiveMinimum: not_required(float) = optional_type_attrib(float)()
    maximum: not_required(float) = optional_type_attrib(float)()
    exclusiveMinimum: not_required(float) = optional_type_attrib(float)()
    multipleOf: not_required(float) = optional_type_attrib(float)()


@attrs(kw_only=True)
class IntegerSchema(PrimitiveSchema):

    type: ClassVar[TypeEnum] = TypeEnum.INTEGER

    minimum: not_required(int) = optional_type_attrib(int)()
    exclusiveMinimum: not_required(int) = optional_type_attrib(int)()
    maximum: not_required(int) = optional_type_attrib(int)()
    exclusiveMinimum: not_required(int) = optional_type_attrib(int)()
    multipleOf: not_required(int) = optional_type_attrib(int)()


@attrs(kw_only=True)
class StringSchema(PrimitiveSchema):

    type: ClassVar[TypeEnum] = TypeEnum.STRING

    format: not_required(str) = optional_type_attrib(str)()
    pattern: not_required(str) = optional_type_attrib(str)()


@attrs(kw_only=True)
class NullSchema(Schema):

    type: ClassVar[TypeEnum] = TypeEnum.NULL

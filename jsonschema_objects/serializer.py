from typing import Any, Iterable

from jinja2 import Environment, FileSystemLoader

from jsonschema_objects.constants import NOT_PROVIDED, TypeEnum
from jsonschema_objects.models import (
    Schema,
    ArraySchema,
    ObjectSchema,
    NumberSchema,
    IntegerSchema,
    ObjectSchema,
)


def validator_type_arg(schema: Schema) -> str:
    return {
        TypeEnum.OBJECT: schema.title,
        TypeEnum.ARRAY: list.__name__,
        TypeEnum.INTEGER: int.__name__,
        TypeEnum.NUMBER: float.__name__,
        TypeEnum.STRING: str.__name__,
        TypeEnum.NULL: "type(None)",
    }[schema.type]


def default_arg(schema: Schema) -> str:
    default = getattr(schema, "default", NOT_PROVIDED)
    if default == NOT_PROVIDED:
        return NOT_PROVIDED
    if isinstance(default, (int, float)) or default is None:
        return default
    if isinstance(default, (str)):
        return f'"{default}"'
    raise TypeError(f"Unsupported default {default} of type {type(default)}")


def serialize_object_schemas(schemas: Iterable[ObjectSchema]) -> str:
    environment = Environment(
        loader=FileSystemLoader("jsonschema_objects/templates"),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    environment.filters["validator_type_arg"] = validator_type_arg
    environment.filters["default_arg"] = default_arg
    template = environment.get_template("template.py.j2")
    return template.render(
        schemas=schemas, type_enum=TypeEnum, not_provided=NOT_PROVIDED
    )

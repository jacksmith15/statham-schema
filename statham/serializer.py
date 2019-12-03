from typing import Iterable, List

from jinja2 import Environment, FileSystemLoader

from statham.constants import NOT_PROVIDED, TypeEnum
from statham.models import ArraySchema, ObjectSchema, Schema
from statham.validators import (
    instance_of,
    NotPassed,
    SCHEMA_ATTRIBUTE_VALIDATORS,
)


def default(schema: Schema, required: bool) -> str:
    default_value = getattr(schema, "default", NOT_PROVIDED)
    if default_value is NOT_PROVIDED:
        if required:
            return ""
        return f"{NotPassed.__name__}()"
    return repr(default_value)


def type_annotation(schema: Schema, required: bool) -> str:
    schema_items = getattr(schema, "items", NOT_PROVIDED)
    mapping = {
        TypeEnum.OBJECT: schema.title,
        TypeEnum.ARRAY: (
            List.__name__
            + (
                f"[{type_annotation(schema_items, False)}]"
                if schema_items is not NOT_PROVIDED
                else ""
            )
        ),
        TypeEnum.INTEGER: int.__name__,
        TypeEnum.NUMBER: float.__name__,
        TypeEnum.STRING: str.__name__,
        TypeEnum.NULL: str(None),
        TypeEnum.BOOLEAN: bool.__name__,
    }
    args = [arg for flag, arg in mapping.items() if flag & schema.type]

    if not required:
        args.append(NotPassed.__name__)
    if len(args) == 1:
        return next(iter(args))
    validator_args = ", ".join(args)
    return f"Union[{validator_args}]"


def validator_type_arg(schema: Schema) -> str:
    mapping = {
        TypeEnum.OBJECT: schema.title,
        TypeEnum.ARRAY: list.__name__,
        TypeEnum.INTEGER: int.__name__,
        TypeEnum.NUMBER: float.__name__,
        TypeEnum.STRING: str.__name__,
        TypeEnum.NULL: "type(None)",
        TypeEnum.BOOLEAN: bool.__name__,
    }
    args = [arg for flag, arg in mapping.items() if flag & schema.type]
    if len(args) == 1:
        return next(iter(args))
    return ", ".join(args)


INDENT = " " * 4


def validators(schema: Schema) -> str:
    return ("\n" + INDENT * 3).join(
        [f"val.{instance_of.__name__}({validator_type_arg(schema)}),"]
        + extra_validators(schema)
    )


def extra_validators(schema: Schema) -> List[str]:
    return [
        (f"val.{validator.__name__}({repr(getattr(schema, attribute))}),")
        for attribute, validator in SCHEMA_ATTRIBUTE_VALIDATORS.items()
        if hasattr(schema, attribute)
        and getattr(schema, attribute) is not NOT_PROVIDED
    ]


def converter(schema: Schema) -> str:
    if isinstance(schema, ObjectSchema):
        return f"con.instantiate({schema.title})"
    if isinstance(schema, ArraySchema) and isinstance(
        schema.items, ObjectSchema
    ):
        return f"con.map_instantiate({schema.items.title})"
    return ""


def serialize_object_schemas(schemas: Iterable[ObjectSchema]) -> str:
    environment = Environment(
        loader=FileSystemLoader("statham/templates"),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    environment.filters["validators"] = validators
    environment.filters["converter"] = converter
    environment.filters["default"] = default
    environment.filters["type_annotation"] = type_annotation
    template = environment.get_template("template.py.j2")
    return template.render(
        schemas=schemas, type_enum=TypeEnum, not_provided=NOT_PROVIDED
    )

from typing import Dict, List, Type, Union

import pytest

from statham.constants import TypeEnum
from statham.exceptions import SchemaParseError
from statham.models import (
    all_subclasses,
    ArraySchema,
    IntegerSchema,
    model_from_types,
    NumberSchema,
    ObjectSchema,
    parse_schema,
    Schema,
    StringSchema,
    _union_model,
)
from tests.conftest import label_schema


def test_schema_instantiates_without_error(valid_schema):
    assert ObjectSchema(**valid_schema)


@pytest.mark.parametrize(
    "path,type_",
    [
        (["properties", "related"], ObjectSchema),
        (["properties", "related", "properties", "name"], StringSchema),
        (["properties", "related", "properties", "value"], IntegerSchema),
        (["properties", "children"], ArraySchema),
        (["properties", "children", "items"], ObjectSchema),
        (
            ["properties", "children", "items", "properties", "name"],
            StringSchema,
        ),
        (
            ["properties", "children", "items", "properties", "proportion"],
            NumberSchema,
        ),
        (["properties", "optional"], model_from_types("null", "string")),
    ],
)
def test_that_nested_schemas_have_been_parsed(
    valid_schema, path: List[str], type_: Type[Schema]
):
    parsed_schema: Union[Schema, Dict[str, Schema]] = ObjectSchema(
        **valid_schema
    )
    for subpath in path:
        try:
            if isinstance(parsed_schema, dict):
                # False positive.
                # pylint: disable=unsubscriptable-object
                parsed_schema = parsed_schema[subpath]
            else:
                parsed_schema = getattr(parsed_schema, subpath)
        except (KeyError, AttributeError):
            raise KeyError(f"Couldn't resolve subpath {subpath} in path {path}")
    assert isinstance(parsed_schema, type_)


def test_that_model_types_produce_spanning_set_of_types():
    """Subclasses of `Schema` need to form a group over (type, union)."""
    declared_model_type_flags = {
        SubSchema.type
        for SubSchema in all_subclasses(Schema)
        if hasattr(SubSchema, "type")
    }
    missing_flags = {
        flag for flag in TypeEnum if flag not in declared_model_type_flags
    }
    assert (
        not missing_flags
    ), f"The following type flag need schema model definitions."


@pytest.mark.parametrize("type_", TypeEnum)
def test_that_there_is_no_type_conflict_among_model_types(type_: TypeEnum):
    declared_models = [
        SubSchema
        for SubSchema in all_subclasses(Schema)
        if hasattr(SubSchema, "type") and SubSchema.type is type_
    ]
    assert (
        len(declared_models) <= 1
    ), f"There are multiple declared models for {type_}: {declared_models}."


@pytest.mark.parametrize(
    "args", [["integer"], ["integer", "number"], ["string", "null", "boolean"]]
)
def test_model_schema_factory_idempotent(args: List[str]):
    assert model_from_types(*args) is model_from_types(*args)


@pytest.mark.parametrize(
    "args,expected_name",
    [
        (["integer"], "IntegerSchema"),
        (["integer", "number"], "IntegerOrNumberSchema"),
        (["string", "null", "boolean"], "BooleanOrNullOrStringSchema"),
    ],
)
def test_model_schema_factory_union_names(args: List[str], expected_name: str):
    assert model_from_types(*args).__name__ == expected_name


def test_model_schema_factory_union_attributes_integer_number():
    kwargs = {
        "type": ["integer", "number"],
        "title": "foo",
        "description": "bar",
        "default": 3,
        "minimum": 1,
        "exclusiveMinimum": 1.5,
        "maximum": 5,
        "exclusiveMaximum": 5.5,
        "multipleOf": 0.2,
    }
    assert parse_schema(kwargs)


def test_model_schema_factory_union_attributes_integer_string():
    kwargs = {
        "type": ["integer", "string"],
        "title": "foo",
        "description": "bar",
        "default": 3,
        "minimum": 1,
        "exclusiveMinimum": 1.5,
        "maximum": 500,
        "exclusiveMaximum": 500.5,
        "multipleOf": 0.2,
        "pattern": r"\d+\.?\d*",
        "format": "number",
        "minLength": 1,
        "maxLength": 5,
    }
    assert parse_schema(kwargs)


def test_parse_schema_without_type():
    with pytest.raises(SchemaParseError):
        parse_schema({})


def test_union_model_fails_for_invalid_types():
    with pytest.raises(SchemaParseError):
        _union_model(ObjectSchema, ArraySchema)


def test_parse_schema_fails_with_unknown_properties():
    with pytest.raises(SchemaParseError) as excinfo:
        parse_schema(label_schema({"type": "string", "foo": "bar"}))
    assert "Failed to parse the following schema" in str(excinfo.value)


def test_parse_schema_fails_for_bad_composition_schema():
    with pytest.raises(SchemaParseError) as excinfo:
        parse_schema(
            label_schema({"anyOf": [{"type": "string"}], "foo": "bar"})
        )
    assert "Failed to parse schema with composition keyword" in str(
        excinfo.value
    )

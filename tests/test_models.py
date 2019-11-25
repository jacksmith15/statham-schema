from typing import Dict, List, Type, Union

import pytest

from statham.constants import TypeEnum
from statham.models import (
    all_subclasses,
    ArraySchema,
    IntegerSchema,
    model_from_types,
    NumberSchema,
    ObjectSchema,
    Schema,
    StringSchema,
)


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

from typing import Any, Dict, List, Type, Union

from attr import attrs
import pytest

from jsonschema_objects.constants import NotProvidedType, NOT_PROVIDED
from jsonschema_objects.models import (
    ArraySchema,
    IntegerSchema,
    model_from_types,
    NumberSchema,
    ObjectSchema,
    optional_type_attrib,
    Schema,
    StringSchema,
    type_attrib,
)


@attrs(kw_only=True)
class MockModel:
    required: str = type_attrib(str)()
    optional: Union[str, NotProvidedType] = optional_type_attrib(str)()


class TestTypeAttributeHelpers:
    @staticmethod
    def test_that_we_can_instantiate_without_optional_arg():
        assert MockModel(required="foo")

    @staticmethod
    @pytest.mark.parametrize("arg", [NOT_PROVIDED, "bar"])
    def test_that_we_can_instantiate_with_valid_optional_arg(arg: Any):
        assert MockModel(required="foo", optional=arg)

    @staticmethod
    def test_that_class_cant_be_instantiated_without_required():
        with pytest.raises(TypeError):
            MockModel(optional="foo")

    @staticmethod
    @pytest.mark.parametrize(
        "arg", [1, 2.3, None, ["foo"], {"bar": "baz"}, NOT_PROVIDED]
    )
    def test_that_class_cant_be_instantiated_with_invalid_required_types(
        arg: Any
    ):
        with pytest.raises(TypeError):
            MockModel(required=arg, optional="foo")

    @staticmethod
    @pytest.mark.parametrize("arg", [None, 1, 2.3, ["foo"], {"bar": "baz"}])
    def test_that_excluded_types_may_not_be_passed_to_optional_attr(arg: Any):
        with pytest.raises(TypeError):
            MockModel(required="foo", optional=arg)


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

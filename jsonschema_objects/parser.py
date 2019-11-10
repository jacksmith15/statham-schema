from collections import defaultdict
from enum import Enum, unique
from functools import partial
from typing import Any, Callable, Dict, List, NamedTuple, Optional, Type, Union

from attr import attrs, attrib, validators


INDENT = " " * 4


# This is a stateful function.
class _Counter:  # pylint: disable=too-few-public-methods
    def __init__(self):
        self.counts = defaultdict(lambda: 0)

    def __call__(self, key: str) -> str:
        self.counts[key] = self.counts[key] + 1
        return f"{key}{self.counts['key']}"


counter: Callable = _Counter()


NotProvidedType = type(
    "NotProvidedType", tuple(), {"__repr__": lambda self: "<NOTPROVIDED>"}
)
NOT_PROVIDED: NotProvidedType = NotProvidedType()


not_required: Callable[[Type], Type] = lambda Type_: Union[Type_, NotProvidedType]


IGNORED = ("$schema", "definitions")


def type_attrib(*types: Type):
    return partial(attrib, validator=[validators.instance_of(tuple(types))])


def optional_type_attrib(*types: Type):
    return partial(type_attrib(NotProvidedType, *types), default=NOT_PROVIDED)


@unique
class TypeEnum(Enum):
    OBJECT = "object"
    ARRAY = "array"
    NUMBER = "number"
    INTEGER = "integer"
    STRING = "string"
    NULL = "null"


TYPE_ANNOTATION = {
    TypeEnum.OBJECT.value: "Dict",
    TypeEnum.ARRAY.value: "List",
    TypeEnum.NUMBER.value: "float",
    TypeEnum.INTEGER.value: "int",
    TypeEnum.STRING.value: "str",
    TypeEnum.NULL.value: "type(None)",
}


# Dataclass.
@attrs(kw_only=True)
class Schema:  # pylint: disable=too-few-public-methods
    title: str = type_attrib(str)(converter=lambda x: x.title())
    type: str = type_attrib(str)()
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

    def as_init(self, key: str) -> str:
        if not self.nullable:
            return [
                f"{key} = None if {key} == NOT_PASSED else {key}",
                f"if {key} is None:",
                f'{INDENT}raise ValueError("{key} cannot be None.")',
                f"self.{key}: {self.type_annotation} = {key}",
            ]
        return [f"self.{key}: {self.type_annotation} = {key}"]


def schema_type(schema: Dict[str, Any], title: Optional[str] = None) -> Type[Schema]:
    if "type" not in schema:
        raise ValueError(f"No type or ref defined in schema: {schema}")
    type_lookup = {
        TypeEnum.ARRAY.value: ArraySchema,
        TypeEnum.OBJECT.value: ObjectSchema,
        TypeEnum.INTEGER.value: IntegerSchema,
        TypeEnum.NUMBER.value: NumberSchema,
        TypeEnum.STRING.value: StringSchema,
        TypeEnum.NULL.value: NullSchema,
    }
    title = title or counter(schema["type"])
    if "description" not in schema:
        schema["description"] = title
    return partial(type_lookup[schema["type"]], title=title)


def parse_schema_recur(schema: Dict[str, Any]) -> Schema:
    return schema_type(schema)(**schema)


def parse_schema(schema: Dict[str, Any], base_uri: str = None) -> Schema:
    deref_schema = dereference_schema(schema, base_uri, schema)
    return parse_schema_recur(deref_schema)


def get_ref(
    schema: Dict[str, Any], base_uri: Optional[str], reference: str
) -> Dict[str, Any]:
    filename, path = reference.split("#")
    if filename:
        assert base_uri
        raise NotImplementedError
    output = schema
    for breadcrumb in path.strip("/").split("/"):
        try:
            output = output[breadcrumb]
        except KeyError:
            raise KeyError(f"Couldnt resolve pointer: {reference}")
    return output


def dereference_schema(
    schema: Dict[str, Any], base_uri: Optional[str], element: Any
) -> Dict[str, Any]:
    deref = partial(dereference_schema, schema, base_uri)
    if isinstance(element, list):
        return [deref(item) for item in element]
    if not isinstance(element, dict):
        return element
    if "$ref" in element:
        ref_schema = get_ref(schema, base_uri, element["$ref"])
        if not isinstance(ref_schema, dict):
            raise NotImplementedError
        ref_schema["title"] = element["$ref"].split("/")[-1]
        return deref(ref_schema)
    return {key: deref(value) for key, value in element.items() if key not in IGNORED}


# Dataclasses
# pylint: disable=too-few-public-methods
@attrs(kw_only=True)
class ArraySchema(Schema):
    items: Schema = type_attrib(Schema)(converter=parse_schema_recur)
    minItems: not_required(int) = optional_type_attrib(int)
    maxItems: not_required(int) = optional_type_attrib(int)

    @property
    def base_type_annotation(self):
        nested_type = self.items.base_type_annotation
        return f"List[{nested_type}]"


@attrs(kw_only=True)
class ObjectSchema(Schema):
    properties: Dict[str, Schema] = type_attrib(dict)(
        converter=lambda x: {prop: parse_schema_recur(schema) for prop, schema in x.items()}
    )
    required: List[str] = optional_type_attrib(list)(
        converter=lambda x: x if x != NOT_PROVIDED else []
    )

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

    def as_init(self, key: str) -> str:
        lines = super().as_init(key)
        lines[-1] = f"self.{key} = {self.title}(**{key})"
        return lines


@attrs(kw_only=True)
class LiteralSchema(Schema):
    default: Any = attrib(default=NOT_PROVIDED)


@attrs(kw_only=True)
class NumberSchema(Schema):
    minimum: not_required(float) = optional_type_attrib(float)()
    exclusiveMinimum: not_required(float) = optional_type_attrib(float)()
    maximum: not_required(float) = optional_type_attrib(float)()
    exclusiveMinimum: not_required(float) = optional_type_attrib(float)()
    multipleOf: not_required(float) = optional_type_attrib(float)()


@attrs(kw_only=True)
class IntegerSchema(Schema):
    minimum: not_required(int) = optional_type_attrib(int)()
    exclusiveMinimum: not_required(int) = optional_type_attrib(int)()
    maximum: not_required(int) = optional_type_attrib(int)()
    exclusiveMinimum: not_required(int) = optional_type_attrib(int)()
    multipleOf: not_required(int) = optional_type_attrib(int)()


@attrs(kw_only=True)
class StringSchema(LiteralSchema):
    format: not_required(str) = optional_type_attrib(str)()
    pattern: not_required(str) = optional_type_attrib(str)()


@attrs(kw_only=True)
class NullSchema(Schema):
    pass


# pylint: enable=too-few-public-methods

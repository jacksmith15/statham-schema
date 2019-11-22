from typing import Dict, Set

from attr import attrs

from statham.exceptions import SchemaParseError
from statham.models import ArraySchema, ObjectSchema, Schema


# This is a dataclass.
# pylint: disable=too-few-public-methods
@attrs(auto_attribs=True)
class ClassDef:
    schema: ObjectSchema
    depends: Set[str]


def _get_first_class_schema(schema: Schema) -> ObjectSchema:
    if isinstance(schema, ObjectSchema):
        return schema
    if isinstance(schema, ArraySchema):
        return _get_first_class_schema(schema.items)
    raise SchemaParseError.no_class_equivalent_schemas()


class ClassDependencyResolver:
    """Iterator which returns classes in declaration order."""

    def __init__(self, schema: Schema):
        self._class_defs: Dict[str, ClassDef] = {}
        _ = self._extract_schemas(_get_first_class_schema(schema))

    def _extract_schemas(self, schema: ObjectSchema) -> Set[str]:
        if schema.title in self._class_defs:
            return self[schema.title].depends
        deps = {schema.title}
        for nested in schema.properties.values():
            try:
                next_schema: ObjectSchema = _get_first_class_schema(nested)
            except SchemaParseError:
                continue
            deps = deps | self._extract_schemas(next_schema)
        self._add(
            schema.title, ClassDef(schema=schema, depends=deps - {schema.title})
        )
        return deps

    def __getitem__(self, key: str) -> ClassDef:
        return self._class_defs[key]

    def __iter__(self) -> "ClassDependencyResolver":
        return self

    def __next__(self) -> ObjectSchema:
        next_item = self._next_key()
        for value in self._class_defs.values():
            value.depends = value.depends - {next_item}
        return self._class_defs.pop(next_item).schema

    def _add(self, key: str, class_def: ClassDef):
        self._class_defs[key] = class_def

    def _next_key(self) -> str:
        try:
            return next(
                key
                for key, value in self._class_defs.items()
                if not value.depends
            )
        except StopIteration as exc:
            if not self._class_defs:
                raise exc
            raise SchemaParseError.unresolvable_declaration()

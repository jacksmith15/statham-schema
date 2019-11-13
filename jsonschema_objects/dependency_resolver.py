from typing import Set

from attr import attrs

from jsonschema_objects.models import ArraySchema, ObjectSchema, Schema


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
    raise ValueError(f"Schema contains no class-equivalent schemas.")


class ClassDependencyResolver:
    """Iterates classes defined by a schema in an order which is safe for declaration."""

    def __init__(self, schema: Schema):
        self.class_defs = {}
        _ = self._extract_schemas(_get_first_class_schema(schema))

    def _extract_schemas(self, schema: ObjectSchema) -> Set[str]:
        if schema.title in self.class_defs:
            return self[schema.title].depends
        deps = {schema.title}
        for nested in schema.properties.values():
            if isinstance(nested, ObjectSchema):
                deps = deps | self._extract_schemas(nested)
            if isinstance(nested, ArraySchema):
                deps = deps | self._extract_schemas(nested.items)
        self._add(schema.title, ClassDef(schema=schema, depends=deps - {schema.title}))
        return deps

    def __getitem__(self, key: str) -> ClassDef:
        return self.class_defs[key]

    def __iter__(self) -> "ClassDependencyResolver":
        return self

    def __next__(self) -> ObjectSchema:
        next_item = self._next_key()
        for value in self.class_defs.values():
            value.depends = value.depends - {next_item}
        return self.class_defs.pop(next_item).schema

    def _add(self, key: str, class_def: ClassDef):
        self.class_defs[key] = class_def

    def _next_key(self) -> str:
        try:
            return next(
                key for key, value in self.class_defs.items() if not value.depends
            )
        except StopIteration as exc:
            if not self.class_defs:
                raise exc
            raise ValueError(f"Unresolvable declaration tree.")

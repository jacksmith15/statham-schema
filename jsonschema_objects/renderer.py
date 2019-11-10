from typing import Any, Dict, NamedTuple, Set, Tuple
from jsonschema_objects.parser import INDENT, ObjectSchema, ArraySchema


def _required_init_lines(key: str) -> str:
    return [
        f"if {key} == NOT_PASSED:",
        f'{INDENT}raise ValueError("{key} is required.")',
    ]


def to_python(schema: ObjectSchema):
    init_lines = []
    for key in schema.required or []:
        init_lines = init_lines + _required_init_lines(key)
    for key, value in schema.properties.items():
        init_lines = init_lines + value.as_init(key)
    init = f"\n{INDENT}{INDENT}".join(init_lines)
    args = ", ".join([value.as_arg(key) for key, value in schema.properties.items()])
    return f"""
class {schema.title}:
{INDENT}def __init__(self, {args}):
{INDENT}{INDENT}{init}
"""


class ClassDef(NamedTuple):
    schema: ObjectSchema
    depends: Set[str]


class ClassTree:
    def __init__(self):
        self.class_defs = {}

    def __getitem__(self, key: str) -> ClassDef:
        return self.class_defs[key]

    def add(self, key: str, class_def: ClassDef):
        self.class_defs[key] = class_def

    def _next(self):
        try:
            return next(key for key, value in self.class_defs.items() if not value.depends)
        except StopIteration:
            raise ValueError(f"Unresolvable declaration tree.")

    def pop(self):
        next_item = self._next()
        for value in self.class_defs.values():
            value.depends = value.depends - {next_item}
        return self.class_defs.pop(next_item)


def collect_class_dependencies(class_tree: ClassTree, schema: ObjectSchema):
    if schema.title in class_tree.class_defs:
        return class_tree[schema.title].depends
    deps = {schema.title}
    for nested in schema.properties.values():
        if isinstance(nested, ObjectSchema):
            deps = deps | collect_class_dependencies(class_tree, nested)
        if isinstance(nested, ArraySchema):
            deps = deps | collect_class_dependencies(class_tree, nested.items)
    class_tree.add(schema.title, ClassDef(schema=schema, depends=deps - {schema.title}))
    return deps


def get_class_defs(schema: ObjectSchema):
    class_tree = ClassTree()
    _deps = collect_class_dependencies(class_tree, schema)
    return class_tree

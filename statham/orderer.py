from itertools import chain
from typing import Dict, Iterator, List, Set


from statham.dsl.elements import Array, CompositionElement, Element
from statham.dsl.elements.meta import ObjectMeta
from statham.dsl.exceptions import SchemaParseError


class ClassDef:
    """Data class for capturing dependencies between Object elements."""

    def __init__(self, element: ObjectMeta, depends: Set[str]):
        self.element: ObjectMeta = element
        self.depends: Set[str] = depends


def _get_dependent_object_elements(element: Element) -> List[ObjectMeta]:
    """Extract any elements which are required by this element.

    Recurses through the schema tree to extract both explicit and
    implicit dependencies.
    """
    if isinstance(element, ObjectMeta):
        return [element]
    if isinstance(element, Array):
        return _get_dependent_object_elements(element.items)
    if isinstance(element, CompositionElement):
        return list(
            chain.from_iterable(
                _get_dependent_object_elements(sub_element)
                for sub_element in element.elements
            )
        )
    return []


def _iter_object_deps(object_type: ObjectMeta) -> Iterator[Element]:
    """Iterate over related elements to an Object subclass."""
    for prop in object_type.properties.values():
        yield prop.element
    if isinstance(object_type.options.additionalProperties, Element):
        yield object_type.options.additionalProperties


class Orderer:
    """Iterator which returns object elements in declaration order.

    Used by the serializer to generate code in the correct order.
    """

    def __init__(self, *elements: Element):
        self._class_defs: Dict[str, ClassDef] = {}
        try:
            self._extract_all(*elements)
        except RecursionError:
            raise SchemaParseError.unresolvable_declaration()

    def _extract_all(self, *elements: Element):
        for element in elements:
            for object_element in _get_dependent_object_elements(element):
                self._extract_elements(object_element)

    def _extract_elements(self, object_type: ObjectMeta) -> Set[str]:
        if object_type.__name__ in self._class_defs:
            return self[object_type.__name__].depends
        deps = {object_type.__name__}
        for sub_element in _iter_object_deps(object_type):
            next_objects = _get_dependent_object_elements(sub_element)
            deps = deps | set(
                chain.from_iterable(map(self._extract_elements, next_objects))
            )
        self._add(
            object_type.__name__,
            ClassDef(
                element=object_type, depends=deps - {object_type.__name__}
            ),
        )
        return deps

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

    def __getitem__(self, key: str) -> ClassDef:
        return self._class_defs[key]

    def __iter__(self) -> "Orderer":
        return self

    def __next__(self) -> ObjectMeta:
        next_item = self._next_key()
        for value in self._class_defs.values():
            value.depends = value.depends - {next_item}
        return self._class_defs.pop(next_item).element

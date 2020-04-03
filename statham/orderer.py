from itertools import chain
from typing import Dict, Iterator, List, Set, Union

from statham.dsl.constants import Maybe, NotPassed
from statham.dsl.elements import CompositionElement, Element
from statham.dsl.elements.meta import ObjectMeta
from statham.dsl.exceptions import SchemaParseError
from statham.dsl.property import _Property


class ClassDef:
    """Data class for capturing dependencies between Object elements."""

    def __init__(self, element: ObjectMeta, depends: Set[str]):
        self.element: ObjectMeta = element
        self.depends: Set[str] = depends


def _get_dependent_object_elements(element: Maybe[Element]) -> List[ObjectMeta]:
    """Extract any elements which are required by this element.

    Recurses through the schema tree to extract both explicit and
    implicit dependencies.
    """
    if isinstance(element, ObjectMeta):
        return [element]
    if isinstance(element, CompositionElement):
        return list(
            chain.from_iterable(
                _get_dependent_object_elements(sub_element)
                for sub_element in element.elements
            )
        )
    get_keyword = lambda kw: getattr(element, kw, NotPassed())
    items: Maybe[Element] = get_keyword("items")
    properties: Maybe[Dict[str, _Property]] = get_keyword("properties")
    additional_properties: Maybe[Union[Element, bool]] = get_keyword(
        "additionalProperties"
    )
    pattern_properties: Maybe[Dict[str, Element]] = get_keyword(
        "patternProperties"
    )
    dependent: Set[ObjectMeta] = set()
    if not isinstance(items, NotPassed):
        dependent = dependent | set(_get_dependent_object_elements(items))
    if not isinstance(properties, NotPassed):
        dependent = dependent | {
            dep
            for prop in properties.values()  # pylint: disable=no-member
            for dep in _get_dependent_object_elements(prop.element)
        }
    if not isinstance(additional_properties, (NotPassed, bool)):
        dependent = dependent | set(
            _get_dependent_object_elements(additional_properties)
        )
    if not isinstance(pattern_properties, NotPassed):
        dependent = dependent | {
            dep
            for elem in pattern_properties.values()  # pylint: disable=no-member
            for dep in _get_dependent_object_elements(elem)
        }
    return sorted(dependent, key=lambda obj_type: obj_type.__name__)


def _iter_object_deps(object_type: ObjectMeta) -> Iterator[Element]:
    """Iterate over related elements to an Object subclass."""
    for prop in object_type.properties.values():
        yield prop.element
    if isinstance(object_type.additionalProperties, Element):
        yield object_type.additionalProperties
    yield from object_type.patternProperties.values()


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

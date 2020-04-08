from typing import Any, Iterator, Set

from statham.dsl.elements.meta import Element, ObjectMeta


def orderer(*elements: Element):
    object_classes = [
        child
        for element in elements
        for child in get_children(element)
        if isinstance(child, ObjectMeta)
    ]
    object_dependencies = {
        object_class.__name__: [
            dep.__name__
            for dep in get_children(object_class)
            if isinstance(dep, ObjectMeta) and dep is not object_class
        ]
        for object_class in object_classes
    }

    def has_cycle(name, seen=None):
        seen = seen or []
        if name in seen:
            return True
        seen.append(name)
        for dep in object_dependencies[name]:
            return has_cycle(dep, seen)
        return False

    def from_name(name: str):
        return next(filter(lambda oc: oc.__name__ == name, object_classes))

    def pop_name(name: str):
        object_dependencies.update(
            {
                name_: [dep for dep in deps if dep != name]
                for name_, deps in object_dependencies.items()
            }
        )
        del object_dependencies[name]

    cycles = sorted(name for name in object_dependencies if has_cycle(name))
    for name in cycles:
        pop_name(name)

    def _next():
        next_name = next(
            map(
                lambda _: _[0],
                filter(lambda _: not _[1], object_dependencies.items()),
            )
        )
        pop_name(next_name)
        return from_name(next_name)

    try:
        while True:
            yield _next()
    except StopIteration:
        assert not object_dependencies.values()
        yield from map(from_name, cycles)
        return


def get_children(element: Any, seen: Set[int] = None) -> Iterator[Element]:
    """Iterate all child elements of an element."""
    seen = seen or set()
    if id(element) in seen:
        return
    seen.add(id(element))
    yield element
    attr = lambda key: getattr(element, key, None)
    if isinstance(attr("items"), Element):
        yield from get_children(element.items, seen)
    if isinstance(attr("items"), list):
        for item in element.items:
            yield from get_children(item, seen)
    if isinstance(attr("properties"), dict):
        for prop in element.properties.values():
            yield from get_children(prop.element, seen)
    if isinstance(attr("additionalProperties"), Element):
        yield from get_children(element.additionalProperties, seen)
    if isinstance(attr("patternProperties"), dict):
        for elem in element.patternProperties.values():
            yield from get_children(elem, seen)
    if isinstance(attr("propertyNames"), Element):
        yield from get_children(element.propertyNames, seen)
    if isinstance(attr("dependencies"), dict):
        for value in element.dependencies.values():
            if isinstance(value, Element):
                yield from get_children(value, seen)
    if isinstance(attr("elements"), list):
        for value in element.elements:
            yield from get_children(value, seen)
    if isinstance(attr("element"), Element):
        yield from get_children(element.element, seen)

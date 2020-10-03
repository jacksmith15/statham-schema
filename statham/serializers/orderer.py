"""Iteration tools for Element trees."""
from itertools import chain
from typing import Any, Dict, Iterator, List, Set

from statham.schema.elements import Element
from statham.schema.elements.meta import ObjectMeta
from statham.schema.exceptions import SchemaParseError


# TODO: Generate non-object elements.


def orderer(*elements: Element) -> Iterator[ObjectMeta]:
    """Iterate object classes in declaration order.

    Inspects the full DAG of elements and orders in such a way that
    each object class' dependencies are returned before it is.

    Accepts multiple elements, in case there are multiple start points of
    the DAG.

    Assumes each object class in the tree has a unique name.
    """
    object_classes: List[ObjectMeta] = get_object_classes(*elements)
    object_dependencies: Dict[str, List[str]] = {
        object_class.__name__: [
            dep.__name__
            for dep in get_children(object_class)
            if isinstance(dep, ObjectMeta)
        ]
        for object_class in object_classes
    }

    def has_cycle(name):
        return name in object_dependencies[name]

    def from_name(name: str) -> ObjectMeta:
        """Get the object class from the name."""
        return next(filter(lambda oc: oc.__name__ == name, object_classes))

    def pop_name(name: str) -> ObjectMeta:
        """Remove a object class from each sub-tree, and return it."""
        object_dependencies.update(
            {
                name_: [dep for dep in deps if dep != name]
                for name_, deps in object_dependencies.items()
            }
        )
        del object_dependencies[name]
        return from_name(name)

    cycles: List[str] = sorted(
        name for name in object_dependencies if has_cycle(name)
    )
    if cycles:
        raise SchemaParseError.unresolvable_declaration()

    def _next() -> ObjectMeta:
        next_name = next(
            map(
                lambda _: _[0],
                filter(lambda _: not _[1], object_dependencies.items()),
            )
        )
        return pop_name(next_name)

    try:
        while True:
            yield _next()
    except StopIteration:
        assert not object_dependencies.values()
        return


def get_object_classes(*elements: Element) -> List[ObjectMeta]:
    return [
        element
        for element in list(elements)
        + [child for element in elements for child in get_children(element)]
        if isinstance(element, ObjectMeta)
    ]


def get_children(element: Any, seen: Set[int] = None) -> Iterator[Element]:
    """Iterate all child elements of an element."""
    seen = seen or set()
    if id(element) in seen:
        yield element
        return
    seen.add(id(element))
    paths = [  # Possible paths to immediate children.
        "items",
        "additionalItems",
        "contains",
        "properties.*.element",
        "additionalProperties",
        "patternProperties.*",
        "propertyNames",
        "dependencies.*",
        "elements",
        "element",
    ]
    children = [
        child
        for path in paths
        for child in _get_path(element, path)
        if isinstance(child, Element)
    ]
    for child in children:
        yield child
        yield from get_children(child, seen)


def _get_path(element, path):
    """Get items matching a dot-separated path.

    Assumes dictionary lookup, but falls back to attribute access. If an
    item is a list, chain the remaining results for each item. If a path
    segment is * then get for all values (dictionary only).

    If there is no match on a path, then return nothing at all.
    """
    first, *rest = path.split(".")
    if first == "*":
        try:
            next_item = list(element.values())
        except AttributeError:
            return []
    else:
        try:
            next_item = element[first]
        except (KeyError, TypeError):
            try:
                next_item = getattr(element, first)
            except AttributeError:
                return []
    if isinstance(next_item, list):
        if not rest:
            return next_item
        return list(
            chain.from_iterable(
                _get_path(next_subitem, ".".join(rest))
                for next_subitem in next_item
            )
        )
    if not rest:
        return [next_item]
    return _get_path(next_item, ".".join(rest))

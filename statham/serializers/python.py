from typing import Set, Type, Union

from statham.dsl.elements import Element, Object
from statham.dsl.elements.meta import ObjectMeta
from statham.serializers.orderer import orderer, get_children


def serialize_python(*elements: Element) -> str:
    """Serialize DSL elements to python declaration string.

    Captures declaration of the first Object elements, and any subsequent
    elements this depends on. Module imports and declaration order are
    dynamically inferred.

    :param elements: The :class:`~statham.dsl.elements.Element` objects
        to serialize.
    :return: Python module contents as a string, declaring the DSL tree.
    """
    declarations = "\n\n".join(
        [object_model.python() for object_model in orderer(*elements)]
    )
    imports = _get_imports(declarations, *elements)
    return "\n\n\n".join(block for block in [imports, declarations] if block)


def _get_imports(declarations: str, *elements: Element) -> str:
    """Get import statements required by the DSL elements."""
    imports = [
        _get_standard_imports(declarations),
        _get_statham_imports(declarations, *elements),
    ]
    return "\n\n".join(block for block in imports if block)


def _get_standard_imports(declaration: str) -> str:
    """Get group if imports from standard library.

    Currently only includes type annotations.
    """
    type_imports = ", ".join(
        [
            annotation
            for annotation in ("Any", "List", "Union")
            if annotation in declaration
        ]
    )
    if not type_imports:
        return ""
    return f"from typing import {type_imports}"


def _get_statham_imports(declaration: str, *elements: Element) -> str:
    """Construct imports from statham submodules."""
    statham_imports = []
    if "Maybe" in declaration:
        statham_imports.append("from statham.dsl.constants import Maybe")
    element_imports = _get_element_imports(*elements)
    if element_imports:
        statham_imports.append(element_imports)
    if "Property" in declaration:
        statham_imports.append("from statham.dsl.property import Property")
    return "\n".join(statham_imports)


def _get_element_imports(*elements: Element) -> str:
    """Get the import string for DSL elements in use."""
    prefix = "from statham.dsl.elements import "
    max_length = 80
    import_names = [
        elem_type.__name__
        for elem_type in set.union(
            *(_get_single_element_imports(element) for element in elements)
        )
    ]
    if not import_names:
        return ""
    imports = ", ".join(sorted(import_names))
    if max_length < len(prefix) + len(imports):
        imports = "\n    ".join(["("] + imports.split(" ")) + ",\n)"
    return prefix + imports


def _get_single_element_imports(
    element: Element,
) -> Set[Union[Type[Element], ObjectMeta]]:
    """Extract the set of element types used by a given element."""
    get_type = (
        lambda elem: Object if isinstance(elem, ObjectMeta) else type(elem)
    )
    children = [element, *get_children(element)]
    return set(map(get_type, children))  # type: ignore

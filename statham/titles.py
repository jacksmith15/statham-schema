from typing import Callable, Tuple

from statham.dsl.constants import COMPOSITION_KEYWORDS


def _pop(reference: str) -> str:
    base, pointer = reference.split("#")
    return "#".join([base, "/".join(pointer.split("/")[:-1])])


def _get_title_from_reference(reference: str) -> str:
    """Convert JSONSchema references to title fields.

    If the reference has a pointer, use the final segment, otherwise
    use the final segment of the base uri stripping any content type
    extension.

    :param reference: The JSONPointer reference.
    """
    reference = reference.rstrip("/")
    base, pointer = reference.split("#")
    if not pointer:
        return base.split("/")[-1].split(".")[0]
    title = pointer.split("/")[-1]
    if title == "items":
        return _get_title_from_reference(_pop(reference)) + "Item"
    if title.isdigit():
        # Handle anonymous schemas in an array.
        # E.G `{"anyOf": [{"type": "object"}]}`
        return _get_title_from_reference(_pop(reference)) + title
    if title in COMPOSITION_KEYWORDS:
        return _get_title_from_reference(_pop(reference))
    return title


def title_labeller() -> Callable[[str], Tuple[str, str]]:
    """Create a title labeller, enumerating repeated titles.

    Used to assign meaningful names to schemas which have no specified
    title.
    """

    def _get_title(reference: str) -> Tuple[str, str]:
        name = _get_title_from_reference(reference)
        return "_x_autotitle", name

    return _get_title

from typing import Callable, Tuple

from json_ref_dict import URI

from statham.dsl.constants import COMPOSITION_KEYWORDS


def _get_title_from_reference(reference: str) -> str:
    """Convert JSONSchema references to title fields.

    If the reference has a pointer, use the final segment, otherwise
    use the final segment of the base uri stripping any content type
    extension.

    :param reference: The JSONPointer reference.
    """
    uri = URI.from_string(reference)
    if not uri.pointer.strip("/"):
        return uri.uri_name.split(".")[0]
    title = uri.pointer.split("/")[-1]
    if title == "items":
        return _get_title_from_reference(repr(uri.back())) + "Item"
    if title.isdigit():
        # Handle anonymous schemas in an array.
        # E.G `{"anyOf": [{"type": "object"}]}`
        return _get_title_from_reference(repr(uri.back())) + title
    if title in COMPOSITION_KEYWORDS:
        return _get_title_from_reference(repr(uri.back()))
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

from collections import defaultdict
from typing import Callable, DefaultDict, Iterator, Tuple


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
        return (
            _get_title_from_reference(
                "#".join([base, "/".join(pointer.split("/")[:-1])])
            )
            + "Item"
        )
    return title


def title_labeller() -> Callable[[str], Tuple[str, str]]:
    """Create a title labeller, enumerating repeated titles.

    Used to assign meaningful names to schemas which have no specified
    title.
    """
    counter: DefaultDict[str, Iterator[int]] = defaultdict(
        lambda: iter(range(0, 1000))
    )

    def _get_title(reference: str) -> Tuple[str, str]:
        name = _get_title_from_reference(reference)
        count = next(counter[name])
        if count:
            name = f"{name}{count}"
        return "title", name

    return _get_title

from itertools import chain
import re
from typing import Any, Callable, Dict, Set, Type


def dict_map(
    function: Callable[[Any], Any], dictionary: Dict[Any, Any]
) -> Dict[Any, Any]:
    """Similar to `map`, but operates on a dictionary's values."""
    return {key: function(value) for key, value in dictionary.items()}


def dict_filter(
    function: Callable[[Any], bool], dictionary: Dict[Any, Any]
) -> Dict[Any, Any]:
    """Similar to `filter`, but operates on a dictionary's values."""
    return {key: value for key, value in dictionary.items() if function(value)}


def all_subclasses(klass: Type) -> Set[Type]:
    return set(klass.__subclasses__()).union(
        [s for c in klass.__subclasses__() for s in all_subclasses(c)]
    )


def _title_format(string: str) -> str:
    """Convert titles in schemas to class names."""
    words = re.split(r"[ _-]", string)
    segments = chain.from_iterable(
        [
            re.findall("[A-Z][^A-Z]*", word[0].upper() + word[1:])
            for word in words
        ]
    )
    return "".join(segment.title() for segment in segments)

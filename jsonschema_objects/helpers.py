from collections import defaultdict
from typing import Any, Callable, Dict, Set, Type, TypeVar

# This is a stateful function.
class _Counter:  # pylint: disable=too-few-public-methods
    """Callable which returns the number of calls for the given argument."""

    def __init__(self):
        self.counts = defaultdict(lambda: 0)

    def __call__(self, key: str) -> str:
        self.counts[key] = self.counts[key] + 1
        return f"{key}{self.counts['key']}"


counter: Callable = _Counter()


DictVal: Type = TypeVar("DictVal")


def dict_map(function: Callable[[DictVal], Any], dictionary: Dict[Any, DictVal]) -> Dict[Any, Any]:
    """Similar to `map`, but operates on a dictionary's values."""
    return {
        key: function(value)
        for key, value in dictionary.items()
    }


def all_subclasses(klass: Type) -> Set[Type]:
    return set(klass.__subclasses__()).union(
        [s for c in klass.__subclasses__() for s in all_subclasses(c)]
    )

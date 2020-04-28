import re
from typing import Any, Dict, Generic, Iterator, TypeVar

from statham.dsl.constants import NotPassed
from statham.dsl.elements.base import Element, Nothing
from statham.dsl.elements.composition import AllOf
from statham.dsl.property import _Property as Property


class Properties:
    """Interface for retrieving relevant schemas given a property name.

    Used internally by :class:`~statham.dsl.elements.Element`.
    """

    def __init__(self, element, props, pattern=None, additional=True):
        self.element = element
        self.props = props or {}
        self.pattern = PatternDict(pattern or {})
        for name, prop in self.props.items():
            prop.bind(name=name, parent=self.element)
        if isinstance(additional, bool):
            self.additional = {True: Element(), False: Nothing()}[additional]
        else:
            self.additional = additional

    def property(self, element, name):
        prop = Property(element)
        prop.bind(name=name, parent=self.element)
        return prop

    def __repr__(self):
        props = [repr(self.props)]
        if self.pattern:
            props.append(f"patternProperties={self.pattern}")
        if self.additional == Nothing():
            props.append("additionalProperties=False")
        elif self.additional != Element():
            props.append(f"additionalProperties={self.additional}")
        return f"{type(self).__name__}({', '.join(props)})"

    def __getitem__(self, key):
        prop = {prop.source: prop for prop in self.props.values()}.get(
            key, None
        )
        pattern_elems = list(self.pattern.getall(key))
        if not (prop or pattern_elems):
            return self.property(self.additional, key)
        if not prop:
            if len(pattern_elems) == 1:
                return self.property(pattern_elems[0], key)
            return self.property(AllOf(*pattern_elems), key)
        if not pattern_elems:
            return prop
        composite = Property(
            AllOf(prop.element, *pattern_elems),
            source=prop.source,
            required=prop.required,
        )
        composite.bind(name=prop.name, parent=prop.parent)
        return composite

    def __contains__(self, key):
        return bool(self[key].element != Nothing())

    def __iter__(self):
        return iter(self.props)

    def __call__(self, value):
        value = {
            **{prop.name: NotPassed() for prop in self.props.values()},
            **value,
        }
        return {
            self[key].name or key: self[key](sub_value)
            for key, sub_value in value.items()
        }


T = TypeVar("T")


class PatternDict(Dict[str, T], Generic[T]):
    """Dict for simplifying PatternProperties lookups."""

    def __getitem__(self, key: str) -> T:
        if not isinstance(key, str):
            raise KeyError
        try:
            return next(self.getall(key))
        except StopIteration:
            raise KeyError

    def getall(self, key: str) -> Iterator[T]:
        for pattern, value in self.items():
            if re.search(pattern, key):
                yield value

    def __contains__(self, key: Any) -> bool:
        try:
            _ = self[key]
            return True
        except KeyError:
            return False

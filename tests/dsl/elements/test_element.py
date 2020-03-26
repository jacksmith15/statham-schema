from typing import Any, Iterator, List, NamedTuple, Tuple
import pytest

from statham.dsl.constants import NotPassed
from statham.dsl.elements import Element
from statham.dsl.exceptions import ValidationError
from tests.helpers import no_raise


class Case(NamedTuple):
    element: Element
    good: List[Any]
    bad: List[Any]


CASES = [
    Case(
        element=Element(),
        good=[None, NotPassed(), True, 1, 1.2, "foo", {}, ["foo", 1]],
        bad=[],
    ),
    Case(
        element=Element(minItems=3),
        good=[None, NotPassed(), True, 1, 1.2, "foo", {}, ["foo", 1, 5]],
        bad=[[], [1, 2]],
    ),
    Case(
        element=Element(minimum=3),
        good=[None, NotPassed(), True, 3, 4.2, "foo", {}, ["foo", 1]],
        bad=[2, 2.1],
    ),
    Case(
        element=Element(minLength=3),
        good=[None, NotPassed(), True, 1, 1.2, "foo", {}, ["foo", 1]],
        bad=["ab", ""],
    ),
    Case(
        element=Element(minItems=3, minimum=3, minLength=3),
        good=[None, NotPassed(), True, 3, 4.2, "foo", {}, ["foo", 1, 5]],
        bad=[[], [1, 2], 2, 2.1, "ab", ""],
    ),
]


def to_test_params(cases: List[Case]) -> Iterator[Tuple[Element, Any, bool]]:
    for case in cases:
        for value in case.good:
            yield (case.element, value, False)
        for value in case.bad:
            yield (case.element, value, True)


@pytest.mark.parametrize("element,value,error", list(to_test_params(CASES)))
def test_element_validation_is_performed_on_given_types(element, value, error):
    with pytest.raises(ValidationError) if error else no_raise():
        element(value)

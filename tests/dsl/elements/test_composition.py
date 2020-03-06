from typing import Type

import pytest

from statham.dsl.elements import AnyOf, Array, CompositionElement, OneOf, String
from tests.helpers import Args, no_raise


class TestCompositionInstantiation:
    @staticmethod
    @pytest.mark.parametrize("element", [OneOf, AnyOf])
    @pytest.mark.parametrize(
        "args", [Args(String()), Args(String(), Array(String()))]
    )
    def test_element_instantiates_with_good_args(
        element: Type[CompositionElement], args: Args
    ):
        with no_raise():
            _ = args.apply(element)

    @staticmethod
    @pytest.mark.parametrize("element", [OneOf, AnyOf])
    @pytest.mark.parametrize("args", [Args()])
    def test_element_raises_on_bad_args(
        element: Type[CompositionElement], args: Args
    ):
        with pytest.raises(TypeError):
            _ = args.apply(element)

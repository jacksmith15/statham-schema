import pytest

from statham.dsl.elements import String
from tests.helpers import Args, no_raise


class TestStringInstantiation:
    @staticmethod
    @pytest.mark.parametrize(
        "args",
        [
            Args(),
            Args(default="sample"),
            Args(format="my_format"),
            Args(pattern=".*"),
            Args(minLength=1),
            Args(maxLength=3),
            Args(
                default="sample",
                format="my_format",
                pattern=".*",
                minLength=1,
                maxLength=3,
            ),
        ],
    )
    def test_element_instantiates_with_good_args(args):
        with no_raise():
            _ = args.apply(String)

    @staticmethod
    @pytest.mark.parametrize("args", [Args(invalid="keyword"), Args("sample")])
    def test_element_raises_on_bad_args(args):
        with pytest.raises(TypeError):
            _ = args.apply(String)

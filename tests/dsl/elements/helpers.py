from typing import Any

import pytest

from statham.dsl.exceptions import ValidationError
from statham.dsl.elements import Element
from statham.dsl.property import UNBOUND_PROPERTY
from tests.helpers import no_raise


def assert_validation(element: Element, success: bool, value: Any):
    if success:
        with no_raise():
            _ = element(value, UNBOUND_PROPERTY)
    else:
        with pytest.raises(ValidationError):
            _ = element(value, UNBOUND_PROPERTY)

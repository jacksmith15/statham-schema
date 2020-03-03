from typing import Dict, Union

from statham.dsl.elements.meta import JSONSchemaModelMeta
from statham.dsl.elements.base import Element
from statham.exceptions import ValidationError
from statham.validators import Attribute, NotPassed


class JSONSchemaModel(metaclass=JSONSchemaModelMeta):
    """Base model for JSONSchema objects.

    Recursively validates and construct properties.
    """

    schema_properties: Dict[str, Union[JSONSchemaModelMeta, Element]]

    def __init__(self, kwargs):
        unexpected_kwargs = set(kwargs) - set(self.schema_properties)
        if unexpected_kwargs:
            raise ValidationError(
                f"Unexpected attributes passed to {self.__class__}: "
                f"{unexpected_kwargs}. Accepted kwargs: "
                f"{set(self.schema_properties)}"
            )
        for attr_name, sub_schema in self.schema_properties.items():
            setattr(
                self,
                attr_name,
                sub_schema(
                    self,
                    Attribute(attr_name, sub_schema),
                    kwargs.get(attr_name, NotPassed()),
                ),
            )

    def __repr__(self):
        attr_repr = ", ".join(
            [
                f"{attr}={repr(getattr(self, attr))}"
                for attr in self.schema_properties
            ]
        )
        return f"{self.__class__.__name__}({attr_repr})"

    def __str__(self):
        return repr(self)

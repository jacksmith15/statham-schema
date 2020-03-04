from typing import Any, cast, Type

from statham import validators as val
from statham.dsl.constants import NotPassed
from statham.dsl.elements.base import Element
from statham.dsl.elements.model import JSONSchemaModel
from statham.dsl.elements.meta import JSONSchemaModelMeta


class Object(Element):
    """JSONSchema object element.

    Wraps a JSONSchemaModel sub-class which provided property-based
    validation.
    """

    def __init__(
        self,
        model: JSONSchemaModelMeta,
        *,
        required: bool = False,
        default: Any = NotPassed(),
    ):
        val.instance_of(JSONSchemaModelMeta)(
            self, val.Attribute("model"), model
        )
        self.model: JSONSchemaModelMeta = model
        self.required = required
        if not isinstance(default, NotPassed):
            val.instance_of(cast(Type, self.model))(
                self, val.Attribute("default"), default
            )
        self.default = default

    @property
    def type_validator(self):
        return val.instance_of(dict, JSONSchemaModel)

    def construct(self, instance, attribute, value):
        if isinstance(self.model, Element):
            return self.model(instance, attribute, value)
        if isinstance(value, self.model):
            return value
        return self.model(value)

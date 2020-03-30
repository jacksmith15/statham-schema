import re
from typing import Any

from statham.dsl.exceptions import ValidationError
from statham.dsl.validation.base import Validator
from statham.dsl.validation.format import format_checker


class Format(Validator):
    types = (str,)
    keywords = ("format",)
    message = "Must match format described by '{format}'."

    def validate(self, value: Any):
        if not format_checker(self.params["format"], value):
            raise ValidationError


class Pattern(Validator):
    types = (str,)
    keywords = ("pattern",)
    message = "Must match regex pattern {pattern}."

    def error_message(self):
        return self.message.format(pattern=repr(self.params["pattern"]))

    def validate(self, value: Any):
        if not re.search(self.params["pattern"], value):
            raise ValidationError


class MinLength(Validator):
    types = (str,)
    keywords = ("minLength",)
    message = "Must be at least {minLength} characters long."

    def validate(self, value: Any):
        if len(value) < self.params["minLength"]:
            raise ValidationError


class MaxLength(Validator):
    types = (str,)
    keywords = ("maxLength",)
    message = "Must be at most {maxLength} characters long."

    def validate(self, value: Any):
        if len(value) > self.params["maxLength"]:
            raise ValidationError

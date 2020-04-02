from typing import List, Union

from statham.dsl.constants import Maybe
from statham.dsl.elements import (
    AnyOf,
    Array,
    Boolean,
    Integer,
    Null,
    Number,
    OneOf,
    Object,
    String,
)
from statham.dsl.property import Property


class Category(Object):

    required_name: str = Property(String(), required=True)


class Child(Object):

    name: Maybe[str] = Property(String())

    category: Maybe[Category] = Property(Category)


class Model(Object):

    children: Maybe[List[Child]] = Property(Array(Child))

    category: Maybe[Category] = Property(Category)

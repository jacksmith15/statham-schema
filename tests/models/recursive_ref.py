from typing import Any, List, Union

from statham.dsl.constants import Maybe
from statham.dsl.elements import (
    AllOf,
    AnyOf,
    Array,
    Boolean,
    Integer,
    Nothing,
    Null,
    Number,
    OneOf,
    Object,
    String,
)
from statham.dsl.property import Property


class Other(Object):

    value: Maybe[str] = Property(String())


class Child(Object):

    parent: Maybe[Parent] = Property(Parent)


class Parent(Object):

    children: Maybe[List[Child]] = Property(Array(Child))

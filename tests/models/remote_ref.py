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


class NestedRemote(Object):

    name: Maybe[str] = Property(String())


class Remote(Object):

    name: Maybe[str] = Property(String())

    nested: Maybe[NestedRemote] = Property(NestedRemote)


class Model(Object):

    filesystem_remote_ref_flat: Maybe[Category] = Property(Category)

    filesystem_remote_ref_directory: Maybe[Remote] = Property(Remote)

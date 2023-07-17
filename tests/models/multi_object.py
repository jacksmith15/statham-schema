from typing import List

from statham.schema.constants import Maybe
from statham.schema.elements import Array, Object, String
from statham.schema.property import Property


class Category(Object):
    """Category with required name."""

    required_name: str = Property(String(), required=True)


class Child(Object):
    """Model with name and reference to category."""

    name: Maybe[str] = Property(String())

    category: Maybe[Category] = Property(Category)


class Model(Object):
    """Model with references to children and category."""

    children: Maybe[List[Child]] = Property(Array(Child))

    category: Maybe[Category] = Property(Category)

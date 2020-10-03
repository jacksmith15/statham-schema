from typing import List

from statham.schema.constants import Maybe
from statham.schema.elements import Array, Object, String
from statham.schema.property import Property


class Category(Object):

    required_name: str = Property(String(), required=True)


class Child(Object):

    name: Maybe[str] = Property(String())

    category: Maybe[Category] = Property(Category)


class Model(Object):

    children: Maybe[List[Child]] = Property(Array(Child))

    category: Maybe[Category] = Property(Category)

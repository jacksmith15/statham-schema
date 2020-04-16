from typing import List

from statham.dsl.constants import Maybe
from statham.dsl.elements import Array, Object, String
from statham.dsl.property import Property


class Model(Object):

    list_of_strings: Maybe[List[str]] = Property(Array(String()))

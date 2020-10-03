from typing import List

from statham.schema.constants import Maybe
from statham.schema.elements import Array, Object, String
from statham.schema.property import Property


class Model(Object):

    list_of_strings: Maybe[List[str]] = Property(Array(String()))

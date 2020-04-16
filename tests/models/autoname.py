from typing import Any, List, Union

from statham.dsl.constants import Maybe
from statham.dsl.elements import AnyOf, Array, Integer, Object, String
from statham.dsl.property import Property


class ListOfStringsItem(Object, additionalProperties=False):

    string_property: Maybe[str] = Property(String())


class ListOfIntegersItem(Object, additionalProperties=False):

    integer_property: Maybe[int] = Property(Integer())


class ListAnyOfItem0(Object, additionalProperties=False):

    string_prop: Maybe[str] = Property(String())


class ListAnyOfItem1(Object, additionalProperties=False):

    integer_prop: Maybe[int] = Property(Integer())


class Autoname(Object):

    list_of_strings: Maybe[List[ListOfStringsItem]] = Property(
        Array(ListOfStringsItem)
    )

    list_of_integers: Maybe[List[ListOfIntegersItem]] = Property(
        Array(ListOfIntegersItem)
    )

    list_any_of: Maybe[
        List[Union[ListAnyOfItem0, ListAnyOfItem1, str]]
    ] = Property(Array(AnyOf(ListAnyOfItem0, ListAnyOfItem1, String())))

from statham.dsl.constants import NotPassed
from statham.dsl.elements.base import Element, Nothing


class Items:
    """Interface for retrieving relevant schemas given an array index.

    Used internally by :class:`~statham.dsl.elements.Element`.
    """

    def __init__(self, items, additional=True):
        self.items = Element() if isinstance(items, NotPassed) else items
        if isinstance(additional, bool):
            self.additional = {True: Element(), False: Nothing()}[additional]
        else:
            self.additional = additional

    @staticmethod
    def property(property_, index):
        return property_.evolve(name=property_.name or "" + f"[{index}]")

    def __repr__(self):
        items = [repr(self.items)]
        if self.additional == Nothing():
            items.append("additionalItems=False")
        elif self.additional != Element():
            items.append(f"additionalItems={self.additional}")
        return f"{type(self).__name__}({', '.join(items)})"

    def __getitem__(self, index):
        if not isinstance(self.items, list):
            return self.items
        try:
            return self.items[index]
        except IndexError:
            return self.additional

    def __call__(self, value, property_):
        return [
            self[index](sub_value, self.property(property_, index))
            for index, sub_value in enumerate(value)
        ]

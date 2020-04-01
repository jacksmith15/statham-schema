from statham.dsl.property import _Property as Property
from statham.dsl.elements import Element, Nothing


class Properties:
    def __init__(self, element, props, additional=True):
        self.element = element
        self.props = props or {}
        for name, prop in self.props.items():
            prop.bind_name(name)
            prop.bind_class(self.element)
        if isinstance(additional, bool):
            self.additional = {True: Element(), False: Nothing()}[additional]
        else:
            self.additional = additional

    def property(self, element):
        prop = Property(element)
        prop.bind_class(self.element)
        return prop

    def __getitem__(self, key):
        try:
            return {prop.source: prop for prop in self.props.values()}[key]
        except KeyError:
            pass
        if not self.additional:
            raise KeyError
        return self.property(self.additional)

    def __contains__(self, key):
        try:
            _ = self[key]
            return True
        except KeyError:
            return False

    def __iter__(self):
        return iter(self.props)

from statham.dsl.property import Property
from statham.dsl.elements import String


def test_property_name():
    property_ = Property(String())
    assert property_.name == None
    property_.bind_name("bound")
    assert property_.name == property_._bound_name == "bound"
    property_._name = "override"
    assert property_.name == property_._name == "override"

from statham.schema.constants import Maybe
from statham.schema.elements import Integer, Object
from statham.schema.property import Property


class MyTestJSONSchema(Object):

    id: Maybe[int] = Property(Integer())

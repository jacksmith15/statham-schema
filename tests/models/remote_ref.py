from statham.schema.constants import Maybe
from statham.schema.elements import Object, String
from statham.schema.property import Property


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

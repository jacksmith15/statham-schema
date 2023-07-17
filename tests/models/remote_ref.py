from statham.schema.constants import Maybe
from statham.schema.elements import Object, String
from statham.schema.property import Property


class Category(Object):
    """Category with required name."""

    required_name: str = Property(String(), required=True)


class NestedRemote(Object):
    """Local reference nested in remote reference"""

    name: Maybe[str] = Property(String())


class Remote(Object):
    """Remote ref in sub-directory."""

    name: Maybe[str] = Property(String())

    nested: Maybe[NestedRemote] = Property(NestedRemote)


class Model(Object):
    """Model defined with remote refs."""

    filesystem_remote_ref_flat: Maybe[Category] = Property(Category)

    filesystem_remote_ref_directory: Maybe[Remote] = Property(Remote)

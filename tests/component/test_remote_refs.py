from tests.models.remote_ref import Category, Model, NestedRemote, Remote


def test_root_model_instantiates():
    assert Model({})


def test_flat_remote_instantiates():
    assert Category(dict(required_name="foo"))


def test_remote_in_subdirectory_instantiates():
    assert Remote({})


def test_nested_remote_instantiates():
    assert NestedRemote({})


def test_model_instantiates_with_nesting():
    data = {
        "filesystem_remote_ref_flat": {"required_name": "foo"},
        "filesystem_remote_ref_directory": {
            "name": "bar",
            "nested": {"name": "foo"},
        },
    }
    assert Model(data)

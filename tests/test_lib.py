import statham


def test_that_library_version_is_semantic():
    version_string = statham.__version__
    version = version_string.split(".")
    assert (
        len(version) == 3
    ), f"Version: {version_string} should have three subcomponents."
    major, minor, fix = version
    for subversion, value in (("major", major), ("minor", minor), ("fix", fix)):
        try:
            int(value)
        except (TypeError, ValueError):
            assert (
                False
            ), f"{subversion}={value} is not a valid integer version."

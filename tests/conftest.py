from statham.dsl.elements.meta import ObjectMeta


def pytest_configure(config):
    # register an additional marker
    config.addinivalue_line(
        "markers",
        "github_issue(id): mark test as corresponding to a github issue.",
    )


# Magic pytest argument.
# pylint: disable=invalid-name
def pytest_assertrepr_compare(op, left, right):
    if (
        isinstance(left, ObjectMeta)
        and isinstance(right, ObjectMeta)
        and op == "=="
    ):
        pubvars = lambda obj: sorted(
            f"  {key}={repr(value)}"
            for key, value in vars(obj).items()
            if not key.startswith("_") or key == "_properties"
        )
        return [
            "Comparing ObjectMeta instances:",
            "Left:",
            *pubvars(left),
            "Right:",
            *pubvars(right),
        ]
    return None

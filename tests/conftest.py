def pytest_configure(config):
    # register an additional marker
    config.addinivalue_line(
        "markers",
        "github_issue(id): mark test as corresponding to a github issue.",
    )

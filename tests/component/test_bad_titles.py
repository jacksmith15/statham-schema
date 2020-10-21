from tests.models.bad_titles import MyTestJSONSchema


def test_schema_has_expected_title():
    assert MyTestJSONSchema.__name__ == "MyTestJSONSchema"

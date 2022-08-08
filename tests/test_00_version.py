import cads_toolbox


def test_version() -> None:
    assert cads_toolbox.__version__ != "999"

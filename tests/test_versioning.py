from src.verysimpletransformers.versioning import define_version, get_version


@define_version(1)
class MyClass:
    first: str


@define_version(2)
class MyClass:
    second: int


class NotVersioned:
    third: float


def test_versioning():
    v1 = get_version(MyClass, 1)
    assert v1.__version__ == 1
    assert "first" in v1.__annotations__ and "second" not in v1.__annotations__

    v2 = get_version(MyClass, 2)
    assert v2.__version__ == 2
    assert "second" in v2.__annotations__ and "first" not in v2.__annotations__

    assert v1 is not v2 and v1 != v2

    latest = get_version(MyClass, "latest")

    assert latest is v2 and v2 == latest
    assert latest is not v1 and v1 != latest

    v3 = get_version(MyClass, 3)
    assert v3 is v2 is latest

    assert get_version(NotVersioned) is None

import pytest
from multiset_lib import MultiSet


@pytest.fixture()
def build():
    MultiSet.build()


def test_simple(build):
    MultiSet.simple_test()


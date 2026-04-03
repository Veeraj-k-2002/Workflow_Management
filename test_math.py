def add(a, b):
    return a + b

# def test_add():
#     assert add(2, 3) == 5

import pytest

@pytest.mark.parametrize("a,b,result", [
    (1,2,3),
    (2,3,5),
    (10,5,15)
])
def test_add(a,b,result):
    assert add(a,b) == result
"""Some test submodule"""
from typing import Any


def testfunc(arg1: Any, kwarg1: Any = None) -> str:
    """testfunc docstring"""
    return f"testfunc: {arg1}, {kwarg1}"


class TestClass:
    def testmeth(self, arg1: Any, kwarg1: Any = None) -> str:
        return f"testmeth: {arg1}, {kwarg1}"

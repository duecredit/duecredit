from typing import Any


def testfunc1(arg1: Any, kwarg1: Any = None) -> str:
    """custom docstring"""
    return f"testfunc1: {arg1}, {kwarg1}"


class TestClass1:
    """wrong custom docstring"""

    def testmeth1(self, arg1: Any, kwarg1: Any = None) -> str:
        """custom docstring"""
        return f"TestClass1.testmeth1: {arg1}, {kwarg1}"


class TestClass12:
    """wrong custom docstring"""

    class Embed:
        """wrong custom docstring"""

        def testmeth1(self, arg1: Any, kwarg1: Any = None) -> str:
            """custom docstring"""
            return f"TestClass12.Embed.testmeth1: {arg1}, {kwarg1}"

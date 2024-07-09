from typing import Any


def testfunc1(arg1: Any, kwarg1: Any = None) -> str:
    """custom docstring"""
    return "testfunc1: {}, {}".format(arg1, kwarg1)


class TestClass1:
    """wrong custom docstring"""

    def testmeth1(self, arg1: Any, kwarg1: Any = None) -> str:
        """custom docstring"""
        return "TestClass1.testmeth1: {}, {}".format(arg1, kwarg1)


class TestClass12:
    """wrong custom docstring"""

    class Embed:
        """wrong custom docstring"""

        def testmeth1(self, arg1: Any, kwarg1: Any = None) -> str:
            """custom docstring"""
            return "TestClass12.Embed.testmeth1: {}, {}".format(arg1, kwarg1)

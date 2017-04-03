def testfunc1(arg1, kwarg1=None):
    """custom docstring"""
    return "testfunc1: %s, %s" % (arg1, kwarg1)


class TestClass1(object):
    """wrong custom docstring"""
    def testmeth1(self, arg1, kwarg1=None):
        """custom docstring"""
        return "TestClass1.testmeth1: %s, %s" % (arg1, kwarg1)


class TestClass12(object):
    """wrong custom docstring"""
    class Embed(object):
        """wrong custom docstring"""
        def testmeth1(self, arg1, kwarg1=None):
            """custom docstring"""
            return "TestClass12.Embed.testmeth1: %s, %s" % (arg1, kwarg1)

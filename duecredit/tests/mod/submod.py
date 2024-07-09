"""Some test submodule"""


def testfunc(arg1, kwarg1=None):
    """testfunc docstring"""
    return "testfunc: %s, %s" % (arg1, kwarg1)


class TestClass(object):
    def testmeth(self, arg1, kwarg1=None):
        return "testmeth: %s, %s" % (arg1, kwarg1)

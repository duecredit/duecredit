def testfunc1(arg1, kwarg1=None):
    return "testfunc1: %s, %s" % (arg1, kwarg1)

class TestClass1(object):
    def testmeth1(self, arg1, kwarg1=None):
        return "TestClass1.testmeth1: %s, %s" % (arg1, kwarg1)


class TestClass12(object):
    class Embed(object):
        def testmeth1(self, arg1, kwarg1=None):
            return "TestClass12.Embed.testmeth1: %s, %s" % (arg1, kwarg1)
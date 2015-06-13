# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##

from ..collector import DueCreditCollector, InactiveDueCreditCollector
from ..entries import BibTeX, Doi

def _test_api(due):
    # add references
    due.add(BibTeX('@article{XXX00, ...}'))
    # could even be by DOI -- we need to fetch and cache those
    due.add(Doi("xxx.yyy/zzz.1", key="XXX01"))

    # and/or load multiple from a file
    due.load('/home/siiioul/deep/good_intentions.bib')

    # Cite entire module
    due.cite('XXX00', use="Answers to existential questions", level="module")

    # dcite  for decorator cite
    # cite specific functionality if/when it gets called up
    #@due.dcite('XXX00', use="Provides an answer for meaningless existence")
    def purpose_of_life():
        return None

    class Children(object):
         # Conception process is usually way too easy to be referenced
         def __init__(self):
             pass

         # including functionality within/by the methods
         #@due.dcite('BirthCertificate')
         def birth(self, gender):
             pass


def test_api():
    yield _test_api, DueCreditCollector()
    yield _test_api, InactiveDueCreditCollector()


if False:
    import inspect
    import traceback

    from mvpa2.support.fff import fff
    def fff_(*args, **kwargs):
        """Forget about smarness -- everything will be explicit
        """
        #import pydb; pydb.debugger()
        st = inspect.stack()
        ftb = traceback.extract_stack(limit=10)
        print("\nstack[1]: %r, module:%r" % (st[1], inspect.ismodule(st[1][0])))
        print("args: %s  kwargs: %s" % (args, kwargs))
        print('traceback: %s' % ftb)
        if ftb[-2][-1].startswith('@'):
            #TODO proper decorator preserving all the meta-information
            def decorate(func):
                print("Decorating %s with %s" % (func, dir(func)))
                #import pydb; pydb.debugger()
                i = 1
                pass 
            return decorate
        print("Nothing to decorate")


    @fff # makes no sense in our context?
    def testf(a1, kwarg1=None):
       pass

    @fff('with args')
    def testf2():
       pass

    def BU():
      class TC(object):
        @fff # makes no sense, right?
        def meth1(self):
            print("calling meth1")

        @fff('meth args')
        def meth2(self):
            print("calling meth2")
    b = BU()

if __name__ == '__main__':
    fff()

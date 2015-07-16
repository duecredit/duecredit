# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##

from duecredit.collector import DueCreditCollector, InactiveDueCreditCollector
from duecredit.entries import BibTeX, Doi

def _test_api(due):
    # add references
    due.add(BibTeX('@article{XXX00, ...}'))
    # could even be by DOI -- we need to fetch and cache those
    due.add(Doi("xxx.yyy/zzz.1", key="XXX01"))

    # and/or load multiple from a file
    due.load('/home/siiioul/deep/good_intentions.bib')

    # Cite entire module
    due.cite('XXX00', description="Answers to existential questions", path="module")
    # Cita some method within some submodule
    due.cite('XXX01', description="More answers to existential questions",
             path="module.submodule:class1.whoknowswhat2.func1")

    # dcite  for decorator cite
    # cite specific functionality if/when it gets called up
    @due.dcite('XXX00', description="Provides an answer for meaningless existence")
    def purpose_of_life():
        return None

    class Child(object):
         # Conception process is usually way too easy to be referenced
         def __init__(self):
             pass

         # including functionality within/by the methods
         @due.dcite('XXX00')
         def birth(self, gender):
             return "Rachel was born"

    kid = Child()
    kid.birth("female")


def test_api():
    yield _test_api, DueCreditCollector()
    yield _test_api, InactiveDueCreditCollector()

if __name__ == '__main__':
    from duecredit import due
    _test_api(due)
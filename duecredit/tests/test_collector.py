# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##

from ..collector import DueCreditCollector, InactiveDueCreditCollector, \
    CollectorSummary, Citation
from ..dueswitch import DueSwitch
from ..entries import BibTeX, Doi
from ..io import PickleOutput

import os
import pytest


def _test_entry(due, entry):
    due.add(entry)

_sample_bibtex = """
@ARTICLE{XXX0,
  author = {Halchenko, Yaroslav O. and Hanke, Michael},
  title = {Open is not enough. Let{'}s take the next step: An integrated, community-driven
    computing platform for neuroscience},
  journal = {Frontiers in Neuroinformatics},
  year = {2012},
  volume = {6},
  number = {00022},
  doi = {10.3389/fninf.2012.00022},
  issn = {1662-5196},
  localfile = {HH12.pdf},
}
"""
_sample_bibtex2 = """
@ARTICLE{Atkins_2002,
  title = {title},
  volume = {666},
  url = {https://doi.org/10.1038/nrd842},
  DOI = {10.1038/nrd842},
  number = {3009},
  journal = {My Fancy. Journ.},
  publisher = {The Publisher},
  author = {Atkins, Joshua H. and Gershell, Leland J.},
  year = {2002},
  month = {Jul},
}
"""
_sample_doi = "10.3389/fninf.2012.00022"


def test_citation_paths():
    entry = BibTeX(_sample_bibtex)

    cit1 = Citation(entry, path="somemodule")
    assert cit1.cites_module
    assert cit1.module == "somemodule"

    cit2 = Citation(entry, path="somemodule.submodule")
    assert cit2.cites_module
    assert cit2.module == "somemodule.submodule"

    assert cit1 in cit1
    assert cit2 in cit1
    assert cit1 not in cit2

    cit3 = Citation(entry, path="somemodule.submodule:class2.func2")
    assert not cit3.cites_module
    assert cit3.module == "somemodule.submodule"

    assert cit2 in cit1
    assert cit3 in cit1
    assert cit3 in cit2
    assert cit2 not in cit3

    cit4 = Citation(entry, path="somemodule2:class2.func2")
    assert not cit4.cites_module
    assert cit4.module == "somemodule2"

    assert cit1 not in cit4
    assert cit4 not in cit1


def test_entry():
    entry = BibTeX(_sample_bibtex)
    _test_entry(DueCreditCollector(), entry)

    entries = [BibTeX(_sample_bibtex), BibTeX(_sample_bibtex),
               Doi(_sample_doi)]
    _test_entry(DueCreditCollector(), entries)


def _test_dcite_basic(due, callable):
    assert callable("magical", 1) == "load"
    # verify that @wraps correctly passes all the docstrings etc
    assert callable.__name__ == "method"
    assert callable.__doc__ == "docstring"


def test_dcite_method():
    # Test basic wrapping that we don't mask out the arguments
    for due in [DueCreditCollector(), InactiveDueCreditCollector()]:
        active = isinstance(due, DueCreditCollector)
        due.add(BibTeX(_sample_bibtex))

        @due.dcite("XXX0", path='method')
        def method(arg1, kwarg2="blah"):
            """docstring"""
            assert arg1 == "magical"
            assert kwarg2 == 1
            return "load"

        class SomeClass:
            @due.dcite("XXX0", path='someclass:method')
            def method(self, arg1, kwarg2="blah"):
                """docstring"""
                assert arg1 == "magical"
                assert kwarg2 == 1
                return "load"

        if active:
            assert due.citations == {}
            assert len(due._entries) == 1

        _test_dcite_basic(due, method)

        if active:
            assert len(due.citations) == 1
            assert len(due._entries) == 1
            citation = due.citations[("method", "XXX0")]
            assert citation.count == 1
            # TODO: this is probably incomplete path but unlikely we would know
            # any better
            assert citation.path == "method"

        instance = SomeClass()
        _test_dcite_basic(due, instance.method)

        if active:
            assert len(due.citations) == 2
            assert len(due._entries) == 1
            # TODO: we should actually get path/counts pairs so here
            citation = due.citations[("someclass:method", "XXX0")]
            assert citation.path == "someclass:method"
            assert citation.count == 1

            # And we explicitly stated that module need to be cited
            assert citation.cite_module

        class SomeClass2:
            # Used to test for classes that are not instantiated
            @due.dcite("XXX0", path="some.module.without.method")
            def method2(self, arg1, kwarg2="blah"):
                assert arg1 == "magical"
                return "load"

        # and a method pointing to the module
        instance2 = SomeClass()

        _test_dcite_basic(due, instance2.method)
        if active:
            assert len(due.citations) == 2  # different paths
            assert len(due._entries) == 1  # the same entry
            # TODO: we should actually get path/counts pairs so here
            # it is already a different path
            # And we still explicitly stated that module need to be cited
            assert citation.cite_module


def _test_args_match_conditions(conds):
    args_match_conditions = DueCreditCollector._args_match_conditions
    assert args_match_conditions(conds)
    assert args_match_conditions(conds, None)
    assert args_match_conditions(conds, someirrelevant=True)
    assert args_match_conditions(conds, method='purge')
    assert args_match_conditions(conds, method='fullpurge')
    assert args_match_conditions(conds, None, 'purge')
    assert args_match_conditions(conds, None, 'fullpurge')
    assert args_match_conditions(conds, None, 'fullpurge', someirrelevant="buga")
    assert not args_match_conditions(conds, None, 'push')
    assert not args_match_conditions(conds, method='push')
    if len(conds) < 2:
        return
    #  got compound case
    assert args_match_conditions(conds, scope='life')
    assert not args_match_conditions(conds, scope='someother')
    # should be "and", so if one not matching -- both not matching
    assert not args_match_conditions(conds, method="wrong", scope='life')
    assert not args_match_conditions(conds, method="purge", scope='someother')
    # assert args_match_conditions(conds, None, None, 'life')  # ambiguous/conflicting


def test_args_match_conditions():
    _test_args_match_conditions({(1, 'method'): {'purge', 'fullpurge', 'DC_DEFAULT'}})
    _test_args_match_conditions({(1, 'method'): {'purge', 'fullpurge', 'DC_DEFAULT'},
                                 (2, 'scope'): {'life', 'DC_DEFAULT'}})


def _test_dcite_match_conditions(due, callable, path):
    assert due.citations == {}
    assert len(due._entries) == 1

    assert callable("magical", "unknown") == "load unknown"
    assert due.citations == {}
    assert len(due._entries) == 1

    assert callable("magical") == "load blah"

    assert len(due.citations) == 1
    assert len(due._entries) == 1
    entry = due._entries['XXX0']
    assert due.citations[(path, 'XXX0')].count == 1

    # Cause the same citation
    assert callable("magical", "blah") == "load blah"
    # Nothing should change
    assert len(due.citations) == 1
    assert len(due._entries) == 1
    assert due.citations[(path, 'XXX0')].count == 2  # Besides the count

    # Now cause new citation given another value
    assert callable("magical", "boo") == "load boo"
    assert len(due.citations) == 2
    assert len(due._entries) == 2
    assert due.citations[(path, 'XXX0')].count == 2  # Count should stay the same for XXX0
    assert due.citations[(path, "10.3389/fninf.2012.00022")].count == 1  # but we get a new one


def test_dcite_match_conditions_function():
    due = DueCreditCollector()
    due.add(BibTeX(_sample_bibtex))

    @due.dcite("XXX0", path='callable',
               conditions={(1, "kwarg2"): {"blah", "DC_DEFAULT"}})
    @due.dcite(Doi(_sample_doi), path='callable',
               conditions={(1, "kwarg2"): {"boo"}})
    def method(arg1, kwarg2="blah"):
        """docstring"""
        assert arg1 == "magical"
        return "load %s" % kwarg2

    _test_dcite_match_conditions(due, method, 'callable')


def test_dcite_match_conditions_method():

    due = DueCreditCollector()
    due.add(BibTeX(_sample_bibtex))

    class Citeable:
        def __init__(self, param=None):
            self.param = param

        @due.dcite("XXX0", path='obj.callable',
                   conditions={(2, "kwarg2"): {"blah", "DC_DEFAULT"},
                               (0, 'self.param'): {"paramvalue"}  # must be matched
                               })
        @due.dcite(Doi(_sample_doi), path='obj.callable',
                   conditions={(2, "kwarg2"): {"boo"}})
        def method(self, arg1, kwarg2="blah"):
            """docstring"""
            assert arg1 == "magical"
            return "load %s" % kwarg2

    citeable = Citeable(param="paramvalue")
    _test_dcite_match_conditions(due, citeable.method, 'obj.callable')

    # now test for self.param -


def test_get_output_handler_method(tmpdir, monkeypatch):
    tempfile = str(tmpdir.mkdir("sub").join("tempfile.txt"))
    monkeypatch.setitem(os.environ, 'DUECREDIT_OUTPUTS', 'pickle')
    entry = BibTeX(_sample_bibtex)
    collector = DueCreditCollector()
    collector.cite(entry, path='module')

    summary = CollectorSummary(collector, fn=tempfile)
    handlers = [summary._get_output_handler(type_, collector)
                for type_ in ['pickle']]

    # assert isinstance(handlers[0], TextOutput)
    assert isinstance(handlers[0], PickleOutput)

    pytest.raises(NotImplementedError, summary._get_output_handler,
                  'nothing', collector)


def test_collectors_uniform_api():
    get_api = lambda objs: [x for x in sorted(sum((dir(obj) for obj in objs), []))
                           if not x.startswith('_') or x in '__call__']
    assert get_api([DueCreditCollector, DueSwitch]) == get_api([InactiveDueCreditCollector])


def _test__docs__(method):
    assert "entry:" in method.__doc__
    assert "tags: " in method.__doc__


def test__docs__():
    _test__docs__(DueCreditCollector.cite)
    _test__docs__(DueCreditCollector.dcite)
    _test__docs__(Citation.__init__)

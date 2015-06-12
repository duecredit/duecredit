from ..collector import DueCreditCollector
from ..entries import BibTeX, Doi

def _test_entry(due, entry):
    due.add(entry)


def test_entry():
    entry = BibTeX("myentry")
    yield _test_entry, DueCreditCollector(), entry

    entries = [BibTeX("myentry"), BibTeX("myentry"), Doi("myentry")]
    yield _test_entry, DueCreditCollector(), entries

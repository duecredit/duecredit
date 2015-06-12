from ..collector import DueCreditCollector

def _test_entry(due, entry):
    due.add(entry)


def test_entry():
    entry = ('thisismykey', 'thisismyreference')
    yield _test_entry, DueCreditCollector(), entry

    entries = [('thisismykey', 'thisismyreference'),
               ('thisisanothermykey', 'thisismyreference'),
               ('thisismykey', 'thisismyreference')]
    yield _test_entry, DueCreditCollector(), entries

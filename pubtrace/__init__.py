"""TODO"""

from .version import __version__, __release_date__

class PubtraceCollector(object):
    """Collect the references

    The mighty beast which will might become later a proxy on the way to talk to a real collector
    """

    def add(self, bib):
        raise NotImplementedError

    def cite(self, *args, **kwargs):
        raise NotImplementedError

    def load(self, filename):
        raise NotImplementedError

_collector = PubtraceCollector()

# Rebind the collector's methods to the module here
if is_active():
    add = _collector.add
    cite = _collector.cite
    load = _collector.load
else:
    # provide stubs which would do nothing

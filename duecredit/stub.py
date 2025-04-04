# emacs: at the end of the file
# ex: set sts=4 ts=4 sw=4 et:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### #
from __future__ import annotations

from typing import Any

"""

Stub file for a guaranteed safe import of duecredit constructs:  if duecredit
is not available.

To use it, place it into your project codebase to be imported, e.g. copy as

    cp stub.py /path/tomodule/module/due.py

Note that it might be better to avoid naming it duecredit.py to avoid shadowing
installed duecredit.

Then use in your code as

    from .due import due, Doi, BibTeX, Text

See  https://github.com/duecredit/duecredit/blob/master/README.md for examples.

Origin:     Originally a part of the duecredit
Copyright:  2015-2021  DueCredit developers
License:    BSD-2
"""

__version__ = "0.0.9"


class InactiveDueCreditCollector:
    """Just a stub at the Collector which would not do anything"""

    def _donothing(self, *_args: Any, **_kwargs: Any) -> None:
        """Perform no good and no bad"""
        pass

    def dcite(self, *_args: Any, **_kwargs: Any):
        """If I could cite I would"""

        def nondecorating_decorator(func):
            return func

        return nondecorating_decorator

    active = False
    activate = add = cite = dump = load = _donothing

    def __repr__(self) -> str:
        return self.__class__.__name__ + "()"


def _donothing_func(*args: Any, **kwargs: Any) -> None:
    """Perform no good and no bad"""
    pass


try:
    from duecredit import BibTeX, Doi, Text, Url, due  # lgtm [py/unused-import]

    if "due" in locals() and not hasattr(due, "cite"):
        raise RuntimeError("Imported due lacks .cite. DueCredit is now disabled")
except Exception as e:
    if not isinstance(e, ImportError):
        import logging

        logging.getLogger("duecredit").error(f"Failed to import duecredit due to {e}")
    # Initiate due stub
    due = InactiveDueCreditCollector()  # type: ignore
    BibTeX = Doi = Url = Text = _donothing_func  # type: ignore

# Emacs mode definitions
# Local Variables:
# mode: python
# py-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# End:

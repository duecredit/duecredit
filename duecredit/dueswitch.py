# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Provides an adapter to switch between two (active, inactive) collectors
"""

import os
import atexit

from .log import lgr
from .utils import never_fail

def _get_duecredit_enable():
    env_enable = os.environ.get('DUECREDIT_ENABLE', 'no')
    if not env_enable.lower() in ('0', '1', 'yes', 'no', 'true', 'false'):
        lgr.warning("Misunderstood value %s for DUECREDIT_ENABLE. "
                    "Use 'yes' or 'no', or '0' or '1'")
    return env_enable.lower() in ('1', 'yes', 'true')


@never_fail
def _get_inactive_due():
    from .stub import InactiveDueCreditCollector
    return InactiveDueCreditCollector()


@never_fail
def _get_active_due():
    from .config import CACHE_DIR, DUECREDIT_FILE
    from duecredit.collector import CollectorSummary, DueCreditCollector
    from .io import load_due

    # TODO:  this needs to move to atexit handling, that we load previous
    # one and them merge with new ones.  Informative bits could be -- how
    # many new citations we got
    if os.path.exists(DUECREDIT_FILE):
        try:
            due_ = load_due(DUECREDIT_FILE)
        except Exception as e:
            lgr.warning("Failed to load previously collected %s. "
                        "DueCredit will not be active for this session."
                        % DUECREDIT_FILE)
            return _get_inactive_due()
    else:
        due_ = DueCreditCollector()

    return due_


class DueSwitch(object):
    """Adapter between two types of collectors -- Inactive and Active

    Once activated though, cannot be fully deactivated since it would inject
    duecredit decorators and register an event atexit.
    """
    def __init__(self, inactive, active, activate=False):
        self.__active = None
        self.__collectors = {False: inactive, True: active}
        self.__activations_done = False
        if not (inactive and active):
            raise ValueError(
                "Both inactive and active collectors should be provided. "
                "Got active=%r, inactive=%r" % (active, inactive)
            )
        self.activate(activate)

    @property
    def active(self):
        return self.__active

    @never_fail
    def dump(self, **kwargs):
        """Dumps summary of the citations

        Parameters
        ----------
        **kwargs: dict
           Passed to `CollectorSummary` constructor.
        """
        from duecredit.collector import CollectorSummary
        due_summary = CollectorSummary(self.__collectors[True], **kwargs)
        due_summary.dump()

    def __prepare_exit_and_injections(self):
        # Wrapper to create and dump summary... passing method doesn't work:
        #  probably removes instance too early

        atexit.register(self.dump)

        # Deal with injector
        from .injections import DueCreditInjector
        injector = DueCreditInjector(collector=self.__collectors[True])
        injector.activate()

    @never_fail
    def activate(self, activate=True):
        # 1st step -- if activating/deactivating switch between the two collectors
        if self.__active is not activate:
            # we need to switch the state
            # InactiveDueCollector also has those special methods defined
            # in DueSwitch so that client code could query/call (for no effect).
            # So we shouldn't delete or bind them either
            is_public_or_special = \
                lambda x: not (x.startswith('_')
                               or x in ('activate', 'active', 'dump'))
            # Clean up current bindings first
            for k in filter(is_public_or_special, dir(self)):
                delattr(self, k)

            new_due = self.__collectors[activate]
            for k in filter(is_public_or_special, dir(new_due)):
                setattr(self, k, getattr(new_due, k))

            self.__active = activate

        # 2nd -- if activating, we might still need to have activations done
        if activate and not self.__activations_done:
            try:
                self.__prepare_exit_and_injections()
            except Exception as e:
                lgr.error("Failed to prepare injections etc: %s" % str(e))
            finally:
                self.__activations_done = True


due = DueSwitch(_get_inactive_due(), _get_active_due(), _get_duecredit_enable())
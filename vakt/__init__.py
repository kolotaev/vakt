"""
Vakt is an SDK for access policies.
"""

import logging

###########################
#    Public API Imports   #
###########################

from .version import version_info, __version__

from .policy import Policy

from .guard import (
    Inquiry,
    Guard,
)

from .effects import (
    ALLOW_ACCESS,
    DENY_ACCESS,
)

from .checker import (
    RegexChecker,
    StringFuzzyChecker,
    StringExactChecker,
    RulesChecker,
)

from . import rules

from .storage.memory import MemoryStorage


################
#  Setting up  #
################

logging.getLogger(__name__).addHandler(logging.NullHandler())

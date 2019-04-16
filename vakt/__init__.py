"""
Vakt is an SDK for access policies.
"""

import logging

###########################
#    Public API Imports   #
###########################

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

from .__version__ import version_info


################
#  Setting up  #
################

logging.getLogger(__name__).addHandler(logging.NullHandler())

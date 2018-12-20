"""
Vakt is an SDK for access policies.
"""

import logging


################
# Declarations #
################

logging.getLogger(__name__).addHandler(logging.NullHandler())

# Types for Policies and Inquiries:
# String-based (simple strings, regexps)
TYPE_STRING_BASED = 1
# Rule-based definitions (Rules).
TYPE_RULE_BASED = 2


################
#    Imports   #
################

from .__version__ import __version__
from . import TYPE_STRING_BASED, TYPE_RULE_BASED

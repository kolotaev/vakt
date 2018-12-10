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
TYPE_STRINGS = 1
# Attribute-based (Rule) definitions.
TYPE_ATTRIBUTES = 2


################
#    Imports   #
################

from .__version__ import __version__
from . import TYPE_STRINGS, TYPE_ATTRIBUTES

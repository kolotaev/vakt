"""
Vakt is an SDK for access policies.
"""

import logging


logging.getLogger(__name__).addHandler(logging.NullHandler())


# Types for Policies and Inquiries:
# String-based (simple strings, regexps)
TYPE_STRINGS = 1
# Attribute-based (Rule) definitions.
TYPE_ATTRIBUTES = 2

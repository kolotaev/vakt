"""
Audit logging for Vakt decisions.
"""

import logging
from operator import attrgetter

log = logging.getLogger(__name__)


class PoliciesNopMsg:
    """
    Class for converting Policies collection into a string during logging.
    Returns an empty string message for the polices collection.
    """
    def __init__(self, policies=()):
        pass

    def __str__(self):
        return ''


class PoliciesUidMsg:
    """
    Class for converting Policies collection into a string during logging.
    Returns Policies UIDs message for the polices collection.
    Example message: [1123, 14545, aaaa-bbb-ccccc]
    """
    def __init__(self, policies=()):
        self.policies = policies

    def __str__(self):
        uids = list(map(attrgetter('uid'), self.policies))
        return '[%s]' % ', '.join(map(str, uids))


class PoliciesDescriptionMsg(PoliciesUidMsg):
    """
    Class for converting Policies collection into a string during logging.
    Returns Policies description message for the polices collection.
    Example message: ['Policy 1 for Admins', 'Policy for regular users']
    """
    def __str__(self):
        descriptions = list(map(attrgetter('description'), self.policies))
        return '[%s]' % ', '.join(map(lambda x: "'%s'" % x, descriptions))


class PoliciesCountMsg(PoliciesUidMsg):
    """
    Class for converting Policies collection into a string during logging.
    Returns Policies count message for the polices collection.
    Example message: count = 89
    """
    def __str__(self):
        return 'count = %d' % len(self.policies)

"""
All Rules relevant to networking context
"""

import ipaddress
import logging
import warnings

from ..rules.base import Rule


log = logging.getLogger(__name__)


__all__ = [
    'CIDR',
]


class CIDR(Rule):
    """
    Rule that is satisfied when inquiry's IP address is in the provided CIDR.
    For example: context={'ip': CIDR('127.0.0.1/32')}
    """

    def __init__(self, cidr):
        self.cidr = cidr

    def satisfied(self, what, inquiry=None):
        if not isinstance(what, str):
            return False
        try:
            ip = ipaddress.ip_address(what)
            net = ipaddress.ip_network(self.cidr)
        except ValueError:
            log.exception('Error %s satisfied', type(self).__name__)
            return False
        return ip in net


# Classes marked for removal in next releases
class CIDRRule(CIDR):
    """Deprecated in favor of CIDR"""
    def __init__(self, *args, **kwargs):
        warnings.warn('CIDRRule will be removed in version 2.0. Use CIDR', DeprecationWarning, stacklevel=2)
        super().__init__(*args, **kwargs)

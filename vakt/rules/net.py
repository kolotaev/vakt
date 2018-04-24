"""
All Rules relevant to networking context
"""

import ipaddress
import logging

from ..rules.base import Rule


log = logging.getLogger(__name__)


class CIDRRule(Rule):
    """Rule that is satisfied when inquiry's IP address is in the provided CIDR"""

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

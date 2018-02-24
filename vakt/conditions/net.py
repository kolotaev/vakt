import ipaddress
import logging

from ..conditions.base import Condition


log = logging.getLogger(__name__)


class CIDRCondition(Condition):
    """Condition that is satisfied when request's IP address is in the provided CIDR"""

    def __init__(self, cidr):
        self.cidr = cidr

    def satisfied(self, what, request=None):
        if not isinstance(what, str):
            return False
        try:
            ip = ipaddress.ip_address(what)
            net = ipaddress.ip_network(self.cidr)
        except ValueError:
            log.exception('Error CIDRCondition satisfied')
            return False
        return ip in net

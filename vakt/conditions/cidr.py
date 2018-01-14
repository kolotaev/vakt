import ipaddress

from ..conditions.base import Condition
from ..util import JsonDumper


class CIDRCondition(Condition, JsonDumper):
    """Condition that is satisfied when request's IP address is in the provided CIDR"""

    def __init__(self, cidr):
        self.cidr = cidr

    def satisfied(self, what, request):
        if not isinstance(what, str):
            return False
        try:
            ip = ipaddress.ip_address(what)
            net = ipaddress.ip_network(self.cidr)
        except ValueError as e:
            # todo - add logging
            return False
        return ip in net

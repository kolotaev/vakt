"""
Exceptions relevant for Vakt workflow.
"""


class InvalidPatternError(Exception):
    """Invalid policy pattern"""
    pass


class PolicyCreationError(Exception):
    """Error during Policy creation occurred."""
    pass


class RuleCreationError(Exception):
    """Error during Rule creation occurred."""
    pass


class PolicyExistsError(Exception):
    """Error when the already existing policy is attempted to be created by Storage"""
    def __init__(self, uid):
        super().__init__('Conflicting UID = %s' % uid)


class UnknownCheckerType(Exception):
    """Storage can't determine Checker type based on provided one."""
    def __init__(self, obj):
        super().__init__("Can't determine Checker type. Given: %s" % type(obj).__name__)


class Irreversible(Exception):
    """Storage migration can't convert record back to a lower version."""
    pass

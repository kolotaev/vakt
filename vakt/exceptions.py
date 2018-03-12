class InvalidPattern(Exception):
    """Invalid policy pattern"""
    pass


class PolicyCreationError(Exception):
    """Error during Policy creation occurred."""
    pass


class RuleCreationError(Exception):
    """Error during Rule creation occurred."""
    pass


class PolicyExists(Exception):
    """Error when the already existing policy is attempted to be created by Storage"""
    pass

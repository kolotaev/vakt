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
    pass

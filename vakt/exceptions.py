class InvalidPattern(Exception):
    """Invalid policy pattern"""
    pass


class PolicyCreationError(Exception):
    """Error during Policy creation occurred."""
    pass


class ConditionCreationError(Exception):
    """Error during Condition creation occurred."""
    pass

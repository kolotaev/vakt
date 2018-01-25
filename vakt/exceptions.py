class InvalidPattern(Exception):
    """Invalid policy pattern"""
    pass


class PolicyCreationError(Exception):
    """Error during Policy creation occurred."""
    pass


class ConditionCreationError(Exception):
    """Error during Condition creation occurred."""
    pass


class PolicyExists(Exception):
    """Error when the already existing policy is attempted to be created by PolicyManager"""
    pass

class InvalidPattern(Exception):
    """Invalid policy pattern"""
    pass


class PolicyCreationError(Exception):
    """Error during policy creation occurred. 'id' is missing."""
    pass

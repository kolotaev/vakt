"""
Version for vakt package
"""

__version__ = '1.2.1'


def version_info():
    """
    Get version of vakt package as tuple
    """
    return tuple(map(int, __version__.split('.')))

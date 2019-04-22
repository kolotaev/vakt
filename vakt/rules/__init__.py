# pylint: disable=wildcard-import

"""
Collection of Rules for vakt
"""

from .inquiry import *
from .list import *
from .logic import *
from .net import *
from .operator import *
from .string import (
    Equal as StrEqual,
    PairsEqual as StrPairsEqual,
    StartsWith,
    EndsWith,
    Contains,
    RegexMatch,
)

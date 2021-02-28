# -*- coding: utf-8 -*-
"""
    Module containing any custom error classes for this package.
"""

##### CLASSES #####
class BaseBanalysisException(Exception):
    """Base class for any custom errors for the banalysis package."""


class MidataCSVError(BaseBanalysisException):
    """Raised when there are errors with the midata CSV."""

"""Task Exceptions

Exceptions relating to tasks
"""


class EnsembleException(Exception):
    """Common ensemble exception for common implementation"""
    pass


class CheckException(EnsembleException):
    """For check failures"""
    pass


class FailureNotToleratedError(RuntimeError):
    """Check failure error cannot be tolerated"""
    pass


class ProcessingException(EnsembleException):
    """For general processing failures"""
    pass


class TaskException(EnsembleException):
    """For task processing failures"""
    pass

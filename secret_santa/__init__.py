"""Secret Santa assignment engine.

A small, modular, and extensible library for assigning Secret Santa
"secret children" to a list of employees, honoring exclusion rules such
as "cannot pick yourself" and "cannot repeat last year's pairing".
"""

from .assigner import BacktrackingSecretSantaAssigner, SecretSantaAssigner
from .exceptions import (
    AssignmentError,
    FileParsingError,
    InsufficientEmployeesError,
    InvalidInputError,
    SecretSantaError,
)
from .models import Assignment, Employee
from .readers import (
    CSVEmployeeReader,
    CSVPreviousAssignmentReader,
    EmployeeReader,
    PreviousAssignmentReader,
)
from .writers import AssignmentWriter, CSVAssignmentWriter

__all__ = [
    "Assignment",
    "AssignmentError",
    "AssignmentWriter",
    "BacktrackingSecretSantaAssigner",
    "CSVAssignmentWriter",
    "CSVEmployeeReader",
    "CSVPreviousAssignmentReader",
    "Employee",
    "EmployeeReader",
    "FileParsingError",
    "InsufficientEmployeesError",
    "InvalidInputError",
    "PreviousAssignmentReader",
    "SecretSantaAssigner",
    "SecretSantaError",
]

__version__ = "1.0.0"

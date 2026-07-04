"""Writers responsible for persisting output data."""
from __future__ import annotations

import csv
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from .exceptions import FileParsingError
from .models import Assignment


class AssignmentWriter(ABC):
    """Abstract interface for writing out Secret Santa assignments."""

    @abstractmethod
    def write(self, assignments: List[Assignment]) -> None:
        raise NotImplementedError


class CSVAssignmentWriter(AssignmentWriter):
    """Writes assignments to a CSV file."""

    FIELDNAMES = (
        "Employee_Name",
        "Employee_EmailID",
        "Secret_Child_Name",
        "Secret_Child_EmailID",
    )

    def __init__(self, file_path: str | Path) -> None:
        self._path = Path(file_path)

    def write(self, assignments: List[Assignment]) -> None:
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with self._path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=self.FIELDNAMES)
                writer.writeheader()
                for assignment in assignments:
                    writer.writerow(
                        {
                            "Employee_Name": assignment.giver.name,
                            "Employee_EmailID": assignment.giver.email,
                            "Secret_Child_Name": assignment.child.name,
                            "Secret_Child_EmailID": assignment.child.email,
                        }
                    )
        except OSError as exc:
            raise FileParsingError(
                f"Could not write output file '{self._path}': {exc}"
            ) from exc

"""Readers responsible for loading input data.

Each reader is defined behind an abstract interface so that new data
sources (Excel, JSON, a database, an API, ...) can be added later without
touching any other part of the system (Open/Closed Principle).
"""
from __future__ import annotations

import csv
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Tuple

from .exceptions import FileParsingError, InvalidInputError
from .models import Employee


class EmployeeReader(ABC):
    """Abstract interface for reading the list of employees."""

    @abstractmethod
    def read(self) -> List[Employee]:
        """Return the list of employees."""
        raise NotImplementedError


class PreviousAssignmentReader(ABC):
    """Abstract interface for reading last year's Secret Santa assignments."""

    @abstractmethod
    def read(self) -> Dict[str, str]:
        """Return a mapping of {employee_email_key: secret_child_email_key}."""
        raise NotImplementedError


def _open_csv_rows(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        raise FileParsingError(f"File not found: {path}")
    if path.suffix.lower() != ".csv":
        raise FileParsingError(f"Expected a .csv file, got: {path.suffix}")

    try:
        with path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                raise FileParsingError(f"File '{path}' has no header row")
            rows = list(reader)
    except (OSError, csv.Error) as exc:
        raise FileParsingError(f"Could not read file '{path}': {exc}") from exc

    return rows


class CSVEmployeeReader(EmployeeReader):
    """Reads employees from a CSV file with Employee_Name / Employee_EmailID columns."""

    REQUIRED_COLUMNS: Tuple[str, str] = ("Employee_Name", "Employee_EmailID")

    def __init__(self, file_path: str | Path) -> None:
        self._path = Path(file_path)

    def read(self) -> List[Employee]:
        rows = _open_csv_rows(self._path)

        missing = [c for c in self.REQUIRED_COLUMNS if rows and c not in rows[0]]
        if rows and missing:
            raise InvalidInputError(
                f"Employee CSV is missing required column(s): {', '.join(missing)}"
            )

        employees: List[Employee] = []
        seen_emails: set[str] = set()

        for index, row in enumerate(rows, start=2):  # header is row 1
            name = (row.get("Employee_Name") or "").strip()
            email = (row.get("Employee_EmailID") or "").strip()

            if not name or not email:
                raise InvalidInputError(
                    f"Row {index} in '{self._path}' has a missing name or email"
                )

            employee = Employee(name=name, email=email)

            if employee.key in seen_emails:
                raise InvalidInputError(
                    f"Duplicate employee email found: '{email}' (row {index})"
                )
            seen_emails.add(employee.key)
            employees.append(employee)

        if not employees:
            raise InvalidInputError(f"No employees found in '{self._path}'")

        return employees


class CSVPreviousAssignmentReader(PreviousAssignmentReader):
    """Reads last year's assignments from a CSV file, if provided.

    Expected columns: Employee_Name, Employee_EmailID, Secret_Child_Name,
    Secret_Child_EmailID.
    """

    REQUIRED_COLUMNS: Tuple[str, ...] = (
        "Employee_Name",
        "Employee_EmailID",
        "Secret_Child_Name",
        "Secret_Child_EmailID",
    )

    def __init__(self, file_path: str | Path | None) -> None:
        self._path = Path(file_path) if file_path else None

    def read(self) -> Dict[str, str]:
        if self._path is None:
            return {}

        rows = _open_csv_rows(self._path)

        missing = [c for c in self.REQUIRED_COLUMNS if rows and c not in rows[0]]
        if rows and missing:
            raise InvalidInputError(
                f"Previous assignments CSV is missing required column(s): "
                f"{', '.join(missing)}"
            )

        history: Dict[str, str] = {}
        for index, row in enumerate(rows, start=2):
            giver_email = (row.get("Employee_EmailID") or "").strip().lower()
            child_email = (row.get("Secret_Child_EmailID") or "").strip().lower()

            if not giver_email or not child_email:
                raise InvalidInputError(
                    f"Row {index} in '{self._path}' has a missing email field"
                )

            history[giver_email] = child_email

        return history

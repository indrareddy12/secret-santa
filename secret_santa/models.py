"""Domain models for the Secret Santa application."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Employee:
    """Represents a single employee.

    Employees are uniquely identified by their email address rather than
    their name, since two different employees can share the same name
    (e.g. "Hamish Murray" and "Hamish Murray" with different emails).
    """

    name: str
    email: str

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("Employee name must not be empty")
        if not self.email or not self.email.strip():
            raise ValueError("Employee email must not be empty")

    @property
    def key(self) -> str:
        """Unique identifier for this employee (case-insensitive email)."""
        return self.email.strip().lower()

    def __hash__(self) -> int:
        return hash(self.key)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Employee):
            return NotImplemented
        return self.key == other.key


@dataclass(frozen=True)
class Assignment:
    """A single Secret Santa assignment: giver -> child."""

    giver: Employee
    child: Employee

    def __post_init__(self) -> None:
        if self.giver.key == self.child.key:
            raise ValueError(
                f"Employee '{self.giver.name}' cannot be assigned to themselves"
            )

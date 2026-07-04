"""Core matching algorithm used to assign secret children to employees."""
from __future__ import annotations

import random
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from .exceptions import AssignmentError, InsufficientEmployeesError
from .models import Assignment, Employee


class SecretSantaAssigner(ABC):
    """Abstract interface for a Secret Santa assignment strategy."""

    @abstractmethod
    def assign(
        self,
        employees: List[Employee],
        previous_assignments: Optional[Dict[str, str]] = None,
    ) -> List[Assignment]:
        """Return a list of Assignment objects, one per employee.

        Args:
            employees: All employees participating this year.
            previous_assignments: Mapping of {employee_email_key:
                secret_child_email_key} from the previous year, used to
                avoid repeating the same pairing.
        """
        raise NotImplementedError


class BacktrackingSecretSantaAssigner(SecretSantaAssigner):
    """Assigns secret children using randomized backtracking search.

    The algorithm:
      1. Builds, for every employee, the set of eligible "children"
         (everyone except themselves and, if applicable, last year's
         secret child).
      2. Performs a backtracking search -- at each step it picks the
         unassigned employee with the Fewest Remaining eligible
         candidates ("most constrained variable" heuristic), which keeps
         the search fast even as the group grows -- and shuffles
         candidate order so that results are not always the same for a
         given input, while still guaranteeing a valid derangement is
         found whenever one exists.

    Raises:
        InsufficientEmployeesError: If there are fewer than two employees.
        AssignmentError: If no valid assignment exists given the
            constraints (this can only happen in pathological edge cases,
            e.g. 2 employees who were paired with each other last year).
    """

    def __init__(self, random_seed: Optional[int] = None) -> None:
        self._random = random.Random(random_seed)

    def assign(
        self,
        employees: List[Employee],
        previous_assignments: Optional[Dict[str, str]] = None,
    ) -> List[Assignment]:
        previous_assignments = previous_assignments or {}

        if len(employees) < 2:
            raise InsufficientEmployeesError(
                "At least 2 employees are required to run Secret Santa"
            )

        candidates = self._build_candidate_map(employees, previous_assignments)

        assignment_keys = self._backtrack(
            employees=employees,
            candidates=candidates,
        )

        if assignment_keys is None:
            raise AssignmentError(
                "Could not find a valid Secret Santa assignment given the "
                "current constraints (e.g. too few employees relative to "
                "the previous year's exclusions)."
            )

        by_key = {employee.key: employee for employee in employees}
        return [
            Assignment(giver=by_key[giver_key], child=by_key[child_key])
            for giver_key, child_key in assignment_keys.items()
        ]

    def _build_candidate_map(
        self,
        employees: List[Employee],
        previous_assignments: Dict[str, str],
    ) -> Dict[str, List[str]]:
        all_keys = [employee.key for employee in employees]
        candidates: Dict[str, List[str]] = {}

        for employee in employees:
            excluded = {employee.key}
            previous_child = previous_assignments.get(employee.key)
            if previous_child:
                excluded.add(previous_child)

            eligible = [key for key in all_keys if key not in excluded]
            candidates[employee.key] = eligible

        return candidates

    def _backtrack(
        self,
        employees: List[Employee],
        candidates: Dict[str, List[str]],
    ) -> Optional[Dict[str, str]]:
        assigned_children: set[str] = set()
        assignment: Dict[str, str] = {}

        remaining = list(employees)

        def choose_next_employee() -> Employee:
            # Most-constrained-variable heuristic: pick the employee with
            # the fewest remaining valid, unassigned candidates.
            def remaining_candidate_count(emp: Employee) -> int:
                return sum(
                    1
                    for c in candidates[emp.key]
                    if c not in assigned_children
                )

            return min(remaining, key=remaining_candidate_count)

        def backtrack_step() -> bool:
            if not remaining:
                return True

            employee = choose_next_employee()
            remaining.remove(employee)

            possible = [
                c for c in candidates[employee.key] if c not in assigned_children
            ]
            self._random.shuffle(possible)

            for child_key in possible:
                assignment[employee.key] = child_key
                assigned_children.add(child_key)

                if backtrack_step():
                    return True

                # Undo and try the next candidate
                del assignment[employee.key]
                assigned_children.remove(child_key)

            remaining.append(employee)
            return False

        success = backtrack_step()
        return dict(assignment) if success else None

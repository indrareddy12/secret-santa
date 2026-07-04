import pytest

from secret_santa.assigner import BacktrackingSecretSantaAssigner
from secret_santa.exceptions import AssignmentError, InsufficientEmployeesError
from secret_santa.models import Employee


def make_employees(n):
    return [Employee(name=f"Employee {i}", email=f"emp{i}@acme.com") for i in range(n)]


class TestBacktrackingSecretSantaAssigner:
    def test_every_employee_gets_exactly_one_child(self):
        employees = make_employees(10)
        assigner = BacktrackingSecretSantaAssigner(random_seed=42)
        assignments = assigner.assign(employees)

        givers = [a.giver.key for a in assignments]
        children = [a.child.key for a in assignments]

        assert len(assignments) == len(employees)
        assert len(set(givers)) == len(employees)  # each employee gives once
        assert len(set(children)) == len(employees)  # each employee receives once

    def test_nobody_assigned_to_self(self):
        employees = make_employees(15)
        assigner = BacktrackingSecretSantaAssigner(random_seed=1)
        assignments = assigner.assign(employees)
        for a in assignments:
            assert a.giver.key != a.child.key

    def test_avoids_previous_year_assignment(self):
        employees = make_employees(5)
        previous = {emp.key: employees[(i + 1) % 5].key for i, emp in enumerate(employees)}

        assigner = BacktrackingSecretSantaAssigner(random_seed=7)
        assignments = assigner.assign(employees, previous)

        for a in assignments:
            assert previous[a.giver.key] != a.child.key

    def test_single_employee_raises(self):
        employees = make_employees(1)
        assigner = BacktrackingSecretSantaAssigner()
        with pytest.raises(InsufficientEmployeesError):
            assigner.assign(employees)

    def test_empty_employees_raises(self):
        assigner = BacktrackingSecretSantaAssigner()
        with pytest.raises(InsufficientEmployeesError):
            assigner.assign([])

    def test_two_employees_works(self):
        employees = make_employees(2)
        assigner = BacktrackingSecretSantaAssigner(random_seed=3)
        assignments = assigner.assign(employees)
        assert len(assignments) == 2
        assert assignments[0].child.key != assignments[0].giver.key

    def test_two_employees_with_previous_year_conflict_is_impossible(self):
        # With only 2 people, if last year A->B and B->A, this year the
        # only non-self option for each person is the other person, which
        # is exactly the excluded (previous) pairing => impossible.
        employees = make_employees(2)
        previous = {
            employees[0].key: employees[1].key,
            employees[1].key: employees[0].key,
        }
        assigner = BacktrackingSecretSantaAssigner()
        with pytest.raises(AssignmentError):
            assigner.assign(employees, previous)

    def test_large_group_completes(self):
        employees = make_employees(100)
        assigner = BacktrackingSecretSantaAssigner(random_seed=99)
        assignments = assigner.assign(employees)
        assert len(assignments) == 100

    def test_randomization_produces_varied_results(self):
        employees = make_employees(10)
        assigner1 = BacktrackingSecretSantaAssigner(random_seed=1)
        assigner2 = BacktrackingSecretSantaAssigner(random_seed=2)

        result1 = {a.giver.key: a.child.key for a in assigner1.assign(employees)}
        result2 = {a.giver.key: a.child.key for a in assigner2.assign(employees)}

        assert result1 != result2

    def test_same_seed_is_deterministic(self):
        employees = make_employees(10)
        assigner1 = BacktrackingSecretSantaAssigner(random_seed=5)
        assigner2 = BacktrackingSecretSantaAssigner(random_seed=5)

        result1 = {a.giver.key: a.child.key for a in assigner1.assign(employees)}
        result2 = {a.giver.key: a.child.key for a in assigner2.assign(employees)}

        assert result1 == result2

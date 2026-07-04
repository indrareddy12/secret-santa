import pytest

from secret_santa.models import Assignment, Employee


class TestEmployee:
    def test_creates_valid_employee(self):
        emp = Employee(name="Alice Smith", email="alice@acme.com")
        assert emp.name == "Alice Smith"
        assert emp.email == "alice@acme.com"

    def test_empty_name_raises(self):
        with pytest.raises(ValueError):
            Employee(name="", email="alice@acme.com")

    def test_empty_email_raises(self):
        with pytest.raises(ValueError):
            Employee(name="Alice", email="")

    def test_key_is_lowercase_email(self):
        emp = Employee(name="Alice", email="Alice@ACME.com")
        assert emp.key == "alice@acme.com"

    def test_equality_based_on_email(self):
        emp1 = Employee(name="Alice", email="alice@acme.com")
        emp2 = Employee(name="Alice Smith", email="Alice@acme.com")
        emp3 = Employee(name="Alice", email="alice2@acme.com")
        assert emp1 == emp2
        assert emp1 != emp3

    def test_same_name_different_email_are_distinct(self):
        emp1 = Employee(name="Hamish Murray", email="hamish@acme.com")
        emp2 = Employee(name="Hamish Murray", email="hamish.sr@acme.com")
        assert emp1 != emp2
        assert len({emp1, emp2}) == 2


class TestAssignment:
    def test_valid_assignment(self):
        giver = Employee(name="Alice", email="alice@acme.com")
        child = Employee(name="Bob", email="bob@acme.com")
        assignment = Assignment(giver=giver, child=child)
        assert assignment.giver == giver
        assert assignment.child == child

    def test_self_assignment_raises(self):
        giver = Employee(name="Alice", email="alice@acme.com")
        same = Employee(name="Alice", email="alice@acme.com")
        with pytest.raises(ValueError):
            Assignment(giver=giver, child=same)

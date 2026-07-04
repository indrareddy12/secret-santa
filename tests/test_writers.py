import csv

from secret_santa.models import Assignment, Employee
from secret_santa.writers import CSVAssignmentWriter


def test_writes_assignments_to_csv(tmp_path):
    output_path = tmp_path / "out" / "assignments.csv"

    alice = Employee(name="Alice Smith", email="alice@acme.com")
    bob = Employee(name="Bob Jones", email="bob@acme.com")
    assignments = [Assignment(giver=alice, child=bob), Assignment(giver=bob, child=alice)]

    writer = CSVAssignmentWriter(output_path)
    writer.write(assignments)

    assert output_path.exists()

    with output_path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 2
    assert rows[0]["Employee_Name"] == "Alice Smith"
    assert rows[0]["Employee_EmailID"] == "alice@acme.com"
    assert rows[0]["Secret_Child_Name"] == "Bob Jones"
    assert rows[0]["Secret_Child_EmailID"] == "bob@acme.com"


def test_creates_parent_directories(tmp_path):
    output_path = tmp_path / "nested" / "dirs" / "assignments.csv"
    alice = Employee(name="Alice", email="alice@acme.com")
    bob = Employee(name="Bob", email="bob@acme.com")

    writer = CSVAssignmentWriter(output_path)
    writer.write([Assignment(giver=alice, child=bob)])

    assert output_path.exists()

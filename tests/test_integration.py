import csv

from secret_santa import (
    BacktrackingSecretSantaAssigner,
    CSVAssignmentWriter,
    CSVEmployeeReader,
    CSVPreviousAssignmentReader,
)


def test_full_workflow_without_previous_year(tmp_path):
    employees_path = tmp_path / "employees.csv"
    employees_path.write_text(
        "Employee_Name,Employee_EmailID\n"
        "Hamish Murray,hamish.murray@acme.com\n"
        "Layla Graham,layla.graham@acme.com\n"
        "Matthew King,matthew.king@acme.com\n"
        "Benjamin Collins,benjamin.collins@acme.com\n"
        "Isabella Scott,isabella.scott@acme.com\n"
        "Charlie Ross,charlie.ross@acme.com\n"
    )
    output_path = tmp_path / "assignments.csv"

    employees = CSVEmployeeReader(employees_path).read()
    previous = CSVPreviousAssignmentReader(None).read()
    assignments = BacktrackingSecretSantaAssigner(random_seed=0).assign(
        employees, previous
    )
    CSVAssignmentWriter(output_path).write(assignments)

    with output_path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 6
    givers = {row["Employee_EmailID"] for row in rows}
    children = {row["Secret_Child_EmailID"] for row in rows}
    assert givers == children  # everyone gives once, everyone receives once

    for row in rows:
        assert row["Employee_EmailID"] != row["Secret_Child_EmailID"]


def test_full_workflow_with_previous_year_exclusion(tmp_path):
    employees_path = tmp_path / "employees.csv"
    employees_path.write_text(
        "Employee_Name,Employee_EmailID\n"
        "A,a@acme.com\n"
        "B,b@acme.com\n"
        "C,c@acme.com\n"
        "D,d@acme.com\n"
    )
    previous_path = tmp_path / "previous.csv"
    previous_path.write_text(
        "Employee_Name,Employee_EmailID,Secret_Child_Name,Secret_Child_EmailID\n"
        "A,a@acme.com,B,b@acme.com\n"
        "B,b@acme.com,C,c@acme.com\n"
        "C,c@acme.com,D,d@acme.com\n"
        "D,d@acme.com,A,a@acme.com\n"
    )
    output_path = tmp_path / "assignments.csv"

    employees = CSVEmployeeReader(employees_path).read()
    previous = CSVPreviousAssignmentReader(previous_path).read()
    assignments = BacktrackingSecretSantaAssigner(random_seed=0).assign(
        employees, previous
    )
    CSVAssignmentWriter(output_path).write(assignments)

    with output_path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))

    for row in rows:
        prev_child = previous[row["Employee_EmailID"]]
        assert row["Secret_Child_EmailID"] != prev_child

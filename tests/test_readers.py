import pytest

from secret_santa.exceptions import FileParsingError, InvalidInputError
from secret_santa.readers import CSVEmployeeReader, CSVPreviousAssignmentReader


@pytest.fixture
def employees_csv(tmp_path):
    path = tmp_path / "employees.csv"
    path.write_text(
        "Employee_Name,Employee_EmailID\n"
        "Alice Smith,alice@acme.com\n"
        "Bob Jones,bob@acme.com\n"
        "Carol Lee,carol@acme.com\n"
    )
    return path


@pytest.fixture
def previous_csv(tmp_path):
    path = tmp_path / "previous.csv"
    path.write_text(
        "Employee_Name,Employee_EmailID,Secret_Child_Name,Secret_Child_EmailID\n"
        "Alice Smith,alice@acme.com,Bob Jones,bob@acme.com\n"
        "Bob Jones,bob@acme.com,Carol Lee,carol@acme.com\n"
        "Carol Lee,carol@acme.com,Alice Smith,alice@acme.com\n"
    )
    return path


class TestCSVEmployeeReader:
    def test_reads_employees_successfully(self, employees_csv):
        reader = CSVEmployeeReader(employees_csv)
        employees = reader.read()
        assert len(employees) == 3
        assert employees[0].name == "Alice Smith"
        assert employees[0].email == "alice@acme.com"

    def test_missing_file_raises(self, tmp_path):
        reader = CSVEmployeeReader(tmp_path / "missing.csv")
        with pytest.raises(FileParsingError):
            reader.read()

    def test_non_csv_extension_raises(self, tmp_path):
        bad_file = tmp_path / "employees.txt"
        bad_file.write_text("Employee_Name,Employee_EmailID\nAlice,alice@acme.com\n")
        reader = CSVEmployeeReader(bad_file)
        with pytest.raises(FileParsingError):
            reader.read()

    def test_missing_column_raises(self, tmp_path):
        path = tmp_path / "employees.csv"
        path.write_text("Name,Email\nAlice,alice@acme.com\n")
        reader = CSVEmployeeReader(path)
        with pytest.raises(InvalidInputError):
            reader.read()

    def test_empty_field_raises(self, tmp_path):
        path = tmp_path / "employees.csv"
        path.write_text("Employee_Name,Employee_EmailID\n,alice@acme.com\n")
        reader = CSVEmployeeReader(path)
        with pytest.raises(InvalidInputError):
            reader.read()

    def test_duplicate_email_raises(self, tmp_path):
        path = tmp_path / "employees.csv"
        path.write_text(
            "Employee_Name,Employee_EmailID\n"
            "Alice,alice@acme.com\n"
            "Alice Duplicate,Alice@ACME.com\n"
        )
        reader = CSVEmployeeReader(path)
        with pytest.raises(InvalidInputError):
            reader.read()

    def test_no_rows_raises(self, tmp_path):
        path = tmp_path / "employees.csv"
        path.write_text("Employee_Name,Employee_EmailID\n")
        reader = CSVEmployeeReader(path)
        with pytest.raises(InvalidInputError):
            reader.read()

    def test_same_name_different_email_both_kept(self, tmp_path):
        path = tmp_path / "employees.csv"
        path.write_text(
            "Employee_Name,Employee_EmailID\n"
            "Hamish Murray,hamish@acme.com\n"
            "Hamish Murray,hamish.sr@acme.com\n"
        )
        reader = CSVEmployeeReader(path)
        employees = reader.read()
        assert len(employees) == 2


class TestCSVPreviousAssignmentReader:
    def test_reads_previous_assignments(self, previous_csv):
        reader = CSVPreviousAssignmentReader(previous_csv)
        history = reader.read()
        assert history["alice@acme.com"] == "bob@acme.com"
        assert history["bob@acme.com"] == "carol@acme.com"

    def test_none_path_returns_empty_dict(self):
        reader = CSVPreviousAssignmentReader(None)
        assert reader.read() == {}

    def test_missing_file_raises(self, tmp_path):
        reader = CSVPreviousAssignmentReader(tmp_path / "missing.csv")
        with pytest.raises(FileParsingError):
            reader.read()

    def test_missing_column_raises(self, tmp_path):
        path = tmp_path / "previous.csv"
        path.write_text("Employee_Name,Employee_EmailID\nAlice,alice@acme.com\n")
        reader = CSVPreviousAssignmentReader(path)
        with pytest.raises(InvalidInputError):
            reader.read()

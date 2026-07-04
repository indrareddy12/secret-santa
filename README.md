# Secret Santa Assignment Engine

A small, modular, and extensible Python application that assigns a "secret
child" to every employee for a company's Secret Santa event, while
respecting two constraints:

1. No employee can be assigned to themselves.
2. No employee can be assigned the same secret child as in the previous
   year (if a previous-year assignment file is supplied).

## Why this design?

The problem is explicitly asked to be solved without a single monolithic
class or function. This solution is split into clearly separated layers,
each with one responsibility, following SOLID principles:

```
secret_santa/
├── models.py       # Employee / Assignment — plain data objects
├── exceptions.py   # A small hierarchy of domain-specific exceptions
├── readers.py      # EmployeeReader / PreviousAssignmentReader (ABCs)
│                   #   + CSV implementations
├── assigner.py     # SecretSantaAssigner (ABC)
│                   #   + BacktrackingSecretSantaAssigner implementation
└── writers.py       # AssignmentWriter (ABC) + CSVAssignmentWriter
main.py             # Thin CLI that wires the pieces together
tests/              # Unit + integration tests (pytest)
sample_data/        # Example input/output CSVs, including the
                    #   employee list provided with the challenge
```

Every I/O concern (reading employees, reading last year's history,
writing results) is hidden behind an abstract base class
(`EmployeeReader`, `PreviousAssignmentReader`, `AssignmentWriter`).
That means:

* Swapping CSV for, say, JSON, Excel, or a database only requires adding
  a new class that implements the same interface — nothing else in the
  codebase changes (Open/Closed Principle).
* The matching algorithm (`assigner.py`) has zero knowledge of files —
  it only works with `Employee` objects and plain dictionaries, so it
  can be unit-tested in isolation and reused in a non-CLI context (e.g.
  a web API).
* `main.py` is a thin orchestration layer with no business logic of its
  own — it just reads, assigns, and writes.

### Identifying employees by email, not name

The sample `Employee-List.xlsx` provided with the challenge contains
several employees who share the same name but have different email
addresses (e.g. three different people named "Hamish Murray"). Because
of this, `Employee` objects are treated as equal/unique based on a
normalized (lower-cased, trimmed) email address rather than on name —
this is what actually distinguishes people in the source data.

### The matching algorithm

`BacktrackingSecretSantaAssigner` builds, for every employee, the set of
people they're still allowed to be assigned to (everyone except
themselves and, if supplied, last year's secret child). It then runs a
randomized backtracking search that:

* Always picks the employee with the **fewest remaining valid options**
  next (the "most constrained variable" heuristic), which keeps the
  search fast even for larger companies and avoids painting itself into
  a corner.
* Shuffles each employee's candidate list before trying it, so that
  re-running the program produces a different, valid assignment each
  time (unless a `--seed` is given for reproducibility).
* Backtracks and tries the next candidate whenever a choice leads to a
  dead end, so it will always find a valid solution if one exists, and
  otherwise clearly reports that none exists (see error handling below).

## Requirements

* Python 3.9+
* `pytest` (only needed to run the test suite)

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Input format

**Employees CSV** (required) — columns:

| Employee_Name | Employee_EmailID |
|---|---|

**Previous year assignments CSV** (optional) — columns:

| Employee_Name | Employee_EmailID | Secret_Child_Name | Secret_Child_EmailID |
|---|---|---|---|

### Running the program

```bash
# First year (no previous assignments to avoid)
python main.py --employees sample_data/employees.csv --output assignments.csv

# Subsequent year, avoiding a repeat of last year's pairing
python main.py \
  --employees sample_data/employees.csv \
  --previous sample_data/previous_assignments.csv \
  --output assignments.csv

# Reproducible run (same seed -> same output, useful for testing/demos)
python main.py --employees sample_data/employees.csv --output assignments.csv --seed 42
```

### Running the Full-Stack Web App

In addition to the command-line utility, a premium web application dashboard is included. To run it:

```bash
# Start the FastAPI backend
python web_app.py
```

Then open your browser to **`http://127.0.0.1:8085`**.

From the Web UI, you can:
* Drag and drop or upload employee and previous assignment CSV files.
* Enter a random seed for reproducible runs.
* View and filter results in real time.
* Download the final assignments CSV.
* Execute the test suite directly from the built-in diagnostic terminal.

Full option list for CLI:

```
--employees   Path to CSV with Employee_Name, Employee_EmailID          (required)
--previous    Path to CSV with last year's assignments                  (optional)
--output      Path to write the resulting assignments CSV to            (default: assignments.csv)
--seed        Integer random seed for reproducible assignment           (optional)
```

### Output format

A CSV file with:

| Employee_Name | Employee_EmailID | Secret_Child_Name | Secret_Child_EmailID |
|---|---|---|---|

The `sample_data/` folder includes:
* `employees.csv` — the employee list from the challenge, converted to CSV
* `previous_assignments.csv` — an example previous-year file (for demoing the exclusion rule)
* `output_assignments.csv` — sample output produced by running the command above

## Running the tests

```bash
pytest
```

The test suite (34 tests) covers:

* **`test_models.py`** — `Employee` validation/equality, `Assignment`
  self-assignment guard.
* **`test_readers.py`** — CSV parsing, missing files, missing/invalid
  columns, duplicate emails, empty files.
* **`test_assigner.py`** — every employee gets exactly one child and
  gives exactly one gift, nobody is assigned to themselves, previous
  year's pairing is always avoided, correct handling of edge cases (1
  employee, 0 employees, an unsatisfiable 2-person case), and
  determinism when a seed is supplied.
* **`test_writers.py`** — correct CSV output, automatic creation of
  missing output directories.
* **`test_integration.py`** — full read → assign → write workflow using
  realistic data (including duplicate names, matching the structure of
  the actual `Employee-List.xlsx`).

## Error handling

All expected failure modes raise a specific, documented exception (see
`secret_santa/exceptions.py`), and `main.py` catches the common base
class `SecretSantaError` to print a clean, user-facing message instead
of a stack trace:

* Missing/unreadable files, wrong extension → `FileParsingError`
* Missing columns, empty/duplicate values → `InvalidInputError`
* Fewer than 2 employees → `InsufficientEmployeesError`
* No valid assignment exists given the constraints → `AssignmentError`

## Possible extensions

Thanks to the abstract-base-class boundaries, these could be added
without touching existing, tested code:

* An `ExcelEmployeeReader` / `JSONEmployeeReader` implementing
  `EmployeeReader`.
* A `DatabaseAssignmentWriter` implementing `AssignmentWriter` to persist
  results directly to a database.
* An alternate assigner (e.g. one that also avoids pairing people from
  the same team) by implementing `SecretSantaAssigner`.

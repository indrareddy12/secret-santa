#!/usr/bin/env python3
"""Command-line entry point for the Secret Santa assignment engine.

Usage:
    python main.py --employees employees.csv --output assignments.csv
    python main.py --employees employees.csv --previous last_year.csv \
        --output assignments.csv
"""
from __future__ import annotations

import argparse
import sys

from secret_santa import (
    BacktrackingSecretSantaAssigner,
    CSVEmployeeReader,
    CSVPreviousAssignmentReader,
    CSVAssignmentWriter,
    SecretSantaError,
)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Assign Secret Santa 'secret children' to employees."
    )
    parser.add_argument(
        "--employees",
        required=True,
        help="Path to the CSV file containing Employee_Name, Employee_EmailID",
    )
    parser.add_argument(
        "--previous",
        required=False,
        default=None,
        help=(
            "Path to the CSV file containing last year's assignments "
            "(Employee_Name, Employee_EmailID, Secret_Child_Name, "
            "Secret_Child_EmailID). Optional."
        ),
    )
    parser.add_argument(
        "--output",
        required=False,
        default="assignments.csv",
        help="Path to write the output assignments CSV file to.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional random seed, useful for reproducible test runs.",
    )
    return parser


def run(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    try:
        employee_reader = CSVEmployeeReader(args.employees)
        previous_reader = CSVPreviousAssignmentReader(args.previous)

        employees = employee_reader.read()
        previous_assignments = previous_reader.read()

        assigner = BacktrackingSecretSantaAssigner(random_seed=args.seed)
        assignments = assigner.assign(employees, previous_assignments)

        writer = CSVAssignmentWriter(args.output)
        writer.write(assignments)

    except SecretSantaError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Success! {len(assignments)} assignments written to '{args.output}'.")
    return 0


if __name__ == "__main__":
    sys.exit(run())

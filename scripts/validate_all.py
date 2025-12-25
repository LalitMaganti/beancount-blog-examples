#!/usr/bin/env python3
"""Validate all beancount example folders parse correctly.

Usage (from repo root):
    python scripts/validate_all.py
"""

import sys
from pathlib import Path

def find_journal_files(examples_dir: Path) -> list[Path]:
    """Find all journal entry points (not includes in src/)."""
    journals = []

    for chapter_dir in sorted(examples_dir.glob("chapter-*")):
        # Find journal files at top level of each chapter folder
        for journal in chapter_dir.glob("journal*.beancount"):
            journals.append(journal)

        # For chapter-6, also check person folders
        for person_dir in ["lalit", "wife", "total"]:
            person_path = chapter_dir / person_dir
            if person_path.exists():
                for journal in person_path.glob("journal*.beancount"):
                    journals.append(journal)

    return journals


def main():
    examples_dir = Path(__file__).parent.parent

    # Try to import beancount
    try:
        from beancount import loader
    except ImportError:
        print("beancount not installed. Run manually with bean-check:\n")
        for journal in find_journal_files(examples_dir):
            rel_path = journal.relative_to(examples_dir)
            print(f"  bean-check {rel_path}")
        sys.exit(0)

    # Find all journal files
    journals = find_journal_files(examples_dir)

    if not journals:
        print("No journal files found!")
        sys.exit(1)

    print(f"Validating {len(journals)} journal files...\n")

    errors = []
    for journal in journals:
        rel_path = journal.relative_to(examples_dir)
        entries, load_errors, options = loader.load_file(str(journal))

        if load_errors:
            errors.append((rel_path, load_errors))
            print(f"✗ {rel_path}")
            for err in load_errors:
                print(f"    {err.message}")
        else:
            print(f"✓ {rel_path}")

    print()
    if errors:
        print(f"{len(errors)} file(s) with errors")
        sys.exit(1)

    print(f"All {len(journals)} files valid!")


if __name__ == "__main__":
    main()

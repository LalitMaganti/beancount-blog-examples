"""HSBC Current Account CSV Importer.

This is a simplified importer for demonstration purposes. It parses a basic CSV
format to illustrate the beangulp importer pattern.

For production-ready importers that handle real UK bank statements (PDFs, edge
cases, multi-currency), see: https://github.com/LalitMaganti/beancount-lalitm
"""

import csv
import datetime
from pathlib import Path

from beancount.core import data
from beancount.core.amount import Amount
from beancount.core.number import D
from beangulp import Importer


class HsbcCurrentImporter(Importer):
    """Importer for HSBC current account CSV statements."""

    def __init__(self, account: str):
        self._account = account

    def name(self) -> str:
        """Return the importer name (method for beancount-import compatibility)."""
        return 'hsbc_current'

    def identify(self, filepath) -> bool:
        """Return True if this importer can handle the file."""
        # Handle beangulp's _FileMemo object
        path = Path(filepath.name if hasattr(filepath, 'name') else filepath)
        # Check if it's a CSV in the hsbc-current folder
        if path.suffix != '.csv':
            return False
        if 'hsbc-current' not in str(path):
            return False
        return True

    def account(self, filepath) -> str:
        """Return the account name for this file."""
        return self._account

    def date(self, filepath) -> datetime.date:
        """Return the date of the file (used for filing)."""
        # Handle beangulp's _FileMemo object
        path = Path(filepath.name if hasattr(filepath, 'name') else filepath)
        # Extract date from filename like statement-2024-01.csv
        name = path.stem
        if 'statement-' in name:
            parts = name.replace('statement-', '').split('-')
            if len(parts) >= 2:
                return datetime.date(int(parts[0]), int(parts[1]), 1)
        return datetime.date.today()

    def extract(self, filepath, existing_entries: data.Entries = None) -> data.Entries:
        """Parse the CSV file and return beancount transactions."""
        # Handle beangulp's _FileMemo object
        path = filepath.name if hasattr(filepath, 'name') else filepath
        entries = []

        with open(path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Parse the date
                date = datetime.datetime.strptime(row['Date'], '%Y-%m-%d').date()

                # Parse the amount
                amount = D(row['Amount'])

                # Create metadata
                meta = data.new_metadata(str(path), 0)

                # Create the transaction with single posting
                # beancount-import will add the categorized other side
                txn = data.Transaction(
                    meta=meta,
                    date=date,
                    flag='*',
                    payee=row['Description'],
                    narration='',
                    tags=set(),
                    links=set(),
                    postings=[
                        data.Posting(
                            account=self._account,
                            units=Amount(amount, 'GBP'),
                            cost=None,
                            price=None,
                            flag=None,
                            meta=None,
                        ),
                    ],
                )
                entries.append(txn)

        return entries

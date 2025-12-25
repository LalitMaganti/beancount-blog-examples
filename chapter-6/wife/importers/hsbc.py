"""Example HSBC importer skeleton.

This shows the pattern for writing a beancount importer.
Real importers would parse PDF/CSV statements and extract transactions.
"""

from beancount.ingest import importer
from beancount.core import data
from beancount.core.amount import Amount
from decimal import Decimal


class HsbcCurrentImporter(importer.ImporterProtocol):
    """Importer for HSBC current account statements."""

    def __init__(self, account: str):
        self.account = account

    def identify(self, file) -> bool:
        """Return True if this importer can handle the file."""
        return 'hsbc' in file.name.lower()

    def file_account(self, file) -> str:
        """Return the account name for this file."""
        return self.account

    def extract(self, file, existing_entries=None) -> list[data.Directive]:
        """Parse the file and return beancount entries.

        In a real importer, you would:
        1. Use pdftotext to extract text from PDF
        2. Use pandas read_fwf to parse the columnar data
        3. Map each row to a beancount Transaction
        """
        # Placeholder - real implementation would parse the file
        return []

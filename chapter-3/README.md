# Chapter 3: Automated Import

Semi-automated transaction import using beancount-import's web UI.

## Key Concepts

### The Import Workflow

1. Download statements from your bank (PDF, CSV, OFX)
2. Drop them in the appropriate `data/` subfolder
3. Run `python beancount_import_config.py` to launch the web UI
4. Review transactions one-by-one (the system auto-suggests categories)
5. Accept or override categorizations with a keystroke
6. Transactions are written directly to your ledger

### Why PDFs Often Beat CSVs

Banks have strong incentives to get PDFs right - customers read them, they're legal documents. CSV exports are often afterthoughts with inconsistent formats. PDFs with proper text layers can be parsed reliably with `pdftotext -layout`.

### The Importer Pattern

Each beangulp importer implements three methods:

```python
class HsbcCurrentImporter(Importer):
    def identify(self, filepath) -> bool:
        """Does this file belong to this importer?"""

    def account(self, filepath) -> str:
        """Which account does this file belong to?"""

    def extract(self, filepath, existing) -> list[Transaction]:
        """Parse the file and return beancount transactions."""
```

The importer extracts raw transactions. beancount-import handles the categorization.

The `importers/hsbc.py` included here is a simplified CSV example for learning. For production-ready importers that handle real UK bank PDFs, see [beancount-lalitm](https://github.com/LalitMaganti/beancount-lalitm).

## Structure

```
chapter-3/
├── journal.beancount
├── beancount_import_config.py   # Main entry point - launches web UI
├── importers/
│   └── hsbc.py                  # Sample HSBC CSV importer
├── data/
│   ├── hsbc-current/            # Drop HSBC statements here
│   └── amex/                    # Drop AMEX statements here
└── src/
    ├── accounts.beancount
    ├── transactions.beancount   # Where accepted transactions are written
    ├── balance.beancount
    └── ignored.beancount        # Transactions you've explicitly skipped
```

## Run

```bash
# Launch the beancount-import web UI
python beancount_import_config.py

# The UI opens at http://localhost:8101
# Review and categorize transactions, then they're saved to your ledger

# Check the ledger after importing
bean-check journal.beancount

# View in Fava
fava journal.beancount
```

#!/usr/bin/env python3
"""Run script for beancount-import.

Usage:
    python beancount_import_config.py

This launches the beancount-import web UI for categorizing transactions.
"""

import os
import sys

from importers.hsbc import HsbcCurrentImporter


def run_reconcile(extra_args):
    import beancount_import.webserver

    journal_dir = os.path.dirname(__file__)
    data_dir = os.path.join(journal_dir, 'data')

    data_sources = [
        dict(
            module='beancount_import.source.generic_importer_source',
            importer=HsbcCurrentImporter('Assets:Lalit:UK:HSBC:Current:GBP'),
            account='Assets:Lalit:UK:HSBC:Current:GBP',
            directory=os.path.join(data_dir, 'hsbc-current'),
        ),
        # Add more importers here as you add accounts, e.g.:
        # dict(
        #     module='beancount_import.source.generic_importer_source',
        #     importer=AmexImporter('Liabilities:Lalit:UK:AMEX:GBP'),
        #     account='Liabilities:Lalit:UK:AMEX:GBP',
        #     directory=os.path.join(data_dir, 'amex'),
        # ),
    ]

    beancount_import.webserver.main(
        extra_args,
        journal_input=os.path.join(journal_dir, 'journal.beancount'),
        ignored_journal=os.path.join(journal_dir, 'src', 'ignored.beancount'),
        default_output=os.path.join(journal_dir, 'src', 'transactions.beancount'),
        open_account_output_map=[
            ('.*', os.path.join(journal_dir, 'src', 'accounts.beancount')),
        ],
        balance_account_output_map=[
            ('.*', os.path.join(journal_dir, 'src', 'balance.beancount')),
        ],
        price_output=os.path.join(journal_dir, 'src', 'prices.beancount'),
        data_sources=data_sources,
    )


if __name__ == '__main__':
    run_reconcile(sys.argv[1:])

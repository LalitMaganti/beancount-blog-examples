"""Configuration for beancount-import.

Run with: python -m beancount_import.webserver --config beancount_import_config.py
"""

import os
from importers.hsbc import HsbcCurrentImporter

# Path to the data directory containing raw statements
data_dir = os.path.join(os.path.dirname(__file__), 'data')

# Define importers for each account type
CONFIG = [
    HsbcCurrentImporter('Assets:Lalit:UK:HSBC:Current:GBP'),
    # Add more importers here as you add accounts
]


def get_importers():
    return CONFIG

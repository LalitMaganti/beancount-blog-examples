"""Lalit's beancount-import configuration."""

import os
from importers.hsbc import HsbcCurrentImporter

data_dir = os.path.join(os.path.dirname(__file__), 'data')

CONFIG = [
    HsbcCurrentImporter('Assets:Lalit:UK:HSBC:Current:GBP'),
]

def get_importers():
    return CONFIG

#!/usr/bin/env python3
"""
Generate textual archive reports from a Beancount ledger.

This script runs SQL queries against your ledger and writes textual reports
that can be version controlled. Run it periodically (e.g., daily via CI) to
maintain a git history of your net worth over time.

Usage:
    uv run scripts/archive.py <output_dir> <journal_file> <open_date> <close_date>

Example:
    uv run scripts/archive.py outputs/ journal.beancount 2024-01-01 2024-12-31
"""

import argparse
import os

import beanquery
from beanquery.query_render import render_text


def execute_sql_to_file(context: beanquery.Connection, sql: str, filepath: str):
    """Execute SQL query and write results to a text file."""
    cursor = context.execute(sql)
    rtypes = cursor.description
    rrows = cursor.fetchall()
    with open(filepath, 'w') as out:
        render_text(rtypes, rrows, context.options['dcontext'], out)


def balance_sheet_sql(currency: str, open_date: str, close_date: str) -> str:
    """Generate SQL for balance sheet in a specific currency."""
    value = f"round(sum(number(convert(value(position, {close_date}), {currency}, {close_date}))), 2)"
    cost = f"round(sum(number(convert(cost(position), {currency}, date))), 2)"
    return f'''
        SELECT
            account,
            {value} AS value,
            {cost} AS cost,
            {value} - {cost} AS unrealized_gain,
            {currency} AS currency
        FROM OPEN ON {open_date} CLOSE ON {close_date} CLEAR
        GROUP BY account, currency
        HAVING round(sum(number), 2) != 0
        ORDER BY account, currency;
    '''


def holdings_sql(currency: str, open_date: str, close_date: str) -> str:
    """Generate SQL for holdings breakdown."""
    return f'''
        SELECT
            account,
            round(sum(number), 2) AS units,
            currency,
            round(sum(number(convert(cost(position), {currency}, date))) / sum(number), 2) AS avg_cost,
            round(sum(number(convert(value(position, {close_date}), {currency}, {close_date}))) / sum(number), 2) AS price,
            round(sum(number(convert(cost(position), {currency}, date))), 2) AS book_val,
            round(sum(number(convert(value(position, {close_date}), {currency}, {close_date}))), 2) AS mkt_val
        FROM OPEN ON {open_date} CLOSE ON {close_date} CLEAR
        WHERE account ~ 'Assets' OR account ~ 'Liabilities'
        GROUP BY account, currency
        HAVING round(sum(number), 2) != 0
        ORDER BY account, currency;
    '''


def equity_sql(open_date: str, close_date: str) -> str:
    """Generate SQL for single-line net worth."""
    return f'''
        SELECT
            only('GBP', sum(convert(position, 'GBP', {close_date}))) AS gbp,
            only('USD', sum(convert(position, 'USD', {close_date}))) AS usd
        FROM OPEN ON {open_date} CLOSE ON {close_date} CLEAR
        WHERE account ~ 'Assets' OR account ~ 'Liabilities'
    '''


def main():
    parser = argparse.ArgumentParser(
        description="Generate archive reports from a Beancount ledger"
    )
    parser.add_argument('output_dir', help='Directory to write reports to')
    parser.add_argument('journal_file', help='Path to the beancount journal')
    parser.add_argument('open_date', help='Start date (YYYY-MM-DD)')
    parser.add_argument('close_date', help='End date (YYYY-MM-DD)')
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    context = beanquery.connect(None)
    context.attach('beancount:' + args.journal_file)

    # Balance sheet
    execute_sql_to_file(
        context,
        balance_sheet_sql("'GBP'", args.open_date, args.close_date),
        os.path.join(args.output_dir, 'balance-sheet.txt'),
    )

    # Holdings breakdown
    execute_sql_to_file(
        context,
        holdings_sql("'GBP'", args.open_date, args.close_date),
        os.path.join(args.output_dir, 'holdings.txt'),
    )

    # Single-line net worth
    execute_sql_to_file(
        context,
        equity_sql(args.open_date, args.close_date),
        os.path.join(args.output_dir, 'networth.txt'),
    )

    print(f"Reports written to {args.output_dir}/")


if __name__ == '__main__':
    main()

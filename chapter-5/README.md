# Chapter 5: Multiple Views

Same transactions, different lenses - no data duplication.

## Key Concepts

### The Problem

Day-to-day, you want simple numbers: take-home pay, not gross salary minus deductions. But at tax time, you need the full breakdown. Recording the same transaction twice is maintenance hell.

### The Solution: rename_accounts

The `rename_accounts` plugin rewrites account names when the journal loads. Merge multiple accounts into one, and their balances combine.

### Gross vs Net Payslip

The same payslip transaction appears differently in each view:

**The actual transaction (in src/transactions.beancount):**
```beancount
2024-01-25 * "Google" "January salary"
  Assets:Lalit:UK:HSBC:Current:GBP           3500.00 GBP  ; Take-home
  Income:Lalit:UK:Google:Salary           -5000.00 GBP  ; Gross
  Expenses:Lalit:UK:Google:Income-Tax        1000.00 GBP
  Expenses:Lalit:UK:Google:National-Insurance 400.00 GBP
  Expenses:Lalit:UK:Google:Pension            100.00 GBP
```

**GROSS view** shows all five lines - useful for tax analysis.

**NET view** collapses to two lines:
```beancount
Income:Lalit:UK:Google:Net-Income        -3500.00 GBP
Assets:Lalit:UK:HSBC:Current:GBP          3500.00 GBP
```

### How It Works

In `journal-net.beancount`:
```beancount
plugin "beancount_reds_plugins.rename_accounts.rename_accounts" "{
  'Income:Lalit:UK:Google:Salary': 'Income:Lalit:UK:Google:Net-Income',
  'Expenses:Lalit:UK:Google:Income-Tax': 'Income:Lalit:UK:Google:Net-Income',
  'Expenses:Lalit:UK:Google:National-Insurance': 'Income:Lalit:UK:Google:Net-Income',
  'Expenses:Lalit:UK:Google:Pension': 'Income:Lalit:UK:Google:Net-Income',
}"
```

Since Income is negative and Expenses are positive, merging them mathematically subtracts deductions from gross pay.

## Structure

```
chapter-5/
├── journal.beancount        # Base journal (for bean-check)
├── journal-gross.beancount  # Full payslip breakdown
├── journal-net.beancount    # Collapsed to net income
├── scripts/
│   └── archive.py           # Generate text reports
├── outputs/                 # Generated reports
└── src/
```

## Run

```bash
# Gross view - see full payslip breakdown
fava journal-gross.beancount

# Net view - see only take-home pay
fava journal-net.beancount
```

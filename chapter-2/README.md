# Chapter 2: Getting Started

Patterns for scaling from one account to many: naming conventions, transit accounts, and balance assertions.

## Key Concepts

### Account Naming Convention

Structure accounts as `Type:Person:Region:Institution:Account:Currency`:

```beancount
Assets:Lalit:UK:HSBC:Current:GBP
Assets:Lalit:UK:Barclays:Current:GBP
Liabilities:Lalit:UK:AMEX:GBP
```

This enables powerful filtering: `:UK:` for all UK accounts, `:HSBC:` for all HSBC accounts.

### Opening Balances

Use `pad` to set starting balances without importing historical transactions:

```beancount
2024-01-01 pad Assets:Lalit:UK:HSBC:Current:GBP Equity:Opening-Balances
2024-01-02 balance Assets:Lalit:UK:HSBC:Current:GBP  1500.00 GBP
```

### Transit Accounts

Track money "in flight" between accounts:

```beancount
; Saturday: money leaves HSBC
2024-03-16 * "Transfer to Barclays"
  Assets:Lalit:UK:HSBC:Current:GBP      -1000.00 GBP
  Assets:Lalit:Transfers:Internal        1000.00 GBP

; Monday: money arrives at Barclays
2024-03-18 * "Transfer from HSBC"
  Assets:Lalit:Transfers:Internal       -1000.00 GBP
  Assets:Lalit:UK:Barclays:Current:GBP   1000.00 GBP
```

The `zerosum` plugin catches unmatched transfers.

### Boundary Accounts

For money going to accounts you're not tracking yet:

```beancount
2024-03-15 * "Transfer to savings (not yet tracked)"
  Assets:Lalit:UK:HSBC:Current:GBP     -500.00 GBP
  Equity:Transfers:Natwest-Savings      500.00 GBP
```

Use a named equity account per destination - makes search-replace easy when you add the account later.

## Structure

```
chapter-2/
├── journal.beancount        # Entry point with plugin config
└── src/
    ├── accounts.beancount   # Account definitions
    ├── transactions.beancount
    └── balance.beancount    # Opening balances
```

## Run

```bash
fava journal.beancount
```

# Chapter 6: Two-Person Household

Two people, shared expenses, one combined net worth - without duplicating transactions.

## Key Concepts

### The Transfer Paradox

When I transfer £500 to my wife:
- **My perspective:** £500 is an expense (money left my account)
- **Her perspective:** £500 is income (money arrived)
- **Household perspective:** Net worth unchanged (money moved between pockets)

Traditional systems force you to pick one truth. Beancount gives you all three.

### The Architecture

Three composable pieces:
- **Lalit's View** = Common + Lalit's transactions
- **Wife's View** = Common + Wife's transactions
- **Household View** = Common + Both + Translation logic

### Two Rules

**Rule 1: Assets are private.** Bank accounts include the person's name:
```beancount
Assets:Lalit:UK:HSBC:Current:GBP
Assets:Wife:UK:HSBC:Current:GBP
```

**Rule 2: Expenses are public.** Shared expenses use generic names:
```beancount
Expenses:Groceries      ; No person prefix
Expenses:Bills:Energy   ; Whoever pays, it's a household expense
```

### Solving the Paradox

**In Lalit's ledger:**
```beancount
2024-01-20 * "Transfer to Wife for bills"
  Expenses:Lalit:Transfers:Wife       500.00 GBP
  Assets:Lalit:UK:HSBC:Current:GBP
```

**In Wife's ledger:**
```beancount
2024-01-20 * "Transfer from Lalit"
  Assets:Wife:UK:HSBC:Current:GBP     500.00 GBP
  Income:Wife:Transfers:Lalit
```

**In the household view**, `rename_accounts` merges them:
```beancount
plugin "beancount_reds_plugins.rename_accounts.rename_accounts" "{
  'Expenses:Lalit:Transfers:Wife': 'Assets:Household:Transfers:Internal',
  'Income:Wife:Transfers:Lalit': 'Assets:Household:Transfers:Internal',
}"
```

The expense (+500) and income (-500) merge into the same account, netting to zero. Household net worth is unchanged.

## Structure

```
chapter-6/
├── common/
│   └── src/
│       ├── accounts.beancount       # Shared expense accounts
│       └── commodities.beancount
├── lalit/
│   ├── src/
│   │   ├── accounts.beancount       # Lalit's personal accounts
│   │   ├── transactions.beancount
│   │   └── journal.beancount
│   └── journal-net.beancount        # Lalit's view
├── wife/
│   ├── src/                         # Same structure
│   └── journal-net.beancount        # Wife's view
└── total/
    └── journal-net.beancount        # Combined household view
```

## Run

```bash
# Individual views
fava lalit/journal-net.beancount
fava wife/journal-net.beancount

# Combined household view
fava total/journal-net.beancount
```

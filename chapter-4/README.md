# Chapter 4: Investments

Investment tracking with commodities, cost basis, and prices.

## Key Concepts

### Everything Is a Commodity

Beancount treats stocks and currencies identically. A share of `AAPL` is a commodity, just like `USD` or `GBP`. Buying stocks is just exchanging one commodity for another.

### Account Structure

Investments follow the same naming convention, with cash and holdings separated:

```beancount
Assets:Lalit:US:IB:Brokerage:USD     ; Cash in the account
Assets:Lalit:US:IB:Brokerage:AAPL    ; Stock holdings
```

Each security gets granular income accounts for tax tracking:

```beancount
Income:Lalit:US:IB:Brokerage:AAPL:Dividends
Income:Lalit:US:IB:Brokerage:AAPL:Capital-Gains
```

### Cost Basis Syntax

Use `{price}` for cost basis (what you paid) and `@ price` for current price:

```beancount
; Buy 10 shares at $185 each
2024-01-10 * "BUY AAPL"
  Assets:Lalit:US:IB:Brokerage:AAPL      10 AAPL {185.00 USD} @ 185.00 USD
  Assets:Lalit:US:IB:Brokerage:USD   -1850.00 USD

; Sell 5 shares (cost $185) at $190 = $25 gain
2024-01-30 * "SELL AAPL"
  Assets:Lalit:US:IB:Brokerage:AAPL      -5 AAPL {185.00 USD} @ 190.00 USD
  Assets:Lalit:US:IB:Brokerage:USD     950.00 USD
  Income:Lalit:US:IB:Brokerage:AAPL:Capital-Gains  -25.00 USD
```

### Currency Exchange

Use `@@` for total cost (instead of per-unit):

```beancount
; Exchange GBP for INR - @@ specifies the total, not per-unit
2024-03-02 * "Wise" "GBP to INR"
  Assets:Lalit:UK:Wise:INR            98000.00 INR @@ 950.00 GBP
  Assets:Lalit:UK:Wise:GBP             -950.00 GBP
```

### Prices

To calculate net worth, Beancount needs prices for all commodities:

```beancount
2024-01-10 price AAPL  185.50 USD
2024-01-10 price USD   0.79 GBP
```

These can be fetched automatically via scripts (see the blog post for details).

## Structure

```
chapter-4/
├── journal.beancount
└── src/
    ├── commodities.beancount  # Stock/fund definitions
    ├── prices.beancount       # Price history
    ├── accounts.beancount     # Investment accounts
    └── transactions.beancount # Buy/sell with cost basis
```

## Run

```bash
fava journal.beancount
```

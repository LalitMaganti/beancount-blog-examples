import datetime
import random
import os

# Configuration
START_DATE = datetime.date(2022, 1, 1)
END_DATE = datetime.date(2024, 4, 1)
OUTPUT_DIR = "demo"

# Financial Profile
SALARY = 3500
RENT = 1200
ISA_INVESTMENT = 1000
GIA_INVESTMENT = 800

# Random seed for reproducible transaction generation
SEED = 42

header = """option "title" "Demo Financials"
option "operating_currency" "GBP"
plugin "beancount.plugins.auto_accounts"

; Fava extensions
2020-01-01 custom "fava-extension" "fava_dashboards"
2020-01-01 custom "fava-extension" "fava_portfolio_returns" "{
  'beangrow_config': 'beangrow.pbtxt',
}"

; Commodities
2020-01-01 commodity GOOG
  name: "Alphabet Inc Class C"
2020-01-01 commodity VWRL
  name: "Vanguard FTSE All-World UCITS ETF"
2020-01-01 commodity USD
2020-01-01 commodity GBP

2020-01-01 open Assets:Lalit:UK:HSBC:Current:GBP          GBP
2020-01-01 open Assets:Lalit:UK:Vanguard:ISA:VWRL         VWRL
2020-01-01 open Assets:Lalit:UK:Vanguard:ISA:GBP          GBP
2020-01-01 open Assets:Lalit:UK:Vanguard:GIA:VWRL         VWRL
2020-01-01 open Assets:Lalit:UK:Vanguard:GIA:GBP          GBP
2020-01-01 open Assets:Lalit:US:Schwab:Brokerage:GOOG     GOOG
2020-01-01 open Assets:Lalit:US:Schwab:Brokerage:USD      USD
2020-01-01 open Liabilities:Lalit:UK:Amex:GBP             GBP
2020-01-01 open Income:Lalit:UK:Google:Salary             GBP
2020-01-01 open Income:Lalit:UK:Google:Stock-Vest         USD
2020-01-01 open Expenses:Housing:Rent                     GBP
2020-01-01 open Expenses:Food:Groceries                   GBP
2020-01-01 open Expenses:Food:Restaurant                  GBP
2020-01-01 open Expenses:Transport:Tube                   GBP
2020-01-01 open Equity:Opening-Balances                   GBP

; Initial Balance
2021-12-31 * "Opening Balance"
  Assets:Lalit:UK:HSBC:Current:GBP              5000.00 GBP
  Equity:Opening-Balances

"""


def load_prices() -> dict[datetime.date, dict[str, float]]:
    """Load prices from the pre-fetched prices.beancount file."""
    prices_file = "demo/prices.beancount"
    prices = {}

    with open(prices_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith(';'):
                continue
            # Parse: 2022-01-03 price AAPL 182.01 USD
            parts = line.split()
            if len(parts) >= 5 and parts[1] == 'price':
                date = datetime.datetime.strptime(parts[0], "%Y-%m-%d").date()
                symbol = parts[2]
                value = float(parts[3])
                if date not in prices:
                    prices[date] = {}
                prices[date][symbol] = value

    return prices


# Initial prices (close to first real prices in the data)
INITIAL_PRICES = {
    "GOOG": 136.0,   # ~Jan 2022
    "VWRL": 84.0,    # ~Jan 2022
    "USD": 0.74,     # ~Jan 2022
}


def get_price(prices: dict, date: datetime.date, symbol: str, last_known: dict) -> float:
    """Get price for date, falling back to last known price for weekends/holidays."""
    if date in prices and symbol in prices[date]:
        last_known[symbol] = prices[date][symbol]
    return last_known.get(symbol, INITIAL_PRICES.get(symbol, 100.0))


def generate():
    random.seed(SEED)

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Load pre-fetched prices
    all_prices = load_prices()
    print(f"Loaded prices for {len(all_prices)} dates")

    transactions = []
    last_known = {}

    current_date = START_DATE

    while current_date <= END_DATE:
        date_str = current_date.strftime("%Y-%m-%d")

        # Get prices for investment transactions
        vwrl_price = get_price(all_prices, current_date, "VWRL", last_known)
        goog_price = get_price(all_prices, current_date, "GOOG", last_known)

        # Monthly Salary, Rent & Stock Vest (1st of month)
        if current_date.day == 1:
            transactions.append(f"""{date_str} * "Google" "Salary"
  Assets:Lalit:UK:HSBC:Current:GBP          {SALARY:.2f} GBP
  Income:Lalit:UK:Google:Salary""")

            transactions.append(f"""{date_str} * "Landlord" "Rent"
  Expenses:Housing:Rent                      {RENT:.2f} GBP
  Assets:Lalit:UK:HSBC:Current:GBP""")

            # Monthly GOOG stock vest - cash goes to Schwab, then purchase GOOG
            goog_price_rounded = round(goog_price, 2)
            vest_units = 2
            vest_value = round(vest_units * goog_price_rounded, 2)
            transactions.append(f"""{date_str} * "Google" "RSU Vest"
  Assets:Lalit:US:Schwab:Brokerage:USD       {vest_value:.2f} USD
  Income:Lalit:UK:Google:Stock-Vest         -{vest_value:.2f} USD""")

            transactions.append(f"""{date_str} * "Schwab" "Buy GOOG"
  Assets:Lalit:US:Schwab:Brokerage:GOOG      {vest_units} GOOG {{{goog_price_rounded:.2f} USD}}
  Assets:Lalit:US:Schwab:Brokerage:USD      -{vest_value:.2f} USD""")

            # Monthly Investment (DCA) - Transfer to ISA and buy VWRL
            vwrl_price_rounded = round(vwrl_price, 2)
            isa_units = int(ISA_INVESTMENT / vwrl_price_rounded)
            isa_cost = round(isa_units * vwrl_price_rounded, 2)
            transactions.append(f"""{date_str} * "Vanguard" "ISA Transfer"
  Assets:Lalit:UK:Vanguard:ISA:GBP           {isa_cost:.2f} GBP
  Assets:Lalit:UK:HSBC:Current:GBP          -{isa_cost:.2f} GBP""")

            transactions.append(f"""{date_str} * "Vanguard" "ISA Buy VWRL"
  Assets:Lalit:UK:Vanguard:ISA:VWRL          {isa_units} VWRL {{{vwrl_price_rounded:.2f} GBP}}
  Assets:Lalit:UK:Vanguard:ISA:GBP          -{isa_cost:.2f} GBP""")

            # Monthly Investment (DCA) - Transfer to GIA and buy VWRL
            gia_units = int(GIA_INVESTMENT / vwrl_price_rounded)
            gia_cost = round(gia_units * vwrl_price_rounded, 2)
            transactions.append(f"""{date_str} * "Vanguard" "GIA Transfer"
  Assets:Lalit:UK:Vanguard:GIA:GBP           {gia_cost:.2f} GBP
  Assets:Lalit:UK:HSBC:Current:GBP          -{gia_cost:.2f} GBP""")

            transactions.append(f"""{date_str} * "Vanguard" "GIA Buy VWRL"
  Assets:Lalit:UK:Vanguard:GIA:VWRL          {gia_units} VWRL {{{vwrl_price_rounded:.2f} GBP}}
  Assets:Lalit:UK:Vanguard:GIA:GBP          -{gia_cost:.2f} GBP""")

        # Weekly Groceries (Random days)
        if random.random() < 0.15:
            amount = random.uniform(30, 120)
            transactions.append(f"""{date_str} * "Tesco" "Groceries"
  Expenses:Food:Groceries                    {amount:.2f} GBP
  Liabilities:Lalit:UK:Amex:GBP             -{amount:.2f} GBP""")

        # Occasional Restaurant
        if random.random() < 0.08:
            amount = random.uniform(20, 80)
            transactions.append(f"""{date_str} * "Nando's" "Dinner"
  Expenses:Food:Restaurant                   {amount:.2f} GBP
  Liabilities:Lalit:UK:Amex:GBP             -{amount:.2f} GBP""")

        # Pay off Credit Card (25th of month)
        if current_date.day == 25:
            payment = 500
            transactions.append(f"""{date_str} * "Amex" "Payment"
  Liabilities:Lalit:UK:Amex:GBP              {payment:.2f} GBP
  Assets:Lalit:UK:HSBC:Current:GBP          -{payment:.2f} GBP""")

        current_date += datetime.timedelta(days=1)

    # Write journal file
    with open(f"{OUTPUT_DIR}/journal.beancount", "w") as f:
        f.write(header)
        f.write("\n\n".join(transactions))
        f.write("\n\n")
        # Include the prices file
        f.write('include "prices.beancount"\n')

    print(f"Generated {len(transactions)} transactions in {OUTPUT_DIR}/journal.beancount")


if __name__ == "__main__":
    generate()

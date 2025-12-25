# beancount-blog-examples

Companion code for [One Number I Trust: Plain-Text Accounting for a Multi-Currency Household](https://lalitm.com/post/one-number-i-trust).

## Quick Start

```bash
git clone https://github.com/LalitMaganti/beancount-blog-examples.git
cd beancount-blog-examples
./scripts/quickstart.sh demo
```

## Structure

| Folder | Description |
|--------|-------------|
| `chapter-2/` | Getting started: accounts, transactions, balance assertions |
| `chapter-3/` | Importers: parsing bank statements with beangulp |
| `chapter-4/` | Investments: cost basis, prices, capital gains |
| `chapter-5/` | Multiple views: gross vs net, rename_accounts plugin |
| `chapter-6/` | Two-person household: shared expenses, combined view |
| `demo/` | 2+ years of synthetic data for screenshots |

## Run

```bash
# Run any chapter
fava chapter-2/journal.beancount

# Or use the quickstart script
./scripts/quickstart.sh chapter-2
```

## License

Apache 2.0 - see [LICENSE](LICENSE) for details.

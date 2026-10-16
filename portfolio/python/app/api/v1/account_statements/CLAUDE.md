# Broker statement import (PDF)

**Purpose:** turn a broker PDF into reviewed transactions and create them in one atomic batch.

**State (2026-10-16):** 🟡 Trade Republic: trades, savings plans and dividends import in EUR; cash rows are listed as skipped. Tested on synthetic statement text only; a real PDF check is open (the text-layout assumptions in `_extract_transactions` are unverified). Not exercised by the demo data.

## Backend — `router.py` (prefix `/api/v1/account-statements`), `core/services/account_statement_service.py`, `core/services/parsers/`
| Endpoint | Behaviour |
|---|---|
| `GET /providers` | Supported parsers: Trade Republic (`parsers/trade_republic.py`), Portfolia's own export (`parsers/portfolia.py`) |
| `POST /parse` (multipart `provider_id`, `file`) | Parsed rows for review (no DB writes) |
| `POST /transactions/bulk-create` | Atomic: insert all rows, recalculate each affected asset, one commit. Also used by the manual Bulk Entry modal |

## Frontend
`PDFUploadModal` (provider + file) → `ParsedDataTable` (map symbols to assets, inline edits, draft saved in localStorage, choose portfolio) → bulk-create. `accountStatementsAPI` in `services/api.js`.

## Trade Republic rules (`parsers/trade_republic.py`, tests `tests/unit/test_trade_republic_import.py`)
- Rows come from the `UMSATZÜBERSICHT` block; the second-to-last amount on a line is the transaction amount, the last is the balance. Dates like `06 März 2025` / `09 Sept. 2025` are matched by month prefix.
- **Handel** → buy/sell (ISIN as symbol). The statement shows only the total, so the fee is assumed: `TRADE_FEE` = €1 per buy/sell trade, €0 for savings plan executions. `price = (total − fee) / qty` for buys, `(total + fee) / qty` for sells; `total_amount` stays the printed total.
- **Erträge** → dividend with `total_amount` = cash received, quantity and price 0. Bulk-create keeps that amount (it no longer recomputes qty × price for dividends) and rejects a dividend ≤ 0.
- **Zinszahlung, Überweisung, Kartentransaktion, Steuern** and unrecognised trades → `skipped[]` with a reason (`CASH_ROW_REASONS`); portfolios have no cash account. The review table lists them under "statement rows not imported".
- Every row is `currency="EUR"`. Bulk-create stores `currency` (default: the portfolio currency) and `taxes`. Values are **not converted**: an EUR transaction on a USD-quoted asset needs FX (plan 2.3).

## Known gaps
- No real statement in the test suite; layout drift (column order, extra amounts on a line) would show up as warnings or wrong amounts.
- In/out direction is not read (the type implies it for trades and dividends).
- Withholding tax is not printed per dividend, so `taxes` stays 0 for TR dividends.
- The frontend maps each ISIN to an asset by hand (`ClientSideAssetSearch`); no ISIN → ticker lookup.
- Per-row `ValueError` messages are shown to the user; other errors are logged and reported generically.

## Planned
Plan 2.3 FX (Yahoo daily rates) so EUR transactions on USD assets value correctly; ISIN → ticker resolution. Later: an LLM fallback parser for unknown brokers via the shared ollama (§1b), and OCR via paperless/Tesseract.

# Broker statement import (PDF)

**Purpose:** turn a broker PDF into reviewed transactions and create them in one atomic batch.

**State (2026-10-16):** ⚠️ buys/sells import; the Trade Republic path loses dividends, tax, fees and currency (details below). Not exercised by the demo data.

## Backend — `router.py` (prefix `/api/v1/account-statements`), `core/services/account_statement_service.py`, `core/services/parsers/`
| Endpoint | Behaviour |
|---|---|
| `GET /providers` | Supported parsers: Trade Republic (`parsers/trade_republic.py`), Portfolia's own export (`parsers/portfolia.py`) |
| `POST /parse` (multipart `provider_id`, `file`) | Parsed rows for review (no DB writes) |
| `POST /transactions/bulk-create` | Atomic: insert all rows, recalculate each affected asset, one commit. Also used by the manual Bulk Entry modal |

## Frontend
`PDFUploadModal` (provider + file) → `ParsedDataTable` (map symbols to assets, inline edits, draft saved in localStorage, choose portfolio) → bulk-create. `accountStatementsAPI` in `services/api.js`.

## Known bugs (Trade Republic)
- The parser emits `interest`, `deposit`, `withdrawal` and `tax` types that are not in `TransactionType`. A statement containing them most likely fails the whole parse with a 400. This was inferred from the code and not run.
- Dividends ("Erträge") are parsed with quantity=0 and price=0. Bulk-create recomputes `total_amount` = 0 and ignores the parsed amount, so **dividends are stored as 0**.
- Tax rows are skipped, and `BulkTransactionItem` has no `taxes` field, so withholding is lost.
- Price = total / quantity, which folds the broker fee into the price (fees = 0).
- "€" is stripped and currency is never set, so euro amounts are stored as USD.
- `Transactions.jsx` checks `summary.total_succeeded`, but the API returns `total_created`, so the list doesn't refresh after an import.
- `str(e)` in 500s and per-row errors.

## Planned
Plan 2.2: keep the dividend amount and withholding tax and set the currency, then run a data migration to recompute affected rows. Also: map deposits/withdrawals/interest to supported types or drop them explicitly. Later: an LLM fallback parser for unknown brokers via the shared ollama (§1b), and OCR via paperless/Tesseract.

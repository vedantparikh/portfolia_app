import csv
import io
from collections import defaultdict
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Optional

from core.schemas.account_statements import (
    Fill,
    ParsedData,
    ParsedInstrument,
    ParsedTransaction,
    ParsingMetadata,
    SkippedRow,
    StatementPeriod,
)
from core.services.parsers.base import PDFParser

# pytr `export_transactions` columns, in order; headers are translated, the order is not.
COLUMNS = (
    "date",
    "type",
    "value",
    "note",
    "isin",
    "shares",
    "fees",
    "taxes",
    "isin2",
    "shares2",
)

TYPES = {
    "buy": "buy",
    "kauf": "buy",
    "sell": "sell",
    "verkauf": "sell",
    "dividend": "dividend",
    "dividende": "dividend",
}
SKIP_REASONS = {
    "split": "Splits are applied automatically from market data",
    "swap": "Security swaps are not supported; check both ISINs' holdings",
    "spinoff": "Spin-offs are not supported",
    "deposit": "Cash deposit: portfolios have no cash account",
    "einlage": "Cash deposit: portfolios have no cash account",
    "removal": "Cash withdrawal or card payment: portfolios have no cash account",
    "entnahme": "Cash withdrawal or card payment: portfolios have no cash account",
    "interest": "Interest on cash: portfolios have no cash account",
    "zinsen": "Interest on cash: portfolios have no cash account",
    "taxes": "Account-level tax: not linked to a trade",
    "steuern": "Account-level tax: not linked to a trade",
    "tax refund": "Account-level tax refund: not linked to a trade",
    "steuerrückerstattung": "Account-level tax refund: not linked to a trade",
    "transfer (inbound)": "Security transfers are not supported yet",
    "umbuchung (eingang)": "Security transfers are not supported yet",
    "transfer (outbound)": "Security transfers are not supported yet",
    "umbuchung (ausgang)": "Security transfers are not supported yet",
}


def parse_number(text: str) -> Optional[Decimal]:
    """'3002.8', '-3.002,8', '10,640298', '1,234.5' → Decimal; '' → None."""
    text = (text or "").strip()
    if not text:
        return None
    if "," in text and "." in text:
        decimal_sep = "," if text.rfind(",") > text.rfind(".") else "."
        text = text.replace("." if decimal_sep == "," else ",", "")
    if "," in text:
        text = text.replace(",", ".")
    try:
        return Decimal(text)
    except InvalidOperation as e:
        raise ValueError(f"not a number: {text!r}") from e


class PytrCsvParser(PDFParser):
    """Trade Republic history exported by pytr (`pytr export_transactions`), amounts in EUR."""

    def parse(self, pdf_content: bytes) -> ParsedData:
        warnings: List[str] = []
        try:
            text = pdf_content.decode("utf-8-sig")
        except UnicodeDecodeError:
            return self._failed("The file is not UTF-8 text; export it again with pytr")

        lines = text.splitlines()
        if not lines:
            return self._failed("The file is empty")
        delimiter = ";" if lines[0].count(";") >= lines[0].count(",") else ","
        reader = csv.reader(io.StringIO(text), delimiter=delimiter)
        header = next(reader)
        if len(header) != len(COLUMNS):
            return self._failed(
                f"Expected the {len(COLUMNS)} pytr columns (Date;Type;Value;Note;ISIN;Shares;"
                f"Fees;Taxes;ISIN2;Shares2), found {len(header)}"
            )

        records = []
        for line_no, cells in enumerate(reader, start=2):
            if not any(c.strip() for c in cells):
                continue
            if len(cells) != len(COLUMNS):
                warnings.append(
                    f"Line {line_no}: expected {len(COLUMNS)} columns, skipped"
                )
                continue
            records.append((line_no, dict(zip(COLUMNS, cells))))
        records.sort(key=lambda r: r[1]["date"])

        transactions: List[ParsedTransaction] = []
        skipped: List[SkippedRow] = []
        fills: Dict[str, List[Fill]] = defaultdict(list)
        names: Dict[str, str] = {}
        counts: Dict[str, int] = defaultdict(int)

        for line_no, row in records:
            try:
                day = datetime.fromisoformat(row["date"].strip()).date().isoformat()
                parsed = self._row(row)
            except ValueError as e:
                warnings.append(f"Line {line_no}: {e}")
                continue
            if isinstance(parsed, str):
                skipped.append(
                    SkippedRow(
                        transaction_date=day,
                        kind=row["type"],
                        description=row["note"],
                        amount=abs(parse_number(row["value"]) or Decimal("0")),
                        currency="EUR",
                        reason=parsed,
                    )
                )
                continue

            isin = parsed["symbol"]
            names.setdefault(isin, parsed["name"])
            counts[isin] += 1
            if parsed["transaction_type"] in ("buy", "sell"):
                fills[isin].append(Fill(date=day, price=parsed["price"]))
            transactions.append(
                ParsedTransaction(
                    id=f"pytr_{line_no}",
                    transaction_date=day,
                    currency="EUR",
                    **parsed,
                )
            )

        days = [t.transaction_date for t in transactions] + [
            s.transaction_date for s in skipped
        ]
        return ParsedData(
            provider="pytr_csv",
            statement_period=StatementPeriod(
                start_date=min(days, default=""), end_date=max(days, default="")
            ),
            transactions=transactions,
            skipped=skipped,
            instruments=[
                ParsedInstrument(
                    isin=isin,
                    name=names[isin],
                    transaction_count=counts[isin],
                    fills=fills[isin],
                )
                for isin in sorted(counts, key=lambda i: -counts[i])
            ],
            metadata=ParsingMetadata(
                total_transactions=len(transactions),
                total_skipped=len(skipped),
                warnings=warnings,
            ),
        )

    def _row(self, row: Dict[str, str]) -> dict | str:
        """Fields of an importable row, or the reason it is skipped."""
        kind = row["type"].strip().lower()
        transaction_type = TYPES.get(kind)
        if transaction_type is None:
            return SKIP_REASONS.get(kind, f"Unsupported type {row['type']!r}")

        isin = row["isin"].strip()
        if not isin:
            return "No ISIN"
        value = parse_number(row["value"]) or Decimal("0")
        shares = parse_number(row["shares"]) or Decimal("0")
        fees = abs(parse_number(row["fees"]) or Decimal("0"))
        taxes = abs(parse_number(row["taxes"]) or Decimal("0"))
        name = row["note"].strip() or isin

        if transaction_type == "dividend":
            if value <= 0:
                return "Dividend without a positive amount"
            return {
                "transaction_type": "dividend",
                "name": name,
                "symbol": isin,
                "quantity": shares,
                "price": value / shares if shares else Decimal("0"),
                "total_amount": value,
                "taxes": taxes,
            }

        if shares <= 0:
            return "Trade without a share count"
        total = -value if transaction_type == "buy" else value
        if total <= 0:
            return "Trade amount has the wrong sign for its type"
        gross = (
            total - fees - taxes if transaction_type == "buy" else total + fees + taxes
        )
        if gross <= 0:
            return "Fees and taxes exceed the trade amount"
        return {
            "transaction_type": transaction_type,
            "name": name,
            "symbol": isin,
            "quantity": shares,
            "price": gross / shares,
            "total_amount": total,
            "fees": fees,
            "taxes": taxes,
        }

    def _failed(self, message: str) -> ParsedData:
        return ParsedData(
            provider="pytr_csv",
            statement_period=StatementPeriod(start_date="", end_date=""),
            transactions=[],
            metadata=ParsingMetadata(total_transactions=0, warnings=[message]),
        )

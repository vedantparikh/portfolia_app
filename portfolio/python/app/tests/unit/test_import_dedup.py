"""Importing the same broker export twice creates nothing new."""

import base64
from datetime import datetime, timezone
from decimal import Decimal

import pytest

from core.database.models import Asset, Portfolio, Transaction, User
from core.database.models.asset import AssetType
from core.database.models.transaction import TransactionType
from core.schemas.account_statements import BulkTransactionItem, ImportedCheckRow
from core.services.account_statement_service import AccountStatementService

CSV = """Date;Type;Value;Note;ISIN;Shares;Fees;Taxes;ISIN2;Shares2
2024-02-20T16:32:07;Buy;-3002.8;Euro Stoxx 50;IE00B4K6B022;60;1;;;
2025-01-03T10:00:00;Buy;-100;Savings plan;IE00B4K6B022;2;;;;
2025-01-03T10:00:00;Buy;-100;Savings plan;IE00B4K6B022;2;;;;
2025-10-23T14:19:56;Dividend;2.24;Euro Stoxx 50;IE00B4K6B022;62;;0.78;;
"""
NEW_ROW = "2025-11-03T10:00:00;Buy;-100;Savings plan;IE00B4K6B022;2;;;;\n"


class FakeMarketData:
    async def get_ticker_info(self, symbol):
        return {"long_name": f"{symbol} Inc", "quote_type": "EQUITY", "currency": "EUR"}


@pytest.fixture
def portfolio(test_db):
    user = User(email="dedup@example.com", username="dedup", password_hash="x")
    test_db.add(user)
    test_db.commit()
    portfolio = Portfolio(user_id=user.id, name="TR", currency="EUR")
    test_db.add(portfolio)
    test_db.commit()
    return portfolio


def _service(test_db):
    service = AccountStatementService(test_db)
    service.market_data = FakeMarketData()
    return service


def _items(service, csv):
    parsed = service.parse_statement(
        "pytr_csv", base64.b64encode(csv.encode()).decode(), "tr.csv"
    )
    return [
        BulkTransactionItem(
            transaction_date=t.transaction_date,
            transaction_type=t.transaction_type,
            symbol="EXW1.DE",
            isin=t.symbol,
            quantity=t.quantity,
            price=t.price or Decimal("0"),
            fees=t.fees,
            taxes=t.taxes,
            total_amount=t.total_amount,
            currency=t.currency,
            source_key=t.source_key,
        )
        for t in parsed.transactions
    ]


async def _import(test_db, portfolio, csv):
    service = _service(test_db)
    _, summary = await service.create_bulk_transactions(
        portfolio.id, _items(service, csv), portfolio.user_id
    )
    return summary


def test_source_keys_are_stable_and_number_identical_rows(test_db):
    first = [i.source_key for i in _items(_service(test_db), CSV)]
    again = [i.source_key for i in _items(_service(test_db), CSV)]

    assert first == again
    assert len(set(first)) == 4
    assert all(len(k) == 64 for k in first)


@pytest.mark.asyncio
async def test_reimporting_the_same_file_creates_nothing(test_db, portfolio):
    first = await _import(test_db, portfolio, CSV)
    second = await _import(test_db, portfolio, CSV)

    assert (first.total_created, first.total_skipped) == (4, 0)
    assert (second.total_created, second.total_skipped, second.total_failed) == (
        0,
        4,
        0,
    )
    assert test_db.query(Transaction).count() == 4


@pytest.mark.asyncio
async def test_partially_new_file_creates_only_the_new_rows(test_db, portfolio):
    await _import(test_db, portfolio, CSV)

    summary = await _import(test_db, portfolio, CSV + NEW_ROW)

    assert (summary.total_created, summary.total_skipped) == (1, 4)
    dates = [t.transaction_date.date().isoformat() for t in test_db.query(Transaction)]
    assert sorted(dates)[-1] == "2025-11-03"
    assert test_db.query(Transaction).count() == 5


@pytest.mark.asyncio
async def test_same_row_twice_in_one_request_is_created_once(test_db, portfolio):
    service = _service(test_db)
    items = _items(service, CSV)

    _, summary = await service.create_bulk_transactions(
        portfolio.id, items + items[:1], portfolio.user_id
    )

    assert (summary.total_created, summary.total_skipped) == (4, 1)


@pytest.mark.asyncio
async def test_rows_imported_before_keys_existed_are_matched_and_keyed(
    test_db, portfolio
):
    asset = Asset(
        symbol="EXW1.DE",
        name="Euro Stoxx 50",
        asset_type=AssetType.ETF,
        isin="IE00B4K6B022",
        currency="EUR",
        user_id=portfolio.user_id,
    )
    test_db.add(asset)
    test_db.flush()
    for _ in range(2):
        test_db.add(
            Transaction(
                portfolio_id=portfolio.id,
                asset_id=asset.id,
                transaction_type=TransactionType.BUY,
                quantity=Decimal("2"),
                price=Decimal("50"),
                total_amount=Decimal("100"),
                currency="EUR",
                transaction_date=datetime(2025, 1, 3, tzinfo=timezone.utc),
            )
        )
    test_db.commit()
    service = _service(test_db)
    items = _items(service, CSV)
    rows = [ImportedCheckRow(**i.model_dump()) for i in items]

    assert service.imported_keys(portfolio.id, rows, portfolio.user_id) == sorted(
        [items[1].source_key, items[2].source_key]
    )
    summary = await _import(test_db, portfolio, CSV)

    assert (summary.total_created, summary.total_skipped) == (2, 2)
    assert (
        test_db.query(Transaction).filter(Transaction.source_key.is_(None)).count() == 0
    )
    assert (await _import(test_db, portfolio, CSV)).total_created == 0


@pytest.mark.asyncio
async def test_manual_rows_without_a_key_are_never_skipped(test_db, portfolio):
    item = BulkTransactionItem(
        transaction_date="2025-03-03",
        transaction_type="buy",
        symbol="EXW1.DE",
        quantity=Decimal("1"),
        price=Decimal("10"),
        total_amount=Decimal("10"),
    )
    service = _service(test_db)

    _, summary = await service.create_bulk_transactions(
        portfolio.id, [item, item], portfolio.user_id
    )

    assert (summary.total_created, summary.total_skipped) == (2, 0)

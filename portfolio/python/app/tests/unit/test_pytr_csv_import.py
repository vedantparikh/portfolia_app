"""pytr CSV import: parsing, ISIN → listing resolution, asset creation on import."""

from decimal import Decimal

import pytest

from core.database.models import Asset, Portfolio, Transaction, User
from core.database.models.asset import AssetType
from core.schemas.account_statements import (
    BulkTransactionItem,
    Fill,
    ListingCandidate,
    ParsedInstrument,
)
from core.services.account_statement_service import AccountStatementService
from core.services.isin_resolver import (
    IsinResolver,
    crypto_symbol,
    fill_match,
    german_variants,
    rank,
)
from core.services.parsers.pytr_csv import PytrCsvParser, parse_number

EN = """Date;Type;Value;Note;ISIN;Shares;Fees;Taxes;ISIN2;Shares2
2025-03-14T07:03:14;Sell;94.76;D-Wave Quantum;US26740W1099;17;1;3.18;;
2024-02-20T16:32:07;Buy;-3002.8;Euro Stoxx 50 EUR (Dist);IE00B4K6B022;60;1;;;
2024-06-03T17:07:26;Deposit;200;Jane Doe;;;;;;
2024-06-26T08:06:40;Split;0;Chipotle Mexican Grill;US1696561059;49;;;;
2025-10-23T14:19:56;Dividend;2.24;Comcast (A);US20030N1019;10.640298;;0.78;;
2025-01-02T10:00:00;Removal;-3.5;Coffee;;;;;;
2025-01-03T10:00:00;Buy;-100;Savings plan;IE00B4K6B022;2;;;;
"""

DE = """Datum;Typ;Wert;Notiz;ISIN;Stück;Gebühren;Steuern;ISIN2;Stück2
2024-02-20T16:32:07;Kauf;-3.002,8;Euro Stoxx 50 EUR (Dist);IE00B4K6B022;60;1;;;
2025-10-23T14:19:56;Dividende;2,24;Comcast (A);US20030N1019;10,640298;;0,78;;
2024-06-03T17:07:26;Einlage;200;Jane Doe;;;;;;
"""


def _parse(text):
    return PytrCsvParser().parse(text.encode())


@pytest.mark.parametrize(
    ("text", "number"),
    [
        ("-3002.8", Decimal("-3002.8")),
        ("-3.002,8", Decimal("-3002.8")),
        ("10,640298", Decimal("10.640298")),
        ("1,234.5", Decimal("1234.5")),
        ("", None),
    ],
)
def test_numbers_in_any_pytr_format(text, number):
    assert parse_number(text) == number


def test_trades_and_dividends_are_imported_in_date_order():
    result = _parse(EN)

    assert [
        (t.transaction_date, t.transaction_type.value, t.symbol)
        for t in result.transactions
    ] == [
        ("2024-02-20", "buy", "IE00B4K6B022"),
        ("2025-01-03", "buy", "IE00B4K6B022"),
        ("2025-03-14", "sell", "US26740W1099"),
        ("2025-10-23", "dividend", "US20030N1019"),
    ]
    assert {t.currency for t in result.transactions} == {"EUR"}
    assert result.statement_period.start_date == "2024-02-20"


def test_value_is_net_cash_and_price_excludes_fees_and_taxes():
    buy, plan, sell, dividend = _parse(EN).transactions

    assert (buy.total_amount, buy.fees, buy.quantity) == (
        Decimal("3002.8"),
        Decimal("1"),
        Decimal("60"),
    )
    assert buy.price == Decimal("3001.8") / 60
    assert (plan.price, plan.fees) == (Decimal("50"), Decimal("0"))
    assert (sell.total_amount, sell.fees, sell.taxes) == (
        Decimal("94.76"),
        Decimal("1"),
        Decimal("3.18"),
    )
    assert sell.price == Decimal("98.94") / 17
    assert (dividend.total_amount, dividend.taxes, dividend.quantity) == (
        Decimal("2.24"),
        Decimal("0.78"),
        Decimal("10.640298"),
    )


def test_splits_and_cash_rows_are_skipped_with_a_reason():
    skipped = {s.kind: s.reason for s in _parse(EN).skipped}

    assert set(skipped) == {"Deposit", "Split", "Removal"}
    assert "automatically" in skipped["Split"]


def test_instruments_carry_fills_for_listing_matching():
    instruments = {i.isin: i for i in _parse(EN).instruments}

    assert instruments["IE00B4K6B022"].transaction_count == 2
    assert [f.date for f in instruments["IE00B4K6B022"].fills] == [
        "2024-02-20",
        "2025-01-03",
    ]
    assert instruments["US20030N1019"].fills == []


def test_german_export_parses_the_same():
    result = _parse(DE)

    assert [t.transaction_type.value for t in result.transactions] == [
        "buy",
        "dividend",
    ]
    assert result.transactions[0].total_amount == Decimal("3002.8")
    assert result.transactions[1].taxes == Decimal("0.78")
    assert [s.kind for s in result.skipped] == ["Einlage"]


def test_wrong_column_count_is_reported():
    result = _parse("Date;Type;Value\n2024-01-01;Buy;-1\n")

    assert result.transactions == []
    assert "Expected the 10 pytr columns" in result.metadata.warnings[0]


def test_crypto_pseudo_isins():
    assert crypto_symbol("XF000XRP0018") == "XRP-EUR"
    assert crypto_symbol("XF000TRUMP04") == "TRUMP-EUR"
    assert crypto_symbol("US0378331005") is None


def test_german_variants_cover_every_venue_of_a_german_code():
    variants = german_variants(["AAPL", "APC.F", "APC.DE", "AAPL.TO"])

    assert variants[:3] == ["APC.F", "APC.SG", "APC.DE"]
    assert len(variants) == 8


def test_fill_match_undoes_later_splits():
    fills = [
        Fill(date="2024-05-01", price=Decimal("800")),
        Fill(date="2024-07-01", price=Decimal("110")),
    ]
    ranges = {"2024-05-01": [79.0, 81.0], "2024-07-01": [108.0, 112.0]}

    assert fill_match(fills, ranges, {"2024-06-10": 10.0}) == (2, 2)
    assert fill_match(fills, ranges, {}) == (1, 2)


def test_rank_prefers_account_currency_then_frankfurt_over_xetra():
    ranked = rank(
        [
            ListingCandidate(
                symbol="APC.DE", currency="EUR", match_percent=100, fills_checked=20
            ),
            ListingCandidate(
                symbol="AAPL", currency="USD", match_percent=100, fills_checked=20
            ),
            ListingCandidate(
                symbol="APC.F", currency="EUR", match_percent=98, fills_checked=20
            ),
            ListingCandidate(
                symbol="APC.MU", currency="EUR", match_percent=60, fills_checked=20
            ),
        ],
        "EUR",
    )

    assert [c.symbol for c in ranked] == ["APC.F", "APC.DE", "AAPL", "APC.MU"]


class FakeMarketData:
    def __init__(self, listings, ranges):
        self.listings, self.ranges = listings, ranges

    async def search_listings(self, query):
        return self.listings.get(query, [])

    async def get_daily_ranges(self, symbol, start, end):
        return self.ranges.get(symbol)

    async def get_ticker_info(self, symbol):
        return {"long_name": f"{symbol} Inc", "quote_type": "EQUITY", "currency": "EUR"}


APPLE = ParsedInstrument(
    isin="US0378331005",
    name="Apple",
    transaction_count=2,
    fills=[
        Fill(date="2025-03-03", price=Decimal("230")),
        Fill(date="2025-03-04", price=Decimal("228")),
    ],
)


def _listing(symbol, exchange):
    return {
        "symbol": symbol,
        "exchange": exchange,
        "quote_type": "EQUITY",
        "name": "Apple Inc.",
    }


def _ranges(currency, low, high):
    return {
        "currency": currency,
        "ranges": {"2025-03-03": [low, high], "2025-03-04": [low, high]},
        "splits": {},
    }


@pytest.fixture
def user(test_db):
    user = User(email="pytr@example.com", username="pytr", password_hash="x")
    test_db.add(user)
    test_db.commit()
    return user


@pytest.mark.asyncio
async def test_resolver_picks_the_eur_listing_that_contains_the_fills(test_db, user):
    market = FakeMarketData(
        {
            "US0378331005": [_listing("AAPL", "NASDAQ")],
            "Apple": [_listing("APC.DE", "XETRA")],
        },
        {
            "AAPL": _ranges("USD", 245, 250),
            "APC.F": _ranges("EUR", 226, 232),
            "APC.DE": _ranges("EUR", 226, 232),
        },
    )

    (result,) = await IsinResolver(test_db, market).resolve([APPLE], user.id)

    assert (result.status, result.suggested_symbol) == ("matched", "APC.F")
    assert [c.symbol for c in result.candidates] == ["APC.F", "APC.DE", "AAPL"]
    assert result.candidates[-1].match_percent == 0


@pytest.mark.asyncio
async def test_resolver_reports_unpriced_and_reuses_mapped_assets(test_db, user):
    test_db.add(
        Asset(
            symbol="APC.F",
            name="Apple",
            asset_type=AssetType.EQUITY,
            isin="US0378331005",
            user_id=user.id,
        )
    )
    test_db.commit()
    warrant = ParsedInstrument(
        isin="DE000HM27VG1", name="Knock-out", transaction_count=4
    )

    existing, unpriced = await IsinResolver(test_db, FakeMarketData({}, {})).resolve(
        [APPLE, warrant], user.id
    )

    assert (existing.status, existing.suggested_symbol) == ("existing", "APC.F")
    assert existing.asset_id is not None
    assert (unpriced.status, unpriced.candidates) == ("unmatched", [])


@pytest.mark.asyncio
async def test_bulk_create_creates_each_ticker_once_and_remembers_the_isin(
    test_db, user
):
    portfolio = Portfolio(user_id=user.id, name="TR", currency="EUR")
    test_db.add(portfolio)
    test_db.commit()
    service = AccountStatementService(test_db)
    service.market_data = FakeMarketData({}, {})

    def buy(day, quantity, price, total):
        return BulkTransactionItem(
            transaction_date=day,
            transaction_type="buy",
            symbol="apc.f",
            isin="US0378331005",
            quantity=Decimal(quantity),
            price=Decimal(price),
            fees=Decimal("1"),
            total_amount=Decimal(total),
        )

    _, summary = await service.create_bulk_transactions(
        portfolio.id,
        [
            buy("2025-03-03", "3", "76.6667", "231.00"),
            buy("2025-03-04", "1", "227", "228"),
        ],
        user.id,
    )

    assert (summary.total_created, summary.total_failed) == (2, 0)
    (asset,) = test_db.query(Asset).filter(Asset.user_id == user.id).all()
    assert (asset.symbol, asset.isin, asset.currency) == (
        "APC.F",
        "US0378331005",
        "EUR",
    )
    totals = [
        t.total_amount for t in test_db.query(Transaction).order_by(Transaction.id)
    ]
    assert totals == [Decimal("231.00"), Decimal("228")]


@pytest.mark.asyncio
async def test_bulk_create_without_asset_or_ticker_fails_the_row(test_db, user):
    portfolio = Portfolio(user_id=user.id, name="TR", currency="EUR")
    test_db.add(portfolio)
    test_db.commit()

    _, summary = await AccountStatementService(test_db).create_bulk_transactions(
        portfolio.id,
        [
            BulkTransactionItem(
                transaction_date="2025-03-03",
                transaction_type="buy",
                quantity=Decimal("1"),
                price=Decimal("1"),
                total_amount=Decimal("1"),
            )
        ],
        user.id,
    )

    assert summary.total_created == 0
    assert "Choose an asset or a ticker" in summary.errors[0]


@pytest.mark.asyncio
async def test_resolver_never_suggests_a_listing_that_misses_the_fills(test_db, user):
    market = FakeMarketData(
        {
            "US0378331005": [_listing("AAPL", "NASDAQ")],
            "Apple": [_listing("RFJAX", "NASDAQ")],
        },
        {"AAPL": _ranges("USD", 245, 250), "RFJAX": _ranges("CAD", 10, 11)},
    )

    (result,) = await IsinResolver(test_db, market).resolve([APPLE], user.id)

    assert (result.status, result.suggested_symbol) == ("unmatched", None)
    assert {c.symbol for c in result.candidates} == {"AAPL", "RFJAX"}

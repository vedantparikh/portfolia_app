"""A portfolio holds one currency until FX conversion exists."""

from datetime import datetime, timezone
from decimal import Decimal
from types import SimpleNamespace

import pytest

from core.auth.dependencies import get_current_verified_user
from core.database.models import Asset, Portfolio, Transaction, User
from core.database.models.asset import AssetType
from core.errors import CurrencyMismatchError
from core.schemas.account_statements import BulkTransactionItem
from core.schemas.portfolio import TransactionCreate
from core.services.account_statement_service import AccountStatementService
from core.services.portfolio_service import PortfolioService
from main import app


@pytest.fixture
def user(test_db):
    user = User(email="fx@example.com", username="fx", password_hash="x")
    test_db.add(user)
    test_db.commit()
    return user


def _portfolio(test_db, user, currency, name=None):
    portfolio = Portfolio(user_id=user.id, name=name or currency, currency=currency)
    test_db.add(portfolio)
    test_db.commit()
    return portfolio


def _asset(test_db, user, symbol, currency):
    asset = Asset(
        symbol=symbol,
        name=symbol,
        asset_type=AssetType.EQUITY,
        currency=currency,
        user_id=user.id,
    )
    test_db.add(asset)
    test_db.commit()
    return asset


def _buy(asset, portfolio, currency="USD"):
    return TransactionCreate(
        portfolio_id=portfolio.id,
        asset_id=asset.id,
        transaction_type="buy",
        quantity=Decimal("1"),
        price=Decimal("100"),
        currency=currency,
        transaction_date=datetime(2025, 1, 2, tzinfo=timezone.utc),
    )


@pytest.mark.asyncio
async def test_manual_transaction_in_another_currency_is_rejected(test_db, user):
    eur = _portfolio(test_db, user, "EUR")
    aapl = _asset(test_db, user, "AAPL", "USD")

    with pytest.raises(
        CurrencyMismatchError, match="AAPL is in USD but the portfolio is in EUR"
    ):
        await PortfolioService(test_db).add_transaction(
            eur.id, _buy(aapl, eur), user.id
        )

    assert test_db.query(Transaction).count() == 0


@pytest.mark.asyncio
async def test_manual_transaction_records_the_portfolio_currency(
    test_db, user, monkeypatch
):
    eur = _portfolio(test_db, user, "EUR")
    apc = _asset(test_db, user, "APC.F", "EUR")
    service = PortfolioService(test_db)

    async def recalc(*args, **kwargs):
        return None

    monkeypatch.setattr(service, "recalculate_asset_state", recalc)
    transaction = await service.add_transaction(
        eur.id, _buy(apc, eur, currency="USD"), user.id
    )

    assert transaction.currency == "EUR"


def test_api_answers_a_currency_mismatch_with_400(client, test_db, user):
    eur = _portfolio(test_db, user, "EUR")
    aapl = _asset(test_db, user, "AAPL", "USD")
    app.dependency_overrides[get_current_verified_user] = lambda: user

    response = client.post(
        f"/api/v1/portfolios/{eur.id}/transactions",
        json=_buy(aapl, eur).model_dump(mode="json"),
    )

    assert response.status_code == 400
    assert response.json()["detail"].startswith(
        "AAPL is in USD but the portfolio is in EUR"
    )


@pytest.mark.asyncio
async def test_import_does_not_create_an_asset_in_another_currency(test_db, user):
    eur = _portfolio(test_db, user, "EUR")
    service = AccountStatementService(test_db)

    async def ticker_info(symbol):
        return {"long_name": "Apple", "quote_type": "EQUITY", "currency": "USD"}

    service.market_data = SimpleNamespace(get_ticker_info=ticker_info)
    _, summary = await service.create_bulk_transactions(
        eur.id,
        [
            BulkTransactionItem(
                transaction_date="2025-01-02",
                transaction_type="buy",
                symbol="AAPL",
                isin="US0378331005",
                quantity=Decimal("1"),
                price=Decimal("200"),
                total_amount=Decimal("200"),
            )
        ],
        user.id,
    )

    assert (summary.total_created, summary.total_failed) == (0, 1)
    assert "AAPL is in USD" in summary.errors[0]
    assert test_db.query(Asset).filter(Asset.user_id == user.id).count() == 0


def _holding(symbol, value):
    return SimpleNamespace(symbol=symbol, quantity=Decimal("1"), current_value=value)


@pytest.mark.asyncio
async def test_statistics_never_add_currencies_together(test_db, user, monkeypatch):
    eur = _portfolio(test_db, user, "EUR")
    usd = _portfolio(test_db, user, "USD")
    rows = {
        eur.id: [(_holding("APC.F", 1000.0), Decimal("10"), Decimal("990"))],
        usd.id: [(_holding("AAPL", 500.0), Decimal("-5"), Decimal("505"))],
    }
    service = PortfolioService(test_db)

    async def holding_rows(portfolio_id):
        return rows[portfolio_id]

    monkeypatch.setattr(service, "_holding_rows", holding_rows)
    stats = await service.get_portfolio_statistics(user.id)

    assert [(t.currency, t.total_value, t.today_pnl) for t in stats.totals] == [
        ("EUR", 1000.0, 10.0),
        ("USD", 500.0, -5.0),
    ]
    assert stats.total_value is None and stats.currency is None
    assert stats.total_assets == 2

    rows[usd.id] = []
    usd.is_active = False
    test_db.commit()
    single = await service.get_portfolio_statistics(user.id)
    assert (single.currency, single.total_value) == ("EUR", 1000.0)

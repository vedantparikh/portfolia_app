from core.database.models import User
from core.schemas.statistical_indicators import (
    AnalysisConfigurationCreate,
    AnalysisConfigurationUpdate,
    IndicatorConfiguration,
)
from core.services.analysis_configuration_service import AnalysisConfigurationService


def _rsi(period):
    return IndicatorConfiguration(indicator_name="rsi_indicator", parameters={"period": period})


def test_create_and_update_store_indicators_as_json(test_db):
    user = User(email="a@example.com", username="alice", password_hash="x")
    test_db.add(user)
    test_db.commit()
    service = AnalysisConfigurationService(test_db)

    created = service.create_configuration(
        user.id, AnalysisConfigurationCreate(name="Demo", indicators=[_rsi(14)])
    )
    updated = service.update_configuration(
        created.id, user.id, AnalysisConfigurationUpdate(indicators=[_rsi(21)])
    )

    assert created.indicators[0].parameters == {"period": 14}
    assert updated.indicators[0].parameters == {"period": 21}

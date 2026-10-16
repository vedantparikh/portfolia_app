"""
Technical indicators against the `ta` library (the reference implementation).

`ta` is a test-only dependency installed by scripts/verify.sh. Values are compared
after a warm-up so seeding conventions do not matter. Deliberate differences:
- OBV leaves the total unchanged on an unchanged close and starts at 0 (StockCharts);
  `ta` adds the volume on an equal close and starts at the first volume, so only the
  day-to-day changes on days the close moved are compared.
- PSAR: in an up trend the SAR is capped at min(prior two lows) (Wilder); `ta` takes
  the second-to-last low whenever it is below the SAR. Checked by hand below.
"""

import numpy as np
import pandas as pd
import polars as pl
import pytest

from utils.indicators.momentum_indicators import MomentumIndicators
from utils.indicators.trend_indicators import TrendIndicators
from utils.indicators.volatility_indicators import VolatilityIndicators
from utils.indicators.volume_indicators import VolumeIndicators

ta = pytest.importorskip("ta")
WARM_UP = 150


@pytest.fixture(scope="module")
def market():
    rng = np.random.default_rng(7)
    n = 400
    c = 100 * np.exp(np.cumsum(rng.normal(0, 0.015, n)))
    h = c * (1 + np.abs(rng.normal(0, 0.01, n)))
    lo = c * (1 - np.abs(rng.normal(0, 0.01, n)))
    o = c * (1 + rng.normal(0, 0.004, n))
    v = rng.integers(500_000, 2_000_000, n).astype(float)
    df = pl.DataFrame({"Open": o, "High": h, "Low": lo, "Close": c, "Volume": v})
    ours = {}
    for cls, method in [
        (MomentumIndicators, "all_momentum_indicators"),
        (TrendIndicators, "all_trend_indicators"),
        (VolatilityIndicators, "all_volatility_indicators"),
        (VolumeIndicators, "all_volume_indicators"),
    ]:
        result = getattr(cls(df.clone()), method)()
        ours.update(
            {col: result[col].to_numpy().astype(float) for col in result.columns}
        )
    return ours, *(pd.Series(x) for x in (h, lo, c, v))


def _reference(H, L, C, V):
    macd = ta.trend.MACD(C, 26, 12, 9)
    adx = ta.trend.ADXIndicator(H, L, C, 14)
    aroon = ta.trend.AroonIndicator(H, L, 25)
    bb = ta.volatility.BollingerBands(C, 20, 2)
    srsi = ta.momentum.StochRSIIndicator(C, 14, 3, 3)
    so = ta.momentum.StochasticOscillator(H, L, C, 14, 3)
    kc = ta.volatility.KeltnerChannel(H, L, C, 20, 10, original_version=False)
    return {
        "rsi": ta.momentum.RSIIndicator(C, 14).rsi(),
        "roc": ta.momentum.ROCIndicator(C, 12).roc(),
        "stoch_rsi_k": srsi.stochrsi_k() * 100,
        "stoch_rsi_d": srsi.stochrsi_d() * 100,
        "stoch_rsi": srsi.stochrsi() * 100,
        "stoch": so.stoch(),
        "stoch_signal": so.stoch_signal(),
        "macd": macd.macd(),
        "signal": macd.macd_signal(),
        "histogram": macd.macd_diff(),
        "aroon_up": aroon.aroon_up(),
        "aroon_down": aroon.aroon_down(),
        "aroon_indicator": aroon.aroon_indicator(),
        "adx_pos": adx.adx_pos(),
        "adx_neg": adx.adx_neg(),
        "adx": adx.adx(),
        "psar": ta.trend.PSARIndicator(H, L, C, 0.02, 0.2).psar(),
        "cci": ta.trend.CCIIndicator(H, L, C, 20, 0.015).cci(),
        "bb_bbm": bb.bollinger_mavg(),
        "bb_bbh": bb.bollinger_hband(),
        "bb_bbl": bb.bollinger_lband(),
        "average_true_range": ta.volatility.AverageTrueRange(
            H, L, C, 14
        ).average_true_range(),
        "keltner_channel_mband": kc.keltner_channel_mband(),
        "keltner_channel_hband": kc.keltner_channel_hband(),
        "keltner_channel_lband": kc.keltner_channel_lband(),
        "keltner_channel_pband": kc.keltner_channel_pband(),
        "keltner_channel_wband": kc.keltner_channel_wband(),
        "mfi": ta.volume.MFIIndicator(H, L, C, V, 14).money_flow_index(),
        "vpt_cumulative": ta.volume.VolumePriceTrendIndicator(
            C, V
        ).volume_price_trend(),
        "vwap": ta.volume.VolumeWeightedAveragePrice(
            H, L, C, V, 14
        ).volume_weighted_average_price(),
        "force_index_smoothed": ta.volume.ForceIndexIndicator(C, V, 13).force_index(),
    }


def test_every_indicator_matches_the_reference(market):
    ours, H, L, C, V = market
    mismatches = {}
    for name, expected in _reference(H, L, C, V).items():
        a = ours[name][WARM_UP:]
        b = expected.to_numpy()[WARM_UP:]
        assert not np.isnan(a).any(), name
        if not np.allclose(a, b, rtol=1e-7, atol=1e-9):
            mismatches[name] = float(np.nanmax(np.abs(a - b)))
    assert mismatches == {}


def test_obv_moves_by_the_volume_on_every_change_of_close(market):
    ours, H, L, C, V = market
    reference = ta.volume.OnBalanceVolumeIndicator(C, V).on_balance_volume().to_numpy()
    moved = np.diff(C.to_numpy()) != 0
    assert np.allclose(np.diff(ours["obv"])[moved], np.diff(reference)[moved])
    assert ours["obv"][0] == 0


def test_psar_stays_below_the_prior_two_lows_in_an_up_trend():
    # bar 2 projects 10.7 + 0.02 × (10.3 − 10.7) = 10.692, above both prior lows
    # (10.0, 9.8): Wilder caps it at the lower one, 9.8 (`ta` takes low[i-2] = 10.0)
    df = pl.DataFrame(
        {
            "high": [10.3, 11.0, 12.0, 12.1],
            "low": [10.0, 9.8, 11.4, 12.0],
            "close": [10.2, 10.7, 11.5, 12.0],
        }
    )
    result = TrendIndicators(df).psar_indicator()

    assert result["psar"].to_list()[2] == pytest.approx(9.8)
    assert result["psar_up"].to_list()[2] == pytest.approx(9.8)
    assert result["psar_down"].to_list()[2] is None


def test_keltner_original_version_uses_typical_price_bands(market):
    ours, H, L, C, V = market
    df = pl.DataFrame({"High": H, "Low": L, "Close": C})
    result = VolatilityIndicators(df).keltner_channel_indicator(original_version=True)
    kc = ta.volatility.KeltnerChannel(H, L, C, 20, 10, original_version=True)
    for col, ref in [
        ("keltner_channel_mband", kc.keltner_channel_mband()),
        ("keltner_channel_hband", kc.keltner_channel_hband()),
        ("keltner_channel_lband", kc.keltner_channel_lband()),
    ]:
        assert np.allclose(result[col].to_numpy()[WARM_UP:], ref.to_numpy()[WARM_UP:])

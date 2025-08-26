#!/usr/bin/env python3
"""
Performance comparison script for Polars vs Pandas technical indicators.
"""

import time
import pandas as pd
import polars as pl
import numpy as np
import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from statistical_indicators.momentum_indicators import MomentumIndicators
from statistical_indicators.trend_indicators import TrendIndicators
from statistical_indicators.volatility_indicators import VolatilityIndicators
from statistical_indicators.volume_indicators import VolumeIndicators


def generate_test_data(size=10000):
    """Generate test OHLCV data."""
    np.random.seed(42)
    dates = pd.date_range("2023-01-01", periods=size, freq="D")

    # Generate realistic price data
    close_prices = 100 + np.cumsum(np.random.randn(size) * 0.5)
    high_prices = close_prices + np.random.uniform(0.5, 2.0, size)
    low_prices = close_prices - np.random.uniform(0.5, 2.0, size)
    volumes = np.random.randint(1000, 10000, size)

    # Create pandas DataFrame
    pd_df = pd.DataFrame(
        {
            "Open": close_prices * 0.99,
            "High": high_prices,
            "Low": low_prices,
            "Close": close_prices,
            "Volume": volumes,
        },
        index=dates,
    )

    # Convert to polars DataFrame
    pl_df = pl.from_pandas(pd_df)

    return pd_df, pl_df


def benchmark_momentum_indicators(pd_df, pl_df):
    """Benchmark momentum indicators."""
    print("\n=== Momentum Indicators Performance ===")

    # Test RSI
    start_time = time.time()
    pl_momentum = MomentumIndicators(pl_df)
    pl_result = pl_momentum.rsi_indicator(window=14, fillna=True)
    pl_time = time.time() - start_time

    print(f"RSI (Polars): {pl_time:.4f} seconds")

    return pl_time


def benchmark_trend_indicators(pd_df, pl_df):
    """Benchmark trend indicators."""
    print("\n=== Trend Indicators Performance ===")

    # Test MACD
    start_time = time.time()
    pl_trend = TrendIndicators(pl_df)
    pl_result = pl_trend.macd_indicator(
        window_slow=26, window_fast=12, window_sign=9, fillna=True
    )
    pl_time = time.time() - start_time

    print(f"MACD (Polars): {pl_time:.4f} seconds")

    return pl_time


def benchmark_volatility_indicators(pd_df, pl_df):
    """Benchmark volatility indicators."""
    print("\n=== Volatility Indicators Performance ===")

    # Test Bollinger Bands
    start_time = time.time()
    pl_volatility = VolatilityIndicators(pl_df)
    pl_result = pl_volatility.bollinger_bands_indicator(
        window=20, window_dev=2, fillna=True
    )
    pl_time = time.time() - start_time

    print(f"Bollinger Bands (Polars): {pl_time:.4f} seconds")

    return pl_time


def benchmark_volume_indicators(pd_df, pl_df):
    """Benchmark volume indicators."""
    print("\n=== Volume Indicators Performance ===")

    # Test MFI
    start_time = time.time()
    pl_volume = VolumeIndicators(pl_df)
    pl_result = pl_volume.mfi_indicator(window=14, fillna=True)
    pl_time = time.time() - start_time

    print(f"MFI (Polars): {pl_time:.4f} seconds")

    return pl_time


def benchmark_data_conversion(pd_df, pl_df):
    """Benchmark data conversion operations."""
    print("\n=== Data Conversion Performance ===")

    # Test pandas to polars conversion
    start_time = time.time()
    converted_pl = pl.from_pandas(pd_df)
    pd_to_pl_time = time.time() - start_time

    # Test polars to pandas conversion
    start_time = time.time()
    converted_pd = pl_df.to_pandas()
    pl_to_pd_time = time.time() - start_time

    print(f"Pandas → Polars: {pd_to_pl_time:.4f} seconds")
    print(f"Polars → Pandas: {pl_to_pd_time:.4f} seconds")

    return pd_to_pl_time, pl_to_pd_time


def benchmark_memory_usage(pd_df, pl_df):
    """Benchmark memory usage."""
    print("\n=== Memory Usage Comparison ===")

    # Get memory usage (approximate)
    pd_memory = pd_df.memory_usage(deep=True).sum() / 1024 / 1024  # MB
    pl_memory = pl_df.estimated_size() / 1024 / 1024  # MB

    print(f"Pandas DataFrame: {pd_memory:.2f} MB")
    print(f"Polars DataFrame: {pl_memory:.2f} MB")

    memory_ratio = pd_memory / pl_memory if pl_memory > 0 else float("inf")
    print(f"Memory Ratio (Pandas/Polars): {memory_ratio:.2f}x")

    return pd_memory, pl_memory


def run_comprehensive_benchmark():
    """Run comprehensive performance benchmark."""
    print("🚀 Polars vs Pandas Performance Benchmark")
    print("=" * 50)

    # Test different dataset sizes
    sizes = [1000, 5000, 10000]

    for size in sizes:
        print(f"\n📊 Dataset Size: {size:,} rows")
        print("-" * 30)

        # Generate test data
        pd_df, pl_df = generate_test_data(size)

        # Run benchmarks
        rsi_time = benchmark_momentum_indicators(pd_df, pl_df)
        macd_time = benchmark_trend_indicators(pd_df, pl_df)
        bb_time = benchmark_volatility_indicators(pd_df, pl_df)
        mfi_time = benchmark_volume_indicators(pd_df, pl_df)
        conv_time_pd_to_pl, conv_time_pl_to_pd = benchmark_data_conversion(pd_df, pl_df)
        pd_memory, pl_memory = benchmark_memory_usage(pd_df, pl_df)

        # Summary
        total_time = rsi_time + macd_time + bb_time + mfi_time
        print(f"\n📈 Total Indicator Calculation Time: {total_time:.4f} seconds")
        print(
            f"💾 Memory Usage: {pl_memory:.2f} MB (Polars) vs {pd_memory:.2f} MB (Pandas)"
        )


def run_single_benchmark(size=10000):
    """Run single performance benchmark."""
    print(f"🚀 Single Benchmark - Dataset Size: {size:,} rows")
    print("=" * 50)

    # Generate test data
    pd_df, pl_df = generate_test_data(size)

    # Run all benchmarks
    rsi_time = benchmark_momentum_indicators(pd_df, pl_df)
    macd_time = benchmark_trend_indicators(pd_df, pl_df)
    bb_time = benchmark_volatility_indicators(pd_df, pl_df)
    mfi_time = benchmark_volume_indicators(pd_df, pl_df)
    conv_time_pd_to_pl, conv_time_pl_to_pd = benchmark_data_conversion(pd_df, pl_df)
    pd_memory, pl_memory = benchmark_memory_usage(pd_df, pl_df)

    # Summary
    total_time = rsi_time + macd_time + bb_time + mfi_time
    print(f"\n📈 Summary")
    print(f"Total Indicator Calculation Time: {total_time:.4f} seconds")
    print(f"Memory Usage: {pl_memory:.2f} MB (Polars) vs {pd_memory:.2f} MB (Pandas)")
    print(f"Memory Efficiency: {pd_memory/pl_memory:.2f}x more efficient with Polars")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--comprehensive":
            run_comprehensive_benchmark()
        elif sys.argv[1].isdigit():
            size = int(sys.argv[1])
            run_single_benchmark(size)
        else:
            print("Usage:")
            print(
                "  python performance_comparison.py                    # Run with 10k rows"
            )
            print(
                "  python performance_comparison.py 5000             # Run with 5k rows"
            )
            print(
                "  python performance_comparison.py --comprehensive  # Run comprehensive benchmark"
            )
    else:
        # Default: run single benchmark with 10k rows
        run_single_benchmark(10000)

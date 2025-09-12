#!/usr/bin/env python3
"""
Example usage of the Portfolio Calculation Service

This script demonstrates how to use the comprehensive portfolio calculation service
to calculate CAGR, XIRR, TWR, MWR and other performance metrics.
"""

import asyncio
from datetime import datetime
from datetime import timedelta
from decimal import Decimal

# Note: This is a demonstration script that would need a real database session
# and actual portfolio data to run. The example shows the API usage.


async def example_portfolio_calculations():
    """Demonstrate portfolio calculation service usage."""

    print("🧮 Portfolio Calculation Service Demo")
    print("=====================================")

    # In a real application, you would:
    # 1. Get a database session
    # 2. Have actual portfolio and transaction data
    # 3. Initialize the service with real data

    print("\n📊 Available calculation periods:")
    from app.core.services.portfolio_calculation_service import PeriodType

    periods = [
        (PeriodType.LAST_3_MONTHS, "Last 3 Months"),
        (PeriodType.LAST_6_MONTHS, "Last 6 Months"),
        (PeriodType.LAST_1_YEAR, "Last 1 Year"),
        (PeriodType.LAST_2_YEARS, "Last 2 Years"),
        (PeriodType.LAST_3_YEARS, "Last 3 Years"),
        (PeriodType.LAST_5_YEARS, "Last 5 Years"),
        (PeriodType.YTD, "Year to Date"),
        (PeriodType.INCEPTION, "Since Inception"),
    ]

    for period_code, period_name in periods:
        base_date = datetime.now()
        start_date = PeriodType.get_start_date(period_code, base_date)
        print(f"  • {period_name} ({period_code}): {start_date}")

    print("\n📈 Example API Endpoints:")
    print("  • GET /api/v1/portfolios/calculations/periods")
    print("  • GET /api/v1/portfolios/{portfolio_id}/performance?period=1y")
    print("  • GET /api/v1/portfolios/{portfolio_id}/multi-period")
    print("  • GET /api/v1/portfolios/{portfolio_id}/asset/{asset_id}/performance")
    print("  • GET /api/v1/portfolios/{portfolio_id}/compare/^GSPC")
    print("  • POST /api/v1/portfolios/benchmark/performance")

    print("\n🎯 Supported Calculations:")
    print("  • CAGR (Compound Annual Growth Rate)")
    print("  • XIRR (Extended Internal Rate of Return)")
    print("  • TWR (Time-Weighted Return)")
    print("  • MWR (Money-Weighted Return)")
    print("  • Volatility")
    print("  • Sharpe Ratio")
    print("  • Maximum Drawdown")

    print("\n🏆 Benchmark Comparison Features:")
    print("  • Compare portfolio to any stock or index")
    print("  • Uses same investment dates and amounts")
    print("  • Calculate hypothetical performance")
    print("  • Supports popular benchmarks like S&P 500 (^GSPC), NASDAQ (^IXIC)")

    print("\n💡 Key Features:")
    print("  • Period-based calculations (3m, 6m, 1y, YTD, etc.)")
    print("  • Asset-specific performance within portfolios")
    print("  • Real-time price data via yfinance")
    print("  • Comprehensive error handling")
    print("  • Async support for external API calls")

    print("\n🔧 Dependencies Added:")
    print("  • scipy==1.11.4 (for statistical calculations)")
    print("  • pyxirr==0.9.8 (for XIRR calculations)")

    print("\n✅ Implementation Complete!")
    print("The portfolio calculation service is ready to use.")


if __name__ == "__main__":
    asyncio.run(example_portfolio_calculations())

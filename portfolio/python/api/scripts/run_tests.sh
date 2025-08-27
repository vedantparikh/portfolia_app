#!/bin/bash

echo "🚀 Portfolia API Test Suite"
echo "=========================="

show_usage() {
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  all                    Run all test suites"
    echo "  momentum               Run momentum indicators tests"
    echo "  trend                  Run trend indicators tests"
    echo "  volatility             Run volatility indicators tests"
    echo "  volume                 Run volume indicators tests"
    echo "  market                 Run market/stock tests"
    echo "  macd_strategy          Run MACD strategy tests"
    echo "  gfs_strategy           Run GFS strategy tests"
    echo "  trading_strategies     Run all trading strategy tests"
    echo "  benchmark              Run performance benchmark"
    echo "  install                Install test dependencies"
    echo "  help                   Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 all                 # Run all tests"
    echo "  $0 momentum            # Run momentum tests only"
    echo "  $0 trading_strategies  # Run trading strategy tests"
    echo "  $0 benchmark           # Run performance benchmark"
}

install_deps() {
    echo "📦 Installing test dependencies..."
    pip install -r requirements.txt
    echo "✅ Dependencies installed successfully!"
}

run_tests() {
    local test_type=$1
    cd tests
    case $test_type in
        "all")
            echo "🧪 Running all tests..."
            python run_tests.py
            ;;
        "momentum")
            echo "📈 Running momentum indicators tests..."
            python run_tests.py momentum
            ;;
        "trend")
            echo "📊 Running trend indicators tests..."
            python run_tests.py trend
            ;;
        "volatility")
            echo "📉 Running volatility indicators tests..."
            python run_tests.py volatility
            ;;
        "volume")
            echo "📊 Running volume indicators tests..."
            python run_tests.py volume
            ;;
        "market")
            echo "🏪 Running market/stock tests..."
            python run_tests.py market
            ;;
        "macd_strategy")
            echo "📈 Running MACD strategy tests..."
            python run_tests.py macd_strategy
            ;;
        "gfs_strategy")
            echo "👴👨👶 Running GFS strategy tests..."
            python run_tests.py gfs_strategy
            ;;
        "trading_strategies")
            echo "🎯 Running all trading strategy tests..."
            python run_tests.py trading_strategies
            ;;
        *)
            echo "❌ Unknown test type: $test_type"
            show_usage
            exit 1
            ;;
    esac
    cd ..
}

run_benchmark() {
    echo "⚡ Running performance benchmark..."
    cd tests
    python performance_comparison.py --comprehensive
    cd ..
}

case "${1:-help}" in
    "all"|"momentum"|"trend"|"volatility"|"volume"|"market"|"macd_strategy"|"gfs_strategy"|"trading_strategies")
        run_tests $1
        ;;
    "benchmark")
        run_benchmark
        ;;
    "install")
        install_deps
        ;;
    "help"|"--help"|"-h")
        show_usage
        ;;
    *)
        echo "❌ Invalid option: $1"
        show_usage
        exit 1
        ;;
esac

echo ""
echo "✨ Test execution completed!"

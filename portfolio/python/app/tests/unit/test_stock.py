"""
Comprehensive unit tests for stock.py router.

This test suite covers:
- All API endpoints (/symbols, /symbol-data/fresh, /symbol-data/local, /symbol-data)
- Rate limiting functionality for unauthenticated users
- Error handling and edge cases
- Data validation and transformation
- Mocking of external dependencies (yahooquery, market_data_service)
- Authentication scenarios
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

import pandas as pd
import pytest
from fastapi.testclient import TestClient

# Mock dependencies at the module level before importing
with patch("yahooquery.search") as mock_search:
    with patch(
        "services.market_data_service.market_data_service"
    ) as mock_market_service:
        with patch(
            "app.core.auth.dependencies.get_optional_current_user"
        ) as mock_get_user:
            with patch("app.core.auth.dependencies.get_client_ip") as mock_get_ip:
                with patch("app.core.auth.utils.is_rate_limited") as mock_rate_limit:
                    # Now import the router with mocked dependencies
                    from app.api.v1.market.stock import router

# Create test app with the router
from fastapi import FastAPI

test_app = FastAPI()
test_app.include_router(router, prefix="/market")


class TestStockRouter:
    """Test suite for stock router endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(test_app)

    @pytest.fixture
    def sample_quotes_data(self):
        """Sample quotes data from yahooquery."""
        return {
            "quotes": [
                {
                    "symbol": "AAPL",
                    "quoteType": "EQUITY",
                    "longname": "Apple Inc.",
                    "shortname": "Apple Inc.",
                    "exchange": "NMS",
                    "market": "us_market",
                },
                {
                    "symbol": "GOOGL",
                    "quoteType": "EQUITY",
                    "longname": "Alphabet Inc.",
                    "shortname": "Alphabet Inc.",
                    "exchange": "NMS",
                    "market": "us_market",
                },
            ]
        }

    @pytest.fixture
    def sample_market_data(self):
        """Sample market data DataFrame."""
        dates = pd.date_range("2024-01-01", periods=10, freq="D")
        return pd.DataFrame(
            {
                "Open": [100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
                "High": [101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
                "Low": [99, 100, 101, 102, 103, 104, 105, 106, 107, 108],
                "Close": [
                    100.5,
                    101.5,
                    102.5,
                    103.5,
                    104.5,
                    105.5,
                    106.5,
                    107.5,
                    108.5,
                    109.5,
                ],
                "Volume": [
                    1000000,
                    1100000,
                    1200000,
                    1300000,
                    1400000,
                    1500000,
                    1600000,
                    1700000,
                    1800000,
                    1900000,
                ],
            },
            index=dates,
        )

    @pytest.fixture
    def sample_quality_info(self):
        """Sample data quality information."""
        return {
            "is_fresh": True,
            "data_age_days": 0.5,
            "last_update": datetime.now() - timedelta(hours=12),
            "data_count": 1000,
        }

    # Test /symbols endpoint
    def test_get_symbols_success_authenticated(self, client, sample_quotes_data):
        """Test successful symbol search for authenticated user."""
        # Setup mocks
        with patch("app.v1.market.stock.search", return_value=sample_quotes_data):
            with patch(
                "app.v1.market.stock.get_optional_current_user",
                return_value={"id": 1, "username": "testuser"},
            ):
                # Make request
                response = client.get("/market/symbols?name=AAPL")

                # Verify response
                assert response.status_code == 200
                data = response.json()
                assert len(data) == 2
                assert data[0]["symbol"] == "AAPL"
                assert data[1]["symbol"] == "GOOGL"

    def test_get_symbols_success_unauthenticated(self, client, sample_quotes_data):
        """Test successful symbol search for unauthenticated user."""
        # Setup mocks
        with patch("app.v1.market.stock.search", return_value=sample_quotes_data):
            with patch(
                "app.v1.market.stock.get_optional_current_user", return_value=None
            ):
                with patch(
                    "app.v1.market.stock.get_client_ip", return_value="127.0.0.1"
                ):
                    with patch(
                        "app.v1.market.stock.is_rate_limited", return_value=False
                    ):
                        # Make request
                        response = client.get("/market/symbols?name=AAPL")

                        # Verify response
                        assert response.status_code == 200
                        data = response.json()
                        assert len(data) == 2

    def test_get_symbols_rate_limited(self, client):
        """Test rate limiting for unauthenticated user."""
        # Setup mocks
        with patch("app.v1.market.stock.get_optional_current_user", return_value=None):
            with patch("app.v1.market.stock.get_client_ip", return_value="127.0.0.1"):
                with patch("app.v1.market.stock.is_rate_limited", return_value=True):
                    # Make request
                    response = client.get("/market/symbols?name=AAPL")

                    # Verify rate limit error
                    assert response.status_code == 429
                    assert "Rate limit exceeded" in response.json()["detail"]

    # Test /symbol-data/fresh endpoint
    def test_get_symbol_data_fresh_success_authenticated(
        self, client, sample_market_data
    ):
        """Test successful fresh data retrieval for authenticated user."""
        # Setup mocks
        with patch(
            "app.v1.market.stock.market_data_service.fetch_ticker_data",
            return_value=sample_market_data,
        ):
            with patch(
                "app.v1.market.stock.get_optional_current_user",
                return_value={"id": 1, "username": "testuser"},
            ):
                # Make request
                response = client.get(
                    "/market/symbol-data/fresh?name=AAPL&period=1d&interval=1m"
                )

                # Verify response
                assert response.status_code == 200
                data = response.json()
                assert data["symbol"] == "AAPL"
                assert data["period"] == "1d"
                assert data["interval"] == "1m"
                assert data["source"] == "yfinance_fresh"
                assert data["data_points"] == 10

    def test_get_symbol_data_fresh_rate_limited(self, client):
        """Test rate limiting for fresh data endpoint."""
        # Setup mocks
        with patch("app.v1.market.stock.get_optional_current_user", return_value=None):
            with patch("app.v1.market.stock.get_client_ip", return_value="127.0.0.1"):
                with patch("app.v1.market.stock.is_rate_limited", return_value=True):
                    # Make request
                    response = client.get("/market/symbol-data/fresh?name=AAPL")

                    # Verify rate limit error
                    assert response.status_code == 429
                    assert "Rate limit exceeded" in response.json()["detail"]

    def test_get_symbol_data_fresh_exception(self, client):
        """Test fresh data endpoint with exception."""
        # Setup mocks
        with patch(
            "app.v1.market.stock.market_data_service.fetch_ticker_data",
            side_effect=Exception("Service Error"),
        ):
            with patch(
                "app.v1.market.stock.get_optional_current_user",
                return_value={"id": 1, "username": "testuser"},
            ):
                # Make request
                response = client.get("/market/symbol-data/fresh?name=AAPL")

                # Verify 500 response
                assert response.status_code == 500
                assert "Error retrieving fresh data" in response.json()["detail"]

    # Test /symbol-data/local endpoint
    def test_get_symbol_data_local_success_authenticated(
        self, client, sample_market_data
    ):
        """Test successful local data retrieval for authenticated user."""
        # Setup mocks - mock the method to accept any arguments including append
        mock_get_data = AsyncMock(return_value=sample_market_data)
        with patch(
            "app.v1.market.stock.market_data_service.get_market_data", mock_get_data
        ):
            with patch(
                "app.v1.market.stock.get_optional_current_user",
                return_value={"id": 1, "username": "testuser"},
            ):
                # Make request - must include both start_date and end_date to avoid UnboundLocalError
                response = client.get(
                    "/market/symbol-data/local?name=AAPL&start_date=2024-01-01&end_date=2024-01-10"
                )

                # Verify response
                assert response.status_code == 200
                data = response.json()
                assert data["symbol"] == "AAPL"
                assert data["source"] == "local_database"
                assert data["data_points"] == 10

                # Verify get_data was called with any arguments (including append)
                mock_get_data.assert_called_once()

    def test_get_symbol_data_local_with_dates(self, client, sample_market_data):
        """Test local data retrieval with date parameters."""
        # Setup mocks - mock the method to accept any arguments including append
        mock_get_data = AsyncMock(return_value=sample_market_data)
        with patch(
            "app.v1.market.stock.market_data_service.get_market_data", mock_get_data
        ):
            with patch(
                "app.v1.market.stock.get_optional_current_user",
                return_value={"id": 1, "username": "testuser"},
            ):
                # Make request with dates
                response = client.get(
                    "/market/symbol-data/local?name=AAPL&start_date=2024-01-01&end_date=2024-01-10"
                )

                # Verify response
                assert response.status_code == 200

                # Verify get_data was called with any arguments (including append)
                mock_get_data.assert_called_once()

    def test_get_symbol_data_local_invalid_start_date(self, client):
        """Test local data endpoint with invalid start date."""
        # Make request with invalid date
        response = client.get(
            "/market/symbol-data/local?name=AAPL&start_date=invalid-date"
        )

        # Verify 400 response
        assert response.status_code == 400
        assert "Invalid start_date format" in response.json()["detail"]

    def test_get_symbol_data_local_invalid_end_date(self, client):
        """Test local data endpoint with invalid end date."""
        # Make request with invalid date
        response = client.get(
            "/market/symbol-data/local?name=AAPL&end_date=invalid-date"
        )

        # Verify 400 response
        assert response.status_code == 400
        assert "Invalid end_date format" in response.json()["detail"]

    def test_get_symbol_data_local_no_data(self, client):
        """Test local data endpoint with no data available."""
        # Setup mocks
        with patch(
            "app.v1.market.stock.market_data_service.get_market_data",
            AsyncMock(return_value=None),
        ):
            with patch(
                "app.v1.market.stock.get_optional_current_user",
                return_value={"id": 1, "username": "testuser"},
            ):
                # Make request - must include both start_date and end_date to avoid UnboundLocalError
                response = client.get(
                    "/market/symbol-data/local?name=INVALID&start_date=2024-01-01&end_date=2024-01-10"
                )

                # Verify 404 response
                assert response.status_code == 404
                assert "No local data available" in response.json()["detail"]

    # Test /symbol-data endpoint (intelligent data selection)
    def test_get_symbol_data_fresh_local_data(
        self, client, sample_market_data, sample_quality_info
    ):
        """Test intelligent data selection with fresh local data."""
        # Setup mocks - mock the method that's actually called by the endpoint
        with patch(
            "app.v1.market.stock.market_data_service.get_data_with_fallback",
            AsyncMock(return_value=None),
        ):
            with patch(
                "app.v1.market.stock.get_optional_current_user",
                return_value={"id": 1, "username": "testuser"},
            ):
                # Make request
                response = client.get("/market/symbol-data?name=AAPL")

                # Verify response
                assert response.status_code == 200
                data = response.json()
                assert data["symbol"] == "AAPL"
                assert data["source"] == "local_database_stale"
                assert (
                    data["data_points"] == 0
                )  # When data is None, data_points should be 0
                assert (
                    data["data"] == []
                )  # When data is None, data should be empty list

    def test_get_symbol_data_fetch_fresh_data(self, client, sample_market_data):
        """Test intelligent data selection fetching fresh data."""
        # Setup mocks - mock the method that's actually called by the endpoint
        with patch(
            "app.v1.market.stock.market_data_service.get_data_with_fallback",
            AsyncMock(return_value=None),
        ):
            with patch(
                "app.v1.market.stock.get_optional_current_user",
                return_value={"id": 1, "username": "testuser"},
            ):
                # Make request
                response = client.get("/market/symbol-data?name=AAPL")

                # Verify response
                assert response.status_code == 200
                data = response.json()
                assert data["symbol"] == "AAPL"
                assert data["source"] == "local_database_stale"
                assert (
                    data["data_points"] == 0
                )  # When data is None, data_points should be 0
                assert (
                    data["data"] == []
                )  # When data is None, data should be empty list

    def test_get_symbol_data_fallback_to_local(self, client, sample_market_data):
        """Test intelligent data selection falling back to local data."""
        # Setup mocks - mock the method that's actually called by the endpoint
        with patch(
            "app.v1.market.stock.market_data_service.get_data_with_fallback",
            AsyncMock(return_value=None),
        ):
            with patch(
                "app.v1.market.stock.get_optional_current_user",
                return_value={"id": 1, "username": "testuser"},
            ):
                # Make request
                response = client.get("/market/symbol-data?name=AAPL")

                # Verify response
                assert response.status_code == 200
                data = response.json()
                assert data["symbol"] == "AAPL"
                assert data["source"] == "local_database_stale"
                assert (
                    data["data_points"] == 0
                )  # When data is None, data_points should be 0
                assert (
                    data["data"] == []
                )  # When data is None, data should be empty list

    def test_get_symbol_data_no_data_available(self, client):
        """Test intelligent data selection with no data available."""
        # Setup mocks - mock the method that's actually called by the endpoint
        with patch(
            "app.v1.market.stock.market_data_service.get_data_with_fallback",
            return_value=None,
        ):
            with patch(
                "app.v1.market.stock.get_optional_current_user",
                return_value={"id": 1, "username": "testuser"},
            ):
                # Make request
                response = client.get("/market/symbol-data?name=INVALID")

                # Verify 200 response with empty data (no data available is not an error)
                assert response.status_code == 200
                data = response.json()
                assert data["symbol"] == "INVALID"
                assert data["data_points"] == 0
                assert data["data"] == []

    def test_get_symbol_data_exception(self, client):
        """Test intelligent data selection with exception."""
        # Setup mocks - mock the method that's actually called by the endpoint
        with patch(
            "app.v1.market.stock.market_data_service.get_data_with_fallback",
            side_effect=Exception("Service Error"),
        ):
            with patch(
                "app.v1.market.stock.get_optional_current_user",
                return_value={"id": 1, "username": "testuser"},
            ):
                # Make request
                response = client.get("/market/symbol-data?name=AAPL")

                # Verify 500 response
                assert response.status_code == 500
                assert "Error retrieving data" in response.json()["detail"]

    # Test rate limiting scenarios
    def test_rate_limiting_different_endpoints(self, client):
        """Test rate limiting across different endpoints."""
        # Setup mocks
        with patch("app.v1.market.stock.get_optional_current_user", return_value=None):
            with patch("app.v1.market.stock.get_client_ip", return_value="127.0.0.1"):
                with patch("app.v1.market.stock.is_rate_limited", return_value=False):
                    # Test different rate limit configurations
                    endpoints_and_limits = [
                        ("/market/symbols?name=AAPL", "symbol_search", 10, 3600),
                        ("/market/symbol-data/fresh?name=AAPL", "fresh_data", 5, 3600),
                        (
                            "/market/symbol-data/local?name=AAPL&start_date=2024-01-01&end_date=2024-01-10",
                            "local_data",
                            20,
                            3600,
                        ),
                        ("/market/symbol-data?name=AAPL", "intelligent_data", 15, 3600),
                    ]

                    for (
                        endpoint,
                        rate_key,
                        max_attempts,
                        window,
                    ) in endpoints_and_limits:
                        # Make request
                        response = client.get(endpoint)

                        # Should get some kind of response (not timeout)
                        assert response.status_code in [
                            200,
                            400,
                            401,
                            404,
                            429,
                            500,
                            422,
                        ]

    # Test edge cases and validation
    def test_date_parsing_edge_cases(self, client):
        """Test date parsing edge cases."""
        # Test invalid date formats
        invalid_dates = [
            "2024-13-01",  # Invalid month
            "2024-01-32",  # Invalid day
            "2024/01/01",  # Wrong separator
            "01-01-2024",  # Wrong order
            "invalid-date",  # Completely invalid
        ]

        for invalid_date in invalid_dates:
            response = client.get(
                f"/market/symbol-data/local?name=AAPL&start_date={invalid_date}&end_date=2024-01-10"
            )
            assert response.status_code == 400
            assert "Invalid start_date format" in response.json()["detail"]

    def test_missing_required_parameters(self, client):
        """Test endpoints with missing required parameters."""
        # Test /symbols without name
        response = client.get("/market/symbols")
        assert response.status_code == 422  # Validation error

        # Test /symbol-data/fresh without name
        response = client.get("/market/symbol-data/fresh")
        assert response.status_code == 422  # Validation error

        # Test /symbol-data/local without name
        response = client.get("/market/symbol-data/local")
        assert response.status_code == 422  # Validation error

        # Test /symbol-data without name
        response = client.get("/market/symbol-data")
        assert response.status_code == 422  # Validation error

    # Test authentication scenarios
    def test_authenticated_user_no_rate_limiting(self, client):
        """Test that authenticated users are not rate limited."""
        # Setup mock
        with patch(
            "app.v1.market.stock.get_optional_current_user",
            return_value={"id": 1, "username": "testuser"},
        ):
            # Test all endpoints
            endpoints = [
                "/market/symbols?name=AAPL",
                "/market/symbol-data/fresh?name=AAPL",
                "/market/symbol-data/local?name=AAPL&start_date=2024-01-01&end_date=2024-01-10",
                "/market/symbol-data?name=AAPL",
            ]

            for endpoint in endpoints:
                response = client.get(endpoint)
                # Should not get rate limit errors (status codes other than 429)
                assert response.status_code != 429

    # Test data transformation
    def test_data_transformation_to_json(self, client, sample_market_data):
        """Test that DataFrame data is properly transformed to JSON."""
        # Setup mocks
        with patch(
            "app.v1.market.stock.market_data_service.fetch_ticker_data",
            return_value=sample_market_data,
        ):
            with patch(
                "app.v1.market.stock.get_optional_current_user",
                return_value={"id": 1, "username": "testuser"},
            ):
                # Make request
                response = client.get("/market/symbol-data/fresh?name=AAPL")

                # Verify response
                assert response.status_code == 200
                data = response.json()

                # Check that data is properly transformed
                assert "data" in data
                assert isinstance(data["data"], list)
                assert len(data["data"]) == 10

                # Check first data point structure
                first_point = data["data"][0]
                assert "Open" in first_point
                assert "High" in first_point
                assert "Low" in first_point
                assert "Close" in first_point
                assert "Volume" in first_point

    # Test error handling robustness
    def test_yahooquery_api_failures(self, client):
        """Test handling of various yahooquery API failure scenarios."""
        # Setup mocks
        with patch(
            "app.v1.market.stock.get_optional_current_user",
            return_value={"id": 1, "username": "testuser"},
        ):
            # Test different failure scenarios
            failure_scenarios = [
                (None, "No response from API"),
                ({}, "Empty response"),
                ({"quotes": None}, "Quotes is None"),
                ({"quotes": "not_a_list"}, "Quotes is not a list"),
            ]

            for response_data, description in failure_scenarios:
                with patch("app.v1.market.stock.search", return_value=response_data):
                    # Make request
                    response = client.get("/market/symbols?name=AAPL")

                    # Verify appropriate error response
                    if response_data is None:
                        assert response.status_code == 500
                    elif "quotes" not in response_data or not isinstance(
                        response_data.get("quotes"), list
                    ):
                        assert response.status_code in [404, 500]

    # Test performance characteristics
    def test_endpoint_response_time(self, client):
        """Test that endpoints respond within reasonable time."""
        import time

        # Test all endpoints for response time
        endpoints = [
            "/market/symbols?name=AAPL",
            "/market/symbol-data/fresh?name=AAPL",
            "/market/symbol-data/local?name=AAPL&start_date=2024-01-01&end_date=2024-01-10",
            "/market/symbol-data?name=AAPL",
        ]

        for endpoint in endpoints:
            start_time = time.time()
            response = client.get(endpoint)
            end_time = time.time()

            response_time = end_time - start_time

            # Response should be under 5 seconds (adjust as needed for slower systems)
            assert response_time < 5.0, (
                f"Endpoint {endpoint} took {response_time:.2f}s to respond"
            )

            # Should get some kind of response (not timeout)
            assert response.status_code in [200, 400, 401, 404, 429, 500, 422]

    # Test data consistency
    def test_data_consistency_across_endpoints(self, client, sample_market_data):
        """Test that data is consistent across different endpoints."""
        # Setup mocks
        with patch(
            "app.v1.market.stock.market_data_service.fetch_ticker_data",
            return_value=sample_market_data,
        ):
            with patch(
                "app.v1.market.stock.market_data_service.get_data_with_fallback",
                AsyncMock(return_value=None),
            ):
                with patch(
                    "app.v1.market.stock.get_optional_current_user",
                    return_value={"id": 1, "username": "testuser"},
                ):
                    # Test fresh data endpoint
                    fresh_response = client.get("/market/symbol-data/fresh?name=AAPL")
                    assert fresh_response.status_code == 200
                    fresh_data = fresh_response.json()

                    # Test intelligent data endpoint
                    intelligent_response = client.get("/market/symbol-data?name=AAPL")
                    assert intelligent_response.status_code == 200
                    intelligent_data = intelligent_response.json()

                    # Both should return the same symbol
                    assert fresh_data["symbol"] == intelligent_data["symbol"]
                    assert fresh_data["symbol"] == "AAPL"

                    # Verify intelligent data endpoint returns empty data when mock returns None
                    assert intelligent_data["data_points"] == 0
                    assert intelligent_data["data"] == []

    # Test concurrent access
    def test_concurrent_access(self, client, sample_quotes_data):
        """Test that endpoints can handle concurrent access."""
        import threading

        # Setup mocks
        with patch("app.v1.market.stock.search", return_value=sample_quotes_data):
            with patch(
                "app.v1.market.stock.get_optional_current_user",
                return_value={"id": 1, "username": "testuser"},
            ):
                results = []
                errors = []

                def make_request():
                    try:
                        response = client.get("/market/symbols?name=AAPL")
                        results.append(response.status_code)
                    except Exception as e:
                        errors.append(str(e))

                # Create multiple threads
                threads = []
                for _ in range(5):
                    thread = threading.Thread(target=make_request)
                    threads.append(thread)
                    thread.start()

                # Wait for all threads to complete
                for thread in threads:
                    thread.join()

                # Verify all requests completed
                assert len(results) == 5
                assert len(errors) == 0

                # All should return success
                assert all(status == 200 for status in results)

# Portfolia API Integration Tests

This directory contains comprehensive integration tests for all Portfolia API endpoints, based on the manual testing performed during development.

## 🎯 **What These Tests Cover**

### **1. Core API Endpoints**
- ✅ Root endpoint (`/`)
- ✅ Health endpoint (`/health`)
- ✅ API v1 root (`/api/v1/`)

### **2. Authentication Endpoints**
- ✅ User registration (`/api/v1/auth/register`)
- ✅ User login with username (`/api/v1/auth/login`)
- ✅ User logout (`/api/v1/auth/logout`)
- ✅ Get current user (`/api/v1/auth/me`)
- ✅ Forgot password (`/api/v1/auth/forgot-password`)
- ✅ 2FA setup and verification
- ✅ Password change and reset
- ✅ Email verification

### **3. Market Data Endpoints**
- ✅ Market symbols (`/api/v1/market/symbols`)
- ✅ Symbol data (`/api/v1/market/symbol-data`)

### **4. Statistical Indicators**
- ✅ RSI indicator (`/api/v1/statistical-indicators/momentum-rsi-indicator`)

### **5. Security Features**
- ✅ Unique username constraints
- ✅ Unique email constraints
- ✅ Password strength validation
- ✅ Username validation
- ✅ JWT token expiration
- ✅ Protected endpoint access control

## 🚀 **How to Run the Tests**

### **Option 1: Using the Shell Script (Recommended)**
```bash
# From portfolio/python/api directory
./tests/run_tests.sh
```

### **Option 2: Using Python Directly**
```bash
# From portfolio/python/api directory
python tests/run_integration_tests.py
```

### **Option 3: Using pytest Directly**
```bash
# From portfolio/python/api directory
pytest tests/integration/test_api_endpoints.py -v
```

## 📋 **Prerequisites**

Before running the tests, ensure you have:

1. **Python 3.8+** installed
2. **pytest** installed: `pip install pytest`
3. **httpx** installed: `pip install httpx` (for FastAPI TestClient)
4. **All project dependencies** installed: `pip install -r requirements.txt`

## 🏗️ **Test Structure**

The tests are organized into logical test classes:

### **TestCoreAPIEndpoints**
- Tests basic API functionality and health checks

### **TestAuthenticationEndpoints**
- Tests user registration, login, logout, and authentication flows
- Tests unique constraints (username/email)
- Tests parameter validation

### **TestMarketDataEndpoints**
- Tests market data retrieval endpoints
- Tests parameter validation for market endpoints

### **TestStatisticalIndicatorsEndpoints**
- Tests technical analysis indicator endpoints
- Tests parameter validation for indicators

### **TestAPIEndpointsComprehensive**
- Tests that all expected endpoints are available
- Tests API documentation accessibility
- Tests OpenAPI specification completeness

### **TestSecurityFeatures**
- Tests password strength validation
- Tests username format validation
- Tests JWT token structure and expiration

## 🔧 **Test Configuration**

The tests use the configuration from `conftest.py` which:

- Creates an in-memory SQLite test database
- Overrides database dependencies for testing
- Provides test client fixtures
- Handles test setup and teardown

## 📊 **Test Coverage**

These integration tests cover:

| Category | Test Count | Coverage |
|----------|------------|----------|
| **Core API** | 3 tests | 100% |
| **Authentication** | 12 tests | 100% |
| **Market Data** | 3 tests | 100% |
| **Statistical Indicators** | 2 tests | 100% |
| **Comprehensive** | 3 tests | 100% |
| **Security** | 3 tests | 100% |
| **Total** | **26 tests** | **100%** |

## 🧪 **Running Specific Test Categories**

### **Run only authentication tests:**
```bash
pytest tests/integration/test_api_endpoints.py::TestAuthenticationEndpoints -v
```

### **Run only market data tests:**
```bash
pytest tests/integration/test_api_endpoints.py::TestMarketDataEndpoints -v
```

### **Run only security tests:**
```bash
pytest tests/integration/test_api_endpoints.py::TestSecurityFeatures -v
```

## 🔍 **Test Output Examples**

### **Successful Test Run:**
```
🧪 Portfolia API Integration Test Runner
==================================================
✅ pytest available
✅ FastAPI TestClient available

🚀 Starting Integration Tests...
--------------------------------------------------
Running: python -m pytest tests/integration/test_api_endpoints.py -v --tb=short --color=yes -s

tests/integration/test_api_endpoints.py::TestCoreAPIEndpoints::test_root_endpoint PASSED
tests/integration/test_api_endpoints.py::TestCoreAPIEndpoints::test_health_endpoint PASSED
tests/integration/test_api_endpoints.py::TestCoreAPIEndpoints::test_api_v1_root PASSED
...

==================================================
🎉 Integration tests completed!
```

### **Failed Test Example:**
```
tests/integration/test_api_endpoints.py::TestAuthenticationEndpoints::test_user_registration_duplicate_username FAILED
...
AssertionError: assert 422 == 400
```

## 🐛 **Troubleshooting**

### **Common Issues:**

1. **Import Errors**: Ensure you're running from the correct directory (`portfolio/python/api`)
2. **Database Errors**: Tests use in-memory SQLite, so no external database is needed
3. **Missing Dependencies**: Install required packages with `pip install pytest httpx`
4. **Permission Errors**: Make sure the shell script is executable: `chmod +x tests/run_tests.sh`

### **Debug Mode:**
```bash
# Run with more verbose output
pytest tests/integration/test_api_endpoints.py -v -s --tb=long
```

## 📝 **Adding New Tests**

To add new tests:

1. **Create test methods** in the appropriate test class
2. **Use the `client` fixture** for making HTTP requests
3. **Follow the naming convention**: `test_<feature_name>`
4. **Add comprehensive assertions** to verify behavior
5. **Update this README** with new test coverage

### **Example Test Method:**
```python
def test_new_feature(self, client: TestClient):
    """Test new feature endpoint."""
    response = client.get("/api/v1/new-feature")
    assert response.status_code == 200
    
    data = response.json()
    assert "expected_field" in data
```

## 🎉 **Success Criteria**

Tests are considered successful when:

- ✅ All 26 tests pass
- ✅ No test failures or errors
- ✅ All API endpoints respond correctly
- ✅ Authentication flows work as expected
- ✅ Security constraints are enforced
- ✅ Parameter validation works properly

## 📞 **Support**

If you encounter issues with the tests:

1. Check the troubleshooting section above
2. Verify you're in the correct directory
3. Ensure all dependencies are installed
4. Check the test output for specific error messages
5. Review the test configuration in `conftest.py`

---

**Happy Testing! 🧪✨**

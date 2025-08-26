#!/usr/bin/env python3
"""
Comprehensive test script for the authentication system.
"""

import requests
import json
import time
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:8080/api/auth"

# Test user data
TEST_USER = {
    "email": "authtest@example.com",
    "username": "authtestuser",
    "password": "AuthTest123!",
    "confirm_password": "AuthTest123!",
    "first_name": "Auth",
    "last_name": "Test",
}


def print_test_result(test_name: str, success: bool, details: str = ""):
    """Print test result with formatting."""
    if success:
        print(f"✅ {test_name}: PASSED")
        if details:
            print(f"   {details}")
    else:
        print(f"❌ {test_name}: FAILED")
        if details:
            print(f"   {details}")
    print()


def test_user_registration():
    """Test user registration."""
    print("🧪 Testing User Registration...")

    try:
        response = requests.post(f"{BASE_URL}/register", json=TEST_USER)

        if response.status_code == 201:
            user_data = response.json()
            print_test_result(
                "User Registration",
                True,
                f"User created with ID: {user_data['id']}, Email: {user_data['email']}",
            )
            return user_data
        else:
            error_detail = response.json().get("detail", "Unknown error")
            print_test_result(
                "User Registration",
                False,
                f"Status: {response.status_code}, Error: {error_detail}",
            )
            return None

    except Exception as e:
        print_test_result("User Registration", False, f"Exception: {str(e)}")
        return None


def test_user_login(email: str, password: str):
    """Test user login."""
    print("🔐 Testing User Login...")

    try:
        response = requests.post(
            f"{BASE_URL}/login", json={"email": email, "password": password}
        )

        if response.status_code == 200:
            token_data = response.json()
            print_test_result(
                "User Login",
                True,
                f"Login successful, Access token: {token_data['access_token'][:20]}...",
            )
            return token_data
        else:
            error_detail = response.json().get("detail", "Unknown error")
            print_test_result(
                "User Login",
                False,
                f"Status: {response.status_code}, Error: {error_detail}",
            )
            return None

    except Exception as e:
        print_test_result("User Login", False, f"Exception: {str(e)}")
        return None


def test_protected_endpoint(access_token: str):
    """Test accessing protected endpoint."""
    print("🔒 Testing Protected Endpoint...")

    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{BASE_URL}/me", headers=headers)

        if response.status_code == 200:
            user_data = response.json()
            print_test_result(
                "Protected Endpoint Access",
                True,
                f"User data retrieved: {user_data['username']} ({user_data['email']})",
            )
            return True
        else:
            error_detail = response.json().get("detail", "Unknown error")
            print_test_result(
                "Protected Endpoint Access",
                False,
                f"Status: {response.status_code}, Error: {error_detail}",
            )
            return False

    except Exception as e:
        print_test_result("Protected Endpoint Access", False, f"Exception: {str(e)}")
        return False


def test_refresh_token(refresh_token: str):
    """Test token refresh."""
    print("🔄 Testing Token Refresh...")

    try:
        headers = {"Authorization": f"Bearer {refresh_token}"}
        response = requests.post(f"{BASE_URL}/refresh", headers=headers)

        if response.status_code == 200:
            new_tokens = response.json()
            print_test_result(
                "Token Refresh",
                True,
                f"New access token: {new_tokens['access_token'][:20]}...",
            )
            return new_tokens
        else:
            error_detail = response.json().get("detail", "Unknown error")
            print_test_result(
                "Token Refresh",
                False,
                f"Status: {response.status_code}, Error: {error_detail}",
            )
            return None

    except Exception as e:
        print_test_result("Token Refresh", False, f"Exception: {str(e)}")
        return None


def test_password_change(access_token: str, current_password: str, new_password: str):
    """Test password change."""
    print("🔑 Testing Password Change...")

    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        password_data = {
            "current_password": current_password,
            "new_password": new_password,
            "confirm_new_password": new_password,
        }

        response = requests.post(
            f"{BASE_URL}/change-password", headers=headers, json=password_data
        )

        if response.status_code == 200:
            result = response.json()
            print_test_result(
                "Password Change",
                True,
                f"Password changed: {result.get('message', 'Success')}",
            )
            return True
        else:
            error_detail = response.json().get("detail", "Unknown error")
            print_test_result(
                "Password Change",
                False,
                f"Status: {response.status_code}, Error: {error_detail}",
            )
            return False

    except Exception as e:
        print_test_result("Password Change", False, f"Exception: {str(e)}")
        return False


def test_user_logout(access_token: str):
    """Test user logout."""
    print("🚪 Testing User Logout...")

    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.post(f"{BASE_URL}/logout", headers=headers)

        if response.status_code == 200:
            result = response.json()
            print_test_result(
                "User Logout",
                True,
                f"Logout successful: {result.get('message', 'Success')}",
            )
            return True
        else:
            error_detail = response.json().get("detail", "Unknown error")
            print_test_result(
                "User Logout",
                False,
                f"Status: {response.status_code}, Error: {error_detail}",
            )
            return False

    except Exception as e:
        print_test_result("User Logout", False, f"Exception: {str(e)}")
        return False


def test_invalid_token_access():
    """Test accessing protected endpoint with invalid token."""
    print("🚫 Testing Invalid Token Access...")

    try:
        headers = {"Authorization": "Bearer invalid_token_here"}
        response = requests.get(f"{BASE_URL}/me", headers=headers)

        if response.status_code == 401:
            print_test_result(
                "Invalid Token Access", True, "Correctly rejected invalid token"
            )
            return True
        else:
            print_test_result(
                "Invalid Token Access",
                False,
                f"Expected 401, got {response.status_code}",
            )
            return False

    except Exception as e:
        print_test_result("Invalid Token Access", False, f"Exception: {str(e)}")
        return False


def test_duplicate_registration():
    """Test duplicate user registration."""
    print("🔄 Testing Duplicate Registration...")

    try:
        response = requests.post(f"{BASE_URL}/register", json=TEST_USER)

        if response.status_code == 400:
            error_detail = response.json().get("detail", "Unknown error")
            if "already registered" in error_detail.lower():
                print_test_result(
                    "Duplicate Registration",
                    True,
                    f"Correctly rejected duplicate: {error_detail}",
                )
                return True
            else:
                print_test_result(
                    "Duplicate Registration", False, f"Unexpected error: {error_detail}"
                )
                return False
        else:
            print_test_result(
                "Duplicate Registration",
                False,
                f"Expected 400, got {response.status_code}",
            )
            return False

    except Exception as e:
        print_test_result("Duplicate Registration", False, f"Exception: {str(e)}")
        return False


def main():
    """Run all authentication tests."""
    print("🚀 Starting Authentication System Tests")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    test_results = []

    # Test 1: User Registration
    user_data = test_user_registration()
    if user_data:
        test_results.append(("User Registration", True))
    else:
        test_results.append(("User Registration", False))
        print("❌ Cannot continue tests without user registration")
        return

    # Test 2: User Login
    tokens = test_user_login(TEST_USER["email"], TEST_USER["password"])
    if tokens:
        test_results.append(("User Login", True))
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
    else:
        test_results.append(("User Login", False))
        print("❌ Cannot continue tests without successful login")
        return

    # Test 3: Protected Endpoint Access
    protected_access = test_protected_endpoint(access_token)
    test_results.append(("Protected Endpoint Access", protected_access))

    # Test 4: Token Refresh
    new_tokens = test_refresh_token(refresh_token)
    if new_tokens:
        test_results.append(("Token Refresh", True))
        access_token = new_tokens["access_token"]  # Use new access token
    else:
        test_results.append(("Token Refresh", False))

    # Test 5: Password Change
    password_changed = test_password_change(
        access_token, TEST_USER["password"], "NewPass456!"
    )
    test_results.append(("Password Change", password_changed))

    # Test 6: Login with New Password
    if password_changed:
        new_login = test_user_login(TEST_USER["email"], "NewPass456!")
        test_results.append(("Login with New Password", new_login is not None))

        if new_login:
            access_token = new_login["access_token"]

    # Test 7: User Logout
    logout_success = test_user_logout(access_token)
    test_results.append(("User Logout", logout_success))

    # Test 8: Invalid Token Access
    invalid_token = test_invalid_token_access()
    test_results.append(("Invalid Token Access", invalid_token))

    # Test 9: Duplicate Registration
    duplicate_reg = test_duplicate_registration()
    test_results.append(("Duplicate Registration", duplicate_reg))

    # Summary
    print("=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, success in test_results if success)
    total = len(test_results)

    for test_name, success in test_results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {test_name}")

    print()
    print(f"Overall Result: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All authentication tests passed! The system is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the implementation.")

    print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()

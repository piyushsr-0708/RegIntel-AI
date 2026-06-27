"""
Test script to verify backend authentication functionality
"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("="*60)
print("BACKEND AUTHENTICATION TEST")
print("="*60)

# Test 1: Health Check
print("\n1. Testing Health Check...")
try:
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    print("   ✓ Health check passed")
except Exception as e:
    print(f"   ✗ Health check failed: {e}")

# Test 2: Login with valid credentials
print("\n2. Testing Login (admin)...")
try:
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        access_token = data.get("access_token")
        print(f"   Token received: {access_token[:50]}...")
        print(f"   Token type: {data.get('token_type')}")
        print("   ✓ Login successful")
        
        # Test 3: Get current user with token
        print("\n3. Testing Get Current User...")
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            user_data = response.json()
            print(f"   Username: {user_data.get('username')}")
            print(f"   Role: {user_data.get('role')}")
            print(f"   Full Name: {user_data.get('full_name')}")
            print("   ✓ Get current user successful")
        else:
            print(f"   ✗ Failed: {response.text}")
    else:
        print(f"   ✗ Login failed: {response.text}")
except Exception as e:
    print(f"   ✗ Login test failed: {e}")

# Test 4: Login with invalid credentials
print("\n4. Testing Login with Invalid Credentials...")
try:
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        data={"username": "admin", "password": "wrongpassword"}
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 401:
        print("   ✓ Correctly rejected invalid credentials")
    else:
        print(f"   ✗ Unexpected response: {response.text}")
except Exception as e:
    print(f"   ✗ Test failed: {e}")

# Test 5: Login as department user
print("\n5. Testing Department User Login (compliance)...")
try:
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        data={"username": "compliance", "password": "compliance123"}
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Token received: {data.get('access_token')[:50]}...")
        print("   ✓ Department login successful")
        
        # Get user info
        headers = {"Authorization": f"Bearer {data.get('access_token')}"}
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            print(f"   Username: {user_data.get('username')}")
            print(f"   Role: {user_data.get('role')}")
            print(f"   Department: {user_data.get('department')}")
    else:
        print(f"   ✗ Login failed: {response.text}")
except Exception as e:
    print(f"   ✗ Test failed: {e}")

# Test 6: API Documentation
print("\n6. Testing API Documentation...")
try:
    response = requests.get(f"{BASE_URL}/api/docs")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✓ Swagger docs accessible")
    else:
        print(f"   ✗ Failed to access docs")
except Exception as e:
    print(f"   ✗ Test failed: {e}")

print("\n" + "="*60)
print("BACKEND AUTHENTICATION TEST COMPLETE")
print("="*60)
print("\nDEFAULT CREDENTIALS:")
print("  Admin: admin / admin123")
print("  Departments: compliance / compliance123")
print("               risk / risk123")
print("               treasury / treasury123")
print("               operations / operations123")
print("               cyber / cyber123")
print("               it / it123")
print("               finance / finance123")
print("               aml / aml123")
print("               legal / legal123")
print("="*60)

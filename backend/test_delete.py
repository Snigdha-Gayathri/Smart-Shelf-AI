import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_delete_endpoint():
    username = f"testuser_{int(time.time())}"
    password = "SecurePassword123!"
    
    print(f"[*] Registering user {username}...")
    rem = requests.post(f"{BASE_URL}/auth/register", json={
        "name": "Test User",
        "username": username,
        "password": password
    })
    
    assert rem.status_code == 200
    print("  [+] Registered successfully.")
    
    print(f"[*] Attempting to delete user without password...")
    rdel_nopass = requests.delete(f"{BASE_URL}/auth/delete", json={
        "username": username,
        "password": "wrongpassword"
    })
    assert rdel_nopass.json().get("status") == "error"
    print("  [+] Successfully rejected incorrect password deletion.")
    
    print(f"[*] Attempting to delete user WITH correct password...")
    rdel_pass = requests.delete(f"{BASE_URL}/auth/delete", json={
        "username": username,
        "password": password
    })
    
    assert rdel_pass.json().get("status") == "ok"
    print("  [+] Successfully deleted user with correct password.")
    
if __name__ == "__main__":
    time.sleep(2)
    test_delete_endpoint()

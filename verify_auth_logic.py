import auth
import os
import sqlite3

# Mock DB Name to avoid messing with real one if possible, but auth.py uses hardcoded name.
# We will backup and restore AUTH_DB if it exists, or just use it.
# Actually, let's just use the real functions but check results.

TEST_USER = "TestUserChecking123"
TEST_PASS = "SecretPass!"

def clean_test_user():
    conn = sqlite3.connect(auth.AUTH_DB)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username = ?", (TEST_USER,))
    conn.commit()
    conn.close()

def main():
    print("Testing Auth Module...")
    
    # Ensure DB init
    auth.init_auth_db()
    
    # Clean previous runs
    try:
        clean_test_user()
    except:
        pass

    # 1. Create User
    print(f"Creating user '{TEST_USER}'...")
    success, msg = auth.create_user_account(TEST_USER, TEST_PASS)
    print(f"Creation result: {success} - {msg}")
    assert success is True
    
    # 2. Duplicate Check
    print("Checking duplicate creation...")
    success, msg = auth.create_user_account(TEST_USER, "AnyPass")
    print(f"Duplicate result: {success} - {msg}")
    assert success is False
    assert "exists" in msg
    
    # 3. Verify Login (Success)
    print("Verifying correct login...")
    is_valid = auth.verify_login(TEST_USER, TEST_PASS)
    print(f"Login success: {is_valid}")
    assert is_valid is True
    
    # 4. Verify Login (Fail)
    print("Verifying wrong password...")
    is_valid = auth.verify_login(TEST_USER, "WrongPass")
    print(f"Login fail: {is_valid}")
    assert is_valid is False
    
    # 5. DB Content Check (Security)
    print("Checking database for plaintext passwords...")
    conn = sqlite3.connect(auth.AUTH_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash, salt FROM users WHERE username = ?", (TEST_USER,))
    row = cursor.fetchone()
    conn.close()
    
    stored_hash, stored_salt = row
    print(f"Stored Hash: {stored_hash}")
    print(f"Stored Salt: {stored_salt}")
    
    assert stored_hash != TEST_PASS
    assert stored_salt is not None
    
    # Cleanup
    clean_test_user()
    print("SUCCESS: Auth logic verified.")

if __name__ == "__main__":
    main()

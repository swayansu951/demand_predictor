import hashlib
import sqlite3
import os
import streamlit as st
import time
import datetime

AUTH_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.db")

def init_auth_db():
    conn = sqlite3.connect(AUTH_DB)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password, salt=None):
    if salt is None:
        salt = os.urandom(32).hex() # 64 chars
    
    # Simple SHA-256 with salt
    # In production, use bcrypt or argon2 (e.g. via 'passlib'), 
    # but hashlib is standard lib and sufficient for this requirement.
    key = hashlib.pbkdf2_hmac(
        'sha256', 
        password.encode('utf-8'), 
        bytes.fromhex(salt), 
        100000 
    )
    return key.hex(), salt

def create_user_account(username, password):
    if not username or not password:
        return False, "Username and password required."
    
    try:
        init_auth_db() # Ensure DB exists
        conn = sqlite3.connect(AUTH_DB)
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            return False, "Username already exists."
        
        # Create user
        p_hash, salt = hash_password(password)
        cursor.execute("INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)", 
                       (username, p_hash, salt))
        conn.commit()
        conn.close()
        return True, "Account created successfully!"
    except Exception as e:
        return False, f"Error creating account: {e}"

def verify_login(username, password):
    try:
        init_auth_db()
        conn = sqlite3.connect(AUTH_DB)
        cursor = conn.cursor()
        
        cursor.execute("SELECT password_hash, salt FROM users WHERE username = ?", (username,))
        record = cursor.fetchone()
        conn.close()
        
        if not record:
            return False
        
        stored_hash, salt = record
        
        # Re-hash input
        input_hash, _ = hash_password(password, salt)
        
        return input_hash == stored_hash
    except Exception:
        return False

# --- UI Components ---
import extra_streamlit_components as stx

def auto_login(cookie_manager):
    """Check for existing session cookie and log in automatically"""
    # Check if already authenticated in session state
    if st.session_state.get('authenticated', False):
        return

    # Check for cookie
    # Note: Cookies might take a moment to load
    cookies = cookie_manager.get_all()
    auth_user = cookies.get('auth_user')
    
    if auth_user:
        # Verify user still exists in DB
        if check_user_exists(auth_user):
            st.session_state.authenticated = True
            st.session_state.current_user = auth_user
            return str(auth_user)
    return None

def check_user_exists(username):
    try:
        init_auth_db()
        conn = sqlite3.connect(AUTH_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists
    except:
        return False

def logout(cookie_manager):
    cookie_manager.delete('auth_user')
    st.session_state.authenticated = False
    st.session_state.current_user = None
    st.rerun()

def login_form(cookie_manager):
    st.subheader("Sign In")
    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")
    
    if st.button("Login", type="primary"):
        if verify_login(username, password):
            st.session_state.authenticated = True
            st.session_state.current_user = username
            
            # Set Cookie (Expires in 30 days)
            cookie_manager.set('auth_user', username, expires_at=datetime.datetime.now() + datetime.timedelta(days=30))
            
            st.success(f"Welcome back, {username}!")
            time.sleep(0.5)
            st.rerun()
        else:
            st.error("Invalid username or password.")

def signup_form():
    st.subheader("Sign Up")
    new_user = st.text_input("New Username", key="signup_user")
    new_pass = st.text_input("New Password", type="password", key="signup_pass")
    confirm_pass = st.text_input("Confirm Password", type="password", key="signup_confirm")
    
    if st.button("Create Account"):
        if new_pass != confirm_pass:
            st.error("Passwords do not match.")
        else:
            # Basic validation
            safe_username = "".join([c for c in new_user if c.isalnum() or c in ('_', '-')]).strip()
            if safe_username != new_user:
                 st.warning("Special characters removed from username.")
            
            if not safe_username:
                st.error("Invalid username.")
                return

            success, msg = create_user_account(safe_username, new_pass)
            if success:
                st.success(msg)
                # Auto-login or ask to switch tab
                st.info("Please switch to the 'Sign In' tab to log in.")
            else:
                st.error(msg)


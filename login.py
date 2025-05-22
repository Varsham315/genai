import streamlit as st
import hashlib  # For securely hashing passwords
import json
import os
  # Replace this with your actual app logic

# File to store user credentials persistently
USER_DB_FILE = "users.json"
# Load users from a JSON file (persistent storage)
def load_users():
    if os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {}  # If the file is corrupted, return an empty database
    return {}
# Save users to a JSON file
def save_users(users):
    with open(USER_DB_FILE, "w") as file:
        json.dump(users, file)
# Initialize user database from the file
user_db = load_users()
# Check if the username and password are correct
def check_credentials(username, password):
    if username in user_db:
        stored_password_hash = user_db[username]
        entered_password_hash = hashlib.sha256(password.encode()).hexdigest()
        return stored_password_hash == entered_password_hash
    return False
# Store credentials in the persistent database
def store_credentials(username, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    user_db[username] = hashed_password
    save_users(user_db)  # Save the updated database to the file
# Handle the main content after login
def handle_authenticated_user():
    st.sidebar.success(f"Logged in as {st.session_state.username}")
    # Add a logout button in the sidebar
    if st.sidebar.button("Logout"):
        st.session_state.clear()  # Clear session state
        st.session_state.logged_in = False
        st.session_state.username = None
    st.title("Welcome to Your Streamlit App!") 
    # Call the main function or content from `chatapp.py`
    # Uncomment the line below if you want to integrate another app module

# Main login function to check login state
def main():
    # If the user is already logged in, show the authenticated content
    if st.session_state.get("logged_in", False):
        handle_authenticated_user()
    else:
        st.title("Login to Streamlit App")
        # Get user credentials
        username = st.text_input("Username", key="username_input")
        password = st.text_input("Password", type="password", key="password_input")
        remember_me = st.checkbox("Remember me (store credentials permanently)", key="remember_me")
        if st.button("Login"):
            if check_credentials(username, password):
                # Store user session state on successful login
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Logged in successfully!")
                handle_authenticated_user()  # Show the authenticated user content
            else:
                st.error("Invalid username or password. Please try again.")
        # Option to sign up a new user
        st.subheader("New user? Create an account")
        new_username = st.text_input("New Username", key="new_username_input")
        new_password = st.text_input("New Password", type="password", key="new_password_input")
        if st.button("Sign Up"):
            if new_username and new_password:
                if new_username in user_db:
                    st.warning("Username already exists. Please choose a different username.")
                else:
                    store_credentials(new_username, new_password)
                    st.success(f"Account created for {new_username}. You can now log in.")
            else:
                st.warning("Please provide a username and password.")
# Execute the login flow
if __name__ == "__main__":
    main()

import streamlit as st
import pickle
from pathlib import Path
import pandas as pd

st.set_page_config(
    page_title="Fitness Coach Platform",
    page_icon="🏋️‍♂️",
    layout="wide"
)

# Initialize session state for user management
if 'users' not in st.session_state:
    st.session_state.users = {}
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

def save_users():
    with open('users.pkl', 'wb') as f:
        pickle.dump(st.session_state.users, f)

def load_users():
    try:
        with open('users.pkl', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return {}

# Load existing users
st.session_state.users = load_users()

st.title("🏋️‍♂️ Fitness Coach Platform")

# Login/Registration tabs
tab1, tab2 = st.tabs(["Login", "Register"])

with tab1:
    st.header("Login")
    login_username = st.text_input("Username", key="login_username")
    login_password = st.text_input("Password", type="password", key="login_password")
    
    if st.button("Login"):
        if login_username in st.session_state.users and st.session_state.users[login_username]['password'] == login_password:
            st.session_state.current_user = login_username
            st.success(f"Welcome back, {login_username}!")
            st.rerun()  # Updated from st.experimental_rerun()
        else:
            st.error("Invalid username or password")

with tab2:
    st.header("Register")
    new_username = st.text_input("Choose Username", key="new_username")
    new_password = st.text_input("Choose Password", type="password", key="new_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
    
    if st.button("Register"):
        if new_username in st.session_state.users:
            st.error("Username already exists!")
        elif new_password != confirm_password:
            st.error("Passwords don't match!")
        else:
            st.session_state.users[new_username] = {
                'password': new_password,
                'fitness_plans': [],
                'workout_logs': [],
                'nutrition_logs': []
            }
            save_users()
            st.success("Registration successful! Please login.")

# Navigation section after successful login
if st.session_state.current_user:
    st.write(f"## Welcome to your Fitness Journey, {st.session_state.current_user}!")
    
    # Create a grid layout for feature buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🎯 Fitness Plan Generator", use_container_width=True):
            st.switch_page("pages.1_🎯_Fitness_Plan.py")
        
        if st.button("📝 Workout Logger", use_container_width=True):
            st.switch_page("Logger.py")
    
    with col2:
        if st.button("🍎 Nutrition Assistant", use_container_width=True):
            st.switch_page("assitant.py")
        
        if st.button("💪 Progress Tracker", use_container_width=True):
            st.switch_page("Tracker.py")
    
    # Logout button
    if st.button("Logout", type="primary"):
        st.session_state.current_user = None
        st.rerun()  # Updated from st.experimental_rerun()

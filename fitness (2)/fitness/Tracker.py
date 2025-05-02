import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import ollama
from datetime import datetime, timedelta

st.set_page_config(page_title="Progress Tracker", page_icon="💪")

def stream_response(prompt):
    response = ''
    stream = ollama.chat(model='deepseek-r1:1.5b', messages=[{'role': 'user', 'content': prompt}], stream=True)
    for chunk in stream:
        response += chunk['message']['content']
        print(chunk['message']['content'], end='', flush=True)
    return response

# Navigation buttons
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    if st.button("← Back to Home"):
        st.switch_page("pages/0_🏠_Home.py")

with col3:
    if st.button("Logout"):
        st.session_state.current_user = None
        st.switch_page("pages/0_🏠_Home.py")

st.title("Progress Tracker")

if 'current_user' not in st.session_state or not st.session_state.current_user:
    st.warning("Please login to access this feature!")
    st.switch_page("pages/0_🏠_Home.py")

# Initialize progress logs if not exists
if 'progress_logs' not in st.session_state:
    st.session_state.progress_logs = []

# Create tabs for different features
tab1, tab2 = st.tabs(["Log Progress", "View Progress"])

with tab1:
    st.header("Log Progress")
    
    with st.form("progress_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            date = st.date_input("Date")
            weight = st.number_input("Weight (kg)", min_value=0.0)
            body_fat = st.number_input("Body Fat %", min_value=0.0, max_value=100.0)
        
        with col2:
            measurements = {
                'chest': st.number_input("Chest (cm)", min_value=0.0),
                'waist': st.number_input("Waist (cm)", min_value=0.0),
                'hips': st.number_input("Hips (cm)", min_value=0.0),
                'arms': st.number_input("Arms (cm)", min_value=0.0),
                'thighs': st.number_input("Thighs (cm)", min_value=0.0)
            }
        
        photos = st.file_uploader("Progress Photos (optional)", accept_multiple_files=True)
        notes = st.text_area("Notes (optional)")
        
        if st.form_submit_button("Log Progress"):
            progress = {
                'date': date,
                'weight': weight,
                'body_fat': body_fat,
                **measurements,
                'notes': notes,
                'timestamp': datetime.now()
            }
            st.session_state.progress_logs.append(progress)
            
            # Get AI analysis of progress
            if len(st.session_state.progress_logs) > 1:
                last_log = st.session_state.progress_logs[-2]
                weight_change = weight - last_log['weight']
                prompt = f"""Analyze this fitness progress:
                Current weight: {weight}kg (changed by {weight_change:+.1f}kg)
                Body fat: {body_fat}%
                Measurements changes:
                - Waist: {measurements['waist']-last_log['waist']:+.1f}cm
                - Chest: {measurements['chest']-last_log['chest']:+.1f}cm
                
                Provide motivation and suggestions for continued improvement."""
                
                analysis = stream_response(prompt)
                st.info("AI Analysis:\n" + analysis)

with tab2:
    st.header("Progress Analysis")
    
    if st.session_state.progress_logs:
        df = pd.DataFrame(st.session_state.progress_logs)
        df['date'] = pd.to_datetime(df['date'])
        
        # Time range selector
        time_range = st.selectbox(
            "Select Time Range",
            ["1 Month", "3 Months", "6 Months", "1 Year", "All Time"]
        )
        
        # Filter data based on time range
        if time_range != "All Time":
            months = int(time_range.split()[0])
            start_date = datetime.now() - timedelta(days=months*30)
            df = df[df['date'] >= start_date]
        
        # Progress visualizations
        fig, axes = plt.subplots(2, 1, figsize=(10, 12))
        
        # Weight and body fat progress
        ax1 = axes[0]
        ax1.plot(df['date'], df['weight'], marker='o', label='Weight (kg)')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Weight (kg)', color='blue')
        ax1.tick_params(axis='y', labelcolor='blue')
        
        ax2 = ax1.twinx()
        ax2.plot(df['date'], df['body_fat'], marker='s', color='red', label='Body Fat %')
        ax2.set_ylabel('Body Fat %', color='red')
        ax2.tick_params(axis='y', labelcolor='red')
        
        ax1.set_title('Weight and Body Fat Progress')
        fig.legend(loc='upper right')
        
        # Body measurements progress
        measurement_cols = ['chest', 'waist', 'hips', 'arms', 'thighs']
        for col in measurement_cols:
            axes[1].plot(df['date'], df[col], marker='o', label=col.capitalize())
        
        axes[1].set_xlabel('Date')
        axes[1].set_ylabel('Centimeters')
        axes[1].set_title('Body Measurements Progress')
        axes[1].legend()
        
        plt.tight_layout()
        st.pyplot(fig)
        
        # Progress summary
        st.subheader("Progress Summary")
        total_time = (df['date'].max() - df['date'].min()).days
        total_weight_change = df['weight'].iloc[-1] - df['weight'].iloc[0]
        
        st.write(f"Total time: {total_time} days")
        st.write(f"Total weight change: {total_weight_change:+.1f} kg")
        st.write(f"Average weekly change: {(total_weight_change/total_time*7):+.2f} kg")
        
        # Get AI insights
        prompt = f"""Analyze this {time_range.lower()} progress:
        - Total weight change: {total_weight_change:+.1f}kg
        - Starting weight: {df['weight'].iloc[0]:.1f}kg
        - Current weight: {df['weight'].iloc[-1]:.1f}kg
        - Body fat change: {df['body_fat'].iloc[-1]-df['body_fat'].iloc[0]:+.1f}%
        
        Provide insights on:
        1. Overall progress
        2. Rate of change
        3. Suggestions for optimization
        4. Next milestone targets
        """
        
        analysis = stream_response(prompt)
        st.subheader("AI Progress Analysis")
        st.write(analysis)
    else:
        st.info("No progress data available. Start logging your measurements to track progress!")
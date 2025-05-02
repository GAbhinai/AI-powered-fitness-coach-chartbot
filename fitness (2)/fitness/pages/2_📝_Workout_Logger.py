import streamlit as st
import pandas as pd
from datetime import datetime
import ollama
from matplotlib import pyplot as plt
import re

st.set_page_config(page_title="Workout Logger", page_icon="📝")

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
        st.switch_page("0_🏠_Home.py")

with col3:
    if st.button("Logout"):
        st.session_state.current_user = None
        st.switch_page("0_🏠_Home.py")

st.title("Workout Logger")

if 'current_user' not in st.session_state or not st.session_state.current_user:
    st.warning("Please login to access this feature!")
    st.switch_page("0_🏠_Home.py")

# Initialize workout log
if 'workout_logs' not in st.session_state:
    st.session_state.workout_logs = []

# Workout Categories
categories = {
    "Strength Training": ["Bench Press", "Squats", "Deadlifts", "Shoulder Press", "Rows", "Pull-ups"],
    "Cardio": ["Running", "Cycling", "Swimming", "Jump Rope", "Elliptical"],
    "Flexibility": ["Yoga", "Stretching", "Pilates"],
    "Custom": ["Add custom exercise"]
}

# Workout form
with st.form("workout_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        date = st.date_input("Date")
        category = st.selectbox("Exercise Category", list(categories.keys()))
        
        if category == "Custom":
            exercise = st.text_input("Enter Custom Exercise")
        else:
            exercise = st.selectbox("Exercise", categories[category])
    
    with col2:
        sets = st.number_input("Sets", min_value=1)
        reps = st.number_input("Reps", min_value=1)
        weight = st.number_input("Weight (kg)", min_value=0.0)
        
    notes = st.text_area("Notes (optional)")
    
    if st.form_submit_button("Log Workout"):
        workout = {
            'date': date,
            'category': category,
            'exercise': exercise,
            'sets': sets,
            'reps': reps,
            'weight': weight,
            'notes': notes,
            'timestamp': datetime.now()
        }
        st.session_state.workout_logs.append(workout)
        
        # Get AI feedback on form
        prompt = f"""Analyze this exercise: {exercise} with {sets} sets of {reps} reps at {weight}kg.
        Provide quick form tips, safety advice, and suggestions for progression."""
        
        feedback = stream_response(prompt)
        feedback= re.sub(r'<.*?>', '',feedback)
        
        # Remove special markers
        feedback= feedback.replace("<think>", "").replace("</think>", "").replace("*","").strip()
        st.info("AI Form Tips:\n" + feedback)

# Display workout history
if st.session_state.workout_logs:
    st.subheader("Workout History")
    
    # Convert logs to DataFrame
    df = pd.DataFrame(st.session_state.workout_logs)
    df['volume'] = df['sets'] * df['reps'] * df['weight']
    
    # Filtering options
    col1, col2 = st.columns(2)
    with col1:
        filter_category = st.multiselect(
            "Filter by Category",
            options=list(categories.keys()),
            default=list(categories.keys())
        )
    
    with col2:
        filter_exercise = st.multiselect(
            "Filter by Exercise",
            options=df['exercise'].unique(),
            default=df['exercise'].unique()
        )
    
    # Apply filters
    filtered_df = df[
        (df['category'].isin(filter_category)) &
        (df['exercise'].isin(filter_exercise))
    ]
    
    # Display filtered data
    st.dataframe(filtered_df.sort_values('date', ascending=False))
    
    # Visualize progress
    st.subheader("Progress Visualization")
    exercise_select = st.selectbox("Select Exercise for Visualization", df['exercise'].unique())
    
    exercise_data = df[df['exercise'] == exercise_select]
    
    if not exercise_data.empty:
        fig, ax = plt.subplots(2, 1, figsize=(10, 8))





        
        
        # Volume progress
        ax[0].plot(exercise_data['date'], exercise_data['volume'], marker='o')
        ax[0].set_title(f'{exercise_select} - Volume Progress')
        ax[0].set_xlabel('Date')
        ax[0].set_ylabel('Volume (kg)')
        
        # Weight progress
        ax[1].plot(exercise_data['date'], exercise_data['weight'], marker='o', color='green')
        ax[1].set_title(f'{exercise_select} - Weight Progress')
        ax[1].set_xlabel('Date')
        ax[1].set_ylabel('Weight (kg)')
        
        plt.tight_layout()
        st.pyplot(fig)
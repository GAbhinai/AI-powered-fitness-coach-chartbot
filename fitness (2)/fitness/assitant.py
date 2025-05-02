import streamlit as st
import pandas as pd
import ollama
from datetime import datetime
import matplotlib.pyplot as plt

st.set_page_config(page_title="Nutrition Assistant", page_icon="🍎")

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

st.title("Nutrition Assistant")

if 'current_user' not in st.session_state or not st.session_state.current_user:
    st.warning("Please login to access this feature!")
    st.switch_page("0_🏠_Home.py")

# Initialize nutrition logs if not exists
if 'nutrition_logs' not in st.session_state:
    st.session_state.nutrition_logs = []

# Create tabs for different features
tab1, tab2, tab3 = st.tabs(["Meal Logger", "Meal Suggestions", "Nutrition Analysis"])

with tab1:
    st.header("Meal Logger")
    
    with st.form("meal_log"):
        col1, col2 = st.columns(2)
        
        with col1:
            meal_date = st.date_input("Date")
            meal_time = st.selectbox("Meal Time", ["Breakfast", "Lunch", "Dinner", "Snack"])
            food_item = st.text_input("Food Item")
        
        with col2:
            calories = st.number_input("Calories", min_value=0)
            protein = st.number_input("Protein (g)", min_value=0)
            carbs = st.number_input("Carbs (g)", min_value=0)
            fats = st.number_input("Fats (g)", min_value=0)
        
        notes = st.text_area("Notes (optional)")
        
        if st.form_submit_button("Log Meal"):
            meal_data = {
                'date': meal_date,
                'time': meal_time,
                'food': food_item,
                'calories': calories,
                'protein': protein,
                'carbs': carbs,
                'fats': fats,
                'notes': notes,
                'timestamp': datetime.now()
            }
            st.session_state.nutrition_logs.append(meal_data)
            st.success("Meal logged successfully!")

with tab2:
    st.header("Meal Suggestions")
    
    meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack"])
    dietary_prefs = st.text_input("Dietary Preferences (e.g., vegetarian, low-carb)")
    target_calories = st.number_input("Target Calories", min_value=0)
    
    if st.button("Get Meal Suggestions"):
        prompt = f"""Suggest 3 healthy {meal_type.lower()} options that are:
        - {dietary_prefs} friendly
        - Approximately {target_calories} calories
        - Include macronutrient breakdown
        - Easy to prepare
        - Include main ingredients and basic preparation steps
        """
        suggestions = stream_response(prompt)
        st.write(suggestions)

with tab3:
    st.header("Nutrition Analysis")
    
    if st.session_state.nutrition_logs:
        df = pd.DataFrame(st.session_state.nutrition_logs)
        
        # Date range filter
        date_range = st.date_input(
            "Select Date Range",
            value=(df['date'].min(), df['date'].max()),
            key="date_range",
            max_value=datetime.now()
        )
        
        # Filter data by date range
        mask = (df['date'] >= date_range[0]) & (df['date'] <= date_range[1])
        filtered_df = df.loc[mask]
        
        # Daily summary
        daily_summary = filtered_df.groupby('date').agg({
            'calories': 'sum',
            'protein': 'sum',
            'carbs': 'sum',
            'fats': 'sum'
        }).reset_index()
        
        st.subheader("Daily Nutrition Summary")
        st.dataframe(daily_summary)
        
        # Visualizations
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))
        
        # Daily calories plot
        ax1.plot(daily_summary['date'], daily_summary['calories'], marker='o')
        ax1.set_title('Daily Calorie Intake')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Calories')
        
        # Macronutrient distribution
        avg_macros = daily_summary[['protein', 'carbs', 'fats']].mean()
        ax2.pie(avg_macros, 
                labels=['Protein', 'Carbs', 'Fats'],
                autopct='%1.1f%%')
        ax2.set_title('Average Macronutrient Distribution')
        
        plt.tight_layout()
        st.pyplot(fig)
        
        # Meal timing analysis
        st.subheader("Meal Timing Analysis")
        meal_timing = filtered_df.groupby('time')['calories'].agg(['mean', 'count']).round(1)
        st.dataframe(meal_timing)
        
        # Get AI analysis
        avg_calories = daily_summary['calories'].mean()
        avg_protein = daily_summary['protein'].mean()
        prompt = f"""Analyze this nutrition data:
        Average daily calories: {avg_calories:.0f}
        Average daily protein: {avg_protein:.0f}g
        
        Provide insights on:
        1. Overall calorie and macro balance
        2. Meal timing distribution
        3. Suggestions for improvement
        """
        
        analysis = stream_response(prompt)
        st.subheader("AI Nutrition Analysis")
        st.write(analysis)
    else:
        st.info("No nutrition data available. Start logging your meals to see analysis!")
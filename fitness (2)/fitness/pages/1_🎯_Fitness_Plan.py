import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import ollama
import re

st.set_page_config(page_title="Fitness Plan Generator", page_icon="🎯")

# Navigation buttons
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    if st.button("← Back to Home"):
        st.switch_page("0_🏠_Home.py")
 
with col3:
    if st.button("Logout"):
        st.session_state.current_user = None
        st.switch_page("0_🏠_Home.py")

st.title("Fitness Plan Generator")

if 'current_user' not in st.session_state or not st.session_state.current_user:
    st.warning("Please login to access this feature!")
    st.switch_page("0_🏠_Home.py")

def stream_response(prompt):
    response = ''
    stream = ollama.chat(model='deepseek-r1:1.5b', messages=[{'role': 'user', 'content': prompt}], stream=True)
    for chunk in stream:
        response += chunk['message']['content']
        print(chunk['message']['content'], end='', flush=True)
    return response

# Inputs
current_weight = st.number_input("Current Weight (kg)", min_value=0.0, step=0.1)
target_weight = st.number_input("Target Weight (kg)", min_value=0.0, step=0.1)
height = st.number_input("Height (cm)", min_value=0)
age = st.number_input("Age", min_value=0)
gender = st.selectbox("Gender", ["Male", "Female"])
activity_level = st.selectbox("Activity Level", 
                            ["Sedentary", "Lightly Active", "Moderately Active", 
                             "Very Active", "Extra Active"])
dietary_preferences = st.text_input("Dietary Preferences (e.g., Vegan, Vegetarian, Non-Vegetarian)")

if st.button("Generate Fitness Plan"):
    # Calculate BMI
    bmi = current_weight / ((height / 100) ** 2)
    
    # Generate prompt for the chatbot
    prompt = f"""User Information:
    Gender: {gender}
    Age: {age}
    Current Weight: {current_weight} kg
    Target Weight: {target_weight} kg
    Height: {height} cm
    BMI: {bmi:.2f}
    Activity Level: {activity_level}
    Dietary Preferences: {dietary_preferences}
    
    Generate a detailed fitness and nutrition plan to achieve the target weight. Include:
    1. Weekly workout schedule with specific exercises
    2. Daily calorie targets
    3. Macronutrient distribution
    4. Meal timing recommendations
    5. Supplement suggestions (if necessary)
    6. Recovery and rest guidelines
    7. Progress tracking metrics"""
    
    response = stream_response(prompt=prompt)
    
    # Save the plan to user's data
    if 'fitness_plans' not in st.session_state:
        st.session_state.fitness_plans = []
    
    plan_data = {
        'date': pd.Timestamp.now(),
        'plan': response,
        'current_weight': current_weight,
        'target_weight': target_weight,
        'bmi': bmi
    }
    st.session_state.fitness_plans.append(plan_data)
    
    # Display the plan
    # Remove HTML tags
    response = re.sub(r'<.*?>', '', response)
    
    # Remove special markers
    response = response.replace("<think>", "").replace("</think>", "").replace("*","").strip()

    st.write("**Your Personalized Fitness Plan:**")
    st.write(response)
    
    # Visualize data
    st.write("**BMI Calculation:**")
    st.write(f"Your BMI is: {bmi:.2f}")
    
    # Calculate recommended calorie intake
    if gender == "Male":
        bmr = 88.362 + (13.397 * current_weight) + (4.799 * height) - (5.677 * age)
    else:
        bmr = 447.593 + (9.247 * current_weight) + (3.098 * height) - (4.330 * age)
    
    activity_multipliers = {
        "Sedentary": 1.2,
        "Lightly Active": 1.375,
        "Moderately Active": 1.55,
        "Very Active": 1.725,
        "Extra Active": 1.9
    }
    
    maintenance_calories = bmr * activity_multipliers[activity_level]

    # Adjust calories based on goal
    if target_weight < current_weight:
        target_calories = maintenance_calories - 500  # Caloric deficit
    elif target_weight > current_weight:
        target_calories = maintenance_calories + 500  # Caloric surplus
    else:
        target_calories = maintenance_calories
    
    # Calculate macronutrient distribution
    protein = (target_calories * 0.3) / 4  # 30% protein
    carbs = (target_calories * 0.4) / 4    # 40% carbs
    fats = (target_calories * 0.3) / 9     # 30% fats
    
    # Display nutritional breakdown
    st.write("**Daily Nutritional Targets:**")
    nutritional_data = {
        "Nutrient": ["Calories", "Protein (g)", "Carbohydrates (g)", "Fats (g)"],
        "Amount": [round(target_calories), round(protein), round(carbs), round(fats)]
    }
    st.table(pd.DataFrame(nutritional_data))
    
    # Create pie chart of macronutrient distribution
    fig, ax = plt.subplots()
    






















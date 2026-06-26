import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="July Burn Challenge", layout="wide")

st.title("🎯 Ultimate Fitness, Calorie & Workout Tracker")

# Sidebar for goal setting
st.sidebar.header("📋 Your Goal Profile")
current_weight = st.sidebar.number_input("Current Weight (kg)", value=71.0, step=0.1)
target_weight = st.sidebar.number_input("Target Weight (kg)", value=65.0, step=0.1)
daily_target_budget = st.sidebar.number_input("Daily Net Calorie Target (kcal)", value=1500, step=50)

# --- MASSIVE FOOD DATABASE (Calories per 1 Gram) ---
FOOD_DB = {
    # --- Your Specific Staples ---
    "Pintola Chocolate Oats": 4.16,  # 416 kcal per 100g (208 kcal per 50g)
    "White Rice (Cooked)": 1.30,
    "Brown Rice (Cooked)": 1.11,
    "Roti / Chapati (1 normal ~ 40g)": 2.75,
    "Paratha (Plain)": 2.90,
    "Dal (Tadka/Fry cooked)": 0.85,
    "Khichdi": 1.20,
    "Poha": 1.30,
    "Dalia": 0.95,
    
    # --- Proteins & Dairy ---
    "Chicken Breast (Raw)": 1.65,
    "Egg (Whole, 1 large ~ 50g)": 1.55,
    "Egg White (1 large ~ 33g)": 0.52,
    "Paneer (Raw)": 2.65,
    "Tofu": 0.76,
    "Soya Chunks (Dry)": 3.45,
    "Whey Protein (1 scoop ~ 33g)": 3.60,
    "Greek Yogurt (Plain)": 0.59,
    "Milk (Full Cream)": 0.62,
    "Milk (Toned)": 0.42,
    
    # --- Indian Meals & Dishes ---
    "Chicken Biryani": 1.50,
    "Veg Biryani": 1.35,
    "Mutton Biryani": 1.80,
    "Butter Chicken": 1.95,
    "Paneer Butter Masala": 1.85,
    "Chole Masala": 1.40,
    "Rajma Masala": 1.25,
    "Aloo Paratha (With Butter)": 2.10,
    "Idli (1 medium ~ 40g)": 1.00,
    "Dosa (Plain)": 1.60,
    "Sambar": 0.50,
    
    # --- Fast Food & "Junk" Food ---
    "Chole Bhature": 2.80,
    "Samosa (1 normal ~ 50g)": 3.10,
    "Pizza (Cheese/Veg/Pepperoni)": 2.65,
    "Burger (Veg Patty)": 2.20,
    "Burger (Chicken Patty)": 2.50,
    "French Fries": 3.12,
    "Momos (Veg Steamed)": 1.20,
    "Momos (Chicken Fried)": 2.40,
    "Noodles / Chow Mein": 1.60,
    "Potato Chips": 5.36,
    "Milk Chocolate": 5.35,
    "Ice Cream (Vanilla)": 2.07,
    
    # --- Fruits & Vegetables ---
    "Banana": 0.89,
    "Apple": 0.52,
    "Mango": 0.60,
    "Watermelon": 0.30,
    "Orange": 0.47,
    "Potato (Boiled)": 0.87,
    "Cucumber": 0.15,
    "Salad (Mixed Greens)": 0.20
}

# --- MASSIVE EXERCISE DATABASE (Calories burned per 1 Minute) ---
EXERCISE_DB = {
    # --- Home & Bodyweight Workouts ---
    "Push-ups (Moderate intensity)": 7.0,
    "Squats (Bodyweight)": 6.5,
    "Plank": 4.5,
    "Burpees (High intensity)": 9.5,
    "Jumping Jacks": 8.0,
    "Mountain Climbers": 8.5,
    "Lunges": 6.0,
    "Home HIIT Workout": 9.0,
    "Yoga / Stretching": 3.5,
    "Free-weight Dumbbell Circuit": 6.0,
    
    # --- Cardio & Outdoor Activities ---
    "Walking (Normal pace ~ 4 km/h)": 4.0,
    "Walking (Brisk / Fast pace)": 5.5,
    "Running / Jogging (Moderate)": 10.0,
    "Swimming (Leisurely/Moderate)": 8.0,
    "Swimming (Vigorous / Laps)": 11.0,
    "Cycling (Casual)": 6.5,
    "Bicycling (Stationary)": 7.5,
    "Skipping Rope / Jump Rope": 11.0,
    "Stair Climbing": 8.5,
    "Gym Weightlifting (General)": 5.5
}

if "food_logs" not in st.session_state:
    st.session_state.food_logs = []
if "workout_logs" not in st.session_state:
    st.session_state.workout_logs = []

# --- LAYOUT INTERFACE ---
col_left, col_right = st.columns(2)

with col_left:
    st.header("🍎 Log Your Intake")
    
    tab1, tab2 = st.tabs(["Database Search", "Quick Manual Entry"])
    
    with tab1:
        food_search = st.text_input("🔍 Search food items...", "", placeholder="Type to filter (e.g., Pintola, Biryani, Eggs)...")
        filtered_foods = [item for item in FOOD_DB.keys() if food_search.lower() in item.lower()]
        
        if not filtered_foods:
            st.warning("No matches found.")
            selected_food = None
        else:
            selected_food = st.selectbox("Select matching food item", filtered_foods)
        
        grams = st.number_input("Enter weight in grams (g)", min_value=1, value=50, step=5)
        
        if st.button("Log Selection", use_container_width=True, disabled=(selected_food is None)):
            calculated_cal = int(FOOD_DB[selected_food] * grams)
            st.session_state.food_logs.append({
                "Item": f"{selected_food} ({grams}g)", 
                "Calories": calculated_cal, 
                "Time": datetime.datetime.now().strftime("%H:%M")
            })
            st.success(f"Logged {selected_food}! {grams}g = {calculated_cal} kcal")

    with tab2:
        manual_food = st.text_input("Item Name", placeholder="e.g., Homemade Special Dish")
        manual_cal = st.number_input("Estimated Calories (kcal)", min_value=0, step=10, key="manual_food_cal")
        if st.button("Log Manual Food", use_container_width=True):
            if manual_food:
                st.session_state.food_logs.append({
                    "Item": manual_food, 
                    "Calories": manual_cal, 
                    "Time": datetime.datetime.now().strftime("%H:%M")
                })
                st.success(f"Logged {manual_food} ({manual_cal} kcal)!")

with col_right:
    st.header("💪 Log Your Exercise")
    
    tab3, tab4 = st.tabs(["Workout Search", "Quick Manual Entry"])
    
    with tab3:
        ex_search = st.text_input("🔍 Search exercises...", "", placeholder="Type to filter (e.g., Pushups, Swimming, Walking)...")
        filtered_exercises = [ex for ex in EXERCISE_DB.keys() if ex_search.lower() in ex.lower()]
        
        if not filtered_exercises:
            st.warning("No matches found.")
            selected_ex = None
        else:
            selected_ex = st.selectbox("Select matching exercise", filtered_exercises)
            
        minutes = st.number_input("Duration in minutes", min_value=1, value=30, step=5)
        
        if st.button("Log Workout Selection", use_container_width=True, disabled=(selected_ex is None)):
            calculated_burn = int(EXERCISE_DB[selected_ex] * minutes)
            st.session_state.workout_logs.append({
                "Activity": f"{selected_ex} ({minutes} mins)", 
                "Burned": calculated_burn, 
                "Time": datetime.datetime.now().strftime("%H:%M")
            })
            st.success(f"Logged {selected_ex}! {minutes} mins = -{calculated_burn} kcal")

    with tab4:
        manual_ex = st.text_input("Exercise Name", placeholder="e.g., Playing Cricket")
        manual_burn = st.number_input("Estimated Burned (kcal)", min_value=0, step=10, key="manual_ex_cal")
        if st.button("Log Manual Workout", use_container_width=True):
            if manual_ex:
                st.session_state.workout_logs.append({
                    "Activity": manual_ex, 
                    "Burned": manual_burn, 
                    "Time": datetime.datetime.now().strftime("%H:%M")
                })
                st.success(f"Logged {manual_ex} (-{manual_burn} kcal)!")

st.divider()

# --- DASHBOARD METRICS ---
st.header("📊 Today's Progress Dashboard")

total_gained = sum(log["Calories"] for log in st.session_state.food_logs)
total_burned = sum(log["Burned"] for log in st.session_state.workout_logs)
net_calories = total_gained - total_burned
calories_remaining = daily_target_budget - net_calories

m1, m2, m3, m4 = st.columns(4)
m1.metric("Food Intake", f"{total_gained} kcal")
m2.metric("Exercise Burned", f"{total_burned} kcal")
m3.metric("Net Balance", f"{net_calories} kcal")

if calories_remaining >= 0:
    m4.metric("Calories Remaining", f"{calories_remaining} kcal", delta=f"{calories_remaining} left")
else:
    m4.metric("Calories Remaining", f"{calories_remaining} kcal", delta=f"{abs(calories_remaining)} over budget", delta_color="inverse")

st.subheader("Today's Activity Log History")
log_col1, log_col2 = st.columns(2)

with log_col1:
    if st.session_state.food_logs:
        st.dataframe(pd.DataFrame(st.session_state.food_logs), use_container_width=True, hide_index=True)
    else:
        st.info("No food logged yet today.")

with log_col2:
    if st.session_state.workout_logs:
        st.dataframe(pd.DataFrame(st.session_state.workout_logs), use_container_width=True, hide_index=True)
    else:
        st.info("No exercises logged yet today.")
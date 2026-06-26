import streamlit as st
import pandas as pd
import datetime
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="July Burn Challenge", layout="wide")

st.title("🎯 Your Personal Monthly Fitness Tracker")

# --- GOAL BUDGETS ---
st.sidebar.header("📋 Your Goal Profile")
daily_target_budget = st.sidebar.number_input("Daily Net Calorie Target (kcal)", value=1500, step=50)

# --- GOOGLE SHEETS CONNECTION ---
# Paste your shared Google Sheet link here inside the quotes
SHEET_URL = "https://docs.google.com/spreadsheets/d/197CJ3z4bCv_g5UXPkg0hveZ_TJt2ogv7vDePOzwh-cw/edit?usp=sharing"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_food_all = conn.read(spreadsheet=SHEET_URL, ttl=0, worksheet="Food Logs")
    df_workout_all = conn.read(spreadsheet=SHEET_URL, ttl=0, worksheet="Workout Logs")
except Exception:
    df_food_all = pd.DataFrame(columns=["Date", "Item", "Calories", "Time"])
    df_workout_all = pd.DataFrame(columns=["Date", "Activity", "Burned", "Time"])

# Ensure columns exist if sheet is empty
if df_food_all.empty or "Date" not in df_food_all.columns:
    df_food_all = pd.DataFrame(columns=["Date", "Item", "Calories", "Time"])
if df_workout_all.empty or "Date" not in df_workout_all.columns:
    df_workout_all = pd.DataFrame(columns=["Date", "Activity", "Burned", "Time"])

# --- DATE SELECTION BAR ---
st.divider()
selected_date = st.date_input("📅 Select Date to View/Log History", datetime.date.today())
date_str = selected_date.strftime("%Y-%m-%d")

# --- FILTER DATA FOR SELECTED DATE ---
df_food_today = df_food_all[df_food_all["Date"] == date_str]
df_workout_today = df_workout_all[df_workout_all["Date"] == date_str]

# --- DATABASES ---
FOOD_DB = {
    "Pintola Chocolate Oats": 4.16,
    "White Rice (Cooked)": 1.30,
    "Brown Rice (Cooked)": 1.11,
    "Roti / Chapati (1 normal ~ 40g)": 2.75,
    "Paratha (Plain)": 2.90,
    "Dal (Tadka/Fry cooked)": 0.85,
    "Chicken Biryani": 1.50,
    "Veg Biryani": 1.35,
    "Mutton Biryani": 1.80,
    "Pizza (Cheese/Veg/Pepperoni)": 2.65,
    "Burger (Veg Patty)": 2.20,
    "French Fries": 3.12,
    "Momos (Veg Steamed)": 1.20,
    "Banana": 0.89,
    "Apple": 0.52
}

EXERCISE_DB = {
    "Push-ups (Moderate intensity)": 7.0,
    "Squats (Bodyweight)": 6.5,
    "Plank": 4.5,
    "Burpees (High intensity)": 9.5,
    "Walking (Normal pace ~ 4 km/h)": 4.0,
    "Walking (Brisk / Fast pace)": 5.5,
    "Running / Jogging (Moderate)": 10.0,
    "Swimming (Leisurely/Moderate)": 8.0,
    "Swimming (Vigorous / Laps)": 11.0
}

# --- INTERFACE LAYOUT ---
col_left, col_right = st.columns(2)

with col_left:
    st.header("🍎 Log Food Intake")
    food_search = st.text_input("🔍 Search food...", "", placeholder="e.g., Pintola, Biryani...")
    filtered_foods = [item for item in FOOD_DB.keys() if food_search.lower() in item.lower()]
    
    if filtered_foods:
        selected_food = st.selectbox("Select matching food", filtered_foods)
        grams = st.number_input("Enter weight (g)", min_value=1, value=50, step=5)
        
        if st.button("Log Food to Cloud", use_container_width=True):
            cal = int(FOOD_DB[selected_food] * grams)
            new_row = pd.DataFrame([{"Date": date_str, "Item": f"{selected_food} ({grams}g)", "Calories": cal, "Time": datetime.datetime.now().strftime("%H:%M")}]).dropna(how='all')
            df_updated = pd.concat([df_food_all, new_row], ignore_index=True)
            conn.update(spreadsheet=SHEET_URL, data=df_updated, worksheet="Food Logs")
            st.success("Food logged successfully to cloud!")
            st.rerun()

with col_right:
    st.header("💪 Log Exercise")
    ex_search = st.text_input("🔍 Search exercise...", "", placeholder="e.g., Pushups, Swimming...")
    filtered_exercises = [ex for ex in EXERCISE_DB.keys() if ex_search.lower() in ex.lower()]
    
    if filtered_exercises:
        selected_ex = st.selectbox("Select matching exercise", filtered_exercises)
        minutes = st.number_input("Duration (mins)", min_value=1, value=30, step=5)
        
        if st.button("Log Workout to Cloud", use_container_width=True):
            burn = int(EXERCISE_DB[selected_ex] * minutes)
            new_row = pd.DataFrame([{"Date": date_str, "Activity": f"{selected_ex} ({minutes}m)", "Burned": burn, "Time": datetime.datetime.now().strftime("%H:%M")}]).dropna(how='all')
            df_updated = pd.concat([df_workout_all, new_row], ignore_index=True)
            conn.update(spreadsheet=SHEET_URL, data=df_updated, worksheet="Workout Logs")
            st.success("Workout logged successfully to cloud!")
            st.rerun()

st.divider()

# --- HISTORICAL DAILY PROGRESS DASHBOARD ---
st.header(f"📊 Dashboard Summary for Date: {date_str}")

total_gained = int(df_food_today["Calories"].astype(float).sum()) if not df_food_today.empty else 0
total_burned = int(df_workout_today["Burned"].astype(float).sum()) if not df_workout_today.empty else 0
net_calories = total_gained - total_burned
calories_remaining = daily_target_budget - net_calories

m1, m2, m3, m4 = st.columns(4)
m1.metric("Food Intake", f"{total_gained} kcal")
m2.metric("Exercise Burned", f"{total_burned} kcal")
m3.metric("Net Balance", f"{net_calories} kcal")
m4.metric("Calories Remaining", f"{calories_remaining} kcal")

# History Tables for selected date
log_col1, log_col2 = st.columns(2)
with log_col1:
    st.subheader("Food Log History")
    if not df_food_today.empty:
        st.dataframe(df_food_today[["Item", "Calories", "Time"]], use_container_width=True, hide_index=True)
    else:
        st.info("No food records found for this date.")

with log_col2:
    st.subheader("Workout Log History")
    if not df_workout_today.empty:
        st.dataframe(df_workout_today[["Activity", "Burned", "Time"]], use_container_width=True, hide_index=True)
    else:
        st.info("No workout records found for this date.")

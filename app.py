import streamlit as st
import pandas as pd
import datetime
import requests
import json

st.set_page_config(page_title="July Burn Challenge", layout="wide")

st.title("🎯 Your Personal Monthly Fitness Tracker")

# --- GOAL BUDGETS ---
st.sidebar.header("📋 Your Goal Profile")
daily_target_budget = st.sidebar.number_input("Daily Net Calorie Target (kcal)", value=1500, step=50)

# --- CONNECTIONS ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/197CJ3z4bCv_g5UXPkg0hveZ_TJt2ogv7vDePOzwh-cw/edit?usp=sharing"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzT3dpTjsSHpdJsnQTu8k9EhwrUwwEcuywkjmEdViwV_QfIAC2ZQaIi1GHhWCSFZNl0Kw/exec"

# Safe function to load data directly via CSV export rules
def load_sheet_data(sheet_url, worksheet_name):
    try:
        csv_url = sheet_url.split("/edit")[0] + f"/gviz/tq?tqx=out:csv&sheet={worksheet_name.replace(' ', '%20')}"
        return pd.read_csv(csv_url)
    except Exception:
        if "Food" in worksheet_name:
            return pd.DataFrame(columns=["Date", "Item", "Calories", "Time"])
        return pd.DataFrame(columns=["Date", "Activity", "Burned", "Time"])

df_food_all = load_sheet_data(SHEET_URL, "Food Logs")
df_workout_all = load_sheet_data(SHEET_URL, "Workout Logs")

# Clean formatting constraints
for df in [df_food_all, df_workout_all]:
    if df.empty:
        continue
    if "Date" not in df.columns:
        df["Date"] = pd.Series(dtype='str')

# --- DATE SELECTION BAR ---
st.divider()
selected_date = st.date_input("📅 Select Date to View/Log History", datetime.date.today())
date_str = selected_date.strftime("%Y-%m-%d")

# --- FILTER DATA FOR SELECTED DATE ---
df_food_today = df_food_all[df_food_all["Date"].astype(str).str.contains(date_str)] if not df_food_all.empty else pd.DataFrame()
df_workout_today = df_workout_all[df_workout_all["Date"].astype(str).str.contains(date_str)] if not df_workout_all.empty else pd.DataFrame()

# --- ADVANCED DYNAMIC FOOD DATABASE ---
FOOD_DB = {
    "Pintola Chocolate Oats": (4.16, "grams"),
    "White Rice (Cooked)": (1.30, "grams"),
    "Brown Rice (Cooked)": (1.11, "grams"),
    "Dal (Tadka/Fry cooked)": (0.85, "grams"),
    "Chicken Biryani": (1.50, "grams"),
    "Veg Biryani": (1.35, "grams"),
    "Mutton Biryani": (1.80, "grams"),
    "Chicken Breast (Cooked)": (1.65, "grams"),
    "Paneer (Raw/Cooked)": (2.95, "grams"),
    "French Fries": (3.12, "grams"),
    "Roti / Chapati (Normal)": (110.0, "quantity"),
    "Paratha (Plain)": (180.0, "quantity"),
    "Egg (Whole Boiled)": (78.0, "quantity"),
    "Egg White": (17.0, "quantity"),
    "Banana (Medium)": (105.0, "quantity"),
    "Apple (Medium)": (95.0, "quantity"),
    "Pizza Slice": (265.0, "quantity"),
    "Burger (Veg Patty)": (290.0, "quantity"),
    "Momos (Veg Steamed - 1 Pc)": (35.0, "quantity"),
    "Full Cream Milk": (0.62, "ml"),
    "Toned Milk": (0.45, "ml"),
    "Protein Shake (Water base)": (0.40, "ml"),
    "Fresh Orange Juice": (0.45, "ml"),
    "Dahi (Curd)": (0.60, "grams"),
    "Aloo Sabji": (0.90, "grams"),
    "Bhindi Masala (Okra)": (0.80, "grams"),
    "Rajma Chawal": (1.20, "grams"),
    "Aloo Paratha": (210.0, "quantity"),
    "Mango Shake": (0.85, "ml"),
}

EXERCISE_DB = {
    "Push-ups": 7.0,
    "Squats": 6.5,
    "Plank": 4.5,
    "Walking (Normal pace)": 4.0,
    "Walking (Brisk pace)": 5.5,
    "Running / Jogging": 10.0,
    "Swimming": 8.0,
    "Gym Weight Training": 6.0
}

# --- INTERFACE LAYOUT WITH AUTO-CLEARING FORMS ---
col_left, col_right = st.columns(2)

with col_left:
    st.header("🍎 Log Food Intake")
    with st.form(key="food_form", clear_on_submit=True):
        food_search = st.text_input("🔍 Search food items...", "")
        filtered_foods = [item for item in FOOD_DB.keys() if food_search.lower() in item.lower()]
        selected_food = st.selectbox("Select matching item", filtered_foods if filtered_foods else list(FOOD_DB.keys()))
        
        cals_per_unit, unit_type = FOOD_DB[selected_food]
        
        if unit_type == "grams":
            amount = st.number_input("Enter Weight in Grams (g)", min_value=1, value=100)
            display_unit = f"{amount}g"
        elif unit_type == "ml":
            amount = st.number_input("Enter Volume in Milliliters (ml)", min_value=1, value=250)
            display_unit = f"{amount}ml"
        else:
            amount = st.number_input("Enter Quantity (Pieces)", min_value=1, value=1)
            display_unit = f"{amount} Pcs"
            
        submit_food = st.form_submit_button("Log Food to Cloud", use_container_width=True)
        if submit_food:
            cal = int(cals_per_unit * amount)
            payload = {
                "worksheet": "Food Logs",
                "date": date_str,
                "item": f"{selected_food} ({display_unit})",
                "calories": cal,
                "time": datetime.datetime.now().strftime("%H:%M")
            }
            res = requests.post(SCRIPT_URL, data=json.dumps(payload))
            st.success(f"Added: {selected_food} ({cal} kcal) logged online!")
            st.rerun()

with col_right:
    st.header("💪 Log Exercise")
    with st.form(key="exercise_form", clear_on_submit=True):
        selected_ex = st.selectbox("Select exercise activity", list(EXERCISE_DB.keys()))
        minutes = st.number_input("Duration (minutes)", min_value=1, value=30)
        
        submit_ex = st.form_submit_button("Log Workout to Cloud", use_container_width=True)
        if submit_ex:
            burn = int(EXERCISE_DB[selected_ex] * minutes)
            payload = {
                "worksheet": "Workout Logs",
                "date": date_str,
                "activity": f"{selected_ex} ({minutes}m)",
                "burned": burn,
                "time": datetime.datetime.now().strftime("%H:%M")
            }
            res = requests.post(SCRIPT_URL, data=json.dumps(payload))
            st.success(f"Added: {selected_ex} (-{burn} kcal) logged online!")
            st.rerun()

st.divider()

# --- HISTORICAL DAILY PROGRESS DASHBOARD ---
st.header(f"📊 Dashboard Summary for Date: {date_str}")

total_gained = int(pd.to_numeric(df_food_today["Calories"], errors='coerce').sum()) if not df_food_today.empty and "Calories" in df_food_today.columns else 0
total_burned = int(pd.to_numeric(df_workout_today["Burned"], errors='coerce').sum()) if not df_workout_today.empty and "Burned" in df_workout_today.columns else 0
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
    if not df_food_today.empty and "Item" in df_food_today.columns:
        st.dataframe(df_food_today[["Item", "Calories", "Time"]], use_container_width=True, hide_index=True)
    else:
        st.info("No food records found for this date.")

with log_col2:
    st.subheader("Workout Log History")
    if not df_workout_today.empty and "Activity" in df_workout_today.columns:
        st.dataframe(df_workout_today[["Activity", "Burned", "Time"]], use_container_width=True, hide_index=True)
    else:
        st.info("No workout records found for this date.")

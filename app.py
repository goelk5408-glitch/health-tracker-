import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="July Burn Challenge", layout="wide")

st.title("🎯 Your Personal Monthly Fitness Tracker")

# --- GOAL BUDGETS ---
st.sidebar.header("📋 Your Goal Profile")
daily_target_budget = st.sidebar.number_input("Daily Net Calorie Target (kcal)", value=1500, step=50)

# --- GOOGLE SHEETS LINK ---
# Paste your shared Google Sheet URL right here
SHEET_URL = "https://docs.google.com/spreadsheets/d/197CJ3z4bCv_g5UXPkg0hveZ_TJt2ogv7vDePOzwh-cw/edit?usp=sharing"

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
    if "Date" not in df.columns:
        df["Date"] = pd.Series(dtype='str')

# --- DATE SELECTION BAR ---
st.divider()
selected_date = st.date_input("📅 Select Date to View History", datetime.date.today())
date_str = selected_date.strftime("%Y-%m-%d")

# --- FILTER DATA FOR SELECTED DATE ---
df_food_today = df_food_all[df_food_all["Date"].astype(str).str.contains(date_str)] if not df_food_all.empty else pd.DataFrame()
df_workout_today = df_workout_all[df_workout_all["Date"].astype(str).str.contains(date_str)] if not df_workout_all.empty else pd.DataFrame()

# --- ADVANCED DYNAMIC FOOD DATABASE ---
# Format: "Item Name": (Calories_Per_Unit, "Unit Type Name")
FOOD_DB = {
    # Weight Based (g) - Cals per 1 gram
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
    
    # Quantity Based (Pcs) - Cals per 1 piece
    "Roti / Chapati (Normal)": (110.0, "quantity"),
    "Paratha (Plain)": (180.0, "quantity"),
    "Egg (Whole Boiled)": (78.0, "quantity"),
    "Egg White": (17.0, "quantity"),
    "Banana (Medium)": (105.0, "quantity"),
    "Apple (Medium)": (95.0, "quantity"),
    "Pizza Slice": (265.0, "quantity"),
    "Burger (Veg Patty)": (290.0, "quantity"),
    "Momos (Veg Steamed - 1 Pc)": (35.0, "quantity"),
    
    # Liquid Based (ml) - Cals per 1 ml
    "Full Cream Milk": (0.62, "ml"),
    "Toned Milk": (0.45, "ml"),
    "Protein Shake (Water base)": (0.40, "ml"),
    "Fresh Orange Juice": (0.45, "ml"),
    "Coca Cola / Pepsi": (0.43, "ml")
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

# --- INTERFACE LAYOUT ---
col_left, col_right = st.columns(2)

with col_left:
    st.header("🍎 Log Food Intake")
    
    # 1. Search filter
    food_search = st.text_input("🔍 Search food items...", "", placeholder="e.g., Oats, Milk, Roti...")
    filtered_foods = [item for item in FOOD_DB.keys() if food_search.lower() in item.lower()]
    
    if not filtered_foods:
        filtered_foods = list(FOOD_DB.keys())
        
    selected_food = st.selectbox("Select matching item", filtered_foods)
    
    # Get configuration details for the selected food item
    cals_per_unit, unit_type = FOOD_DB[selected_food]
    
    # 2. Dynamic Input Label generation based on unit type
    if unit_type == "grams":
        amount = st.number_input("Enter Weight in Grams (g)", min_value=1, value=100, step=10)
        display_unit = f"{amount}g"
    elif unit_type == "ml":
        amount = st.number_input("Enter Volume in Milliliters (ml)", min_value=1, value=250, step=50)
        display_unit = f"{amount}ml"
    else:
        amount = st.number_input("Enter Quantity (Pieces/Numbers)", min_value=1, value=1, step=1)
        display_unit = f"{amount} Pcs"
        
    if st.button("Calculate Food Calories", use_container_width=True):
        cal = int(cals_per_unit * amount)
        st.info(f"✨ {selected_food} ({display_unit}) = {cal} kcal")
        st.warning("🔗 Note: Check the logs below for historical database tracking summaries.")

with col_right:
    st.header("💪 Log Exercise")
    selected_ex = st.selectbox("Select exercise activity", list(EXERCISE_DB.keys()))
    minutes = st.number_input("Duration (minutes)", min_value=1, value=30, step=5)
    
    if st.button("Calculate Exercise Burn", use_container_width=True):
        burn = int(EXERCISE_DB[selected_ex] * minutes)
        st.info(f"🔥 {selected_ex} ({minutes}m) = {burn} kcal")

st.divider()

# --- HISTORICAL DAILY PROGRESS DASHBOARD ---
st.header(f"📊 Dashboard Summary for Date: {date_str}")

total_gained = int(df_food_today["Calories"].astype(float).sum()) if not df_food_today.empty and "Calories" in df_food_today.columns else 0
total_burned = int(df_workout_today["Burned"].astype(float).sum()) if not df_workout_today.empty and "Burned" in df_workout_today.columns else 0
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

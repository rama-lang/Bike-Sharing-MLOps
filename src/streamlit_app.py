import streamlit as st
import requests

st.set_page_config(page_title="Bike Sharing Predictor", layout="centered")

st.title("🚲 Bike Sharing Prediction System")
st.write("Enter details below to predict how many bikes will be rented!")

# యూజర్ నుంచి ఇన్పుట్ తీసుకోవడానికి కాలమ్స్
col1, col2 = st.columns(2)

with col1:
    season = st.selectbox("Season", [1, 2, 3, 4])
    hr = st.slider("Hour of the Day", 0, 23, 10)
    temp = st.number_input("Temperature (0 to 1 scale)", 0.0, 1.0, 0.5)
    hum = st.number_input("Humidity (0 to 1 scale)", 0.0, 1.0, 0.5)

with col2:
    holiday = st.selectbox("Is it a Holiday?", [0, 1])
    workingday = st.selectbox("Working Day?", [0, 1])
    windspeed = st.number_input("Windspeed", 0.0, 1.0, 0.1)
    weekday = st.selectbox("Weekday (0-6)", [0, 1, 2, 3, 4, 5, 6])

# ప్రిడిక్షన్ బటన్
if st.button("Predict Now"):
    # మన FastAPI కి రిక్వెస్ట్ పంపిస్తున్నాం (పోర్ట్ 9000 గుర్తుంచుకో)
    params = {
        "season": season, "yr": 1, "mnth": 1, "hr": hr, "holiday": holiday,
        "weekday": weekday, "workingday": workingday, "weathersit": 1,
        "temp": temp, "atemp": temp, "hum": hum, "windspeed": windspeed
    }
    
    try:
        response = requests.get("http://localhost:9000/predict", params=params)
        prediction = response.json()["predicted_bikes"]
        st.success(f"🚀 Estimated Bike Rentals: {prediction}")
        st.balloons()
    except Exception as e:
        st.error(f"Error connecting to API: {e}")
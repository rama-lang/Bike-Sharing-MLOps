import streamlit as st
import requests
import pandas as pd
import os  
import streamlit.components.v1 as components

# Page Config
st.set_page_config(page_title="Bike Sharing MLOps Portal", layout="wide")

st.title("🚴 Bike Sharing Prediction & Monitoring")
st.markdown("---")

# Layout columns: Sidebar for inputs, Main for results
col1, col2 = st.columns([1, 2])

with col1:
    st.header("🛠️ Input Features")
    season = st.selectbox("Season", [1, 2, 3, 4], help="1:Spring, 2:Summer, 3:Fall, 4:Winter")
    mnth = st.slider("Month", 1, 12, 6)
    hr = st.slider("Hour of Day", 0, 23, 12)
    temp = st.slider("Temperature (Normalized)", 0.0, 1.0, 0.5)
    hum = st.slider("Humidity (Normalized)", 0.0, 1.0, 0.5)
    
    predict_btn = st.button("🚀 Predict Bike Demand", use_container_width=True)

with col2:
    st.header("📊 Prediction Results")
    if predict_btn:
        # Docker నుండి Windows API కి కనెక్ట్ అవ్వడానికి సరైన URL
        url = "http://host.docker.internal:9999/predict"
        params = {
            "season": season, "mnth": mnth, "hr": hr,
            "holiday": 0, "weekday": 3, "workingday": 1,
            "weathersit": 1, "temp": temp, "atemp": temp,
            "hum": hum, "windspeed": 0.1
        }
        
        try:
            with st.spinner('Calculating demand...'):
                response = requests.get(url, params=params, timeout=5)
                
            if response.status_code == 200:
                res = response.json()
                prediction = res.get('predicted_bikes', 0)
                st.metric(label="Predicted Bikes Needed", value=int(prediction))
                st.balloons()
            else:
                st.error(f"❌ API Error: {response.text}")
        except Exception as e:
            st.error(f"📡 Connection Failed: Make sure api.py is running on port 9999!")

    st.markdown("---")
    
    # --- Monitoring Section ---
    st.header("📈 Model Monitoring")
    st.info("View the latest Data Drift analysis from Evidently AI.")
    
    if st.button("🔍 View Data Drift Report"):
        # 🔥 కొత్త docker-compose Path కి అనుగుణంగా మార్చాను
        #report_path = "/opt/airflow/src/monitoring_report.html" 
        report_path = "monitoring_report.html"
        
        if os.path.exists(report_path):
            try:
                with open(report_path, 'r', encoding='utf-8') as f:
                    html_data = f.read()
                # నేరుగా బ్రౌజర్‌లో HTML రిపోర్ట్‌ని చూపిస్తుంది
                components.html(html_data, height=1000, scrolling=True)
            except Exception as e:
                st.error(f"Error reading report: {e}")
        else:
            st.warning(f"⚠️ Report file not found at: {report_path}")
            st.info("Please run the Airflow DAG first to generate the report.")

# Sidebar status
st.sidebar.markdown(f"""
---
**System Status:**
- **Frontend:** Running (Docker)
- **Shared Path:** `/opt/airflow/src/`
- **Backend API:** http://localhost:9999
- **Database:** PostgreSQL
- **Monitoring:** Evidently AI
""")
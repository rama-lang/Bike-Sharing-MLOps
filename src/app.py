from fastapi import FastAPI
import joblib
import pandas as pd
import yaml
import os

app = FastAPI(title="Bike Sharing Prediction API")

# 1. పాత్ ని కంటైనర్ కి తగ్గట్టు సెట్ చేస్తున్నాం
MODEL_PATH = "models/bike_model.pkl" 

# ఒకవేళ ఫైల్ లేకపోతే ఎర్రర్ రాకుండా జాగ్రత్త
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
    print("✅ Model loaded successfully!")
else:
    # ఒకవేళ అక్కడ లేకపోతే ప్రస్తుత ఫోల్డర్ లో వెతుకు
    model = joblib.load("bike_model.pkl") 

@app.get("/")
def home():
    return {"status": "Success", "message": "Bike Sharing API is live!"}

@app.get("/predict")
def predict(season: int, yr: int, mnth: int, hr: int, holiday: int, 
            weekday: int, workingday: int, weathersit: int, 
            temp: float, atemp: float, hum: float, windspeed: float):
    
    data_dict = {
        'season': [season], 'yr': [yr], 'mnth': [mnth], 'hr': [hr],
        'holiday': [holiday], 'weekday': [weekday], 'workingday': [workingday],
        'weathersit': [weathersit], 'temp': [temp], 'atemp': [atemp],
        'hum': [hum], 'windspeed': [windspeed]
    }

    features = pd.DataFrame(data_dict)
    prediction = model.predict(features)
    
    return {
        "predicted_bikes": int(prediction[0])
    }
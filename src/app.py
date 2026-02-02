from fastapi import FastAPI
import joblib
import pandas as pd
import yaml

app = FastAPI(title = "Bike Shating Prediction API")

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

model = joblib.load(config['model']['save_path'])

@app.get("/")
def home():
    return{"status": "Success" , "message": "Bike Sharing API is live!"}

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
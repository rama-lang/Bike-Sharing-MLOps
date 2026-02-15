import sys
import os
from datetime import datetime
import pandas as pd
from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uvicorn

# --- 1. Prometheus Import ---
from prometheus_fastapi_instrumentator import Instrumentator 

# Path Config
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CURRENT_DIR)
from predict import make_prediction 

app = FastAPI(title="BikesBooking Prediction API")

# --- 2. Initialize Prometheus Instrumentator ---
# ఇది API స్టార్ట్ అవ్వగానే మెట్రిక్స్ ట్రాక్ చేయడం మొదలుపెడుతుంది
Instrumentator().instrument(app).expose(app)

# ✅ Windows నుండి Docker Postgres కి కనెక్ట్ అవ్వాలంటే 'localhost' వాడాలి
DATABASE_URL = "postgresql+psycopg2://airflow:airflow@localhost:5432/airflow"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class PredictionLog(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    season = Column(Integer); mnth = Column(Integer); hr = Column(Integer)
    holiday = Column(Integer); weekday = Column(Integer); workingday = Column(Integer)
    weathersit = Column(Integer); temp = Column(Float); atemp = Column(Float)
    hum = Column(Float); windspeed = Column(Float)
    predicted_cnt = Column(Float)

Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {
        "message": "API Live", 
        "db": "Postgres Connected",
        "monitoring": "Prometheus Enabled at /metrics"
    }

@app.get("/predict")
async def predict(
    season: int = 1, mnth: int = 1, hr: int = 12, 
    holiday: int = 0, weekday: int = 0, workingday: int = 1, 
    weathersit: int = 1, temp: float = 0.5, atemp: float = 0.5, 
    hum: float = 0.5, windspeed: float = 0.0
):
    db = SessionLocal()
    try:
        data_dict = {
            "season": season, "mnth": mnth, "hr": hr,
            "holiday": holiday, "weekday": weekday, "workingday": workingday,
            "weathersit": weathersit, "temp": temp, "atemp": atemp,
            "hum": hum, "windspeed": windspeed
        }
        
        prediction = make_prediction(data_dict)
        predicted_val = max(0, int(round(float(prediction[0]))))

        new_log = PredictionLog(**data_dict, predicted_cnt=float(predicted_val))
        db.add(new_log)
        db.commit()
        print(f"✅ Saved to Postgres: {predicted_val}")
        return {"predicted_bikes": predicted_val}
    except Exception as e:
        print(f"❌ API Error: {str(e)}")
        return {"error": str(e)}
    finally:
        db.close()

if __name__ == "__main__":
    # Windows లో రన్ చేస్తున్నావు కాబట్టి 0.0.0.0 and port 9999 పర్ఫెక్ట్
    uvicorn.run(app, host="0.0.0.0", port=9999)
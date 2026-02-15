import pandas as pd
import os
import joblib
import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import numpy as np
import random
import sys

def train_model():
    # --- 1. CONFIG ---
    if os.path.exists("/opt/airflow"):
        TRACKING_URI = "http://mlflow_server:5000"
        BASE_PATH = "/opt/airflow"
    else:
        TRACKING_URI = "http://localhost:5000"
        BASE_PATH = "."
        
    mlflow.set_tracking_uri(TRACKING_URI)
    mlflow.set_experiment("bike-sharing-experiment")
    
    # --- 2. PATHS ---
    X_train_path = os.path.join(BASE_PATH, "data/processed/X_train.csv")
    y_train_path = os.path.join(BASE_PATH, "data/processed/y_train.csv")
    save_path = os.path.join(BASE_PATH, "models/bike_model.pkl")

    try:
        X_train_raw = pd.read_csv(X_train_path)
        y_train = pd.read_csv(y_train_path)
        features = ['season', 'mnth', 'hr', 'holiday', 'weekday', 'workingday', 'weathersit', 'temp', 'atemp', 'hum', 'windspeed']
        X_train = X_train_raw[[col for col in features if col in X_train_raw.columns]]
        
        with mlflow.start_run(run_name="Airflow_Training_Run") as run:
            model = RandomForestRegressor(n_estimators=random.randint(100, 200), random_state=42)
            model.fit(X_train, y_train.values.ravel())
            
            rmse = np.sqrt(mean_squared_error(y_train, model.predict(X_train)))
            mlflow.log_metric("rmse", rmse)
            mlflow.log_param("n_estimators", model.n_estimators)

            # 🚨 ఇక్కడే మ్యాజిక్! 
            # log_model వాడకుండా నేరుగా artifact లాగా సేవ్ చేస్తున్నాం
            joblib.dump(model, "bike_model.pkl")
            mlflow.log_artifact("bike_model.pkl", artifact_path="model")
            
            # రిజిస్ట్రేషన్ కోసం సింపుల్ API ని వాడుతున్నాం
            model_name = "Bike_Sharing_Model"
            run_id = run.info.run_id
            model_uri = f"runs:/{run_id}/model"
            
            print(f"📦 Registering model from {model_uri}...")
            
            # client ని వాడి నేరుగా రిజిస్టర్ చేయడం (ఇది 404 ని దాటేస్తుంది)
            client = MlflowClient()
            try:
                client.create_registered_model(model_name)
            except:
                pass # ఆల్రెడీ ఉంటే ఇగ్నోర్ చేయ్
                
            res = client.create_model_version(name=model_name, source=model_uri, run_id=run_id)
            current_version = res.version
            
            # Alias సెట్ చేయడం
            client.set_registered_model_alias(model_name, "champion", str(current_version))

            # లోకల్ సేవింగ్ (ముఖ్యంగా api.py కోసం)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            joblib.dump(model, save_path)
            
            print(f"✅ SUCCESS! RMSE: {rmse:.4f} | Version: {current_version}")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    train_model()
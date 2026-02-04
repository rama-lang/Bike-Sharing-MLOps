import pandas as pd
import os
import joblib
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import numpy as np
import random

def train_model():
    # --- 1. SMART CONFIG ---
    if os.path.exists("/opt/airflow"):
        BASE_PATH = "/opt/airflow"
        TRACKING_URI = "http://172.18.0.1:5000"
    else:
        BASE_PATH = "."
        TRACKING_URI = "http://localhost:5000"
        
    mlflow.set_tracking_uri(TRACKING_URI)
    
    try:
        mlflow.set_experiment("Bike_Sharing_Production")
    except Exception:
        mlflow.set_experiment("Bike_Sharing_Production")

    # --- 2. PATHS ---
    X_train_path = os.path.join(BASE_PATH, "data/processed/X_train.csv")
    y_train_path = os.path.join(BASE_PATH, "data/processed/y_train.csv")
    save_path = os.path.join(BASE_PATH, "models/bike_model.pkl")

    if not os.path.exists(X_train_path):
        raise FileNotFoundError(f"❌ డేటా దొరకలేదు రా! Path: {X_train_path}")

    try:
        X_train = pd.read_csv(X_train_path)
        y_train = pd.read_csv(y_train_path)
        
        # --- 3. MLFLOW RUN ---
        with mlflow.start_run(run_name="Airflow_Automated_Training"):
            n_est = random.randint(50, 250) 
            print(f"🚀 Training with n_estimators: {n_est}")
            
            model = RandomForestRegressor(n_estimators=n_est, random_state=42)
            model.fit(X_train, y_train.values.ravel())

            predictions = model.predict(X_train)
            rmse = np.sqrt(mean_squared_error(y_train, predictions))

            # ✅ ఇవి కచ్చితంగా ఈ 'with' బ్లాక్ లోపలే ఉండాలి
            mlflow.log_param("n_estimators", n_est)
            mlflow.log_metric("rmse", rmse)

            # ✅ మోడల్ ని రిజిస్టర్ చేయడం - ఇది కూడా లోపలే ఉండాలి
            mlflow.sklearn.log_model(
                sk_model=model, 
                artifact_path="bike_rf_model",
                registered_model_name="Bike_Sharing_Model"
            )
            
            # --- 4. LOCAL SAVING ---
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            joblib.dump(model, save_path)
            
            print(f"✅ SUCCESS! RMSE: {rmse}")
            print("✅ Model registered in MLflow Registry!")
            
        return rmse

    except Exception as e:
        print(f"❌ ERROR inside train_model: {str(e)}")
        raise e

if __name__ == "__main__":
    train_model()
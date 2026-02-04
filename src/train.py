import pandas as pd
import os
import joblib
import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient # <--- ఇది ముఖ్యం
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import numpy as np
import random

def automated_promotion(model_name, current_rmse, current_version):
    """
    పాత ఛాంపియన్ తో కొత్త మోడల్ ని కంపేర్ చేసి ఆటోమేటిక్ గా ప్రమోట్ చేస్తుంది.
    """
    client = MlflowClient()
    alias = "champion"
    
    try:
        # 1. ప్రస్తుతం ఉన్న ఛాంపియన్ డేటా తేవడం
        champ_ver = client.get_model_version_by_alias(model_name, alias)
        champ_run = client.get_run(champ_ver.run_id)
        champ_rmse = champ_run.data.metrics.get("rmse")
        
        print(f"🏆 Current Champion RMSE: {champ_rmse}")
        print(f"🆕 New Model RMSE: {current_rmse}")

        # 2. కంపారిజన్: కొత్తది బెటర్ అయితే అలియాస్ మార్చు
        if current_rmse < champ_rmse:
            print(f"🚀 Success: New model is better! Moving @champion to Version {current_version}")
            client.set_registered_model_alias(model_name, alias, str(current_version))
        else:
            print("😴 Old champion is still the best. No promotion.")
            
    except Exception:
        # ఒకవేళ అసలు ఛాంపియన్ లేకపోతే (First time)
        print("🥇 No champion found. Setting Version 1 as the first champion!")
        client.set_registered_model_alias(model_name, alias, "1")

def train_model():
    # --- 1. SMART CONFIG ---
    if os.path.exists("/opt/airflow"):
        BASE_PATH = "/opt/airflow"
        TRACKING_URI = "http://172.18.0.1:5000"
    else:
        BASE_PATH = "."
        TRACKING_URI = "http://localhost:5000"
        
    mlflow.set_tracking_uri(TRACKING_URI)
    mlflow.set_experiment("Bike_Sharing_Production")

    # --- 2. PATHS ---
    X_train_path = os.path.join(BASE_PATH, "data/processed/X_train.csv")
    y_train_path = os.path.join(BASE_PATH, "data/processed/y_train.csv")
    save_path = os.path.join(BASE_PATH, "models/bike_model.pkl")

    if not os.path.exists(X_train_path):
        raise FileNotFoundError(f"❌ Data not found: {X_train_path}")

    try:
        X_train = pd.read_csv(X_train_path)
        y_train = pd.read_csv(y_train_path)
        
        # --- 3. MLFLOW RUN ---
        with mlflow.start_run(run_name="Airflow_Automated_Training") as run:
            n_est = random.randint(50, 250) 
            print(f"🚀 Training with n_estimators: {n_est}")
            
            model = RandomForestRegressor(n_estimators=n_est, random_state=42)
            model.fit(X_train, y_train.values.ravel())

            predictions = model.predict(X_train)
            rmse = np.sqrt(mean_squared_error(y_train, predictions))

            mlflow.log_param("n_estimators", n_est)
            mlflow.log_metric("rmse", rmse)

            # మోడల్ రిజిస్టర్ చేయడం
            model_info = mlflow.sklearn.log_model(
                sk_model=model, 
                artifact_path="bike_rf_model",
                registered_model_name="Bike_Sharing_Model"
            )
            
            # రిజిస్టర్ అయ్యాక దాని వెర్షన్ తెలుసుకోవడం
            model_name = "Bike_Sharing_Model"
            # MLflow logic to get the latest version number
            client = MlflowClient()
            model_version_details = client.get_latest_versions(model_name, stages=["None"])
            current_version = model_version_details[0].version

            # --- 4. AUTOMATED PROMOTION ---
            # ఇక్కడ మనం రాసిన లాజిక్ కాల్ అవుతుంది
            automated_promotion(model_name, rmse, current_version)

            # --- 5. LOCAL SAVING ---
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            joblib.dump(model, save_path)
            
            print(f"✅ SUCCESS! RMSE: {rmse} | Version: {current_version}")
            
        return rmse

    except Exception as e:
        print(f"❌ ERROR inside train_model: {str(e)}")
        raise e

if __name__ == "__main__":
    train_model()
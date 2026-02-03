import pandas as pd
import yaml
import os
import joblib
import mlflow
import mlflow.sklearn
import traceback
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

# కంటైనర్ లోపల పాత్స్
CONFIG_PATH = "/opt/airflow/src/config.yaml"
MODELS_DIR = "/opt/airflow/models"

def train_model():
    # 1. వర్కింగ్ డైరెక్టరీ మార్పు
    os.chdir("/opt/airflow")
    
    mlflow.set_experiment("Bike_Sharing_Production")

    if not os.path.exists(CONFIG_PATH):
        print(f"❌ Error: Config file not found at {CONFIG_PATH}")
        return

    with open(CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)
    
    try:
        # 2. డేటా లోడింగ్
        processed_dir = config['data']['processed_dir']
        X_train = pd.read_csv(f"/opt/airflow/{processed_dir}/X_train.csv")
        y_train = pd.read_csv(f"/opt/airflow/{processed_dir}/y_train.csv")
        print(f"✅ Data loaded from {processed_dir}")

        with mlflow.start_run(run_name="Random_Forest_Training"):
            print("🚀 Model training started...........")

            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_train, y_train.values.ravel())

            y_pred = model.predict(X_train)
            mse = mean_squared_error(y_train, y_pred)

            mlflow.log_metric("training_mse", mse)

            # --- ఇక్కడ జాగ్రత్తగా చూడు (ఇండెంట్ కరెక్ట్ గా ఉండాలి) ---
            
            # 3. ఫోల్డర్ క్రియేషన్
            os.makedirs(MODELS_DIR, exist_ok=True)
            
            # 4. పాత్ సెట్టింగ్
            file_name = os.path.basename(config['model']['save_path'])
            final_save_path = os.path.join(MODELS_DIR, file_name)

            print(f"DEBUG: Saving model to {final_save_path}")
            
            # 5. మోడల్ సేవింగ్
            joblib.dump(model, final_save_path)
            mlflow.sklearn.log_model(model, "bike_rf_model")

            print(f"✅ Success! Model saved at: {final_save_path}")
            print(f"📊 MLflow Logged - MSE: {mse}")

    except Exception as e:
        print(f"❌ ERROR OCCURRED: {str(e)}")
        print(traceback.format_exc()) 
        raise e 

if __name__ == "__main__":
    train_model()